#!/usr/bin/env python3
"""Singular backtest for the 220-method Codex system.

Rule
----
For every strategy (scenario) and coin, at most one trade may be open at any
moment.  If a new signal arrives while that coin already has an open trade for
the same strategy, the signal is ignored.  This is enforced across all
timeframes and across long/short sides, so 1h/4h/1d/1w signals can no longer
stack on the same coin.

The folder is intentionally separate from the normal backtest (`backtest.py`,
`results/`).  Outputs are written under `Singular-Backtest/results/`.

Run:
    python Singular-Backtest/prepare_data.py
    python Singular-Backtest/run_singular.py --workers 10

Results:
    results/singular_trades.parquet   accepted singular trades
    results/normal_trades.parquet     all candidate trades (normal engine)
    results/singular_summary.csv      scenario x timeframe metrics
    results/singular_coins.csv        coin-level metrics
    results/singular_results.json     compact payload for dashboard use
"""
from __future__ import annotations

import argparse
import concurrent.futures as cf
import json
import os
import sys
import traceback
import warnings
from pathlib import Path

import numpy as np
import pandas as pd

warnings.filterwarnings(
    "ignore",
    message="Converting to PeriodArray/Index representation will drop timezone information.",
)

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
import backtest as bt  # noqa: E402

EXIT_NAMES = ("timeout", "stop", "ema20_trail")
TF_RANK = {"1h": 0, "4h": 1, "1d": 2, "1w": 3}
SIDE_RANK = {"long": 0, "short": 1}


def parse_scenarios(path: Path) -> list[tuple[int, str]]:
    import re
    text = path.read_text(encoding="utf-8")
    return [(int(a), b) for a, b in re.findall(r"^## (\d{3}) — (.+)$", text, re.M)]


def build_candidates(symbol: str, base: pd.DataFrame, cfg: dict,
                     scenarios: list[tuple[int, str]]) -> pd.DataFrame:
    cost = cfg["fee_rate_per_side"] + cfg["slippage_rate_per_side"]
    risk = cfg["risk_fraction"]
    max_lev = cfg["max_leverage"]
    max_bars = cfg["max_bars_in_trade"]
    rows: list[tuple] = []
    for tf in cfg["timeframes"]:
        try:
            x = bt.indicators(bt.resample(base, tf))
        except Exception:
            continue
        if len(x) < 60:
            continue
        cache: dict = {}
        times = x.open_time.to_numpy()
        opens = x.open.to_numpy()
        highs = x.high.to_numpy()
        lows = x.low.to_numpy()
        closes = x.close.to_numpy()
        atrs = x.atr.to_numpy()
        ema20 = x.ema20.to_numpy()
        for sid, title in scenarios:
            if 161 <= sid <= 180 and tf != "1h":
                continue
            for long in (True, False):
                try:
                    sig = bt.scenario_signal(x, sid, title, long, cache)
                except Exception:
                    continue
                sig = sig.fillna(False).to_numpy(dtype=np.bool_)
                core = bt._simulate_core(
                    opens, highs, lows, closes, atrs, ema20, sig, long,
                    cost, max_bars,
                )
                for a, b, r, reason in core:
                    entry = opens[a] * (1 + cost if long else 1 - cost)
                    stop_pct = (1.5 * atrs[a - 1]) / entry
                    # ATR == 0 artefacts (e.g. a halted/illiquid bar) produce
                    # meaningless R multiples; they are not tradable signals.
                    if not np.isfinite(stop_pct) or stop_pct < 1e-6:
                        continue
                    actual_risk = min(risk, max_lev * stop_pct)
                    rows.append((
                        symbol, tf, sid, title, "long" if long else "short",
                        pd.Timestamp(times[a - 1]), pd.Timestamp(times[a]),
                        pd.Timestamp(times[b]), float(r),
                        float(r * actual_risk), EXIT_NAMES[reason],
                        float(entry), float(stop_pct),
                    ))
    cols = ["symbol", "timeframe", "scenario_id", "scenario", "side",
            "signal_time", "entry_time", "exit_time", "r_multiple", "return",
            "exit_reason", "entry_price", "stop_pct"]
    return pd.DataFrame(rows, columns=cols)


def merge_singular(cand: pd.DataFrame, scope: str) -> pd.DataFrame:
    """Accept a trade only when no other trade of the same strategy/coin is open."""
    if cand.empty:
        return cand.copy()
    cand = cand.copy()
    cand["tf_rank"] = cand["timeframe"].map(TF_RANK).fillna(9).astype(int)
    cand["side_rank"] = cand["side"].map(SIDE_RANK).fillna(9).astype(int)
    key = ["scenario_id"] if scope == "scenario" else ["scenario_id", "timeframe"]
    accepted: list[int] = []
    for _, group in cand.groupby(key, sort=False):
        group = group.sort_values(
            ["signal_time", "tf_rank", "side_rank"], kind="mergesort"
        )
        last_exit = None
        for idx, row in group.iterrows():
            if last_exit is not None and row["signal_time"] < last_exit:
                continue
            accepted.append(idx)
            last_exit = row["exit_time"]
    return cand.loc[sorted(accepted)].drop(columns=["tf_rank", "side_rank"])


def process_symbol(job: tuple) -> dict:
    (symbol, data_file, out_dir, cfg, scenarios, scope, force,
     from_cache) = job
    out_dir = Path(out_dir)
    cand_path = out_dir / "normal_trades" / f"{symbol}.parquet"
    sing_path = out_dir / "singular_trades" / f"{symbol}.parquet"
    if not force and not from_cache and cand_path.exists() and sing_path.exists():
        return {"symbol": symbol, "status": "cached"}
    try:
        if from_cache and cand_path.exists():
            cand = pd.read_parquet(cand_path)
        else:
            base = pd.read_parquet(data_file)
            if base.empty:
                return {"symbol": symbol, "status": "empty"}
            base = (base.sort_values("open_time")
                    .drop_duplicates("open_time").reset_index(drop=True))
            cand = build_candidates(symbol, base, cfg, scenarios)
            cand_path.parent.mkdir(parents=True, exist_ok=True)
            cand.to_parquet(cand_path, index=False, compression="zstd")
        sing = merge_singular(cand, scope)
        sing_path.parent.mkdir(parents=True, exist_ok=True)
        sing.to_parquet(sing_path, index=False, compression="zstd")
        return {"symbol": symbol, "status": "ok",
                "normal": int(len(cand)),
                "singular": int(len(sing))}
    except Exception as exc:
        return {"symbol": symbol, "status": "error", "error": repr(exc),
                "trace": traceback.format_exc(limit=3)}


def _metrics(g: pd.DataFrame) -> dict:
    if g.empty:
        return {
            "trades": 0, "wins": 0, "losses": 0, "win_rate": 0.0,
            "avg_ret": 0.0, "ret2026": 0.0, "avg_r": 0.0,
            "win_hold_h": 0.0, "profit_days": 0, "loss_days": 0,
            "symbols": 0, "compounded": 0.0, "max_loss_r": 0.0,
        }
    win = g["r_multiple"] > 0
    hold = (g["exit_time"] - g["entry_time"]).dt.total_seconds() / 3600.0
    daily = g.groupby(g["exit_time"].dt.floor("D"))["return"].sum()
    y2026 = g[g["exit_time"].dt.year == 2026]
    per_symbol = g.groupby("symbol")["return"].apply(lambda s: float(np.prod(1 + s) - 1))
    return {
        "trades": int(len(g)),
        "wins": int(win.sum()),
        "losses": int((~win).sum()),
        "win_rate": float(win.mean()),
        "avg_ret": float(g["return"].mean() * 100),
        "ret2026": float(y2026["return"].mean() * 100) if len(y2026) else 0.0,
        "avg_r": float(g["r_multiple"].mean()),
        "win_hold_h": float(hold[win].mean()) if win.any() else 0.0,
        "profit_days": int((daily > 0).sum()),
        "loss_days": int((daily < 0).sum()),
        "symbols": int(g["symbol"].nunique()),
        "compounded": float(per_symbol.mean() * 100),
        "max_loss_r": float(g["r_multiple"].min()),
    }


def _blocked(cand: pd.DataFrame, sing: pd.DataFrame, keys: list[str]) -> pd.Series:
    c = cand.groupby(keys, dropna=False).size()
    s = sing.groupby(keys, dropna=False).size() if not sing.empty else pd.Series(dtype=int)
    out = c.subtract(s, fill_value=0).astype(int)
    return out


def _round_floats(obj, nd: int = 4):
    if isinstance(obj, float):
        return round(obj, nd)
    if isinstance(obj, dict):
        return {k: _round_floats(v, nd) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_round_floats(v, nd) for v in obj]
    return obj


def _metric_rows(df: pd.DataFrame, keys: list[str], prefix: str) -> pd.DataFrame:
    rows = []
    if df.empty:
        return pd.DataFrame(columns=keys)
    for key, group in df.groupby(keys, sort=True, observed=True):
        if not isinstance(key, tuple):
            key = (key,)
        row = dict(zip(keys, key))
        row.update({f"{prefix}{k}": v for k, v in _metrics(group).items()})
        rows.append(row)
    return pd.DataFrame(rows)


def _coin_metric_rows(df: pd.DataFrame, prefix: str) -> pd.DataFrame:
    rows = []
    if df.empty:
        return pd.DataFrame(columns=["scenario_id", "timeframe", "symbol"])
    for key, g in df.groupby(["scenario_id", "timeframe", "symbol"],
                             sort=True, observed=True):
        sid, tf, symbol = key
        n = len(g)
        win = g["r_multiple"] > 0
        comp = float(np.prod(1 + g["return"]) - 1) * 100
        rows.append({
            "scenario_id": sid, "timeframe": tf, "symbol": symbol,
            f"{prefix}trades": n,
            f"{prefix}avg_ret": float(g["return"].mean() * 100),
            f"{prefix}win_rate": float(win.mean()),
            f"{prefix}avg_r": float(g["r_multiple"].mean()),
            f"{prefix}compounded": comp,
        })
    return pd.DataFrame(rows)


def _cast_counts(df: pd.DataFrame) -> pd.DataFrame:
    for col in df.columns:
        if col.endswith(("trades", "wins", "losses", "profit_days",
                         "loss_days", "symbols", "combinations")):
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0).astype(int)
    return df


def aggregate(out_dir: Path, scope: str, cfg: dict,
              scenarios: list[tuple[int, str]]) -> dict:
    names = {int(sid): title for sid, title in scenarios}
    cols = ["symbol", "timeframe", "scenario_id", "side", "signal_time",
            "entry_time", "exit_time", "r_multiple", "return", "exit_reason"]

    def load(folder: str) -> pd.DataFrame:
        files = sorted((out_dir / folder).glob("*.parquet"))
        if not files:
            return pd.DataFrame(columns=cols)
        parts = [pd.read_parquet(p, columns=cols) for p in files]
        df = pd.concat(parts, ignore_index=True)
        return df

    normal = load("normal_trades")
    singular = load("singular_trades")

    nm = _metric_rows(normal, ["scenario_id", "timeframe"], "n_")
    sm = _metric_rows(singular, ["scenario_id", "timeframe"], "s_")
    if nm.empty:
        rows = []
    else:
        merged = nm.merge(sm, on=["scenario_id", "timeframe"], how="left")
        metric_cols = [c for c in merged.columns
                       if c not in ("scenario_id", "timeframe")]
        merged[metric_cols] = merged[metric_cols].fillna(0)
        merged = _cast_counts(merged)
        rows = []
        for r in merged.itertuples(index=False):
            d = r._asdict()
            sid = int(d.pop("scenario_id"))
            tf = str(d.pop("timeframe"))
            blocked = int(d["n_trades"] - d["s_trades"])
            rows.append({
                "sid": sid, "name": names.get(sid, ""), "tf": tf,
                "blocked": blocked,
                "blocked_pct": (blocked / d["n_trades"] * 100) if d["n_trades"] else 0.0,
                **d,
            })

    # Coin-level breakdown (used for the "coin coin" drill-down).
    ncoin = _coin_metric_rows(normal, "n_")
    scoin = _coin_metric_rows(singular, "s_")
    if ncoin.empty:
        coins = []
    else:
        cm = ncoin.merge(scoin, on=["scenario_id", "timeframe", "symbol"],
                         how="left")
        fill = [c for c in cm.columns
                if c not in ("scenario_id", "timeframe", "symbol")]
        cm[fill] = cm[fill].fillna(0)
        cm = _cast_counts(cm)
        coins = []
        for r in cm.itertuples(index=False):
            d = r._asdict()
            coins.append({
                "sid": int(d["scenario_id"]), "tf": str(d["timeframe"]),
                "symbol": str(d["symbol"]),
                "blocked": int(d["n_trades"] - d["s_trades"]),
                "n_trades": int(d["n_trades"]),
                "n_avg_ret": float(d["n_avg_ret"]),
                "n_win_rate": float(d["n_win_rate"]),
                "n_compounded": float(d["n_compounded"]),
                "s_trades": int(d["s_trades"]),
                "s_avg_ret": float(d["s_avg_ret"]),
                "s_win_rate": float(d["s_win_rate"]),
                "s_compounded": float(d["s_compounded"]),
            })

    # Scenario totals across timeframes.
    nsc = _metric_rows(normal, ["scenario_id"], "n_")
    ssc = _metric_rows(singular, ["scenario_id"], "s_")
    scenario_rows = []
    if not nsc.empty:
        m = nsc.merge(ssc, on=["scenario_id"], how="left")
        fill = [c for c in m.columns if c != "scenario_id"]
        m[fill] = m[fill].fillna(0)
        m = _cast_counts(m)
        for r in m.itertuples(index=False):
            d = r._asdict()
            sid = int(d.pop("scenario_id"))
            scenario_rows.append({
                "sid": sid, "name": names.get(sid, ""),
                "blocked": int(d["n_trades"] - d["s_trades"]),
                **d,
            })

    def totals(df: pd.DataFrame) -> dict:
        m = _metrics(df)
        m["combinations"] = (int(df.groupby(["scenario_id", "timeframe"]).ngroups)
                             if len(df) else 0)
        return m

    payload = {
        "repo": "Codex-Bulut-Backtests",
        "generated_at": pd.Timestamp.now(tz="UTC").strftime("%Y-%m-%dT%H:%M:%SZ"),
        "rule": ("Aynı stratejide (senaryoda) aynı coin için aynı anda en fazla "
                 "bir açık işlem. Sinyal, işlem açıkken gelirse bloke edilir."),
        "scope": scope,
        "data": {
            "symbols": int(normal["symbol"].nunique()) if len(normal) else 0,
            "start": str(normal["entry_time"].min()) if len(normal) else "",
            "end": str(normal["exit_time"].max()) if len(normal) else "",
            "timeframes": list(cfg["timeframes"]),
            "source": ("D:/1mdatabinance (monthly 1h CSV history merged with "
                       "daily 1m parquet, resampled to UTC 1h)"),
        },
        "totals": {
            "normal": totals(normal),
            "singular": totals(singular),
            "blocked": int(len(normal) - len(singular)),
        },
        "strategies": rows,
        "scenarios": scenario_rows,
        "coins": coins,
    }
    (out_dir / "singular_results.json").write_text(
        json.dumps(_round_floats(payload), ensure_ascii=False,
                   separators=(",", ":")),
        encoding="utf-8",
    )
    pd.DataFrame(rows).to_csv(out_dir / "singular_summary.csv", index=False)
    pd.DataFrame(coins).to_csv(out_dir / "singular_coins.csv", index=False)
    return payload


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", type=Path, default=ROOT)
    ap.add_argument("--data-dir", type=Path, default=ROOT / "data" / "1h")
    ap.add_argument("--out", type=Path,
                    default=Path(__file__).resolve().parent / "results")
    ap.add_argument("--workers", type=int, default=max(1, (os.cpu_count() or 4) - 2))
    ap.add_argument("--scope", choices=["scenario", "scenario_tf"],
                    default="scenario")
    ap.add_argument("--limit-symbols", type=int)
    ap.add_argument("--symbols", nargs="*", help="optional symbol subset")
    ap.add_argument("--limit-scenarios", type=int, help="debug only")
    ap.add_argument("--from-cache", action="store_true",
                    help="reuse normal_trades parquet and only rebuild singular")
    ap.add_argument("--force", action="store_true")
    args = ap.parse_args()

    cfg = json.loads((args.root / "config.json").read_text(encoding="utf-8"))
    scenarios = parse_scenarios(args.root / "strategy.md")
    if args.limit_scenarios:
        scenarios = scenarios[:args.limit_scenarios]
    files = sorted(args.data_dir.glob("*.parquet"))
    if args.symbols:
        wanted = {s.upper() for s in args.symbols}
        files = [p for p in files if p.stem.upper() in wanted]
    if args.limit_symbols:
        files = files[:args.limit_symbols]
    if not files:
        raise SystemExit(f"no parquet files in {args.data_dir}; run prepare_data.py")

    args.out.mkdir(parents=True, exist_ok=True)
    print(f"{len(files)} symbols | {len(scenarios)} scenarios | "
          f"scope={args.scope} | workers={args.workers}", flush=True)
    jobs = [(p.stem, str(p), str(args.out), cfg, scenarios, args.scope,
             args.force, args.from_cache) for p in files]
    manifest = []
    with cf.ProcessPoolExecutor(max_workers=args.workers) as ex:
        for i, res in enumerate(ex.map(process_symbol, jobs), 1):
            manifest.append(res)
            if res.get("status") == "error":
                print(f"[{i}/{len(jobs)}] {res['symbol']}: ERROR {res['error']}",
                      flush=True)
                print(res.get("trace", ""), flush=True)
            else:
                print(f"[{i}/{len(jobs)}] {res['symbol']}: {res['status']} "
                      f"normal={res.get('normal', '-')} "
                      f"singular={res.get('singular', '-')}", flush=True)
    (args.out / "run_manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")

    payload = aggregate(args.out, args.scope, cfg, scenarios)
    print(f"strategies={len(payload['strategies'])} "
          f"coins={len(payload['coins'])} "
          f"normal_trades={payload['totals']['normal']['trades']} "
          f"singular_trades={payload['totals']['singular']['trades']} "
          f"blocked={payload['totals']['blocked']}", flush=True)
    print(f"wrote {args.out / 'singular_results.json'}", flush=True)


if __name__ == "__main__":
    main()

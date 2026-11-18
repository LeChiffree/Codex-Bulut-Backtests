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


def _aggregate_duckdb(out_dir: Path, scope: str, cfg: dict,
                      scenarios: list[tuple[int, str]]) -> dict:
    """Aggregate large universes without materializing all trades in RAM."""
    import duckdb

    names = {int(sid): title for sid, title in scenarios}
    con = duckdb.connect(str(out_dir / "aggregate.duckdb"))
    con.execute("PRAGMA threads=6")
    con.execute("PRAGMA memory_limit='8GB'")
    for view, folder in (("n", "normal_trades"), ("s", "singular_trades")):
        pattern = (out_dir / folder / "*.parquet").as_posix().replace("'", "''")
        con.execute(f"CREATE OR REPLACE VIEW {view} AS SELECT * FROM read_parquet('{pattern}')")

    metric_names = ["trades", "wins", "losses", "win_rate", "avg_ret",
                    "ret2026", "avg_r", "win_hold_h", "profit_days",
                    "loss_days", "symbols", "compounded", "max_loss_r"]

    def metrics(view: str, keys: list[str], prefix: str) -> pd.DataFrame:
        select_keys = ",".join(keys)
        group = f" GROUP BY {select_keys}" if keys else ""
        comma = f"{select_keys}," if keys else ""
        join = " AND ".join(f"b.{k}=x.{k}" for k in keys) or "TRUE"
        base = con.execute(f"""
            SELECT {comma}
              count(*)::BIGINT trades,
              sum((r_multiple>0)::INT)::BIGINT wins,
              sum((r_multiple<=0)::INT)::BIGINT losses,
              avg((r_multiple>0)::INT) win_rate,
              avg(return)*100 avg_ret,
              avg(return) FILTER (WHERE year(exit_time)=2026)*100 ret2026,
              avg(r_multiple) avg_r,
              avg(date_diff('second',entry_time,exit_time)/3600.0)
                FILTER (WHERE r_multiple>0) win_hold_h,
              count(DISTINCT symbol)::BIGINT symbols,
              min(r_multiple) max_loss_r
            FROM {view}{group}
        """).df()
        comp = con.execute(f"""
            WITH per_symbol AS (
              SELECT {comma} symbol,
                exp(sum(ln(greatest(1+return,1e-12))))-1 value
              FROM {view} GROUP BY {comma} symbol
            )
            SELECT {comma} avg(value)*100 compounded FROM per_symbol{group}
        """).df()
        daily = con.execute(f"""
            WITH d AS (
              SELECT {comma} date_trunc('day',exit_time) exit_day, sum(return) value
              FROM {view} GROUP BY {comma} exit_day
            )
            SELECT {comma} sum((value>0)::INT)::BIGINT profit_days,
              sum((value<0)::INT)::BIGINT loss_days FROM d{group}
        """).df()
        result = base
        for extra in (comp, daily):
            result = (result.merge(extra, on=keys, how="left") if keys
                      else pd.concat([result.reset_index(drop=True),
                                      extra.reset_index(drop=True)], axis=1))
        for name in metric_names:
            if name not in result:
                result[name] = 0
        result = result.fillna(0)
        return result.rename(columns={n: f"{prefix}{n}" for n in metric_names})

    nm = metrics("n", ["scenario_id", "timeframe"], "n_")
    sm = metrics("s", ["scenario_id", "timeframe"], "s_")
    merged = _cast_counts(nm.merge(sm, on=["scenario_id", "timeframe"], how="left").fillna(0))
    rows = []
    for r in merged.itertuples(index=False):
        d = r._asdict(); sid = int(d.pop("scenario_id")); tf = str(d.pop("timeframe"))
        blocked = int(d["n_trades"] - d["s_trades"])
        rows.append({"sid": sid, "name": names.get(sid, ""), "tf": tf,
                     "blocked": blocked,
                     "blocked_pct": blocked / d["n_trades"] * 100 if d["n_trades"] else 0,
                     **d})

    coin_sql = lambda view, p: con.execute(f"""
        SELECT scenario_id,timeframe,symbol,count(*)::BIGINT {p}trades,
          avg(return)*100 {p}avg_ret,avg((r_multiple>0)::INT) {p}win_rate,
          avg(r_multiple) {p}avg_r,
          (exp(sum(ln(greatest(1+return,1e-12))))-1)*100 {p}compounded
        FROM {view} GROUP BY scenario_id,timeframe,symbol
    """).df()
    cm = coin_sql("n", "n_").merge(coin_sql("s", "s_"),
        on=["scenario_id", "timeframe", "symbol"], how="left").fillna(0)
    coins = [{"sid": int(r.scenario_id), "tf": str(r.timeframe),
              "symbol": str(r.symbol), "blocked": int(r.n_trades-r.s_trades),
              "n_trades": int(r.n_trades), "n_avg_ret": float(r.n_avg_ret),
              "n_win_rate": float(r.n_win_rate), "n_compounded": float(r.n_compounded),
              "s_trades": int(r.s_trades), "s_avg_ret": float(r.s_avg_ret),
              "s_win_rate": float(r.s_win_rate), "s_compounded": float(r.s_compounded)}
             for r in cm.itertuples(index=False)]

    nsc = metrics("n", ["scenario_id"], "n_")
    ssc = metrics("s", ["scenario_id"], "s_")
    scenario_rows = []
    for r in _cast_counts(nsc.merge(ssc, on="scenario_id", how="left").fillna(0)).itertuples(index=False):
        d = r._asdict(); sid = int(d.pop("scenario_id"))
        scenario_rows.append({"sid": sid, "name": names.get(sid, ""),
                              "blocked": int(d["n_trades"]-d["s_trades"]), **d})

    def total(view: str) -> dict:
        d = metrics(view, [], "").iloc[0].to_dict()
        d["combinations"] = int(con.execute(
            f"SELECT count(*) FROM (SELECT DISTINCT scenario_id,timeframe FROM {view})"
        ).fetchone()[0])
        return {k: (int(v) if k in {"trades","wins","losses","profit_days","loss_days","symbols","combinations"} else float(v)) for k,v in d.items()}

    normal_total, singular_total = total("n"), total("s")
    bounds = con.execute("SELECT min(entry_time),max(exit_time),count(DISTINCT symbol) FROM n").fetchone()
    payload = {"repo": "Codex-Bulut-Backtests",
      "generated_at": pd.Timestamp.now(tz="UTC").strftime("%Y-%m-%dT%H:%M:%SZ"),
      "rule": "Aynı stratejide (senaryoda) aynı coin için aynı anda en fazla bir açık işlem. Sinyal, işlem açıkken gelirse bloke edilir.",
      "scope": scope,
      "data": {"symbols": int(bounds[2]), "start": str(bounds[0]), "end": str(bounds[1]),
               "timeframes": list(cfg["timeframes"]),
               "source": "D:/1mdatabinance (monthly 1h CSV history merged with daily 1m parquet, resampled to UTC 1h)"},
      "totals": {"normal": normal_total, "singular": singular_total,
                 "blocked": int(normal_total["trades"]-singular_total["trades"])},
      "strategies": rows, "scenarios": scenario_rows, "coins": coins}
    (out_dir / "singular_results.json").write_text(json.dumps(_round_floats(payload), ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    pd.DataFrame(rows).to_csv(out_dir / "singular_summary.csv", index=False)
    pd.DataFrame(coins).to_csv(out_dir / "singular_coins.csv", index=False)
    con.close()
    return payload


def aggregate(out_dir: Path, scope: str, cfg: dict,
              scenarios: list[tuple[int, str]]) -> dict:
    if len(list((out_dir / "normal_trades").glob("*.parquet"))) > 150:
        return _aggregate_duckdb(out_dir, scope, cfg, scenarios)
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
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(errors="backslashreplace")
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
    ap.add_argument("--aggregate-only", action="store_true",
                    help="skip symbol processing and rebuild summaries from existing parquet files")
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
    if not args.aggregate_only:
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

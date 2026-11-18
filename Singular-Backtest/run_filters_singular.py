#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Codex Bulut — filtre düzeyinde tekil (one-open-trade) analiz.

Normal laboratuvar 56 filtreyi işlem sonrası uygular. Bu betik aynı filtre
durumlarını kullanarak her filtre için **ayrı** tekil tarama yapar:

  - aday işlemler: `Singular-Backtest/results/normal_trades/*.parquet`
  - filtre durumları: `results/filter_states.parquet` (build_filters.py üretir)
  - kural: aynı senaryo + coin için, filtreyi geçen işlemler arasında, önceki
    işlem kapanmadan gelen sinyal bloke edilir (TF ve yön fark etmez).

Çıktı: `Singular-Backtest/results/filter_singular.json`
  anahtar: "{scenario_id}|{timeframe}|{filter_id}"

Kullanım (önce normal filtre durumları):
  python build_filters.py           # filter_states.parquet üretir (ağ gerekir)
  python Singular-Backtest/run_filters_singular.py
"""
from __future__ import annotations

import argparse
import glob
import json
import multiprocessing
import os
from pathlib import Path

import numpy as np
import pandas as pd
from numba import njit

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
STATES = ROOT / "results" / "filter_states.parquet"
DEFS = ROOT / "results" / "filter_definitions.json"
TRADES = HERE / "results" / "normal_trades"
OUT = HERE / "results" / "filter_singular.json"
TF_RANK = {"1h": 0, "4h": 1, "1d": 2, "1w": 3}
SIDE_RANK = {"long": 0, "short": 1}
Y26_NS = np.datetime64("2026-01-01T00:00:00", "ns").astype("int64")


@njit(cache=True)
def month_key_of_days(days):
    """Epoch gününden (1970-01-01 = 0) yıl*12+ay (0 tabanlı) türetir."""
    out = np.empty(days.shape[0], np.int64)
    for i in range(days.shape[0]):
        z = days[i] + 719468
        era = (z if z >= 0 else z - 146096) // 146097
        doe = z - era * 146097
        yoe = (doe - doe // 1460 + doe // 36524 - doe // 146096) // 365
        y = yoe + era * 400
        doy = doe - (365 * yoe + yoe // 4 - yoe // 100)
        mp = (5 * doy + 2) // 153
        month = mp + (3 if mp < 10 else -9)
        year = y + (1 if month <= 2 else 0)
        out[i] = year * 12 + (month - 1)
    return out


@njit(cache=True)
def greedy(entry, exit_, mask, scen_idx, n_scen):
    last = np.full(n_scen, -1, np.int64)
    acc = np.zeros(entry.shape[0], np.bool_)
    for i in range(entry.shape[0]):
        if not mask[i]:
            continue
        g = scen_idx[i]
        if entry[i] >= last[g]:
            acc[i] = True
            last[g] = exit_[i]
    return acc


def load_defs():
    try:
        return json.load(open(DEFS, encoding="utf-8"))
    except UnicodeDecodeError:
        return json.load(open(DEFS, encoding="cp1254"))


def agg_groups(g):
    """(scenario_id, timeframe) bazında tekil/normal metrikler (vektörel)."""
    if len(g) == 0:
        return None
    g = g.copy()
    r = g["return"].to_numpy(np.float64)
    xt = g["exit_time"].to_numpy("datetime64[ns]").astype(np.int64)
    et = g["entry_time"].to_numpy("datetime64[ns]").astype(np.int64)
    dur_h = (xt - et) / 3_600_000_000_000.0
    g["_win"] = (r > 0).astype(np.int64)
    y26 = xt >= Y26_NS
    g["_r26"] = np.where(y26, r, 0.0)
    g["_n26"] = y26.astype(np.int64)
    g["_durwin"] = np.where(r > 0, dur_h, 0.0)
    g["_dur"] = dur_h
    day = xt // 86_400_000_000_000
    g["_day"] = day
    grp = g.groupby(["scenario_id", "timeframe"], sort=False)
    out = grp.agg(n=("return", "size"), wins=("_win", "sum"), sumret=("return", "sum"),
                  sum26=("_r26", "sum"), n26=("_n26", "sum"),
                  durwin=("_durwin", "sum"), dursum=("_dur", "sum"))
    d = (g.groupby(["scenario_id", "timeframe", "_day"], sort=False)["return"]
         .sum().reset_index(name="sumret"))
    d["_week"] = (d["_day"].to_numpy(np.int64) + 3) // 7
    d["_month"] = month_key_of_days(d["_day"].to_numpy(np.int64))

    def period_counts(key, prefix):
        x = (d.groupby(["scenario_id", "timeframe", key], sort=False)["sumret"]
             .sum().reset_index())
        x["pos"] = (x["sumret"] > 0).astype(np.int64)
        x["neg"] = (x["sumret"] < 0).astype(np.int64)
        c = x.groupby(["scenario_id", "timeframe"], sort=False)[["pos", "neg"]].sum()
        return c.rename(columns={"pos": prefix + "pos", "neg": prefix + "neg"})

    return (out.join(period_counts("_day", ""))
               .join(period_counts("_week", "w"))
               .join(period_counts("_month", "m")))


def metrics_from_row(row):
    n = int(row["n"])
    wins = int(row["wins"])
    losses = n - wins
    return dict(
        trades=n,
        wins=wins,
        losses=losses,
        retAll=float(row["sumret"] / n) if n else 0.0,
        ret2026=float(row["sum26"] / row["n26"]) if row["n26"] else 0.0,
        winRatio=(wins / losses) if losses else None,
        winHoldH=float(row["durwin"] / wins) if wins else None,
        profitDays=int(row["pos"]),
        lossDays=int(row["neg"]),
        profitWeeks=int(row["wpos"]),
        lossWeeks=int(row["wneg"]),
        profitMonths=int(row["mpos"]),
        lossMonths=int(row["mneg"]),
    )


def accumulate(store, fid, frame):
    """Sembol bazlı toplamları anahtar bazında biriktir."""
    if frame is None:
        return
    for (sid, tf), row in frame.iterrows():
        key = (fid, int(sid), tf)
        a = store.get(key)
        if a is None:
            a = store[key] = np.zeros(12, np.float64)
        a[0] += row["n"]
        a[1] += row["wins"]
        a[2] += row["sumret"]
        a[3] += row["sum26"]
        a[4] += row["n26"]
        a[5] += row["durwin"]
        a[6] += row["pos"]
        a[7] += row["neg"]
        a[8] += row["wpos"]
        a[9] += row["wneg"]
        a[10] += row["mpos"]
        a[11] += row["mneg"]


def finalize(store):
    out = {}
    for (fid, sid, tf), a in store.items():
        out[(fid, sid, tf)] = metrics_from_row({
            "n": a[0], "wins": a[1], "sumret": a[2], "sum26": a[3],
            "n26": a[4], "durwin": a[5], "pos": a[6], "neg": a[7],
            "wpos": a[8], "wneg": a[9], "mpos": a[10], "mneg": a[11],
        })
    return out


def merge_store(dst, src):
    for k, a in src.items():
        if k in dst:
            dst[k] += a
        else:
            dst[k] = a.copy()


_TRADE_COLS = ["symbol", "timeframe", "scenario_id", "scenario",
               "signal_time", "entry_time", "exit_time", "return", "side"]


def process_files(file_paths, states, filters):
    """Bir sembol dilimindeki tüm işlemleri tarar; (acc, norm, names, total_n) döner."""
    acc = {}
    norm = {}
    names = {}
    total_n = 0
    for path in file_paths:
        df = pd.read_parquet(path, columns=_TRADE_COLS)
        if df.empty:
            continue
        for sid, nm in df[["scenario_id", "scenario"]].drop_duplicates().itertuples(index=False):
            names[int(sid)] = nm
        df["signal_time"] = pd.to_datetime(df["signal_time"], utc=True)
        df["entry_time"] = pd.to_datetime(df["entry_time"], utc=True)
        df["exit_time"] = pd.to_datetime(df["exit_time"], utc=True)
        df["_tf"] = df["timeframe"].map(TF_RANK).fillna(9).astype(np.int8)
        df["_side"] = df["side"].map(SIDE_RANK).fillna(9).astype(np.int8)
        df = df.sort_values(["signal_time", "_tf", "_side"], kind="stable").reset_index(drop=True)

        st = states.reindex(df["entry_time"], method="ffill")
        scen = df["scenario_id"].to_numpy(np.int64)
        uniq, scen_idx = np.unique(scen, return_inverse=True)
        signal = df["signal_time"].to_numpy("int64")
        exit_ = df["exit_time"].to_numpy("int64")
        total_n += len(df)

        for fid in filters:
            mask = np.ones(len(df), np.bool_) if fid == "baseline" else st[fid].fillna(False).to_numpy(np.bool_)
            if not mask.any():
                continue
            gn = agg_groups(df[mask])
            accumulate(norm, fid, gn)
            a = greedy(signal, exit_, mask, scen_idx, len(uniq))
            ga = agg_groups(df[a])
            accumulate(acc, fid, ga)
    return acc, norm, names, total_n


def _process_chunk(args):
    chunk, states_path, filters = args
    states = pd.read_parquet(states_path).set_index("entry_time").sort_index()
    return process_files(chunk, states, filters)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--trades", default=str(TRADES))
    ap.add_argument("--states", default=str(STATES))
    ap.add_argument("--out", default=str(OUT))
    ap.add_argument("--symbols", type=int, default=0)
    ap.add_argument("--workers", type=int, default=0)
    args = ap.parse_args()

    states = pd.read_parquet(args.states).set_index("entry_time").sort_index()
    defs = load_defs()
    filters = [c for c in states.columns if c in defs]
    if "baseline" not in filters:
        filters.insert(0, "baseline")
    print(f"[filters] {len(filters)} filtre, {len(states):,} saat")

    files = sorted(glob.glob(os.path.join(args.trades, "*.parquet")))
    if args.symbols:
        files = files[: args.symbols]
    print(f"[filters] {len(files)} sembol dosyası")

    acc = {}
    norm = {}
    total_n = 0
    names = {}

    nworkers = args.workers or 1
    if nworkers > 1 and len(files) > 1:
        nworkers = min(nworkers, len(files), os.cpu_count() or 1)
        chunks = [files[i::nworkers] for i in range(nworkers)]
        ctx = multiprocessing.get_context("spawn")
        print(f"[filters] {nworkers} işçi ile paralel tarama")
        with ctx.Pool(nworkers) as pool:
            results = pool.map(_process_chunk, [(c, args.states, filters) for c in chunks])
        for acc_i, norm_i, names_i, tn in results:
            merge_store(acc, acc_i)
            merge_store(norm, norm_i)
            names.update(names_i)
            total_n += tn
    else:
        acc, norm, names, total_n = process_files(files, states, filters)

    print(f"[filters] toplam {total_n:,} aday işlem tarandı")
    acc = finalize(acc)
    norm = finalize(norm)

    out = {}
    for (fid, sid, tf), m in acc.items():
        out[f"{sid}|{tf}|{fid}"] = {
            "filter_id": fid,
            "filter_label": defs.get(fid, fid),
            "scenario_name": names.get(sid, ""),
            **m,
        }
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    json.dump(out, open(args.out, "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":"))
    print(f"[filters] yazıldı: {args.out} ({len(out):,} satır)")

    # normal (filtre uygulanmış, tekil değil) — dashboard normal sütunlarını
    # aynı veri setiyle hizalı tutmak için
    outn = {}
    for (fid, sid, tf), m in norm.items():
        outn[f"{sid}|{tf}|{fid}"] = {
            "filter_id": fid,
            "filter_label": defs.get(fid, fid),
            "scenario_name": names.get(sid, ""),
            **m,
        }
    npath = str(Path(args.out).with_name("filter_normal.json"))
    json.dump(outn, open(npath, "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":"))
    print(f"[filters] normal yazıldı: {npath} ({len(outn):,} satır)")

    try:
        allr = json.load(open(r"C:/Users/GIGABAYT/Projects/all-in-dashboard/allinone.json", encoding="utf-8"))["rows"]
        ref = {}
        for r in allr:
            if r["source"] != "Codex Bulut":
                continue
            ref[(r["strategy"], r["timeframe"], r["filter"])] = r
        mism = 0
        checked = 0
        for (fid, sid, tf), m in norm.items():
            r = ref.get((names.get(sid, ""), tf, defs.get(fid, fid)))
            if not r:
                continue
            checked += 1
            if int(r["trades"]) != m["trades"] or abs((r["retAll"] or 0) - m["retAll"]) > 1e-4:
                mism += 1
        print(f"[filters] normal doğrulama: {checked:,} satır, {mism:,} uyuşmazlık")
        if checked == 0:
            print("  norm örnek:", list(norm.keys())[:3])
            print("  ref örnek:", list(ref.keys())[:3])
    except Exception as e:
        print("[filters] normal doğrulama atlandı:", e)


if __name__ == "__main__":
    main()

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
Y26 = np.datetime64("2026-01-01T00:00:00")


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
    et = g["entry_time"].to_numpy("datetime64[ns]")
    xt = g["exit_time"].to_numpy("datetime64[ns]")
    dur_h = (xt - et) / np.timedelta64(1, "h")
    g["_win"] = (r > 0).astype(np.int64)
    y26 = et >= Y26
    g["_r26"] = np.where(y26, r, 0.0)
    g["_n26"] = y26.astype(np.int64)
    g["_durwin"] = np.where(r > 0, dur_h, 0.0)
    g["_dur"] = dur_h
    grp = g.groupby(["scenario_id", "timeframe"], sort=False)
    out = grp.agg(n=("return", "size"), wins=("_win", "sum"), sumret=("return", "sum"),
                  sum26=("_r26", "sum"), n26=("_n26", "sum"),
                  durwin=("_durwin", "sum"), dursum=("_dur", "sum"))
    g["_day"] = g["exit_time"].dt.floor("D")
    d = g.groupby(["scenario_id", "timeframe", "_day"], sort=False)["return"].sum().reset_index()
    d["pos"] = (d["return"] > 0).astype(np.int64)
    d["neg"] = (d["return"] < 0).astype(np.int64)
    pdld = d.groupby(["scenario_id", "timeframe"], sort=False)[["pos", "neg"]].sum()
    return out.join(pdld)


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
    )


def accumulate(store, fid, frame):
    """Sembol bazlı toplamları anahtar bazında biriktir."""
    if frame is None:
        return
    for (sid, tf), row in frame.iterrows():
        key = (fid, int(sid), tf)
        a = store.get(key)
        if a is None:
            a = store[key] = np.zeros(8, np.float64)
        a[0] += row["n"]
        a[1] += row["wins"]
        a[2] += row["sumret"]
        a[3] += row["sum26"]
        a[4] += row["n26"]
        a[5] += row["durwin"]
        a[6] += row["pos"]
        a[7] += row["neg"]


def finalize(store):
    out = {}
    for (fid, sid, tf), a in store.items():
        out[(fid, sid, tf)] = metrics_from_row({
            "n": a[0], "wins": a[1], "sumret": a[2], "sum26": a[3],
            "n26": a[4], "durwin": a[5], "pos": a[6], "neg": a[7],
        })
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--trades", default=str(TRADES))
    ap.add_argument("--states", default=str(STATES))
    ap.add_argument("--out", default=str(OUT))
    ap.add_argument("--symbols", type=int, default=0)
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

    for k, path in enumerate(files, 1):
        df = pd.read_parquet(path, columns=["symbol", "timeframe", "scenario_id", "scenario",
                                            "entry_time", "exit_time", "return", "side"])
        if df.empty:
            continue
        for sid, nm in df[["scenario_id", "scenario"]].drop_duplicates().itertuples(index=False):
            names[int(sid)] = nm
        df["entry_time"] = pd.to_datetime(df["entry_time"], utc=True)
        df["exit_time"] = pd.to_datetime(df["exit_time"], utc=True)
        df["_tf"] = df["timeframe"].map(TF_RANK).fillna(9).astype(np.int8)
        df["_side"] = df["side"].map(SIDE_RANK).fillna(9).astype(np.int8)
        df = df.sort_values(["entry_time", "_tf", "_side"], kind="stable").reset_index(drop=True)

        st = states.reindex(df["entry_time"], method="ffill")
        scen = df["scenario_id"].to_numpy(np.int64)
        uniq, scen_idx = np.unique(scen, return_inverse=True)
        entry = df["entry_time"].to_numpy("int64")
        exit_ = df["exit_time"].to_numpy("int64")
        total_n += len(df)

        for fid in filters:
            mask = np.ones(len(df), np.bool_) if fid == "baseline" else st[fid].fillna(False).to_numpy(np.bool_)
            if not mask.any():
                continue
            gn = agg_groups(df[mask])
            accumulate(norm, fid, gn)
            a = greedy(entry, exit_, mask, scen_idx, len(uniq))
            ga = agg_groups(df[a])
            accumulate(acc, fid, ga)

        if k % 10 == 0 or k == len(files):
            print(f"  {k}/{len(files)} sembol — {total_n:,} aday işlem", flush=True)

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

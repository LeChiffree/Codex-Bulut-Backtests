#!/usr/bin/env python3
"""Validate the Singular-Backtest outputs.

Checks:
  1. No two accepted singular trades overlap for the same scenario + coin.
  2. Every accepted singular trade exists in the normal candidate set.
  3. Per-side normal trades do not overlap (engine invariant).
  4. Reports blocked-signal counts.

Run after `run_singular.py`:
    python Singular-Backtest/verify_singular.py
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent


def load(folder: Path, cols: list[str]) -> pd.DataFrame:
    files = sorted(folder.glob("*.parquet"))
    if not files:
        raise SystemExit(f"no parquet files in {folder}")
    return pd.concat([pd.read_parquet(p, columns=cols) for p in files],
                     ignore_index=True)


def overlap_count(df: pd.DataFrame, keys: list[str]) -> int:
    """Count trades whose signal arrived before the previous trade exited."""
    bad = 0
    for _, g in df.groupby(keys, sort=False, observed=True):
        g = g.sort_values("signal_time", kind="mergesort")
        if len(g) < 2:
            continue
        prev_exit = g["exit_time"].shift(1)
        bad += int((g["signal_time"] < prev_exit).sum())
    return bad


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--results", type=Path, default=ROOT / "results")
    args = ap.parse_args()
    base = args.results
    cols = ["symbol", "timeframe", "scenario_id", "side", "signal_time",
            "entry_time", "exit_time", "r_multiple", "return"]
    normal_files = sorted((base / "normal_trades").glob("*.parquet"))
    if not normal_files:
        raise SystemExit(f"no parquet files in {base / 'normal_trades'}")
    normal_count = singular_count = violations = side_overlaps = missing = 0
    key = ["symbol", "timeframe", "scenario_id", "side", "entry_time"]
    for i, normal_file in enumerate(normal_files, 1):
        singular_file = base / "singular_trades" / normal_file.name
        if not singular_file.exists():
            raise SystemExit(f"missing singular file: {singular_file}")
        normal = pd.read_parquet(normal_file, columns=cols)
        singular = pd.read_parquet(singular_file, columns=cols)
        normal_count += len(normal)
        singular_count += len(singular)
        violations += overlap_count(singular, ["scenario_id", "symbol"])
        side_overlaps += overlap_count(
            normal, ["scenario_id", "symbol", "timeframe", "side"]
        )
        merged = singular[key].merge(normal[key].drop_duplicates(), on=key,
                                     how="left", indicator=True)
        missing += int((merged["_merge"] != "both").sum())
        if i % 50 == 0 or i == len(normal_files):
            print(f"verified {i}/{len(normal_files)} symbols", flush=True)

    print(f"normal trades   : {normal_count:,}")
    print(f"singular trades : {singular_count:,}")
    print(f"blocked         : {normal_count - singular_count:,}")
    print(f"singular overlaps (scenario+coin): {violations}")
    print(f"normal per-side overlaps        : {side_overlaps}")
    print(f"singular trades missing in normal: {missing}")

    blocked = normal_count - singular_count
    pct = blocked / normal_count * 100 if normal_count else 0
    print(f"blocked ratio   : {pct:.2f}%")
    if violations or side_overlaps or missing:
        print("FAILED")
        sys.exit(1)
    print("OK")


if __name__ == "__main__":
    main()

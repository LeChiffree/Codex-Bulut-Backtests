#!/usr/bin/env python3
"""Prepare local Binance USD-M 1h parquet files for the Singular backtest.

The repository normally downloads data from data.binance.vision.  This helper
builds the same `data/1h/<SYMBOL>.parquet` layout from the user's monthly CSV
archive (D:/1mdatabinance by default) so the singular run can be reproduced
offline.
"""
from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

COLS = {
    "open_time": "open_time",
    "open": "open",
    "high": "high",
    "low": "low",
    "close": "close",
    "volume": "volume",
    "quote_asset_volume": "quote_volume",
    "number_of_trades": "trades",
    "taker_buy_base_asset_volume": "taker_base",
    "taker_buy_quote_asset_volume": "taker_quote",
}
KEEP = ["open_time", "open", "high", "low", "close", "volume",
        "quote_volume", "trades", "taker_base", "taker_quote"]


def load_symbol(csv_dir: Path) -> pd.DataFrame | None:
    files = sorted(csv_dir.glob("*.csv"))
    if not files:
        return None
    frames = []
    for path in files:
        try:
            df = pd.read_csv(path)
        except Exception:
            continue
        if df.empty:
            continue
        missing = [c for c in COLS if c not in df.columns]
        if missing:
            continue
        frames.append(df[list(COLS)].rename(columns=COLS))
    if not frames:
        return None
    df = pd.concat(frames, ignore_index=True)
    ts = pd.to_numeric(df["open_time"], errors="coerce")
    unit = "us" if ts.dropna().median() > 10**14 else "ms"
    df["open_time"] = pd.to_datetime(ts, unit=unit, utc=True)
    for col in KEEP[1:]:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    df = df.dropna(subset=["open_time", "open", "high", "low", "close"])
    df = df.drop_duplicates("open_time").sort_values("open_time").reset_index(drop=True)
    return df[KEEP]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv-root", type=Path, default=Path("D:/1mdatabinance/1h"))
    ap.add_argument("--out-root", type=Path,
                    default=Path(__file__).resolve().parent.parent / "data" / "1h")
    ap.add_argument("--symbols", nargs="*", help="Optional symbol subset")
    args = ap.parse_args()

    args.out_root.mkdir(parents=True, exist_ok=True)
    wanted = set(args.symbols) if args.symbols else None
    dirs = sorted(p for p in args.csv_root.iterdir() if p.is_dir())
    written = 0
    for i, csv_dir in enumerate(dirs, 1):
        symbol = csv_dir.name
        if wanted and symbol not in wanted:
            continue
        df = load_symbol(csv_dir)
        if df is None or df.empty:
            print(f"[{i}/{len(dirs)}] {symbol}: empty")
            continue
        out = args.out_root / f"{symbol}.parquet"
        df.to_parquet(out, index=False, compression="zstd", row_group_size=100_000)
        written += 1
        print(f"[{i}/{len(dirs)}] {symbol}: {len(df):,} bars "
              f"{df.open_time.min().date()} -> {df.open_time.max().date()}", flush=True)
    print(f"wrote {written} files to {args.out_root}")


if __name__ == "__main__":
    main()

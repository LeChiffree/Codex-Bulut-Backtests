#!/usr/bin/env python3
"""Prepare local Binance USD-M 1h parquet files for the Singular backtest.

The repository normally downloads data from data.binance.vision.  This helper
builds the same `data/1h/<SYMBOL>.parquet` layout from either the monthly 1h
CSV archive or the daily 1m parquet archive under D:/1mdatabinance.  The latter
is resampled to closed UTC hours and is the preferred source for fresh runs.
"""
from __future__ import annotations

import argparse
import concurrent.futures as cf
import os
import sys
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


def _normalize(frame: pd.DataFrame) -> pd.DataFrame | None:
    if frame.empty:
        return None
    missing = [c for c in COLS if c not in frame.columns]
    if missing:
        return None
    df = frame[list(COLS)].rename(columns=COLS).copy()
    ts = pd.to_numeric(df["open_time"], errors="coerce")
    unit = "us" if ts.dropna().median() > 10**14 else "ms"
    df["open_time"] = pd.to_datetime(ts, unit=unit, utc=True)
    for col in KEEP[1:]:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    return df.dropna(subset=["open_time", "open", "high", "low", "close"])


def _resample_1h(df: pd.DataFrame) -> pd.DataFrame:
    df = df.set_index("open_time").sort_index()
    out = df.resample("1h", origin="epoch", label="left", closed="left").agg({
        "open": "first", "high": "max", "low": "min", "close": "last",
        "volume": "sum", "quote_volume": "sum", "trades": "sum",
        "taker_base": "sum", "taker_quote": "sum",
    })
    return out.dropna(subset=["open", "high", "low", "close"]).reset_index()


def load_symbol(source_dir: Path) -> pd.DataFrame | None:
    parquet_files = sorted(source_dir.glob("*.parquet"))
    csv_files = sorted(source_dir.glob("*.csv"))
    files = parquet_files or csv_files
    if not files:
        return None
    frames = []
    for path in files:
        try:
            raw = pd.read_parquet(path) if path.suffix == ".parquet" else pd.read_csv(path)
        except Exception:
            continue
        df = _normalize(raw)
        if df is not None and not df.empty:
            frames.append(df)
    if not frames:
        return None
    df = pd.concat(frames, ignore_index=True)
    df = df.drop_duplicates("open_time").sort_values("open_time").reset_index(drop=True)
    if parquet_files:
        # The live archive stores daily 1m parquet files.  A directory with a
        # median spacing below one hour must be aggregated before backtesting.
        spacing = df["open_time"].diff().dropna().median()
        if pd.notna(spacing) and spacing < pd.Timedelta(hours=1):
            df = _resample_1h(df)
    return df[KEEP]


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(errors="backslashreplace")
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv-root", type=Path, default=Path("D:/1mdatabinance/1m"),
                    help="symbol directories containing monthly CSV or daily parquet files")
    ap.add_argument("--history-root", type=Path, default=Path("D:/1mdatabinance/1h"),
                    help="optional older 1h archive merged before the fresher source")
    ap.add_argument("--out-root", type=Path,
                    default=Path(__file__).resolve().parent.parent / "data" / "1h")
    ap.add_argument("--symbols", nargs="*", help="Optional symbol subset")
    ap.add_argument("--symbols-file", type=Path,
                    default=Path("D:/1mdatabinance/selected_symbols.txt"),
                    help="one symbol per line; combined with --symbols when supplied")
    ap.add_argument("--all-symbols", action="store_true",
                    help="ignore the default selected-symbol list and process every symbol directory")
    ap.add_argument("--workers", type=int, default=min(6, max(1, (os.cpu_count() or 4) - 2)),
                    help="parallel symbol readers (default: up to 6)")
    args = ap.parse_args()

    args.out_root.mkdir(parents=True, exist_ok=True)
    wanted = {s.upper() for s in args.symbols} if args.symbols else set()
    if not args.all_symbols and args.symbols_file and args.symbols_file.is_file():
        wanted.update(
            line.strip().upper() for line in
            args.symbols_file.read_text(encoding="utf-8").splitlines()
            if line.strip()
        )
    wanted = wanted or None
    dirs = sorted(p for p in args.csv_root.iterdir() if p.is_dir())
    jobs = []
    for i, csv_dir in enumerate(dirs, 1):
        symbol = csv_dir.name
        if wanted and symbol not in wanted:
            continue
        jobs.append((i, csv_dir, symbol))

    def prepare(job):
        i, csv_dir, symbol = job
        fresh = load_symbol(csv_dir)
        history_dir = args.history_root / symbol if args.history_root else None
        history = (load_symbol(history_dir)
                   if history_dir is not None and history_dir.is_dir() else None)
        parts = [part for part in (history, fresh) if part is not None and not part.empty]
        df = None if not parts else pd.concat(parts, ignore_index=True)
        if df is not None:
            # Fresh rows are appended last and win on overlapping timestamps.
            df = (df.drop_duplicates("open_time", keep="last")
                  .sort_values("open_time").reset_index(drop=True))
        if df is None or df.empty:
            return i, symbol, None, "empty"
        out = args.out_root / f"{symbol}.parquet"
        df.to_parquet(out, index=False, compression="zstd", row_group_size=100_000)
        detail = (f"{len(df):,} bars {df.open_time.min().date()} -> "
                  f"{df.open_time.max().date()}")
        return i, symbol, out, detail

    written = 0
    with cf.ThreadPoolExecutor(max_workers=args.workers) as executor:
        for i, symbol, out, detail in executor.map(prepare, jobs):
            if out is not None:
                written += 1
            print(f"[{i}/{len(dirs)}] {symbol}: {detail}", flush=True)
    print(f"wrote {written} files to {args.out_root}")


if __name__ == "__main__":
    main()

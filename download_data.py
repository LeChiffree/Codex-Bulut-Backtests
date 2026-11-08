#!/usr/bin/env python3
"""Download and compact Binance USD-M 1h public klines."""
from __future__ import annotations

import argparse
import concurrent.futures as cf
import io
import json
import time
import zipfile
from datetime import date, datetime
from pathlib import Path
from urllib.parse import quote
import xml.etree.ElementTree as ET

import pandas as pd
import requests

S3 = "https://s3-ap-northeast-1.amazonaws.com/data.binance.vision"
VISION = "https://data.binance.vision/data/futures/um/monthly/klines"
EXCHANGE_INFO = "https://www.binance.com/fapi/v1/exchangeInfo"
NS = {"s": "http://s3.amazonaws.com/doc/2006-03-01/"}
COLS = ["open_time", "open", "high", "low", "close", "volume", "close_time",
        "quote_volume", "trades", "taker_base", "taker_quote", "ignore"]


def months(start: str, end: str):
    p = pd.period_range(start, end, freq="M")
    return [str(x) for x in p]


def last_complete_month() -> str:
    return str((pd.Timestamp.utcnow().tz_localize(None).to_period("M") - 1))


def discover_symbols(session: requests.Session) -> list[str]:
    prefix = "data/futures/um/monthly/klines/"
    token = None
    symbols = []
    while True:
        params = {"list-type": "2", "prefix": prefix, "delimiter": "/", "max-keys": 1000}
        if token:
            params["continuation-token"] = token
        r = session.get(S3, params=params, timeout=60)
        r.raise_for_status()
        root = ET.fromstring(r.content)
        for node in root.findall("s:CommonPrefixes/s:Prefix", NS):
            symbol = node.text.rstrip("/").split("/")[-1]
            if symbol.endswith("USDT"):
                symbols.append(symbol)
        if root.findtext("s:IsTruncated", namespaces=NS) != "true":
            break
        token = root.findtext("s:NextContinuationToken", namespaces=NS)
    return sorted(set(symbols))


def zip_url(symbol: str, month: str) -> str:
    return f"{VISION}/{symbol}/1h/{symbol}-1h-{month}.zip"


def read_zip(content: bytes) -> pd.DataFrame:
    with zipfile.ZipFile(io.BytesIO(content)) as zf:
        name = next(n for n in zf.namelist() if n.endswith(".csv"))
        raw = zf.open(name)
        df = pd.read_csv(raw, header=None)
    if len(df.columns) < 12:
        raise ValueError("Beklenmeyen Binance kline şeması")
    df = df.iloc[:, :12]
    df.columns = COLS
    if not pd.api.types.is_numeric_dtype(df["open_time"]):
        df = df[pd.to_numeric(df["open_time"], errors="coerce").notna()]
    return df


def latest_volume(item: tuple[str, str]) -> tuple[str, float, int] | None:
    symbol, month = item
    try:
        r = requests.get(zip_url(symbol, month), timeout=35)
        if r.status_code != 200:
            return None
        df = read_zip(r.content)
        qv = pd.to_numeric(df["quote_volume"], errors="coerce").sum()
        return symbol, float(qv), len(df)
    except Exception:
        return None


def select_universe(root: Path, n: int, end_month: str) -> list[dict]:
    universe_file = root / "metadata" / "universe.json"
    if universe_file.exists():
        payload = json.loads(universe_file.read_text())
        if payload.get("ranking_month") == end_month and payload.get("requested_size") == n:
            return payload["symbols"]
    with requests.Session() as s:
        archive_symbols = set(discover_symbols(s))
        info = s.get(EXCHANGE_INFO, timeout=60).json()
    # "Coin" is intentional: Binance also exposes equity, commodity, FX and
    # index perpetuals in the same archive. The user's requested universe is
    # restricted to live crypto USDT perpetual contracts.
    live_crypto = {
        x["symbol"] for x in info.get("symbols", [])
        if x.get("status") == "TRADING"
        and x.get("contractType") == "PERPETUAL"
        and x.get("quoteAsset") == "USDT"
        and x.get("underlyingType") == "COIN"
    }
    symbols = sorted(archive_symbols & live_crypto)
    print(f"Arşivde {len(symbols)} USDT sembolü bulundu; {end_month} hacmi ölçülüyor", flush=True)
    ranked = []
    with cf.ThreadPoolExecutor(max_workers=32) as ex:
        for i, row in enumerate(ex.map(latest_volume, [(s, end_month) for s in symbols]), 1):
            if row:
                ranked.append({"symbol": row[0], "quote_volume": row[1], "bars": row[2]})
            if i % 200 == 0:
                print(f"  tarandı {i}/{len(symbols)}", flush=True)
    ranked.sort(key=lambda x: x["quote_volume"], reverse=True)
    selected = ranked[:n]
    universe_file.parent.mkdir(parents=True, exist_ok=True)
    universe_file.write_text(json.dumps({
        "created_at": datetime.utcnow().isoformat() + "Z",
        "ranking_month": end_month,
        "requested_size": n,
        "eligible_symbols": len(ranked),
        "symbols": selected,
    }, ensure_ascii=False, indent=2))
    return selected


def download_symbol(root: Path, symbol: str, month_list: list[str]) -> dict:
    out = root / "data" / "1h" / f"{symbol}.parquet"
    if out.exists():
        try:
            old = pd.read_parquet(out, columns=["open_time"])
            if len(old) and pd.to_datetime(old["open_time"], utc=True).max().to_period("M").strftime("%Y-%m") >= month_list[-1]:
                return {"symbol": symbol, "status": "cached", "rows": len(old)}
        except Exception:
            pass
    frames = []
    missing = []
    for month in month_list:
        for attempt in range(4):
            try:
                r = requests.get(zip_url(symbol, month), timeout=50)
                if r.status_code == 404:
                    missing.append(month)
                    break
                r.raise_for_status()
                frames.append(read_zip(r.content))
                break
            except Exception:
                if attempt == 3:
                    missing.append(month)
                else:
                    time.sleep(1.5 * (attempt + 1))
    if not frames:
        return {"symbol": symbol, "status": "empty", "rows": 0, "missing": missing}
    df = pd.concat(frames, ignore_index=True)
    numeric = [c for c in COLS if c not in ("open_time", "close_time", "ignore")]
    for c in numeric:
        df[c] = pd.to_numeric(df[c], errors="coerce")
    ts = pd.to_numeric(df["open_time"], errors="coerce")
    unit = "us" if ts.dropna().median() > 10**14 else "ms"
    df["open_time"] = pd.to_datetime(ts, unit=unit, utc=True)
    df = df.dropna(subset=["open_time", "open", "high", "low", "close"]).drop_duplicates("open_time").sort_values("open_time")
    keep = ["open_time", "open", "high", "low", "close", "volume", "quote_volume", "trades", "taker_base", "taker_quote"]
    out.parent.mkdir(parents=True, exist_ok=True)
    df[keep].to_parquet(out, index=False, compression="zstd", row_group_size=100_000)
    return {"symbol": symbol, "status": "ok", "rows": len(df), "first": str(df.open_time.min()), "last": str(df.open_time.max()), "missing": missing}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", type=Path, default=Path(__file__).resolve().parent)
    ap.add_argument("--size", type=int, default=500)
    ap.add_argument("--start", default="2019-09")
    ap.add_argument("--workers", type=int, default=12)
    args = ap.parse_args()
    end = last_complete_month()
    selected = select_universe(args.root, args.size, end)
    month_list = months(args.start, end)
    manifest_path = args.root / "metadata" / "download_manifest.jsonl"
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    print(f"{len(selected)} sembol, {len(month_list)} ay indiriliyor", flush=True)
    with cf.ThreadPoolExecutor(max_workers=args.workers) as ex, manifest_path.open("a") as mf:
        futures = {ex.submit(download_symbol, args.root, x["symbol"], month_list): x["symbol"] for x in selected}
        done = 0
        for fut in cf.as_completed(futures):
            done += 1
            symbol = futures[fut]
            try:
                result = fut.result()
            except Exception as e:
                result = {"symbol": symbol, "status": "error", "error": repr(e)}
            mf.write(json.dumps(result, ensure_ascii=False) + "\n")
            mf.flush()
            print(f"[{done:03d}/{len(futures)}] {symbol}: {result.get('status')} {result.get('rows', 0)}", flush=True)


if __name__ == "__main__":
    main()


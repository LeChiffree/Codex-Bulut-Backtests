#!/usr/bin/env python3
"""Build compact scan data for the Codex strategy scanner.

Reads the pre-aggregated result CSVs and writes dashboard/data/scan.json.
Does not modify the source results.
"""
from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
RESULTS = ROOT / "results"
OUT = ROOT / "dashboard" / "data" / "scan.json"
TF_ORDER = ["1d", "4h", "1h", "1w"]


def number(value, digits: int = 6) -> float:
    if pd.isna(value):
        return 0.0
    return round(float(value), digits)


def main() -> None:
    filters = json.loads((RESULTS / "filter_definitions.json").read_text(encoding="utf-8"))
    filter_df = pd.read_csv(RESULTS / "filter_overall_results.csv")
    annual_df = pd.read_csv(RESULTS / "annual_results.csv")

    rows = []
    for (sid, tf), group in filter_df.groupby(["scenario_id", "timeframe"], sort=False):
        baseline = group[group["filter_id"] == "baseline"]
        if baseline.empty:
            continue
        base = baseline.iloc[0]
        fmap = {}
        for item in group.itertuples(index=False):
            fmap[str(item.filter_id)] = {
                "ret": number(item.total_return),
                "wr": number(item.win_rate),
                "r": number(item.avg_r),
                "trades": int(item.trades or 0),
                "symbols": int(item.symbols) if not pd.isna(item.symbols) else 0,
            }

        yearly = annual_df[
            (annual_df["scenario_id"] == sid) & (annual_df["timeframe"] == tf)
        ]
        years = {
            str(int(item.year)): number(item.annual_return)
            for item in yearly.itertuples(index=False)
            if not pd.isna(item.annual_return)
        }
        rows.append(
            {
                "sid": int(sid),
                "name": str(base.scenario),
                "tf": str(tf),
                "f": fmap,
                "y": years,
                "pos": sum(1 for value in years.values() if value > 0),
                "ny": len(years),
            }
        )

    rows.sort(key=lambda row: (row["sid"], TF_ORDER.index(row["tf"]) if row["tf"] in TF_ORDER else 9))
    payload = {
        "filters": [{"id": key, "name": name} for key, name in filters.items()],
        "rows": rows,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    print(f"wrote {OUT} | {len(rows)} combinations | {len(filters)} filters | {OUT.stat().st_size / 1024 / 1024:.1f} MB")


if __name__ == "__main__":
    main()

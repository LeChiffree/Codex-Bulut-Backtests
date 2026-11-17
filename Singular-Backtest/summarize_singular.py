#!/usr/bin/env python3
"""Print a compact summary of Singular-Backtest results."""
from __future__ import annotations

import argparse
import json
from pathlib import Path


def pct(value: float) -> str:
    return f"{value:+.4f}%"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", type=Path,
                    default=Path(__file__).resolve().parent / "results" /
                    "singular_results.json")
    ap.add_argument("--min-trades", type=int, default=100)
    ap.add_argument("--top", type=int, default=10)
    args = ap.parse_args()
    data = json.loads(args.json.read_text(encoding="utf-8"))
    t = data["totals"]
    n, s = t["normal"], t["singular"]
    print(f"repo       : {data['repo']}")
    print(f"scope      : {data['scope']}")
    print(f"coins      : {data['data']['symbols']}")
    print(f"period     : {data['data']['start']} -> {data['data']['end']}")
    print(f"normal     : {n['trades']:,} trades | win {n['win_rate']:.2%} | "
          f"avg {pct(n['avg_ret'])} | avgR {n['avg_r']:+.4f}")
    print(f"singular   : {s['trades']:,} trades | win {s['win_rate']:.2%} | "
          f"avg {pct(s['avg_ret'])} | avgR {s['avg_r']:+.4f}")
    blocked = t["blocked"]
    print(f"blocked    : {blocked:,} ({blocked / n['trades']:.2%})")

    rows = [r for r in data["strategies"] if r["n_trades"] >= args.min_trades]
    rows.sort(key=lambda r: r["s_avg_ret"], reverse=True)
    print(f"\nTop {args.top} by singular avg return (min {args.min_trades} trades)")
    print(f"{'sid':>4} {'tf':>3} {'normal':>9} {'singular':>9} {'delta':>8} "
          f"{'s_trades':>9} {'blocked':>8}")
    for r in rows[:args.top]:
        delta = r["s_avg_ret"] - r["n_avg_ret"]
        print(f"{r['sid']:>4} {r['tf']:>3} {pct(r['n_avg_ret']):>9} "
              f"{pct(r['s_avg_ret']):>9} {pct(delta):>8} "
              f"{r['s_trades']:>9,} {r['blocked']:>8,}")


if __name__ == "__main__":
    main()

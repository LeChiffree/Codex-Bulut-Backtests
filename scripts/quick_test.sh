#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PYTHON="${PYTHON:-$ROOT/.venv/bin/python}"
mkdir -p "$ROOT/results/refined_5m/by_symbol" "$ROOT/results/tmp"
"$PYTHON" "$ROOT/download_data.py" --root "$ROOT" --size 3 --start 2025-01-01 --workers 3
"$PYTHON" "$ROOT/backtest.py" --root "$ROOT" --limit-symbols 3 --workers 3
echo 'Hızlı test tamamlandı.'

#!/usr/bin/env bash
# Regression gate wrapper — exit non-zero if eval metrics regress vs baseline.
#
# Usage: bash scripts/check_regression.sh [CURRENT_PATH]
# Default: data/eval/latest_results.json

set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$PROJECT_ROOT"

CURRENT="${1:-data/eval/latest_results.json}"
BASELINE="data/eval/baseline_results.json"

if [ ! -f "$CURRENT" ]; then
  echo "No current results at $CURRENT — run scripts/run_eval.sh first." >&2
  exit 2
fi

uv run python -m app.eval.diff --current "$CURRENT" --baseline "$BASELINE"

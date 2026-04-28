#!/usr/bin/env bash
# Run the full eval pipeline and diff against the locked baseline.
#
# Usage:  bash scripts/run_eval.sh [--skip-langsmith] [--update-baseline]
#
# Steps:
#   1. Run the golden dataset through the graph, compute Ragas + custom metrics,
#      write JSON to data/eval/latest_results.json.
#   2. Diff against data/eval/baseline_results.json.
#   3. If LANGCHAIN_API_KEY is set (and --skip-langsmith not passed), also run
#      a LangSmith experiment so results land in the UI.

set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$PROJECT_ROOT"

SKIP_LANGSMITH=0
UPDATE_BASELINE=0
for arg in "$@"; do
  case "$arg" in
    --skip-langsmith) SKIP_LANGSMITH=1 ;;
    --update-baseline) UPDATE_BASELINE=1 ;;
    *) echo "unknown arg: $arg" >&2; exit 2 ;;
  esac
done

RESULTS_PATH="data/eval/latest_results.json"
BASELINE_PATH="data/eval/baseline_results.json"

echo "▶ Running golden dataset through the graph …"
uv run python -m app.eval.cli --output "$RESULTS_PATH"

echo
echo "▶ Diffing against baseline ($BASELINE_PATH) …"
if [ "$UPDATE_BASELINE" -eq 1 ]; then
  uv run python -m app.eval.diff --current "$RESULTS_PATH" --baseline "$BASELINE_PATH" --update-baseline
else
  uv run python -m app.eval.diff --current "$RESULTS_PATH" --baseline "$BASELINE_PATH"
fi

if [ "$SKIP_LANGSMITH" -eq 0 ] && [ -n "${LANGCHAIN_API_KEY:-}" ]; then
  echo
  echo "▶ Launching LangSmith experiment on dataset golden-v1 …"
  uv run python scripts/run_langsmith_eval.py || {
    echo "LangSmith experiment failed (non-fatal)" >&2
  }
else
  echo
  echo "ℹ Skipping LangSmith experiment (no API key or --skip-langsmith set)."
fi

"""CLI entry point for the local eval pipeline.

Run:  uv run python -m app.eval.cli --output data/eval/latest_results.json
"""

from __future__ import annotations

import argparse
from pathlib import Path

from app.eval.metrics import compute_custom_metrics, compute_ragas_metrics
from app.eval.report import generate_report
from app.eval.runner import run_eval
from app.utils.helpers import get_logger

logger = get_logger(__name__)

DEFAULT_DATASET = Path("data/eval/golden_dataset.json")
DEFAULT_OUTPUT = Path("data/eval/latest_results.json")


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the local eval pipeline.")
    parser.add_argument("--dataset", type=Path, default=DEFAULT_DATASET)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument(
        "--skip-ragas",
        action="store_true",
        help="Skip Ragas metrics (faster; for quick iteration).",
    )
    args = parser.parse_args()

    if not args.dataset.exists():
        logger.error("Dataset not found: %s", args.dataset)
        return 1

    results = run_eval(args.dataset)
    results = compute_custom_metrics(results)
    if not args.skip_ragas:
        results = compute_ragas_metrics(results)

    generate_report(results, args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

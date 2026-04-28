"""Regression gate — diff current eval results against the locked baseline.

Run:
    uv run python -m app.eval.diff --current data/eval/latest_results.json
    uv run python -m app.eval.diff --current data/eval/latest_results.json --update-baseline

Exit codes:
    0  — all metrics within allowed drift (or improved)
    1  — one or more metrics regressed beyond the allowed delta
    2  — unusable inputs (missing file, malformed JSON, etc.)

Allowed deltas: a *positive* number is the max amount the metric may move
in the bad direction. For `jargon_leak_rate` (lower is better) +0.02 means
the rate may increase by at most 0.02. For everything else +0.03 means the
metric may drop by at most 0.03.
"""

from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path
from typing import Any

from app.utils.helpers import get_logger

logger = get_logger(__name__)

DEFAULT_CURRENT = Path("data/eval/latest_results.json")
DEFAULT_BASELINE = Path("data/eval/baseline_results.json")

# Metrics to gate on. `lower_is_better` flips which direction counts as bad.
GATE_CONFIG: dict[str, dict[str, Any]] = {
    "faithfulness": {"max_drift": 0.03, "lower_is_better": False},
    "answer_relevancy": {"max_drift": 0.03, "lower_is_better": False},
    "keyword_hit_rate": {"max_drift": 0.03, "lower_is_better": False},
    "jargon_leak_rate": {"max_drift": 0.02, "lower_is_better": True},
}


def _load(path: Path) -> dict:
    if not path.exists():
        logger.error("Not found: %s", path)
        sys.exit(2)
    try:
        return json.loads(path.read_text())
    except json.JSONDecodeError as exc:
        logger.error("Invalid JSON in %s: %s", path, exc)
        sys.exit(2)


def _overall(report: dict) -> dict:
    overall = report.get("overall") or {}
    if not overall:
        logger.error("Report has no 'overall' block")
        sys.exit(2)
    return overall


def diff_reports(current: dict, baseline: dict) -> tuple[list[dict], bool]:
    """Return (rows, gate_failed). Each row has metric, current, baseline, delta, status."""
    cur_overall = _overall(current)
    base_overall = _overall(baseline)

    rows: list[dict] = []
    gate_failed = False

    for metric, cfg in GATE_CONFIG.items():
        cur = cur_overall.get(metric)
        base = base_overall.get(metric)
        if cur is None or base is None:
            rows.append(
                {
                    "metric": metric,
                    "current": cur,
                    "baseline": base,
                    "delta": None,
                    "status": "SKIP",
                    "reason": "metric missing from one side",
                }
            )
            continue

        delta = round(float(cur) - float(base), 4)
        # Convert delta into "movement in the bad direction"
        bad_delta = -delta if not cfg["lower_is_better"] else delta
        limit = cfg["max_drift"]
        if bad_delta > limit + 1e-9:
            status = "FAIL"
            gate_failed = True
        elif bad_delta > 0:
            status = "WARN"
        else:
            status = "OK"
        rows.append(
            {
                "metric": metric,
                "current": round(float(cur), 4),
                "baseline": round(float(base), 4),
                "delta": delta,
                "status": status,
                "reason": f"max_drift={limit}",
            }
        )

    return rows, gate_failed


def _print_table(rows: list[dict]) -> None:
    header = f"{'Metric':<22} {'Baseline':>10} {'Current':>10} {'Delta':>10}  Status"
    print(header)
    print("-" * len(header))
    for r in rows:
        base = "  N/A" if r["baseline"] is None else f"{r['baseline']:>10.4f}"
        cur = "  N/A" if r["current"] is None else f"{r['current']:>10.4f}"
        delta = "  N/A" if r["delta"] is None else f"{r['delta']:>+10.4f}"
        print(f"{r['metric']:<22} {base} {cur} {delta}  {r['status']}  ({r['reason']})")


def main() -> int:
    parser = argparse.ArgumentParser(description="Diff eval results vs baseline.")
    parser.add_argument("--current", type=Path, default=DEFAULT_CURRENT)
    parser.add_argument("--baseline", type=Path, default=DEFAULT_BASELINE)
    parser.add_argument(
        "--update-baseline",
        action="store_true",
        help="Overwrite baseline with current after printing the diff. "
        "Use only with an explicit commit justifying the move.",
    )
    args = parser.parse_args()

    current = _load(args.current)
    baseline = _load(args.baseline)
    rows, failed = diff_reports(current, baseline)

    print()
    print("REGRESSION GATE — overall metrics")
    print("=" * 68)
    _print_table(rows)
    print()

    if args.update_baseline:
        shutil.copyfile(args.current, args.baseline)
        print(f"Baseline updated: {args.baseline} ← {args.current}")
        return 0

    if failed:
        print("Gate FAILED — see FAIL rows above. Commit blocked.")
        return 1
    print("Gate OK.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

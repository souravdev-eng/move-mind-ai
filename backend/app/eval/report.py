"""Eval report — writes JSON results and prints a human-readable summary to stdout."""

from __future__ import annotations

import json
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from app.eval.metrics import THRESHOLDS, passes_threshold
from app.utils.helpers import get_logger

logger = get_logger(__name__)

METRIC_KEYS = [
    "keyword_hit_rate",
    "jargon_leak_rate",
    "faithfulness",
    "answer_relevancy",
]


def _avg(values: list[float | None]) -> float | None:
    clean = [v for v in values if v is not None]
    return round(sum(clean) / len(clean), 3) if clean else None


def _pass_fail(metric: str, value: float | None) -> str:
    if value is None:
        return "N/A"
    return "PASS" if passes_threshold(metric, value) else "FAIL"


def generate_report(
    results: list[dict[str, Any]],
    output_path: str | Path,
) -> dict[str, Any]:
    """
    Build the eval report, save it to output_path as JSON, and print a summary.

    Returns the full report dict.
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # ── Per-category aggregates ──────────────────────────────────────────────
    by_category: dict[str, list[dict]] = defaultdict(list)
    for r in results:
        by_category[r["category"]].append(r)

    category_summary: dict[str, dict] = {}
    for cat, items in by_category.items():
        cat_summary: dict[str, Any] = {"count": len(items)}
        for m in METRIC_KEYS:
            avg = _avg([r.get(m) for r in items])
            cat_summary[m] = avg
        category_summary[cat] = cat_summary

    # ── Overall aggregates ───────────────────────────────────────────────────
    overall: dict[str, Any] = {"total_questions": len(results)}
    for m in METRIC_KEYS:
        overall[m] = _avg([r.get(m) for r in results])

    # ── Full report ──────────────────────────────────────────────────────────
    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "overall": overall,
        "by_category": category_summary,
        "results": results,
    }

    output_path.write_text(json.dumps(report, indent=2, default=str))
    logger.info("Report saved to %s", output_path)

    # ── Human-readable summary ───────────────────────────────────────────────
    _print_summary(overall, category_summary, results)

    return report


def _print_summary(
    overall: dict,
    by_category: dict,
    results: list[dict],
) -> None:
    width = 68
    sep = "─" * width

    print()
    print("=" * width)
    print("  MOVE MIND AI — EVAL REPORT")
    print("=" * width)

    # Overall scores
    print()
    print("  OVERALL SCORES")
    print(f"  {sep}")
    print(f"  {'Metric':<25} {'Score':>8}  {'Target':<10} {'Status':>6}")
    print(f"  {sep}")
    for m, cfg in THRESHOLDS.items():
        val = overall.get(m)
        score_str = f"{val:.3f}" if val is not None else "  N/A"
        status = _pass_fail(m, val)
        print(f"  {m:<25} {score_str:>8}  {cfg['label']:<10} {status:>6}")

    # Per-category breakdown
    print()
    print("  BY CATEGORY")
    print(f"  {sep}")
    for cat, data in by_category.items():
        khr = data.get("keyword_hit_rate")
        jlr = data.get("jargon_leak_rate")
        faith = data.get("faithfulness")
        rel = data.get("answer_relevancy")
        khr_str = f"{khr:.2f}" if khr is not None else " N/A"
        jlr_str = f"{jlr:.2f}" if jlr is not None else " N/A"
        faith_str = f"{faith:.2f}" if faith is not None else " N/A"
        rel_str = f"{rel:.2f}" if rel is not None else " N/A"
        print(
            f"  {cat:<22} n={data['count']}  "
            f"kw={khr_str}  jargon={jlr_str}  "
            f"faith={faith_str}  rel={rel_str}"
        )

    # Failed questions
    failures = [
        r
        for r in results
        if not passes_threshold("keyword_hit_rate", r.get("keyword_hit_rate"))
        or not passes_threshold("jargon_leak_rate", r.get("jargon_leak_rate"))
    ]

    if failures:
        print()
        print(f"  QUESTIONS NEEDING ATTENTION ({len(failures)})")
        print(f"  {sep}")
        for r in failures:
            khr = r.get("keyword_hit_rate")
            jlr = r.get("jargon_leak_rate")
            print(f"  [{r['id']}] kw={khr:.2f} jargon={jlr:.2f}")
            if r.get("missed_keywords"):
                print(f"    missing keywords : {', '.join(r['missed_keywords'])}")
            if r.get("leaked_jargon"):
                print(f"    jargon leaked    : {', '.join(r['leaked_jargon'])}")
    else:
        print()
        print("  All questions passed keyword and jargon checks.")

    print()
    print("=" * width)
    print()

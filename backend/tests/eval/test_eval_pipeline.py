"""
Eval pipeline test — runs the full golden dataset through the graph and asserts metric thresholds.

Usage:
    pytest tests/eval/test_eval_pipeline.py -v -s          # full run
    pytest tests/eval/ -v -s -m integration                # same, explicit mark
"""

import json
from pathlib import Path

import pytest

GOLDEN_DATASET_PATH = Path("data/eval/golden_dataset.json")
RESULTS_OUTPUT_PATH = Path("data/eval/baseline_results.json")

THRESHOLDS = {
    "keyword_hit_rate": 0.75,   # ≥ 75% of expected business keywords present
    "jargon_leak_rate": 0.10,   # < 10% of forbidden technical terms leaked
    "faithfulness": 0.75,       # ≥ 75% — answer grounded in retrieved context
    "answer_relevancy": 0.65,   # ≥ 65% — answer is relevant to the question
}


@pytest.mark.integration
def test_eval_pipeline_runs_and_meets_thresholds():
    """
    Full eval: run golden dataset, compute metrics, save report, assert thresholds.
    This is the single gating test — pass it before any merge to feat/eval.
    """
    from app.eval.metrics import compute_custom_metrics, compute_ragas_metrics
    from app.eval.report import generate_report
    from app.eval.runner import run_eval

    assert GOLDEN_DATASET_PATH.exists(), f"Golden dataset not found at {GOLDEN_DATASET_PATH}"

    # Run all questions through the live graph
    results = run_eval(GOLDEN_DATASET_PATH)
    assert len(results) > 0, "Runner returned no results"

    # Compute metrics
    results = compute_custom_metrics(results)
    results = compute_ragas_metrics(results)

    # Save full report
    report = generate_report(results, RESULTS_OUTPUT_PATH)

    overall = report["overall"]

    # ── Assert thresholds ────────────────────────────────────────────────────
    khr = overall.get("keyword_hit_rate")
    jlr = overall.get("jargon_leak_rate")
    faith = overall.get("faithfulness")
    rel = overall.get("answer_relevancy")

    assert khr is not None, "keyword_hit_rate not computed"
    assert jlr is not None, "jargon_leak_rate not computed"

    assert khr >= THRESHOLDS["keyword_hit_rate"], (
        f"keyword_hit_rate {khr:.3f} below threshold {THRESHOLDS['keyword_hit_rate']}"
    )
    assert jlr < THRESHOLDS["jargon_leak_rate"], (
        f"jargon_leak_rate {jlr:.3f} above threshold {THRESHOLDS['jargon_leak_rate']}"
    )

    if faith is not None:
        assert faith >= THRESHOLDS["faithfulness"], (
            f"faithfulness {faith:.3f} below threshold {THRESHOLDS['faithfulness']}"
        )

    if rel is not None:
        assert rel >= THRESHOLDS["answer_relevancy"], (
            f"answer_relevancy {rel:.3f} below threshold {THRESHOLDS['answer_relevancy']}"
        )


@pytest.mark.integration
def test_no_jargon_in_any_single_answer():
    """
    Every individual answer must have jargon_leak_rate == 0.
    One leaky answer is a bug — not just an average problem.
    """
    from app.eval.metrics import compute_custom_metrics
    from app.eval.runner import run_eval

    results = run_eval(GOLDEN_DATASET_PATH)
    results = compute_custom_metrics(results)

    leaky = [r for r in results if r["jargon_leak_rate"] > 0]

    if leaky:
        details = "\n".join(
            f"  [{r['id']}] leaked: {r['leaked_jargon']}"
            for r in leaky
        )
        pytest.fail(f"{len(leaky)} answers leaked technical jargon:\n{details}")

"""Eval metrics — custom keyword checks + Ragas faithfulness and answer relevancy."""

from __future__ import annotations

import warnings
from typing import Any

from app.utils.helpers import get_logger

logger = get_logger(__name__)

# ---------------------------------------------------------------------------
# Custom metrics — grounded in our golden dataset schema
# ---------------------------------------------------------------------------


def keyword_hit_rate(answer: str, expected_keywords: list[str]) -> float:
    """
    Fraction of expected business keywords found in the answer (case-insensitive).

    A score of 1.0 means all expected terms appeared.
    Target: > 0.80
    """
    if not expected_keywords:
        return 1.0
    answer_lower = answer.lower()
    hits = sum(1 for kw in expected_keywords if kw.lower() in answer_lower)
    return round(hits / len(expected_keywords), 3)


def jargon_leak_rate(answer: str, expected_not_contains: list[str]) -> float:
    """
    Fraction of forbidden technical terms found in the answer (case-insensitive).

    A score of 0.0 is perfect — no jargon leaked through.
    Target: < 0.10
    """
    if not expected_not_contains:
        return 0.0
    answer_lower = answer.lower()
    leaks = sum(1 for term in expected_not_contains if term.lower() in answer_lower)
    return round(leaks / len(expected_not_contains), 3)


def compute_custom_metrics(results: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Add keyword_hit_rate and jargon_leak_rate to each result in-place."""
    for r in results:
        r["keyword_hit_rate"] = keyword_hit_rate(r["answer"], r["expected_keywords"])
        r["jargon_leak_rate"] = jargon_leak_rate(
            r["answer"], r["expected_not_contains"]
        )
        # Flag individual keyword misses and jargon leaks for easy review
        answer_lower = r["answer"].lower()
        r["missed_keywords"] = [
            kw for kw in r["expected_keywords"] if kw.lower() not in answer_lower
        ]
        r["leaked_jargon"] = [
            term for term in r["expected_not_contains"] if term.lower() in answer_lower
        ]
    return results


# ---------------------------------------------------------------------------
# Ragas metrics — faithfulness + answer relevancy
# ---------------------------------------------------------------------------


def compute_ragas_metrics(results: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """
    Run Ragas faithfulness and answer_relevancy on each result.

    Scores are added in-place as 'faithfulness' and 'answer_relevancy'.
    If Ragas fails for any reason, scores are set to None and a warning is logged.
    """
    try:
        import openai
        from ragas import evaluate
        from ragas.dataset_schema import EvaluationDataset, SingleTurnSample
        from ragas.embeddings import LangchainEmbeddingsWrapper
        from ragas.llms import llm_factory
        from ragas.metrics import AnswerRelevancy, Faithfulness
        from langchain_openai import OpenAIEmbeddings

        from app.config import settings

        client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
        # Use smart model (gpt-4o) — gpt-4o-mini hits token limits on long log contexts
        llm = llm_factory(settings.OPENAI_SMART, client=client)
        lc_embeddings = OpenAIEmbeddings(
            model=settings.EMBEDDING_MODEL_NAME,
            api_key=settings.OPENAI_API_KEY,
        )

        with warnings.catch_warnings():
            warnings.simplefilter("ignore", DeprecationWarning)
            embeddings = LangchainEmbeddingsWrapper(lc_embeddings)

        metrics = [
            Faithfulness(llm=llm),
            AnswerRelevancy(llm=llm, embeddings=embeddings),
        ]

        samples = [
            SingleTurnSample(
                user_input=r["question"],
                response=r["answer"],
                retrieved_contexts=r["contexts"]
                if r["contexts"]
                else ["no context retrieved"],
            )
            for r in results
        ]

        logger.info("Running Ragas evaluation on %d samples …", len(samples))
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", DeprecationWarning)
            ragas_result = evaluate(
                dataset=EvaluationDataset(samples=samples),
                metrics=metrics,
            )

        df = ragas_result.to_pandas()

        import math

        def _safe(val) -> float | None:
            try:
                f = float(val)
                return None if math.isnan(f) else round(f, 3)
            except (TypeError, ValueError):
                return None

        for i, r in enumerate(results):
            r["faithfulness"] = (
                _safe(df.loc[i, "faithfulness"])
                if "faithfulness" in df.columns
                else None
            )
            r["answer_relevancy"] = (
                _safe(df.loc[i, "answer_relevancy"])
                if "answer_relevancy" in df.columns
                else None
            )

        logger.info("Ragas evaluation complete")

    except Exception as exc:
        logger.warning("Ragas evaluation failed: %s — scores set to None", exc)
        for r in results:
            r.setdefault("faithfulness", None)
            r.setdefault("answer_relevancy", None)

    return results


# ---------------------------------------------------------------------------
# Thresholds
# ---------------------------------------------------------------------------

THRESHOLDS = {
    "keyword_hit_rate": {"target": 0.80, "label": "≥ 0.80"},
    "jargon_leak_rate": {"target": 0.10, "label": "< 0.10", "lower_is_better": True},
    "faithfulness": {"target": 0.80, "label": "≥ 0.80"},
    "answer_relevancy": {"target": 0.70, "label": "≥ 0.70"},
}


def passes_threshold(metric: str, value: float | None) -> bool:
    """Return True if the metric value meets its target threshold."""
    if value is None:
        return False
    cfg = THRESHOLDS.get(metric, {})
    if cfg.get("lower_is_better"):
        return value < cfg["target"]
    return value >= cfg["target"]

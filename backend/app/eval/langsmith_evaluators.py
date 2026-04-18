"""LangSmith-compatible evaluators for the `golden-v1` dataset.

Each evaluator takes the standard LangSmith signature
    (inputs, outputs, reference_outputs) -> dict
and returns `{"key": <metric_name>, "score": <float>, "comment": <str>}`.

Two of these are pure functions ported from `app/eval/metrics.py`
(keyword_hit, jargon_leak). A third is an LLM-as-judge groundedness check
that reads the answer and the retrieved contexts.
"""

from __future__ import annotations

import json
import re
from typing import Any

from app.eval.metrics import jargon_leak_rate, keyword_hit_rate
from app.utils.helpers import get_llm, get_logger

logger = get_logger(__name__)

_JSON_BLOCK = re.compile(r"\{.*\}", re.DOTALL)

_GROUNDEDNESS_PROMPT = """\
You are a strict evaluator scoring how well an answer is grounded in the \
retrieved context.

Context (retrieved chunks):
---
{context}
---

Answer:
---
{answer}
---

Task: Return JSON with one float `score` in [0, 1] and one short `reason`.
- score = 1.0 means every claim in the answer is directly supported by the context.
- score = 0.0 means the answer is unsupported or contradicts the context.
- Penalize fabricated entities, made-up counts, and unsupported causal claims.

Respond with ONLY the JSON object — no prose, no markdown fences.
Example: {{"score": 0.85, "reason": "All key claims supported except booking timestamp."}}
"""


def _get(outputs: dict, reference: dict, key: str, default: Any = None) -> Any:
    if key in (outputs or {}):
        return outputs.get(key, default)
    return (reference or {}).get(key, default)


def keyword_hit_evaluator(
    inputs: dict, outputs: dict, reference_outputs: dict
) -> dict:
    """Fraction of `expected_keywords` present in the answer."""
    answer = (outputs or {}).get("answer", "") or ""
    expected = (reference_outputs or {}).get("expected_keywords", []) or []
    score = keyword_hit_rate(answer, expected)
    missing = [kw for kw in expected if kw.lower() not in answer.lower()]
    return {
        "key": "keyword_hit_rate",
        "score": score,
        "comment": f"missing={missing}" if missing else "all expected keywords present",
    }


def jargon_leak_evaluator(
    inputs: dict, outputs: dict, reference_outputs: dict
) -> dict:
    """Fraction of forbidden jargon terms found in the answer (lower is better)."""
    answer = (outputs or {}).get("answer", "") or ""
    forbidden = (reference_outputs or {}).get("expected_not_contains", []) or []
    score = jargon_leak_rate(answer, forbidden)
    leaked = [t for t in forbidden if t.lower() in answer.lower()]
    return {
        "key": "jargon_leak_rate",
        "score": score,
        "comment": f"leaked={leaked}" if leaked else "no jargon leaked",
    }


def groundedness_evaluator(
    inputs: dict, outputs: dict, reference_outputs: dict
) -> dict:
    """LLM-as-judge: does the answer stick to the retrieved context?"""
    answer = (outputs or {}).get("answer", "") or ""
    contexts = (outputs or {}).get("contexts", []) or []
    if not answer or not contexts:
        return {
            "key": "groundedness",
            "score": 0.0,
            "comment": "no answer or no retrieved context",
        }

    context_text = "\n\n---\n\n".join(contexts)[:12000]
    prompt = _GROUNDEDNESS_PROMPT.format(context=context_text, answer=answer)

    try:
        raw = get_llm("fast").invoke(prompt).content
    except Exception as exc:  # noqa: BLE001
        logger.warning("[groundedness] LLM call failed: %s", exc)
        return {"key": "groundedness", "score": 0.0, "comment": f"llm error: {exc}"}

    match = _JSON_BLOCK.search(raw if isinstance(raw, str) else str(raw))
    if not match:
        return {"key": "groundedness", "score": 0.0, "comment": f"unparseable: {raw[:120]}"}

    try:
        data = json.loads(match.group())
        score = float(data.get("score", 0.0))
        score = max(0.0, min(1.0, score))
        reason = str(data.get("reason", ""))[:200]
        return {"key": "groundedness", "score": round(score, 3), "comment": reason}
    except (json.JSONDecodeError, ValueError) as exc:
        return {"key": "groundedness", "score": 0.0, "comment": f"parse error: {exc}"}


ALL_EVALUATORS = [keyword_hit_evaluator, jargon_leak_evaluator, groundedness_evaluator]

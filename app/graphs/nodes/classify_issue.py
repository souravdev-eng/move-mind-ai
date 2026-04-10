"""Node: classify_issue — determine whether the reported issue is a bug or a business condition."""

from __future__ import annotations

import json
import re

from langchain_core.output_parsers import StrOutputParser

from app.graphs.state import GraphState
from app.prompts.templates import ISSUE_CLASSIFIER_PROMPT
from app.utils.helpers import format_docs, get_llm, get_logger

logger = get_logger(__name__)

_JSON_BLOCK = re.compile(r"\{.*\}", re.DOTALL)


def _parse_classification(raw: str) -> dict:
    """Extract JSON from the LLM response, tolerating markdown code fences."""
    match = _JSON_BLOCK.search(raw)
    if not match:
        logger.warning("[classify_issue] No JSON found in response: %s", raw[:200])
        return {"issue_type": "unknown", "confidence": 0.0, "reason": "Could not parse classification."}
    try:
        data = json.loads(match.group())
        issue_type = data.get("issue_type", "unknown")
        if issue_type not in {"bug", "business_condition", "unknown"}:
            issue_type = "unknown"
        confidence = float(data.get("confidence", 0.0))
        confidence = max(0.0, min(1.0, confidence))
        reason = str(data.get("reason", "")).strip()
        return {"issue_type": issue_type, "confidence": round(confidence, 2), "reason": reason}
    except (json.JSONDecodeError, ValueError) as exc:
        logger.warning("[classify_issue] JSON parse error: %s", exc)
        return {"issue_type": "unknown", "confidence": 0.0, "reason": "Classification parsing failed."}


def classify_issue(state: GraphState) -> dict:
    """
    Classify the reported issue as a bug, business_condition, or unknown.

    Uses the generated plain-English answer and the retrieved log evidence.
    Runs only when there is enough context to classify (CID or documents present).
    """
    answer = state.get("answer", "")
    context_docs = state.get("reranked_documents") or state.get("documents", [])

    # Skip classification if there is nothing to classify
    if not answer or not context_docs:
        logger.info("[classify_issue] skipped — no answer or documents")
        return {
            "issue_type": "unknown",
            "issue_confidence": 0.0,
            "issue_classification_reason": "Not enough information to classify.",
        }

    context = format_docs(context_docs)
    chain = ISSUE_CLASSIFIER_PROMPT | get_llm("fast") | StrOutputParser()

    try:
        raw = chain.invoke({"answer": answer, "context": context})
        result = _parse_classification(raw)
    except Exception as exc:
        logger.warning("[classify_issue] LLM call failed: %s", exc)
        result = {"issue_type": "unknown", "confidence": 0.0, "reason": "Classification unavailable."}

    logger.info(
        "[classify_issue] type=%s confidence=%.2f reason=%s",
        result["issue_type"],
        result["confidence"],
        result["reason"][:80],
    )

    return {
        "issue_type": result["issue_type"],
        "issue_confidence": result["confidence"],
        "issue_classification_reason": result["reason"],
    }

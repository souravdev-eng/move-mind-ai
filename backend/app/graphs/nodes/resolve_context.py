"""Node: resolve_context - persist structured debugging intent across turns."""

from __future__ import annotations

import re

from app.graphs.state import GraphState
from app.rag.retrieval import (
    build_scope_filter,
    extract_customer_id,
    extract_execution_id,
    extract_page_path,
    question_targets_api_timeline,
)
from app.utils.helpers import get_logger
from langsmith import traceable

logger = get_logger(__name__)

API_VIEW_NAMED = "named_operations"
API_VIEW_TRANSPORT = "transport_requests"
API_VIEW_ALL = "all_api_types"

COUNT_PATTERN = re.compile(
    r"\b(?:all\s+)?(\d+)\s+(?:api|apis|requests|request|queries|query|operations|operation)\b",
    re.IGNORECASE,
)


def _infer_api_view(question: str, previous_api_view: str | None) -> str | None:
    text = question.lower()
    if "all type" in text or "both" in text or "all api types" in text:
        return API_VIEW_ALL
    if "graphql_request" in text or "transport" in text or "network request" in text:
        return API_VIEW_TRANSPORT
    if (
        "query name" in text
        or "query names" in text
        or "operation" in text
        or "operations" in text
        or "api name" in text
        or "api names" in text
    ):
        return API_VIEW_NAMED
    if question_targets_api_timeline(question):
        return previous_api_view or API_VIEW_NAMED
    return previous_api_view


def _extract_requested_api_count(question: str) -> int | None:
    """Capture explicit numeric counts like 'all 9 api'."""
    match = COUNT_PATTERN.search(question)
    return int(match.group(1)) if match else None

@traceable(run_type="llm")
def resolve_context(state: GraphState) -> dict:
    """Resolve persistent debugging scope such as CID, route, and API intent."""
    question = state["question"]

    customer_id = extract_customer_id(question) or state.get("active_customer_id")
    execution_id = extract_execution_id(question) or state.get("active_execution_id")
    page_path = extract_page_path(question) or state.get("active_page_path")

    # For rewritten follow-ups, allow the question text to refresh missing scope.
    scope_filter = build_scope_filter(question, state.get("messages", [])) or {}
    customer_id = customer_id or scope_filter.get("customer_id")
    page_path = page_path or scope_filter.get("page_path")

    analysis_mode = state.get("analysis_mode")
    if question_targets_api_timeline(question):
        analysis_mode = "api_calls"

    api_view = _infer_api_view(question, state.get("api_view"))
    requested_api_count = _extract_requested_api_count(question)

    logger.info(
        "[context] cid=%s execution=%s page=%s mode=%s api_view=%s count=%s",
        customer_id,
        execution_id,
        page_path,
        analysis_mode,
        api_view,
        requested_api_count,
    )
    return {
        "active_customer_id": customer_id,
        "active_execution_id": execution_id,
        "active_page_path": page_path,
        "analysis_mode": analysis_mode,
        "api_view": api_view,
        "requested_api_count": requested_api_count,
    }

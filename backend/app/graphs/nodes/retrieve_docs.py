"""Node: retrieve_docs - fetch CMS3 log chunks with metadata-scoped hybrid retrieval."""

from langsmith import traceable

from app.config import settings
from app.graphs.state import GraphState
from app.obs.tracing import attach_span_metadata
from app.rag.retrieval import retrieve_candidates
from app.utils.helpers import doc_to_dict, get_logger

logger = get_logger(__name__)


@traceable(run_type="retriever")
def retrieve_docs(state: GraphState) -> dict:
    """Fetch relevant summary and event chunks for the current question."""
    documents = retrieve_candidates(
        state["question"],
        chat_history=state.get("messages", []),
        session_context={
            "active_customer_id": state.get("active_customer_id"),
            "active_execution_id": state.get("active_execution_id"),
            "active_page_path": state.get("active_page_path"),
            "analysis_mode": state.get("analysis_mode"),
            "api_view": state.get("api_view"),
        },
    )
    logger.info("[retrieve] %d candidate chunks", len(documents))
    attach_span_metadata(
        {
            "k_summary": settings.RETRIEVER_SUMMARY_K,
            "k_event": settings.RETRIEVER_EVENT_K,
            "num_returned": len(documents),
            "analysis_mode": state.get("analysis_mode") or "general",
        }
    )
    return {"documents": [doc_to_dict(document) for document in documents]}

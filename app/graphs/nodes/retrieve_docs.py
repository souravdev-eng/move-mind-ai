"""Node: retrieve_docs - fetch CMS3 log chunks with metadata-scoped hybrid retrieval."""

from app.graphs.state import GraphState
from app.rag.retrieval import retrieve_candidates
from app.utils.helpers import doc_to_dict, get_logger
from langsmith import traceable

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
    return {"documents": [doc_to_dict(document) for document in documents]}

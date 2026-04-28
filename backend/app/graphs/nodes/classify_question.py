"""Node: classify_question - decide between direct retrieval and query rewriting."""

from app.chains.classify_chain import get_classify_chain
from app.graphs.state import GraphState
from app.utils.helpers import get_logger, question_needs_context_resolution
from langsmith import traceable

logger = get_logger(__name__)


@traceable(run_type="llm")
def classify_question(state: GraphState) -> dict:
    """Classify the question as standalone retrieval or follow-up rewrite."""
    if question_needs_context_resolution(state["question"], state.get("messages", [])):
        logger.info("[classify] rewrite (heuristic)")
        return {"query_type": "rewrite"}

    result = (
        get_classify_chain()
        .invoke(
            {"question": state["question"], "chat_history": state.get("messages", [])}
        )
        .strip()
        .lower()
    )
    if result not in {"retrieve", "rewrite"}:
        result = "retrieve"
    logger.info("[classify] %s", result)
    return {"query_type": result}

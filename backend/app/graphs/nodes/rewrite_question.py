"""Node: rewrite_question - rewrite follow-up prompts into standalone CMS3 queries."""

from app.chains.query_rewrite_chain import get_query_rewrite_chain
from app.graphs.state import GraphState
from app.utils.helpers import get_logger
from langsmith import traceable

logger = get_logger(__name__)


@traceable(run_type="llm")
def rewrite_question(state: GraphState) -> dict:
    """Rewrite a follow-up user message into a standalone retrieval query."""
    rewritten_question = (
        get_query_rewrite_chain()
        .invoke(
            {"question": state["question"], "chat_history": state.get("messages", [])}
        )
        .strip()
    )
    logger.info("[rewrite] %s", rewritten_question)
    return {"question": rewritten_question}

"""Node: retrieve_docs — fetch relevant documents from the selected retriever."""

from app.graphs.state import GraphState
from app.rag.retriever_registry import get_retriever_registry
from app.utils.helpers import get_logger

logger = get_logger(__name__)


def retrieve_docs(state: GraphState) -> dict:
    """Fetch relevant documents from the selected retriever."""
    registry = get_retriever_registry()
    retriever = registry[state["retriever_name"]]["retriever"]
    docs = retriever.invoke(state["question"])
    logger.info("[retrieve] → %d chunks from '%s'", len(docs), state["retriever_name"])
    return {"documents": docs}

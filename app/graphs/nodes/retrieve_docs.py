"""Node: retrieve_docs — fetch relevant documents from the default retriever."""

from app.graphs.state import GraphState
from app.rag.retriever_registry import get_default_retriever
from app.utils.helpers import get_logger

logger = get_logger(__name__)


def retrieve_docs(state: GraphState) -> dict:
    """Fetch relevant documents from the default retriever."""
    retriever = get_default_retriever()
    docs = retriever.invoke(state["question"])
    logger.info("[retrieve] → %d chunks", len(docs))
    return {"documents": docs}

"""Shared FastAPI dependencies — singleton LangGraph RAG graph."""

from app.graphs.agent import build_rag_graph
from app.utils.helpers import get_logger

logger = get_logger(__name__)

_graph = None


def init_rag_graph() -> None:
    """Initialize the LangGraph RAG graph (called once at app startup)."""
    global _graph
    logger.info("Building LangGraph RAG graph...")
    _graph = build_rag_graph()
    logger.info("LangGraph RAG graph ready.")


def get_rag_graph():
    """Return the compiled LangGraph graph."""
    if _graph is None:
        raise RuntimeError("RAG graph not initialized. Call init_rag_graph() first.")
    return _graph

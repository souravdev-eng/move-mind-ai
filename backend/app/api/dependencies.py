"""Shared FastAPI dependencies — singleton LangGraph RAG graph."""

from app.db.connection import close_pool, get_checkpointer, init_pool
from app.graphs.agent import build_rag_graph
from app.utils.helpers import get_logger

logger = get_logger(__name__)

_graph = None


async def init_rag_graph() -> None:
    """Open the Postgres pool and build the graph with a durable checkpointer."""
    global _graph
    logger.info("Initialising Postgres pool...")
    await init_pool()
    checkpointer = get_checkpointer()
    logger.info("Building LangGraph RAG graph (PostgresSaver)...")
    _graph = build_rag_graph(checkpointer=checkpointer)
    logger.info("LangGraph RAG graph ready.")


async def shutdown_rag_graph() -> None:
    """Close the Postgres pool on shutdown."""
    await close_pool()


def get_rag_graph():
    """Return the compiled LangGraph graph."""
    if _graph is None:
        raise RuntimeError("RAG graph not initialized. Call init_rag_graph() first.")
    return _graph

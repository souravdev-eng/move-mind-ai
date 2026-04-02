"""Retriever factory — returns the default Pinecone retriever."""

from app.config import settings
from app.rag.pinecone_store import get_vectorstore
from app.utils.helpers import get_logger

logger = get_logger(__name__)

_retriever = None


def get_default_retriever():
    """Return a singleton Pinecone retriever for CMS3 log debugging."""
    global _retriever
    if _retriever is None:
        store = get_vectorstore()
        _retriever = store.as_retriever(search_kwargs={"k": settings.RETRIEVER_TOP_K})
        logger.info(
            "Default retriever loaded from Pinecone index '%s' (top_k=%d, namespace='%s')",
            settings.PINECONE_INDEX_NAME,
            settings.RETRIEVER_TOP_K,
            settings.PINECONE_NAMESPACE,
        )
    return _retriever

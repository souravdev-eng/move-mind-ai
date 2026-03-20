"""Retriever registry — named retrievers that the router can pick from.

Add new retrievers here as you build more vectorstores.
"""

from pathlib import Path

from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings

from app.config import settings
from app.utils.helpers import get_logger

logger = get_logger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

_registry: dict | None = None


def _build_registry() -> dict:
    """Load vectorstores and build the retriever registry."""
    vectorstore_path = PROJECT_ROOT / settings.VECTORSTORE_PATH
    embeddings = OpenAIEmbeddings(
        api_key=settings.OPENAI_API_KEY,
        model=settings.EMBEDDING_MODEL_NAME,
    )

    admin_tech_store = FAISS.load_local(
        str(vectorstore_path), embeddings, allow_dangerous_deserialization=True
    )

    return {
        "admin_tech_docs": {
            "retriever": admin_tech_store.as_retriever(
                search_kwargs={"k": settings.RETRIEVER_TOP_K}
            ),
            "description": (
                "Technical documentation for the AMS Admin Tool — "
                "architecture, features, code quality, operations."
            ),
        },
        # "business_metrics": {
        #     "retriever": business_store.as_retriever(search_kwargs={"k": 5}),
        #     "description": "Business KPIs, revenue data, quarterly reports.",
        # },
    }


def get_retriever_registry() -> dict:
    """Return the singleton retriever registry (lazy-loaded)."""
    global _registry
    if _registry is None:
        _registry = _build_registry()
        logger.info("Retriever registry loaded: %s", list(_registry.keys()))
    return _registry

"""Retriever factory — returns the default FAISS retriever."""

from pathlib import Path

from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings

from app.config import settings
from app.utils.helpers import get_logger

logger = get_logger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

_retriever = None


def get_default_retriever():
    """Return a singleton retriever for the admin tech docs (lazy-loaded)."""
    global _retriever
    if _retriever is None:
        vectorstore_path = PROJECT_ROOT / settings.VECTORSTORE_PATH
        embeddings = OpenAIEmbeddings(
            api_key=settings.OPENAI_API_KEY,
            model=settings.EMBEDDING_MODEL_NAME,
        )

        store = FAISS.load_local(
            str(vectorstore_path), embeddings, allow_dangerous_deserialization=True
        )
        _retriever = store.as_retriever(search_kwargs={"k": settings.RETRIEVER_TOP_K})
        logger.info("Default retriever loaded (top_k=%d)", settings.RETRIEVER_TOP_K)
    return _retriever

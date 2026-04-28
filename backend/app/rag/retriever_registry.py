"""Lightweight retriever factory for direct Pinecone access."""

from __future__ import annotations

from app.config import settings
from app.rag.pinecone_store import get_vectorstore


def get_default_retriever(*, k: int | None = None, metadata_filter: dict | None = None):
    """Return a Pinecone-backed retriever with optional metadata filtering."""
    search_kwargs = {"k": k or settings.RETRIEVER_EVENT_K}
    if metadata_filter:
        search_kwargs["filter"] = metadata_filter
    return get_vectorstore().as_retriever(search_kwargs=search_kwargs)

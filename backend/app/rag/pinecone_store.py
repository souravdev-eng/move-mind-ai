"""Shared Pinecone client and vector store helpers for the CMS3 log assistant."""

from __future__ import annotations

import time

from langchain_openai import OpenAIEmbeddings

from app.config import settings
from app.utils.helpers import get_logger

logger = get_logger(__name__)

_embeddings: OpenAIEmbeddings | None = None
_pc = None
_vectorstore = None


def get_embeddings() -> OpenAIEmbeddings:
    """Return a cached embeddings client for Pinecone indexing and search."""
    global _embeddings
    if _embeddings is None:
        _embeddings = OpenAIEmbeddings(
            api_key=settings.OPENAI_API_KEY,
            model=settings.EMBEDDING_MODEL_NAME,
        )
    return _embeddings


def get_pinecone_client():
    """Return a cached Pinecone control-plane client."""
    global _pc
    if _pc is None:
        if not settings.PINECONE_API_KEY:
            raise ValueError(
                "PINECONE_API_KEY is required for Pinecone-backed retrieval."
            )

        from pinecone import Pinecone

        _pc = Pinecone(api_key=settings.PINECONE_API_KEY)
    return _pc


def ensure_index() -> None:
    """Create the Pinecone index if it does not already exist."""
    pc = get_pinecone_client()
    existing_indexes = {index_info["name"] for index_info in pc.list_indexes()}

    if settings.PINECONE_INDEX_NAME in existing_indexes:
        return

    from pinecone import ServerlessSpec

    logger.info(
        "Creating Pinecone index '%s' (%d dims, %s, %s/%s)",
        settings.PINECONE_INDEX_NAME,
        settings.EMBEDDING_DIMENSION,
        settings.PINECONE_METRIC,
        settings.PINECONE_CLOUD,
        settings.PINECONE_REGION,
    )
    pc.create_index(
        name=settings.PINECONE_INDEX_NAME,
        dimension=settings.EMBEDDING_DIMENSION,
        metric=settings.PINECONE_METRIC,
        spec=ServerlessSpec(
            cloud=settings.PINECONE_CLOUD,
            region=settings.PINECONE_REGION,
        ),
    )

    while not pc.describe_index(settings.PINECONE_INDEX_NAME).status["ready"]:
        time.sleep(1)


def get_vectorstore():
    """Return a cached Pinecone-backed LangChain vector store."""
    global _vectorstore
    if _vectorstore is None:
        from langchain_pinecone import PineconeVectorStore

        ensure_index()
        pc = get_pinecone_client()
        index = (
            pc.Index(host=settings.PINECONE_INDEX_HOST)
            if settings.PINECONE_INDEX_HOST
            else pc.Index(settings.PINECONE_INDEX_NAME)
        )
        _vectorstore = PineconeVectorStore(
            index=index,
            embedding=get_embeddings(),
            namespace=settings.PINECONE_NAMESPACE,
        )
    return _vectorstore

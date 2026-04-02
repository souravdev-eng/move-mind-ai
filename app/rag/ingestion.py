"""Ingestion pipeline — load CMS3 log chunks, embed them, and upsert to Pinecone.

Usage:
    python -m app.rag.ingestion                           # default: data/processed/cms3_log_chunks.json
    python -m app.rag.ingestion --source path/to/chunks.json

Pipeline (runs after the preprocessing notebook):
    data/processed/cms3_log_chunks.json
      → Load Document objects (page_content + enriched metadata)
      → Embed with OpenAI embeddings
      → Upsert into Pinecone
"""

import hashlib
import json
from pathlib import Path

from langchain_core.documents import Document

from app.config import settings
from app.rag.chunks_loader import load_processed_chunks
from app.rag.pinecone_store import get_vectorstore
from app.utils.helpers import get_logger

logger = get_logger(__name__)

# Resolve paths relative to the project root
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
DEFAULT_CHUNKS_PATH = PROJECT_ROOT / "data" / "processed" / "cms3_log_chunks.json"


def _build_document_ids(documents: list) -> list[str]:
    """Create stable vector IDs so repeated ingests overwrite instead of duplicating."""
    ids: list[str] = []
    for doc in documents:
        payload = json.dumps(
            {"page_content": doc.page_content, "metadata": doc.metadata},
            sort_keys=True,
            default=str,
        )
        ids.append(hashlib.sha1(payload.encode("utf-8")).hexdigest())
    return ids


def _sanitize_metadata_value(value):
    """Normalize metadata into Pinecone-compatible scalar values."""
    if value is None:
        return None
    if hasattr(value, "item"):
        value = value.item()
    if isinstance(value, (str, int, float, bool)):
        return value
    if isinstance(value, list):
        sanitized = [_sanitize_metadata_value(item) for item in value]
        return [item for item in sanitized if item is not None]
    return str(value)


def _sanitize_documents_for_pinecone(documents: list[Document]) -> list[Document]:
    """Drop null metadata values before Pinecone upsert."""
    sanitized_documents: list[Document] = []
    for doc in documents:
        metadata = {
            key: sanitized
            for key, value in doc.metadata.items()
            if (sanitized := _sanitize_metadata_value(value)) is not None
        }
        sanitized_documents.append(
            Document(page_content=doc.page_content, metadata=metadata)
        )
    return sanitized_documents


def build_vectorstore(chunks_path: Path | str = DEFAULT_CHUNKS_PATH):
    """End-to-end ingestion: load chunks → embed → upsert into Pinecone.

    Args:
        chunks_path: Path to the JSON file exported by the preprocessing notebook.

    Returns:
        The Pinecone-backed vector store.
    """
    chunks_path = Path(chunks_path)

    # ── 1. Load ──────────────────────────────────────────────────────────
    logger.info("Loading chunks from %s", chunks_path)
    documents = load_processed_chunks(chunks_path)
    logger.info("Loaded %d chunks", len(documents))
    documents = _sanitize_documents_for_pinecone(documents)

    # ── 2. Embed + Upsert ────────────────────────────────────────────────
    logger.info(
        "Upserting %d chunks into Pinecone index '%s' (namespace='%s')",
        len(documents),
        settings.PINECONE_INDEX_NAME,
        settings.PINECONE_NAMESPACE,
    )
    vectorstore = get_vectorstore()
    ids = _build_document_ids(documents)
    vectorstore.add_documents(documents=documents, ids=ids)
    logger.info(
        "Pinecone upsert complete for index '%s' (namespace='%s')",
        settings.PINECONE_INDEX_NAME,
        settings.PINECONE_NAMESPACE,
    )

    return vectorstore


def verify_vectorstore() -> None:
    """Quick sanity check — query Pinecone and inspect the top matches."""
    vectorstore = get_vectorstore()
    logger.info(
        "Verification query against Pinecone index '%s' (namespace='%s')",
        settings.PINECONE_INDEX_NAME,
        settings.PINECONE_NAMESPACE,
    )

    # Test similarity search
    results = vectorstore.similarity_search(
        "For this customer, why did the flow move after move scope?",
        k=3,
    )
    logger.info("Test query returned %d results:", len(results))
    for i, doc in enumerate(results):
        logger.info(
            "  [%d] %s — %s (%.80s...)",
            i,
            doc.metadata.get("customer_id", "?"),
            doc.metadata.get("chunk_type", "?"),
            doc.page_content,
        )


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Embed CMS3 log chunks and upsert them into Pinecone."
    )
    parser.add_argument(
        "--source",
        type=str,
        default=str(DEFAULT_CHUNKS_PATH),
        help="Path to the processed chunks JSON file.",
    )
    parser.add_argument(
        "--verify",
        action="store_true",
        help="Run a verification query after building the index.",
    )
    args = parser.parse_args()

    build_vectorstore(args.source)

    if args.verify:
        verify_vectorstore()

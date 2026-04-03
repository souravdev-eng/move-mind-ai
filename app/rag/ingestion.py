"""CMS3 ingestion pipeline for preprocessing, embedding, and Pinecone upsert."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from langchain_core.documents import Document

from app.config import settings
from app.rag.chunks_loader import load_processed_chunks
from app.rag.pinecone_store import get_vectorstore
from app.rag.preprocessing import (
    build_chunk_documents,
    export_chunk_documents,
    load_raw_logs,
)
from app.utils.helpers import get_logger, sanitize_metadata_value

logger = get_logger(__name__)


def _build_document_ids(documents: list[Document]) -> list[str]:
    """Create stable vector ids so repeated ingests overwrite instead of duplicating."""
    ids: list[str] = []
    for document in documents:
        payload = json.dumps(
            {"page_content": document.page_content, "metadata": document.metadata},
            sort_keys=True,
            default=str,
        )
        ids.append(hashlib.sha1(payload.encode("utf-8")).hexdigest())
    return ids


def _sanitize_documents_for_pinecone(documents: list[Document]) -> list[Document]:
    """Drop null metadata values before Pinecone upsert."""
    sanitized_documents: list[Document] = []
    for document in documents:
        metadata = {
            key: sanitized
            for key, value in document.metadata.items()
            if (sanitized := sanitize_metadata_value(value)) is not None
        }
        sanitized_documents.append(
            Document(page_content=document.page_content, metadata=metadata)
        )
    return sanitized_documents


def _looks_like_processed_chunks(payload: object) -> bool:
    """Check if a JSON file already contains processed chunk objects."""
    if not isinstance(payload, list) or not payload:
        return False
    sample = payload[0]
    return isinstance(sample, dict) and {"page_content", "metadata"} <= set(sample)


def load_documents_for_ingestion(
    source_path: str | Path,
    *,
    source_format: str = "auto",
    export_processed: bool = False,
    processed_output_path: str | Path | None = None,
) -> list[Document]:
    """Load ingestion documents from processed chunks or raw CMS3 logs."""
    source_path = Path(source_path)

    if source_format == "processed":
        return load_processed_chunks(source_path)

    if source_format == "raw":
        raw_logs = load_raw_logs(source_path)
        documents = build_chunk_documents(raw_logs)
    else:
        payload = json.loads(source_path.read_text())
        if _looks_like_processed_chunks(payload):
            return load_processed_chunks(source_path)
        documents = build_chunk_documents(payload)

    if export_processed:
        export_target = Path(processed_output_path or settings.PROCESSED_CHUNKS_PATH)
        export_chunk_documents(documents, export_target)

    return documents


def build_vectorstore(
    source_path: str | Path | None = None,
    *,
    source_format: str = "auto",
    export_processed: bool = False,
    processed_output_path: str | Path | None = None,
):
    """End-to-end ingestion from raw logs or processed chunks into Pinecone."""
    source_path = Path(source_path or settings.PROCESSED_CHUNKS_PATH)

    logger.info("Preparing ingestion documents from %s", source_path)
    documents = load_documents_for_ingestion(
        source_path,
        source_format=source_format,
        export_processed=export_processed,
        processed_output_path=processed_output_path,
    )
    logger.info("Loaded %d ingestion chunks", len(documents))

    documents = _sanitize_documents_for_pinecone(documents)
    vectorstore = get_vectorstore()

    logger.info(
        "Upserting %d chunks into Pinecone index '%s' (namespace='%s')",
        len(documents),
        settings.PINECONE_INDEX_NAME,
        settings.PINECONE_NAMESPACE,
    )
    vectorstore.add_documents(documents=documents, ids=_build_document_ids(documents))
    logger.info("Pinecone upsert complete")
    return vectorstore


def verify_vectorstore() -> None:
    """Run a CMS3-specific sanity query against Pinecone."""
    vectorstore = get_vectorstore()
    results = vectorstore.similarity_search(
        "For CID 7093495, why did the journey move after /ccflownew/move-scope?",
        k=3,
    )
    logger.info("Verification query returned %d results", len(results))
    for index, document in enumerate(results, start=1):
        logger.info(
            "[%d] type=%s cid=%s page=%s preview=%.90s",
            index,
            document.metadata.get("chunk_type", "?"),
            document.metadata.get("customer_id", "?"),
            document.metadata.get("page_path", "?"),
            document.page_content,
        )


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Preprocess CMS3 logs if needed, then upsert chunks into Pinecone."
    )
    parser.add_argument(
        "--source",
        type=str,
        default=settings.PROCESSED_CHUNKS_PATH,
        help="Path to raw CMS3 logs or processed chunks JSON.",
    )
    parser.add_argument(
        "--source-format",
        choices=["auto", "raw", "processed"],
        default="auto",
        help="How to interpret the input source.",
    )
    parser.add_argument(
        "--export-processed",
        action="store_true",
        help="Export processed chunks when ingesting from raw logs.",
    )
    parser.add_argument(
        "--processed-output",
        type=str,
        default=settings.PROCESSED_CHUNKS_PATH,
        help="Where to export processed chunks when --export-processed is used.",
    )
    parser.add_argument(
        "--verify",
        action="store_true",
        help="Run a verification query after the upsert finishes.",
    )
    args = parser.parse_args()

    build_vectorstore(
        source_path=args.source,
        source_format=args.source_format,
        export_processed=args.export_processed,
        processed_output_path=args.processed_output,
    )

    if args.verify:
        verify_vectorstore()

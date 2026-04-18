"""Helpers for loading processed CMS3 chunks from disk."""

from __future__ import annotations

import json
from pathlib import Path

from langchain_core.documents import Document

from app.utils.helpers import get_logger

logger = get_logger(__name__)


def load_processed_chunks(chunk_file_path: Path | str) -> list[Document]:
    """Load pre-processed chunks from the shared page_content + metadata JSON shape."""
    chunk_file_path = Path(chunk_file_path)
    chunks = json.loads(chunk_file_path.read_text())

    documents = [
        Document(page_content=chunk["page_content"], metadata=chunk["metadata"])
        for chunk in chunks
    ]

    if not documents:
        raise ValueError(f"No processed chunks found in {chunk_file_path}")

    logger.info("Loaded %d processed chunks from %s", len(documents), chunk_file_path)
    logger.info("Sample document preview: %.100s", documents[0].page_content)
    return documents

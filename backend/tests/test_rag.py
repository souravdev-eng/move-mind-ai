"""Tests for app.rag."""


def test_load_processed_chunks():
    """Smoke test: processed chunks load from disk and return Documents."""
    from pathlib import Path

    from app.rag.chunks_loader import load_processed_chunks

    chunks_path = Path("data/processed/cms3_log_chunks.json")
    if not chunks_path.exists():
        import pytest

        pytest.skip("Processed chunks file not present — run ingestion first")

    docs = load_processed_chunks(chunks_path)
    assert len(docs) > 0
    assert docs[0].page_content
    assert "chunk_type" in docs[0].metadata


def test_document_sanitization():
    """Metadata sanitization drops null values and preserves valid ones."""
    from langchain_core.documents import Document

    from app.rag.ingestion import _sanitize_documents_for_pinecone

    docs = [
        Document(
            page_content="test content",
            metadata={"customer_id": "123", "empty_field": None, "step": 1},
        )
    ]
    sanitized = _sanitize_documents_for_pinecone(docs)
    assert len(sanitized) == 1
    assert "customer_id" in sanitized[0].metadata
    assert "empty_field" not in sanitized[0].metadata

"""Tests for app.rag."""

from app.rag.ingestion import load_documents, split_documents


def test_split_documents_returns_chunks():
    """Splitting a synthetic document produces chunks."""
    from langchain_core.documents import Document

    docs = [Document(page_content="Hello world. " * 500)]
    chunks = split_documents(docs)
    assert len(chunks) > 0

"""Shared graph state schema used by all nodes."""

from typing import TypedDict

from langchain_core.documents import Document


class GraphState(TypedDict):
    """State that flows through the RAG graph."""

    question: str
    retriever_name: str
    documents: list[Document]
    answer: str

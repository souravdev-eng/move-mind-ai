"""Tests for app.graphs."""


def test_rag_graph_compiles():
    """Smoke test: RAG graph compiles without errors."""
    from app.graphs.agent import build_rag_graph

    graph = build_rag_graph()
    assert graph is not None

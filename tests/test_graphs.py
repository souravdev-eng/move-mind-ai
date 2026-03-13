"""Tests for app.graphs."""


def test_agent_graph_compiles():
    """Smoke test: agent graph compiles without errors."""
    from app.graphs.agent import build_agent_graph

    graph = build_agent_graph()
    assert graph is not None

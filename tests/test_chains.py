"""Tests for app.chains."""


def test_simple_chain_builds():
    """Smoke test: chain object is created without errors."""
    from app.chains.base import build_simple_chain

    chain = build_simple_chain()
    assert chain is not None

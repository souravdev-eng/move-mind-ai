"""Tests for app.chains."""


def test_classify_chain_builds():
    """Smoke test: classify chain is created without errors."""
    from app.chains.classify_chain import get_classify_chain

    chain = get_classify_chain()
    assert chain is not None


def test_answer_chain_builds():
    """Smoke test: answer chain is created without errors."""
    from app.chains.answer_chain import get_answer_chain

    chain = get_answer_chain("what happened to CID 123?")
    assert chain is not None


def test_rewrite_chain_builds():
    """Smoke test: query rewrite chain is created without errors."""
    from app.chains.query_rewrite_chain import get_query_rewrite_chain

    chain = get_query_rewrite_chain()
    assert chain is not None

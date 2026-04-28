"""End-to-end smoke test: full question → answer pipeline.

Requires live OpenAI + Pinecone credentials (.env).
Run with: pytest tests/test_smoke.py -v -s
"""

import pytest


@pytest.mark.integration
def test_full_pipeline_cid_question():
    """Full graph run: CID investigation question returns a non-empty answer with sources."""
    from app.graphs.agent import build_rag_graph

    graph = build_rag_graph()
    config = {"configurable": {"thread_id": "smoke-test-001"}}

    result = graph.invoke(
        {
            "question": "What happened to CID 7093495?",
            "original_question": "What happened to CID 7093495?",
        },
        config=config,
    )

    assert result.get("answer"), "Expected a non-empty answer"
    assert len(result["answer"]) > 50, "Answer too short — likely a failure response"
    assert result.get("documents") or result.get("reranked_documents"), (
        "Expected retrieved documents"
    )

    print("\n--- ANSWER ---")
    print(result["answer"])
    print(f"\n--- RETRIEVED: {len(result.get('documents', []))} docs ---")
    print(f"--- RERANKED:  {len(result.get('reranked_documents', []))} docs ---")
    print(f"--- QUERY TYPE: {result.get('query_type')} ---")
    print(f"--- ACTIVE CID: {result.get('active_customer_id')} ---")


@pytest.mark.integration
def test_full_pipeline_followup_question():
    """Multi-turn: follow-up question uses context from prior turn."""
    from app.graphs.agent import build_rag_graph

    graph = build_rag_graph()
    config = {"configurable": {"thread_id": "smoke-test-002"}}

    # Turn 1 — establish context
    graph.invoke(
        {
            "question": "What happened to CID 7093495?",
            "original_question": "What happened to CID 7093495?",
        },
        config=config,
    )

    # Turn 2 — follow-up without repeating CID
    result = graph.invoke(
        {
            "question": "Why did the journey stop there?",
            "original_question": "Why did the journey stop there?",
        },
        config=config,
    )

    assert result.get("answer"), "Expected a non-empty follow-up answer"
    assert result.get("active_customer_id") == "7093495", (
        f"Expected CID to persist across turns, got: {result.get('active_customer_id')}"
    )
    assert result.get("query_type") == "rewrite", (
        f"Expected follow-up to be rewritten, got query_type: {result.get('query_type')}"
    )

    print("\n--- FOLLOW-UP ANSWER ---")
    print(result["answer"])
    print(f"\n--- QUERY TYPE: {result.get('query_type')} ---")
    print(f"--- ACTIVE CID: {result.get('active_customer_id')} ---")
    print(f"--- EFFECTIVE Q: {result.get('question')} ---")

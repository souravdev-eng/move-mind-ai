"""Eval runner — drives golden dataset questions through the RAG graph and collects raw results."""

from __future__ import annotations

import json
import uuid
from pathlib import Path
from typing import Any

from app.graphs.agent import build_rag_graph
from app.utils.helpers import get_logger

logger = get_logger(__name__)


def _invoke(graph, question: str, session_id: str) -> dict:
    """Run one question through the graph and return the result dict."""
    config = {"configurable": {"thread_id": session_id}}
    return graph.invoke(
        {"question": question, "original_question": question},
        config=config,
    )


def run_eval(dataset_path: str | Path) -> list[dict[str, Any]]:
    """
    Run all questions in the golden dataset through the live graph.

    For multi-turn questions the prior question is run first in the same session
    so the follow-up has the correct context — matching real manager behaviour.

    Returns a list of result dicts, one per golden question.
    """
    dataset_path = Path(dataset_path)
    dataset: list[dict] = json.loads(dataset_path.read_text())

    logger.info("Loading RAG graph …")
    graph = build_rag_graph()

    results: list[dict] = []

    for i, item in enumerate(dataset, start=1):
        qid = item["id"]
        category = item["category"]
        question = item["question"]

        logger.info("[%d/%d] Running %s — %s", i, len(dataset), qid, question[:60])

        session_id = f"eval-{qid}-{uuid.uuid4().hex[:8]}"

        if category == "multi_turn" and item.get("prior_question"):
            # Warm up the session with the prior question first
            logger.info("  → priming session with prior question: %s", item["prior_question"][:60])
            _invoke(graph, item["prior_question"], session_id)

        result = _invoke(graph, question, session_id)

        contexts = [
            doc["page_content"]
            for doc in (result.get("reranked_documents") or result.get("documents", []))
        ]

        results.append({
            "id": qid,
            "category": category,
            "question": question,
            "answer": result.get("answer", ""),
            "contexts": contexts,
            "query_type": result.get("query_type", ""),
            "active_customer_id": result.get("active_customer_id", ""),
            # Golden dataset fields for metric computation
            "expected_keywords": item.get("expected_keywords", []),
            "expected_not_contains": item.get("expected_not_contains", []),
            "notes": item.get("notes", ""),
        })

    logger.info("Runner complete — %d results collected", len(results))
    return results

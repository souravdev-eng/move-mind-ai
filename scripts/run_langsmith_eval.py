"""Run the `golden-v1` dataset through the live graph as a LangSmith experiment.

Run:  uv run python scripts/run_langsmith_eval.py
Env:  LANGCHAIN_API_KEY must be set and the `golden-v1` dataset must exist.
      Use `uv run python scripts/upload_dataset.py` first if it doesn't.

Each example is invoked through the real RAG graph. Token/cost metadata
is captured on every run via `invoke_with_observability`. Evaluators
run inside LangSmith so results show up in the experiment UI with
per-example drill-down to traces.
"""

from __future__ import annotations

import os
import sys
import uuid
from datetime import datetime, timezone

from app.config import settings
from app.eval.langsmith_evaluators import ALL_EVALUATORS
from app.graphs.agent import build_rag_graph
from app.obs.tracing import build_run_config, invoke_with_observability

DATASET_NAME = "golden-v1"


def main() -> int:
    if not (os.environ.get("LANGCHAIN_API_KEY") or settings.LANGCHAIN_API_KEY):
        print("LANGCHAIN_API_KEY not set; aborting.", file=sys.stderr)
        return 1

    from langsmith import Client, evaluate

    client = Client()

    print("Building graph …")
    graph = build_rag_graph()

    def target(inputs: dict) -> dict:
        """Invoke the RAG graph for one example and shape outputs for evaluators."""
        question = inputs["question"]
        session_id = f"eval-{uuid.uuid4().hex[:8]}"
        config, run_id = build_run_config(
            session_id,
            env="eval",
            explanation_mode="manager",
            question=question,
        )
        result = invoke_with_observability(
            graph,
            {"question": question, "original_question": question},
            config=config,
            run_id=run_id,
        )
        contexts = [
            doc["page_content"]
            for doc in (result.get("reranked_documents") or result.get("documents", []))
        ]
        return {
            "answer": result.get("answer", ""),
            "contexts": contexts,
            "issue_type": result.get("issue_type"),
            "query_type": result.get("query_type"),
        }

    experiment_prefix = f"golden-v1-{datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S')}"
    print(f"Starting LangSmith experiment: {experiment_prefix}")

    results = evaluate(
        target,
        data=DATASET_NAME,
        evaluators=ALL_EVALUATORS,
        experiment_prefix=experiment_prefix,
        client=client,
        max_concurrency=4,
    )

    print("Experiment complete.")
    print(f"  View in LangSmith: {getattr(results, 'experiment_name', experiment_prefix)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

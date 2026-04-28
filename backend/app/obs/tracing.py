"""Tracing helpers — enrich every graph run with metadata, tokens, and cost.

Usage:

    config = build_run_config(session_id, env="dev", explanation_mode="manager")
    result = invoke_with_observability(graph, inputs, config)

After the call, the parent LangSmith run carries:
  - metadata.env / explanation_mode / session_id
  - metadata.cid (extracted from graph state)
  - metadata.issue_type (classifier output)
  - metadata.cost_usd, total_input_tokens, total_output_tokens, per_model
  - tags: [env, explanation_mode, issue_type]

Everything is best-effort. If LangSmith is disabled or the SDK fails,
the graph still runs and the caller still gets `result`.
"""

from __future__ import annotations

import os
import time
import uuid
from contextlib import nullcontext
from typing import Any

from langchain_core.callbacks.usage import get_usage_metadata_callback
from langsmith import get_current_run_tree, tracing_context

from app.config import settings
from app.obs.pricing import cost_from_usage
from app.utils.helpers import get_logger

logger = get_logger(__name__)


def attach_span_metadata(meta: dict) -> None:
    """Attach structured attributes to the current LangSmith span (best-effort)."""
    try:
        run = get_current_run_tree()
        if run is not None:
            run.add_metadata(meta)
    except Exception:  # noqa: BLE001
        pass


def _tracing_enabled() -> bool:
    """Tracing is enabled when the env var is truthy AND an API key exists."""
    env_flag = os.environ.get("LANGCHAIN_TRACING_V2", "").lower() in {
        "1",
        "true",
        "yes",
    }
    return env_flag and bool(settings.LANGCHAIN_API_KEY)


def build_run_config(
    session_id: str,
    *,
    env: str = "dev",
    explanation_mode: str = "manager",
    question: str | None = None,
    extra_metadata: dict | None = None,
    extra_tags: list[str] | None = None,
) -> tuple[dict[str, Any], str]:
    """Build a RunnableConfig with thread_id, metadata, tags, and a pre-assigned run_id.

    Returns (config, run_id). `run_id` lets callers update the root run later.
    """
    run_id = str(uuid.uuid4())
    metadata: dict[str, Any] = {
        "env": env,
        "explanation_mode": explanation_mode,
        "session_id": session_id,
    }
    if question:
        metadata["question_preview"] = question[:200]
    if extra_metadata:
        metadata.update(extra_metadata)

    tags = [f"env:{env}", f"mode:{explanation_mode}"]
    if extra_tags:
        tags.extend(extra_tags)

    config: dict[str, Any] = {
        "configurable": {"thread_id": session_id},
        "metadata": metadata,
        "tags": tags,
        "run_id": run_id,
    }
    return config, run_id


def _update_run(run_id: str, *, metadata: dict, tags: list[str]) -> None:
    """Best-effort patch of the root run's metadata and tags."""
    if not _tracing_enabled():
        return
    try:
        from langsmith import Client

        client = Client()
        client.update_run(run_id, extra={"metadata": metadata}, tags=tags)
    except Exception as exc:  # noqa: BLE001
        logger.warning("[obs] LangSmith run update failed: %s", exc)


def _enrichment_from_result(result: dict) -> tuple[dict, list[str]]:
    """Pull cid, issue_type, query_type from graph output into metadata + tags."""
    metadata: dict[str, Any] = {}
    tags: list[str] = []

    cid = result.get("active_customer_id")
    if cid:
        metadata["cid"] = str(cid)
        tags.append(f"cid:{cid}")

    issue_type = result.get("issue_type")
    if issue_type:
        metadata["issue_type"] = issue_type
        tags.append(f"issue:{issue_type}")

    query_type = result.get("query_type")
    if query_type:
        metadata["query_type"] = query_type

    confidence = result.get("issue_confidence")
    if confidence is not None:
        metadata["issue_confidence"] = confidence

    return metadata, tags


def enrich_run_from_state(run_id: str | None, state: dict) -> None:
    """Post-hoc: push cid / issue_type / query_type onto the root run.

    Used when the streaming path lacks token/latency data (legacy callers).
    Prefer `enrich_run_from_stream` when cost + latency are available.
    """
    if not run_id:
        return
    metadata, tags = _enrichment_from_result(state)
    _update_run(run_id, metadata=metadata, tags=tags)


def enrich_run_from_stream(
    run_id: str | None,
    state: dict,
    usage_metadata: dict | None,
    latency_ms: int | None,
) -> None:
    """Post-hoc enrichment for the streaming path.

    Combines graph state (cid/issue/query_type) with token/cost totals computed
    from the usage callback and the measured end-to-end latency.
    """
    if not run_id:
        return
    metadata, tags = _enrichment_from_result(state)
    usage_totals = cost_from_usage(usage_metadata or {})
    metadata.update(usage_totals)
    if latency_ms is not None:
        metadata["latency_ms"] = latency_ms
    _update_run(run_id, metadata=metadata, tags=tags)


def project_scope(env: str):
    """Return a `tracing_context(project_name=...)` scope for the given env.

    Falls back to a no-op context when LangSmith tracing is disabled. Used by
    both the blocking and streaming paths to route runs into per-env projects.
    """
    if not _tracing_enabled():
        return nullcontext()
    project = settings.langsmith_project_for(env)
    return tracing_context(project_name=project)


def invoke_with_observability(
    graph,
    inputs: dict,
    config: dict,
    *,
    run_id: str | None = None,
) -> dict:
    """Invoke the graph while collecting tokens/cost/latency and patching the root run.

    `run_id` must match `config["run_id"]` when tracing updates are desired.
    """
    env = (config.get("metadata") or {}).get("env", "dev")

    t0 = time.perf_counter()
    with project_scope(env), get_usage_metadata_callback() as cb:
        result = graph.invoke(inputs, config=config)
    latency_ms = int((time.perf_counter() - t0) * 1000)

    usage_totals = cost_from_usage(cb.usage_metadata or {})
    run_meta, run_tags = _enrichment_from_result(result)
    run_meta.update(usage_totals)
    run_meta["latency_ms"] = latency_ms

    if run_id:
        _update_run(run_id, metadata=run_meta, tags=run_tags)

    return result

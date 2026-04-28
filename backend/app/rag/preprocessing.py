"""CMS3 log normalization and chunk building helpers."""

from __future__ import annotations

import json
from collections import Counter, defaultdict
from pathlib import Path

from langchain_core.documents import Document

from app.utils.helpers import get_logger

logger = get_logger(__name__)


def load_raw_logs(raw_log_path: str | Path) -> list[dict]:
    """Load the raw CMS3 event list from disk."""
    raw_log_path = Path(raw_log_path)
    logs = json.loads(raw_log_path.read_text())
    logger.info("Loaded %d raw CMS3 log events from %s", len(logs), raw_log_path)
    return logs


def normalize_log_event(log: dict) -> dict:
    """Convert a raw CMS3 log event into a retrieval-friendly record."""
    configuration = log.get("configuration") or {}
    result = log.get("result") or {}
    trace = log.get("trace") or {}

    decision_result = result.get("decision_result")
    target = configuration.get("target")
    condition = configuration.get("condition")

    lines = [
        f"timestamp: {log.get('timestamp', '')}",
        f"journey_id: {log.get('journey_id', '')}",
        f"execution_id: {log.get('execution_id', '')}",
        f"customer_id: {log.get('customer_id', 'unknown')}",
        f"step_order: {log.get('step_order', 'unknown')}",
        f"action: {log.get('action', '')}",
        f"event_type: {log.get('eventType', '')}",
        f"status: {log.get('status', '')}",
        f"level: {log.get('level', '')}",
        f"page_path: {log.get('page_path', '')}",
        f"source: {log.get('source', '')}",
        f"message: {log.get('message', '')}",
    ]

    if condition is not None:
        lines.append(f"condition: {condition}")
    if target is not None:
        lines.append(f"target: {target}")
    if decision_result is not None:
        lines.append(f"decision_result: {decision_result}")
    if result:
        lines.append(f"result_json: {json.dumps(result, sort_keys=True)}")
    if configuration:
        lines.append(f"configuration_json: {json.dumps(configuration, sort_keys=True)}")
    if log.get("error_code"):
        lines.append(f"error_code: {log['error_code']}")
    if log.get("error_message"):
        lines.append(f"error_message: {log['error_message']}")
    if trace:
        lines.append(f"trace_json: {json.dumps(trace, sort_keys=True)}")

    return {
        "id": log.get("id"),
        "timestamp": log.get("timestamp"),
        "journey_id": log.get("journey_id"),
        "execution_id": log.get("execution_id"),
        "customer_id": log.get("customer_id"),
        "step_id": log.get("step_id"),
        "previous_step_id": log.get("previous_step_id"),
        "step_order": log.get("step_order"),
        "status": log.get("status"),
        "level": log.get("level"),
        "action": log.get("action"),
        "event_type": log.get("eventType"),
        "page_path": log.get("page_path"),
        "source": log.get("source"),
        "message": log.get("message"),
        "target": target,
        "condition": condition,
        "decision_result": decision_result,
        "error_code": log.get("error_code"),
        "error_message": log.get("error_message"),
        "environment": trace.get("environment"),
        "release": trace.get("release"),
        "session_id": trace.get("session_id"),
        "event_text": "\n".join(lines),
        "raw": log,
    }


def build_group_key(event: dict) -> str:
    """Use customer_id as the business key and execution_id as the run boundary."""
    customer_id = event.get("customer_id") or "unknown_customer"
    execution_id = event.get("execution_id") or "unknown_execution"
    return f"cid:{customer_id} | exec:{execution_id}"


def group_logs_by_customer_and_execution(events: list[dict]) -> dict[str, list[dict]]:
    """Group normalized events into customer/execution buckets."""
    grouped: dict[str, list[dict]] = defaultdict(list)
    for event in events:
        grouped[build_group_key(event)].append(event)

    for group_key, items in grouped.items():
        grouped[group_key] = sorted(
            items,
            key=lambda item: (item.get("step_order") or 0, item.get("timestamp") or ""),
        )
    return dict(grouped)


def build_event_document(event: dict) -> Document:
    """Create one precise evidence chunk for a single CMS3 event."""
    metadata = {
        "chunk_type": "event",
        "source": "cms3_logs",
        "journey_id": event.get("journey_id"),
        "execution_id": event.get("execution_id"),
        "customer_id": event.get("customer_id"),
        "step_id": event.get("step_id"),
        "previous_step_id": event.get("previous_step_id"),
        "step_order": event.get("step_order"),
        "status": event.get("status"),
        "level": event.get("level"),
        "action": event.get("action"),
        "event_type": event.get("event_type"),
        "page_path": event.get("page_path"),
        "target": event.get("target"),
        "decision_result": event.get("decision_result"),
        "error_code": event.get("error_code"),
        "environment": event.get("environment"),
        "release": event.get("release"),
    }
    return Document(page_content=event["event_text"], metadata=metadata)


def build_execution_summary_document(group_key: str, events: list[dict]) -> Document:
    """Create one broad chunk that summarizes an execution's route and conditions."""
    routes = [
        event["page_path"]
        for event in events
        if event.get("action") == "route_entered" and event.get("page_path")
    ]
    unique_routes = list(dict.fromkeys(routes))

    condition_hits = []
    for event in events:
        if event.get("action") == "evaluate_ui_condition":
            condition_hits.append(
                {
                    "step_order": event.get("step_order"),
                    "condition": event.get("condition"),
                    "decision_result": event.get("decision_result"),
                    "target": event.get("target"),
                    "page_path": event.get("page_path"),
                }
            )

    customer_ids = sorted(
        {event["customer_id"] for event in events if event.get("customer_id")}
    )
    execution_ids = sorted(
        {event["execution_id"] for event in events if event.get("execution_id")}
    )
    statuses = Counter(event.get("status") for event in events)
    actions = Counter(event.get("action") for event in events)

    content_lines = [
        f"group_key: {group_key}",
        f"journey_id: {events[0].get('journey_id')}",
        f"customer_ids: {customer_ids or ['unknown']}",
        f"execution_ids: {execution_ids or ['unknown']}",
        f"event_count: {len(events)}",
        f"step_range: {events[0].get('step_order')} -> {events[-1].get('step_order')}",
        f"status_counts: {dict(statuses)}",
        f"top_actions: {dict(actions.most_common(8))}",
        f"route_path: {' -> '.join(unique_routes)}",
        "condition_checks:",
    ]

    for hit in condition_hits[:12]:
        content_lines.append(
            f"- step {hit['step_order']} | page={hit['page_path']} | "
            f"condition={hit['condition']} | result={hit['decision_result']} | "
            f"target={hit['target']}"
        )

    metadata = {
        "chunk_type": "execution_summary",
        "source": "cms3_logs",
        "group_key": group_key,
        "journey_id": events[0].get("journey_id"),
        "execution_id": execution_ids[0] if execution_ids else None,
        "customer_id": customer_ids[0] if customer_ids else None,
        "event_count": len(events),
        "status": (
            "error"
            if any(
                event.get("status") != "success"
                or event.get("error_code")
                or event.get("error_message")
                for event in events
            )
            else "success"
        ),
        "first_step_order": events[0].get("step_order"),
        "last_step_order": events[-1].get("step_order"),
        "route_count": len(unique_routes),
    }
    return Document(page_content="\n".join(content_lines), metadata=metadata)


def build_chunk_documents(raw_logs: list[dict]) -> list[Document]:
    """Create execution-summary and event chunks from raw CMS3 logs."""
    normalized_logs = [normalize_log_event(log) for log in raw_logs]
    execution_groups = group_logs_by_customer_and_execution(normalized_logs)

    all_chunks: list[Document] = []
    for group_key, events in execution_groups.items():
        all_chunks.append(build_execution_summary_document(group_key, events))
        all_chunks.extend(build_event_document(event) for event in events)

    logger.info(
        "Built %d chunks across %d customer/execution groups",
        len(all_chunks),
        len(execution_groups),
    )
    return all_chunks


def export_chunk_documents(documents: list[Document], export_path: str | Path) -> Path:
    """Persist processed chunks in the shared page_content + metadata shape."""
    export_path = Path(export_path)
    export_path.parent.mkdir(parents=True, exist_ok=True)

    payload = [
        {"page_content": document.page_content, "metadata": document.metadata}
        for document in documents
    ]
    export_path.write_text(json.dumps(payload, indent=2, default=str))
    logger.info("Exported %d chunks to %s", len(payload), export_path)
    return export_path

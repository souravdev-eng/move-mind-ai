"""CMS3 retrieval helpers built around metadata-scoped Pinecone search."""

from __future__ import annotations

import json
import re
from functools import lru_cache

from langchain_core.documents import Document
from langchain_core.messages import BaseMessage

from app.config import settings
from app.rag.chunks_loader import load_processed_chunks
from app.rag.pinecone_store import get_vectorstore

CID_PATTERN = re.compile(r"\bCID\s*[:#-]?\s*(\d+)\b", re.IGNORECASE)
PAGE_PATTERN = re.compile(r"(/[A-Za-z0-9._/-]+)")
EXECUTION_PATTERN = re.compile(r"\b(exec-[A-Za-z0-9-]+)\b", re.IGNORECASE)


def extract_customer_id(query: str) -> str | None:
    """Extract a CID/customer id from the user query."""
    match = CID_PATTERN.search(query)
    return match.group(1) if match else None


def extract_page_path(query: str) -> str | None:
    """Extract a CMS3 route path from the user query."""
    match = PAGE_PATTERN.search(query)
    return match.group(1) if match else None


def extract_execution_id(query: str) -> str | None:
    """Extract an execution id from the user query or prior answer text."""
    match = EXECUTION_PATTERN.search(query)
    return match.group(1) if match else None


def _message_content(message: BaseMessage | dict) -> str:
    """Convert LangChain chat message content into plain text."""
    if isinstance(message, dict):
        content = message.get("content", "")
    else:
        content = message.content
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = []
        for item in content:
            if isinstance(item, dict):
                text = item.get("text")
                if text:
                    parts.append(text)
            else:
                parts.append(str(item))
        return " ".join(parts)
    return str(content)


def _fallback_from_history(
    extractor, chat_history: list[BaseMessage] | None
) -> str | None:
    """Search most recent chat messages for a missing CID or page path."""
    if not chat_history:
        return None

    for message in reversed(chat_history):
        value = extractor(_message_content(message))
        if value:
            return value
    return None


def question_targets_api_timeline(question: str) -> bool:
    """Whether the user is asking for API-call counts, lists, or ordering."""
    text = question.lower()
    markers = (
        " api",
        "apis",
        "graphql",
        "request",
        "requests",
        "endpoint",
        "endpoints",
        "bullet",
        "order-wise",
        "in order",
    )
    return any(marker in text for marker in markers)


def build_scope_filter(
    question: str,
    chat_history: list[BaseMessage] | None = None,
    session_context: dict | None = None,
) -> dict | None:
    """Build the metadata filter used to narrow log retrieval."""
    metadata_filter = {}
    session_context = session_context or {}

    customer_id = extract_customer_id(question) or session_context.get("active_customer_id")
    page_path = extract_page_path(question) or session_context.get("active_page_path")

    if not customer_id:
        customer_id = _fallback_from_history(extract_customer_id, chat_history)
    if not page_path:
        page_path = _fallback_from_history(extract_page_path, chat_history)

    if customer_id:
        metadata_filter["customer_id"] = customer_id
    if page_path:
        metadata_filter["page_path"] = page_path

    return metadata_filter or None


@lru_cache(maxsize=1)
def _processed_chunk_docs() -> tuple[Document, ...]:
    """Cache processed chunks for deterministic aggregation-style queries."""
    return tuple(load_processed_chunks(settings.PROCESSED_CHUNKS_PATH))


def _sorted_event_docs(
    customer_id: str | None,
    execution_id: str | None,
) -> list[Document]:
    """Return filtered event chunks ordered by execution step."""
    event_docs: list[Document] = []
    for document in _processed_chunk_docs():
        metadata = document.metadata
        if metadata.get("chunk_type") != "event":
            continue
        if customer_id and str(metadata.get("customer_id")) != customer_id:
            continue
        if execution_id and metadata.get("execution_id") != execution_id:
            continue
        event_docs.append(document)

    return sorted(
        event_docs,
        key=lambda doc: (
            doc.metadata.get("step_order") or 0,
            doc.metadata.get("page_path") or "",
        ),
    )


def _resolve_execution_id(
    customer_id: str | None,
    execution_id: str | None,
    chat_history: list[BaseMessage] | None,
) -> str | None:
    """Prefer an explicit execution id, else infer one when the customer has one run."""
    if execution_id:
        return execution_id

    execution_id = _fallback_from_history(extract_execution_id, chat_history)
    if execution_id:
        return execution_id

    if not customer_id:
        return None

    execution_ids = {
        document.metadata.get("execution_id")
        for document in _processed_chunk_docs()
        if document.metadata.get("chunk_type") == "event"
        and str(document.metadata.get("customer_id")) == customer_id
        and document.metadata.get("execution_id")
    }
    if len(execution_ids) == 1:
        return next(iter(execution_ids))
    return None


def build_api_timeline_documents(
    question: str,
    chat_history: list[BaseMessage] | None = None,
    session_context: dict | None = None,
) -> list[Document]:
    """Build a structured API timeline summary for journey-level API questions."""
    session_context = session_context or {}
    customer_id = extract_customer_id(question) or _fallback_from_history(
        extract_customer_id, chat_history
    )
    customer_id = customer_id or session_context.get("active_customer_id")
    execution_id = _resolve_execution_id(
        customer_id,
        extract_execution_id(question) or session_context.get("active_execution_id"),
        chat_history,
    )

    if not customer_id and not execution_id:
        return []

    event_docs = _sorted_event_docs(customer_id, execution_id)
    if not event_docs:
        return []

    if customer_id and not execution_id:
        execution_ids = {
            document.metadata.get("execution_id")
            for document in event_docs
            if document.metadata.get("execution_id")
        }
        if len(execution_ids) > 1:
            return []

    request_events = [
        document
        for document in event_docs
        if document.metadata.get("action") == "graphql_request"
    ]
    named_api_events = [
        document
        for document in event_docs
        if str(document.metadata.get("action") or "").startswith("gql_")
    ]
    if not request_events and not named_api_events:
        return []

    resolved_customer_id = customer_id or str(
        next(
            (
                document.metadata.get("customer_id")
                for document in event_docs
                if document.metadata.get("customer_id")
            ),
            "",
        )
    )
    resolved_execution_id = execution_id or next(
        (
            document.metadata.get("execution_id")
            for document in event_docs
            if document.metadata.get("execution_id")
        ),
        None,
    )

    lines = [
        "api_timeline_type: cms3_journey_api_timeline",
        f"customer_id: {resolved_customer_id or 'unknown'}",
        f"execution_id: {resolved_execution_id or 'unknown'}",
        (
            "interpretation_note: In these logs, `graphql_request` events are transport-level "
            "GraphQL requests, while `gql_*` actions are named business operations."
        ),
        f"graphql_request_count: {len(request_events)}",
        f"named_graphql_operation_count: {len(named_api_events)}",
        "ordered_graphql_requests:",
    ]
    for index, document in enumerate(request_events, start=1):
        metadata = document.metadata
        lines.append(
            f"{index}. step={metadata.get('step_order')} | "
            f"page={metadata.get('page_path')} | action=graphql_request"
        )

    lines.append("ordered_named_graphql_operations:")
    for index, document in enumerate(named_api_events, start=1):
        metadata = document.metadata
        lines.append(
            f"{index}. step={metadata.get('step_order')} | "
            f"page={metadata.get('page_path')} | action={metadata.get('action')}"
        )

    summary_document = Document(
        page_content="\n".join(lines),
        metadata={
            "chunk_type": "api_timeline_summary",
            "retrieval_strategy": "structured_api_timeline",
            "customer_id": resolved_customer_id,
            "execution_id": resolved_execution_id,
            "graphql_request_count": len(request_events),
            "named_graphql_operation_count": len(named_api_events),
        },
    )

    # Preserve a few raw supporting events after the summary for concrete evidence.
    supporting_docs = named_api_events[:5] or request_events[:5]
    return [summary_document, *supporting_docs]


def dedupe_documents(documents: list[Document]) -> list[Document]:
    """Keep document order stable while removing duplicate chunks."""
    unique_documents: list[Document] = []
    seen = set()
    for document in documents:
        key = (
            document.page_content,
            json.dumps(document.metadata, sort_keys=True, default=str),
        )
        if key in seen:
            continue
        seen.add(key)
        unique_documents.append(document)
    return unique_documents


def retrieve_candidates(
    question: str,
    *,
    chat_history: list[BaseMessage] | None = None,
    session_context: dict | None = None,
    k_summary: int | None = None,
    k_events: int | None = None,
) -> list[Document]:
    """Retrieve summary and event chunks, then merge them into one candidate set."""
    if question_targets_api_timeline(question):
        api_timeline_documents = build_api_timeline_documents(
            question,
            chat_history,
            session_context,
        )
        if api_timeline_documents:
            return api_timeline_documents

    vectorstore = get_vectorstore()
    base_filter = build_scope_filter(question, chat_history, session_context) or {}

    summary_filter = {"chunk_type": "execution_summary"}
    if "customer_id" in base_filter:
        summary_filter["customer_id"] = base_filter["customer_id"]

    event_filter = {"chunk_type": "event", **base_filter}

    summary_docs = vectorstore.similarity_search(
        question,
        k=k_summary or settings.RETRIEVER_SUMMARY_K,
        filter=summary_filter,
    )
    event_docs = vectorstore.similarity_search(
        question,
        k=k_events or settings.RETRIEVER_EVENT_K,
        filter=event_filter,
    )
    return dedupe_documents(summary_docs + event_docs)

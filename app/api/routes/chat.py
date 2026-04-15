"""Chat endpoints for the CMS3 log-debugging assistant."""

from __future__ import annotations

import json
import uuid

from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from app.api.dependencies import get_rag_graph
from app.graphs.constants import (
    NODE_CLASSIFY_ISSUE,
    NODE_CLASSIFY_QUESTION,
    NODE_GENERATE_ANSWER,
    NODE_RERANK_DOCS,
    NODE_RESOLVE_CONTEXT,
    NODE_RETRIEVE_DOCS,
    NODE_REWRITE_QUESTION,
)
from app.models.schemas import ChatRequest, ChatResponse, SourceDocument
from app.obs.tracing import (
    build_run_config,
    enrich_run_from_state,
    invoke_with_observability,
)
from app.utils.helpers import get_logger

router = APIRouter()
logger = get_logger(__name__)


def _run_config(
    session_id: str | None, question: str, explanation_mode: str
) -> tuple[dict, str, str]:
    """Build an observability-aware RunnableConfig; returns (config, thread_id, run_id)."""
    thread_id = session_id or str(uuid.uuid4())
    config, run_id = build_run_config(
        thread_id,
        env="dev",
        explanation_mode=explanation_mode,
        question=question,
    )
    return config, thread_id, run_id


def _docs_to_sources(documents: list[dict]) -> list[SourceDocument]:
    """Convert graph-state document dicts into API source objects."""
    sources: list[SourceDocument] = []
    for document in documents:
        metadata = document.get("metadata", {})
        sources.append(
            SourceDocument(
                content=document.get("page_content", "")[:400],
                chunk_type=metadata.get("chunk_type", "") or "",
                customer_id=str(metadata.get("customer_id", "") or ""),
                execution_id=str(metadata.get("execution_id", "") or ""),
                journey_id=str(metadata.get("journey_id", "") or ""),
                page_path=str(metadata.get("page_path", "") or ""),
                action=str(metadata.get("action", "") or ""),
                step_order=metadata.get("step_order"),
                target=str(metadata.get("target", "") or ""),
                decision_result=metadata.get("decision_result"),
                status=str(metadata.get("status", "") or ""),
                error_code=str(metadata.get("error_code", "") or ""),
            )
        )
    return sources


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Run the CMS3 debugging graph and return the answer plus evidence."""
    explanation_mode = "manager"
    config, thread_id, run_id = _run_config(
        request.session_id, request.message, explanation_mode
    )

    if request.stream:
        return StreamingResponse(
            _stream_response(request.message, config, thread_id, run_id),
            media_type="text/event-stream",
        )

    graph = get_rag_graph()
    result = invoke_with_observability(
        graph,
        {"question": request.message, "original_question": request.message},
        config=config,
        run_id=run_id,
    )

    documents = result.get("documents", [])
    reranked_documents = result.get("reranked_documents", [])
    source_documents = reranked_documents or documents

    return ChatResponse(
        answer=result["answer"],
        session_id=thread_id,
        query_type=result.get("query_type"),
        effective_question=result.get("question"),
        retrieved_count=len(documents),
        reranked_count=len(reranked_documents),
        sources=_docs_to_sources(source_documents),
        issue_type=result.get("issue_type"),
        issue_confidence=result.get("issue_confidence"),
        issue_classification_reason=result.get("issue_classification_reason"),
    )


_STATUS_NODES = {
    NODE_CLASSIFY_QUESTION,
    NODE_REWRITE_QUESTION,
    NODE_RESOLVE_CONTEXT,
    NODE_RETRIEVE_DOCS,
    NODE_RERANK_DOCS,
    NODE_GENERATE_ANSWER,
    NODE_CLASSIFY_ISSUE,
}


async def _stream_response(question: str, config: dict, thread_id: str, run_id: str):
    """SSE generator with node statuses, streamed answer tokens, and final evidence."""
    graph = get_rag_graph()
    documents: list[dict] = []
    reranked_documents: list[dict] = []
    query_type: str | None = None
    effective_question = question
    final_answer = ""
    emitted_token = False
    active_customer_id: str | None = None

    yield f"data: {json.dumps({'type': 'session', 'session_id': thread_id})}\n\n"

    issue_type: str | None = None
    issue_confidence: float | None = None
    issue_classification_reason: str | None = None

    async for event in graph.astream_events(
        {"question": question, "original_question": question},
        config=config,
        version="v2",
    ):
        kind = event["event"]
        name = event.get("name", "")
        tags = event.get("tags", [])

        if kind == "on_chain_start" and name in _STATUS_NODES:
            yield f"data: {json.dumps({'type': 'status', 'node': name})}\n\n"

        elif kind == "on_chain_end" and name == NODE_CLASSIFY_QUESTION:
            output = event.get("data", {}).get("output", {})
            query_type = output.get("query_type")

        elif kind == "on_chain_end" and name == NODE_REWRITE_QUESTION:
            output = event.get("data", {}).get("output", {})
            effective_question = output.get("question", effective_question)

        elif kind == "on_chain_end" and name == NODE_RETRIEVE_DOCS:
            output = event.get("data", {}).get("output", {})
            documents = output.get("documents", [])
            yield (
                "data: "
                + json.dumps(
                    {
                        "type": "retrieval",
                        "retrieved_count": len(documents),
                    }
                )
                + "\n\n"
            )

        elif kind == "on_chain_end" and name == NODE_RERANK_DOCS:
            output = event.get("data", {}).get("output", {})
            reranked_documents = output.get("reranked_documents", [])
            yield (
                "data: "
                + json.dumps(
                    {
                        "type": "rerank",
                        "reranked_count": len(reranked_documents),
                    }
                )
                + "\n\n"
            )

        elif kind == "on_chat_model_stream" and NODE_GENERATE_ANSWER in tags:
            chunk = event.get("data", {}).get("chunk")
            if chunk and getattr(chunk, "content", None):
                emitted_token = True
                yield (
                    f"data: {json.dumps({'type': 'token', 'content': chunk.content})}\n\n"
                )

        elif kind == "on_chain_end" and name == NODE_GENERATE_ANSWER:
            output = event.get("data", {}).get("output", {})
            final_answer = output.get("answer", "") or ""

        elif kind == "on_chain_end" and name == NODE_RESOLVE_CONTEXT:
            output = event.get("data", {}).get("output", {})
            active_customer_id = output.get("active_customer_id") or active_customer_id

        elif kind == "on_chain_end" and name == NODE_CLASSIFY_ISSUE:
            output = event.get("data", {}).get("output", {})
            issue_type = output.get("issue_type")
            issue_confidence = output.get("issue_confidence")
            issue_classification_reason = output.get("issue_classification_reason")

    if final_answer and not emitted_token:
        yield f"data: {json.dumps({'type': 'token', 'content': final_answer})}\n\n"

    sources = _docs_to_sources(reranked_documents or documents)
    yield (
        "data: "
        + json.dumps(
            {
                "type": "sources",
                "session_id": thread_id,
                "query_type": query_type,
                "effective_question": effective_question,
                "retrieved_count": len(documents),
                "reranked_count": len(reranked_documents),
                "sources": [source.model_dump() for source in sources],
                "issue_type": issue_type,
                "issue_confidence": issue_confidence,
                "issue_classification_reason": issue_classification_reason,
            }
        )
        + "\n\n"
    )

    enrich_run_from_state(
        run_id,
        {
            "active_customer_id": active_customer_id,
            "issue_type": issue_type,
            "issue_confidence": issue_confidence,
            "query_type": query_type,
        },
    )

    yield "data: [DONE]\n\n"

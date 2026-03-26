"""Chat endpoints – invoke LangGraph RAG pipeline via REST."""

import json
import uuid

from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from app.api.dependencies import get_rag_graph
from app.graphs.constants import (
    NODE_CLASSIFY_QUESTION,
    NODE_GENERATE_ANSWER,
    NODE_RETRIEVE_DOCS,
    NODE_REWRITE_QUESTION,
)
from app.models.schemas import ChatRequest, ChatResponse, SourceDocument
from app.utils.helpers import get_logger

router = APIRouter()
logger = get_logger(__name__)


def _thread_config(session_id: str | None) -> dict:
    """Build the LangGraph config with thread_id for memory."""
    thread_id = session_id or str(uuid.uuid4())
    return {"configurable": {"thread_id": thread_id}}


def _docs_to_sources(docs) -> list[SourceDocument]:
    """Convert LangChain Documents to SourceDocument schema objects."""
    return [
        SourceDocument(
            content=doc.page_content[:300],
            doc_title=doc.metadata.get("doc_title", ""),
            doc_type=doc.metadata.get("doc_type", ""),
            section=doc.metadata.get("section", ""),
            source=doc.metadata.get("source", ""),
        )
        for doc in docs
    ]


@router.post("/chat")
async def chat(request: ChatRequest):
    """Send a message and get an AI-generated response.

    Uses the LangGraph RAG graph:
        route_query → retrieve_docs → generate_answer

    - If `stream=false` (default): returns JSON with answer + sources.
    - If `stream=true`: returns SSE stream of token chunks, then sources.
    """
    config = _thread_config(request.session_id)

    if request.stream:
        return StreamingResponse(
            _stream_response(request.message, config),
            media_type="text/event-stream",
        )

    # ── Sync: invoke the full graph ──────────────────────────────────────
    graph = get_rag_graph()
    result = graph.invoke({"question": request.message}, config=config)

    sources = _docs_to_sources(result.get("documents", []))

    return ChatResponse(
        answer=result["answer"],
        sources=sources,
    )


# Node names for status tracking
_STATUS_NODES = {
    NODE_CLASSIFY_QUESTION,
    NODE_REWRITE_QUESTION,
    NODE_RETRIEVE_DOCS,
    NODE_GENERATE_ANSWER,
}


async def _stream_response(question: str, config: dict):
    """SSE generator — token-level streaming via astream_events.

    Emits:
        {type: 'status', node: '...'}           — when a node starts
        {type: 'token',  content: '...'}         — LLM tokens from generate_answer
        {type: 'sources', sources: [...]}        — retrieved source docs
        [DONE]                                   — end of stream
    """
    graph = get_rag_graph()
    documents = []

    async for event in graph.astream_events(
        {"question": question}, config=config, version="v2"
    ):
        kind = event["event"]
        name = event.get("name", "")
        tags = event.get("tags", [])

        # ── Node start → status update ────────────────────────────────
        if kind == "on_chain_start" and name in _STATUS_NODES:
            yield f"data: {json.dumps({'type': 'status', 'node': name})}\n\n"

        # ── Retrieve docs complete → capture documents ────────────────
        elif kind == "on_chain_end" and name == NODE_RETRIEVE_DOCS:
            output = event.get("data", {}).get("output", {})
            documents = output.get("documents", [])
            yield f"data: {json.dumps({'type': 'status', 'node': NODE_RETRIEVE_DOCS, 'count': len(documents)})}\n\n"

        # ── LLM token from generate_answer → stream to client ─────────
        elif kind == "on_chat_model_stream" and NODE_GENERATE_ANSWER in tags:
            chunk = event.get("data", {}).get("chunk")
            if chunk and hasattr(chunk, "content") and chunk.content:
                yield f"data: {json.dumps({'type': 'token', 'content': chunk.content})}\n\n"

    # ── Send source documents ─────────────────────────────────────────
    sources = [
        {
            "content": doc.page_content[:300],
            "doc_title": doc.metadata.get("doc_title", ""),
            "doc_type": doc.metadata.get("doc_type", ""),
            "section": doc.metadata.get("section", ""),
            "source": doc.metadata.get("source", ""),
        }
        for doc in documents
    ]

    yield f"data: {json.dumps({'type': 'sources', 'sources': sources})}\n\n"
    yield "data: [DONE]\n\n"

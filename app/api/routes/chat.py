"""Chat endpoints – invoke LangGraph RAG pipeline via REST."""

import json
import uuid

from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from app.api.dependencies import get_rag_graph
from app.graphs.constants import NODE_GENERATE_ANSWER, NODE_RETRIEVE_DOCS
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


async def _stream_response(question: str, config: dict):
    """SSE generator — stream graph events, emit tokens + sources."""
    graph = get_rag_graph()

    # Stream graph node-by-node using astream
    documents = []
    async for event in graph.astream({"question": question}, config=config):
        # Each event is {node_name: {state_updates}}
        if NODE_RETRIEVE_DOCS in event:
            documents = event[NODE_RETRIEVE_DOCS].get("documents", [])
            yield f"data: {json.dumps({'type': 'status', 'node': NODE_RETRIEVE_DOCS, 'count': len(documents)})}\n\n"

        elif NODE_GENERATE_ANSWER in event:
            answer = event[NODE_GENERATE_ANSWER].get("answer", "")
            yield f"data: {json.dumps({'type': 'answer', 'content': answer})}\n\n"

    # Send source documents
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

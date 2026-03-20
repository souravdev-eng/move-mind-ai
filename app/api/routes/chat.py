"""Chat endpoints – invoke LangGraph RAG pipeline via REST."""

import json

from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from app.api.dependencies import get_rag_graph
from app.graphs.constants import NODE_GENERATE_ANSWER, NODE_RETRIEVE_DOCS, NODE_ROUTE_QUERY
from app.models.schemas import ChatRequest, ChatResponse, SourceDocument
from app.utils.helpers import get_logger

router = APIRouter()
logger = get_logger(__name__)


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
    if request.stream:
        return StreamingResponse(
            _stream_response(request.message),
            media_type="text/event-stream",
        )

    # ── Sync: invoke the full graph ──────────────────────────────────────
    graph = get_rag_graph()
    result = graph.invoke({"question": request.message})

    sources = _docs_to_sources(result.get("documents", []))

    return ChatResponse(
        answer=result["answer"],
        sources=sources,
    )


async def _stream_response(question: str):
    """SSE generator — stream graph events, emit tokens + sources."""
    graph = get_rag_graph()

    # Stream graph node-by-node using astream
    documents = []
    async for event in graph.astream({"question": question}):
        # Each event is {node_name: {state_updates}}
        if NODE_ROUTE_QUERY in event:
            retriever_name = event[NODE_ROUTE_QUERY].get("retriever_name", "")
            yield f"data: {json.dumps({'type': 'status', 'node': NODE_ROUTE_QUERY, 'retriever': retriever_name})}\n\n"

        elif NODE_RETRIEVE_DOCS in event:
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

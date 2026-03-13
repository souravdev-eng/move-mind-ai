"""Chat endpoints – invoke chains, graphs, or RAG pipelines via REST."""

from fastapi import APIRouter

from app.models.schemas import ChatRequest, ChatResponse

router = APIRouter()


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Send a message and get an AI-generated response."""
    # TODO: Wire up your pipeline here, e.g.:
    #   from app.chains.base import build_simple_chain
    #   chain = build_simple_chain()
    #   answer = chain.invoke({"input": request.message})
    answer = f"Echo: {request.message}"
    return ChatResponse(answer=answer)

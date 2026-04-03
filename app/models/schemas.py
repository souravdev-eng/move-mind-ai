"""Shared API schemas for the CMS3 debugging assistant."""

from __future__ import annotations

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    """Incoming chat request."""

    message: str
    session_id: str | None = None
    stream: bool = False


class SourceDocument(BaseModel):
    """Retrieved CMS3 evidence chunk returned alongside the answer."""

    content: str
    chunk_type: str = ""
    customer_id: str = ""
    execution_id: str = ""
    journey_id: str = ""
    page_path: str = ""
    action: str = ""
    step_order: int | None = None
    target: str = ""
    decision_result: str | int | bool | None = None
    status: str = ""
    error_code: str = ""


class ChatResponse(BaseModel):
    """Outgoing chat response."""

    answer: str
    session_id: str
    query_type: str | None = None
    effective_question: str | None = None
    retrieved_count: int = 0
    reranked_count: int = 0
    sources: list[SourceDocument] = Field(default_factory=list)

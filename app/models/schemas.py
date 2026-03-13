"""Shared Pydantic schemas."""

from pydantic import BaseModel


class ChatRequest(BaseModel):
    """Incoming chat request."""

    message: str
    session_id: str | None = None


class ChatResponse(BaseModel):
    """Outgoing chat response."""

    answer: str
    sources: list[str] = []

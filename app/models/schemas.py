"""Shared Pydantic schemas."""

from pydantic import BaseModel


class ChatRequest(BaseModel):
    """Incoming chat request."""

    message: str
    session_id: str | None = None
    stream: bool = False


class SourceDocument(BaseModel):
    """A retrieved source chunk returned alongside the answer."""

    content: str
    doc_title: str = ""
    doc_type: str = ""
    section: str = ""
    source: str = ""


class ChatResponse(BaseModel):
    """Outgoing chat response."""

    answer: str
    sources: list[SourceDocument] = []

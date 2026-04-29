"""Pydantic schemas for Conversation and Message API requests/responses."""

from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field, field_validator


class ConversationResponse(BaseModel):
    """Conversation metadata response."""

    id: str
    session_id: str
    title: str | None
    meta: dict[str, Any] | None
    created_at: datetime
    updated_at: datetime

    @field_validator('id', mode='before')
    @classmethod
    def convert_uuid_to_str(cls, v: UUID | str) -> str:
        if isinstance(v, UUID):
            return str(v)
        return v

    model_config = {"from_attributes": True}


class MessageResponse(BaseModel):
    """Message response."""

    id: str
    conversation_id: str
    role: str
    content: str
    sources: dict[str, Any] | list[Any] | None
    agent_metadata: dict[str, Any] | None
    attachments: dict[str, Any] | None
    created_at: datetime

    @field_validator('id', 'conversation_id', mode='before')
    @classmethod
    def convert_uuid_to_str(cls, v: UUID | str) -> str:
        if isinstance(v, UUID):
            return str(v)
        return v

    @field_validator('sources', mode='before')
    @classmethod
    def convert_sources_to_dict(cls, v: dict[str, Any] | list[Any] | None) -> dict[str, Any] | None:
        if isinstance(v, list):
            return {"items": v}
        return v

    model_config = {"from_attributes": True}


class ConversationWithMessages(ConversationResponse):
    """Conversation with its messages."""

    messages: list[MessageResponse] = Field(default_factory=list)


class ConversationCreate(BaseModel):
    """Create a new conversation."""

    session_id: str
    title: str | None = None
    meta: dict[str, Any] | None = None


class ConversationUpdate(BaseModel):
    """Update conversation metadata."""

    title: str | None = None
    meta: dict[str, Any] | None = None

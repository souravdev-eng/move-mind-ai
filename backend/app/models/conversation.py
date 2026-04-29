"""SQLAlchemy models for conversation persistence."""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import JSON, DateTime, ForeignKey, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Conversation(Base):
    """Conversation metadata table — maps to LangGraph thread_id."""

    __tablename__ = "conversations"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    session_id: Mapped[str] = mapped_column(String(255), unique=True, index=True)  # LangGraph thread_id
    title: Mapped[str | None] = mapped_column(Text, nullable=True)  # Auto-generated from first message
    meta: Mapped[dict | None] = mapped_column(JSON, nullable=True)  # project_id, user_id, tags
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    def __repr__(self) -> str:
        return f"<Conversation(id={self.id}, session_id={self.session_id}, title={self.title})>"


class Message(Base):
    """Message table — stores human + AI messages with sources and agent metadata."""

    __tablename__ = "messages"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    conversation_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("conversations.id", ondelete="CASCADE"), index=True
    )
    role: Mapped[str] = mapped_column(String(50))  # 'human' | 'ai'
    content: Mapped[str] = mapped_column(Text)
    sources: Mapped[dict | None] = mapped_column(JSON, nullable=True)  # Retrieved docs/sources
    agent_metadata: Mapped[dict | None] = mapped_column(JSON, nullable=True)  # issue_type, confidence, node timings
    attachments: Mapped[dict | None] = mapped_column(JSON, nullable=True)  # File refs (Phase: file upload)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    def __repr__(self) -> str:
        return f"<Message(id={self.id}, conversation_id={self.conversation_id}, role={self.role})>"

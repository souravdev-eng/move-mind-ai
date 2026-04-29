"""Message persistence service — saves human + AI messages to PostgreSQL."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.conversation import Conversation, Message


async def get_or_create_conversation(
    session: AsyncSession, session_id: str, title: str | None = None
) -> Conversation:
    """Get conversation by session_id, or create if it doesn't exist."""
    result = await session.execute(
        select(Conversation).where(Conversation.session_id == session_id)
    )
    conversation = result.scalar_one_or_none()

    if conversation is None:
        conversation = Conversation(session_id=session_id, title=title)
        session.add(conversation)
        await session.commit()
        await session.refresh(conversation)

    return conversation


async def save_message(
    session: AsyncSession,
    conversation_id: uuid.UUID | str,
    role: str,
    content: str,
    sources: dict[str, Any] | None = None,
    agent_metadata: dict[str, Any] | None = None,
    attachments: dict[str, Any] | None = None,
) -> Message:
    """Save a message to the database."""
    # Convert string to UUID if needed
    if isinstance(conversation_id, str):
        conversation_id = uuid.UUID(conversation_id)
    
    message = Message(
        conversation_id=conversation_id,
        role=role,
        content=content,
        sources=sources,
        agent_metadata=agent_metadata,
        attachments=attachments,
    )
    session.add(message)
    await session.commit()
    await session.refresh(message)
    return message


async def update_conversation_title(
    session: AsyncSession, conversation_id: uuid.UUID | str, title: str
) -> Conversation:
    """Update conversation title."""
    # Convert string to UUID if needed
    if isinstance(conversation_id, str):
        conversation_id = uuid.UUID(conversation_id)
    
    result = await session.execute(
        select(Conversation).where(Conversation.id == conversation_id)
    )
    conversation = result.scalar_one_or_none()

    if conversation is None:
        raise ValueError(f"Conversation {conversation_id} not found")

    if conversation.title is None:
        conversation.title = title
        await session.commit()
        await session.refresh(conversation)

    return conversation

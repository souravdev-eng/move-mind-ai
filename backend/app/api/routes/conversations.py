"""Conversation CRUD API endpoints."""

from __future__ import annotations

import uuid
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_async_session
from app.models.conversation import Conversation, Message
from app.models.conversation_schemas import (
    ConversationCreate,
    ConversationResponse,
    ConversationUpdate,
    ConversationWithMessages,
    MessageResponse,
)
from app.utils.helpers import get_logger

router = APIRouter()
logger = get_logger(__name__)


@router.get("/conversations", response_model=list[ConversationResponse])
async def list_conversations(
    skip: int = 0,
    limit: int = 50,
    session: AsyncSession = Depends(get_async_session),
) -> list[Conversation]:
    """List all conversations, paginated."""
    result = await session.execute(
        select(Conversation).order_by(Conversation.updated_at.desc()).offset(skip).limit(limit)
    )
    return list(result.scalars().all())


@router.get("/conversations/{conversation_id}", response_model=ConversationWithMessages)
async def get_conversation(
    conversation_id: str,
    include_messages: bool = True,
    session: AsyncSession = Depends(get_async_session),
) -> Conversation:
    """Get a conversation by ID, optionally with messages."""
    try:
        conv_uuid = uuid.UUID(conversation_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid conversation ID format"
        )

    result = await session.execute(select(Conversation).where(Conversation.id == conv_uuid))
    conversation = result.scalar_one_or_none()

    if conversation is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found"
        )

    if include_messages:
        msg_result = await session.execute(
            select(Message)
            .where(Message.conversation_id == conv_uuid)
            .order_by(Message.created_at.asc())
        )
        conversation.messages = list(msg_result.scalars().all())

    return conversation


@router.get("/conversations/by-session/{session_id}", response_model=ConversationResponse)
async def get_conversation_by_session_id(
    session_id: str,
    session: AsyncSession = Depends(get_async_session),
) -> Conversation:
    """Get a conversation by LangGraph session_id (thread_id)."""
    result = await session.execute(
        select(Conversation).where(Conversation.session_id == session_id)
    )
    conversation = result.scalar_one_or_none()

    if conversation is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found"
        )

    return conversation


@router.post("/conversations", response_model=ConversationResponse, status_code=status.HTTP_201_CREATED)
async def create_conversation(
    data: ConversationCreate,
    session: AsyncSession = Depends(get_async_session),
) -> Conversation:
    """Create a new conversation."""
    conversation = Conversation(
        session_id=data.session_id, title=data.title, meta=data.meta
    )
    session.add(conversation)
    await session.commit()
    await session.refresh(conversation)
    return conversation


@router.patch("/conversations/{conversation_id}", response_model=ConversationResponse)
async def update_conversation(
    conversation_id: str,
    data: ConversationUpdate,
    session: AsyncSession = Depends(get_async_session),
) -> Conversation:
    """Update conversation metadata (title, meta)."""
    try:
        conv_uuid = uuid.UUID(conversation_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid conversation ID format"
        )

    result = await session.execute(select(Conversation).where(Conversation.id == conv_uuid))
    conversation = result.scalar_one_or_none()

    if conversation is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found"
        )

    if data.title is not None:
        conversation.title = data.title
    if data.meta is not None:
        conversation.meta = data.meta

    await session.commit()
    await session.refresh(conversation)
    return conversation


@router.delete("/conversations/{conversation_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_conversation(
    conversation_id: str,
    session: AsyncSession = Depends(get_async_session),
) -> None:
    """Delete a conversation (cascade deletes messages)."""
    try:
        conv_uuid = uuid.UUID(conversation_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid conversation ID format"
        )

    result = await session.execute(select(Conversation).where(Conversation.id == conv_uuid))
    conversation = result.scalar_one_or_none()

    if conversation is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found"
        )

    await session.delete(conversation)
    await session.commit()

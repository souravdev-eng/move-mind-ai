"""General-purpose helpers used across the project."""

from __future__ import annotations

import logging
import re
from functools import lru_cache

from langchain_core.documents import Document
from langchain_core.messages import BaseMessage
from langchain_openai import ChatOpenAI

from app.config import settings


def get_logger(name: str) -> logging.Logger:
    """Return a pre-configured logger."""
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(
            logging.Formatter("%(asctime)s | %(name)s | %(levelname)s | %(message)s")
        )
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    return logger


def normalize_for_checkpoint(value):
    """Convert nested metadata into msgpack-safe Python primitives."""
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    if hasattr(value, "item"):
        return normalize_for_checkpoint(value.item())
    if isinstance(value, dict):
        return {
            str(key): normalize_for_checkpoint(item) for key, item in value.items()
        }
    if isinstance(value, list):
        return [normalize_for_checkpoint(item) for item in value]
    if isinstance(value, tuple):
        return [normalize_for_checkpoint(item) for item in value]
    return str(value)


def sanitize_metadata_value(value):
    """Normalize metadata into Pinecone-compatible scalar or list values."""
    if value is None:
        return None
    value = normalize_for_checkpoint(value)
    if isinstance(value, (str, int, float, bool)):
        return value
    if isinstance(value, list):
        sanitized = [sanitize_metadata_value(item) for item in value]
        return [item for item in sanitized if item is not None]
    return str(value)


def doc_to_dict(doc: Document) -> dict:
    """Convert a Document to a msgpack-safe dict."""
    return {
        "page_content": doc.page_content,
        "metadata": normalize_for_checkpoint(dict(doc.metadata)),
    }


def dict_to_doc(data: dict) -> Document:
    """Convert a plain dict back to a Document."""
    return Document(page_content=data["page_content"], metadata=data.get("metadata", {}))


def format_docs(docs: list[dict | Document], separator: str = "\n\n---\n\n") -> str:
    """Format CMS3 documents into a readable context block for the answer model."""

    def _render(doc: dict | Document) -> str:
        if isinstance(doc, dict):
            metadata = doc.get("metadata", {})
            page_content = doc["page_content"]
        else:
            metadata = doc.metadata
            page_content = doc.page_content

        return (
            f"[chunk_type={metadata.get('chunk_type', '?')} | "
            f"cid={metadata.get('customer_id', '?')} | "
            f"execution={metadata.get('execution_id', '?')} | "
            f"page={metadata.get('page_path', '?')} | "
            f"action={metadata.get('action', '?')}]\n"
            f"{page_content}"
        )

    return separator.join(_render(doc) for doc in docs)


def question_needs_reasoning(question: str) -> bool:
    """Heuristic for when the answer path should use the reasoning model preset."""
    text = question.lower()
    reasoning_markers = (
        "why",
        "failure",
        "root cause",
        "reason",
        "caused",
        "estimator flow",
        "explain",
    )
    return any(marker in text for marker in reasoning_markers)


_FOLLOW_UP_MARKERS = (
    "there",
    "that",
    "it",
    "that journey",
    "then",
    "next",
    "previous",
    "before that",
    "after that",
    "that screen",
    "that page",
    "that route",
    "which condition",
    "why did it",
    "why did that",
    "where did it",
    "what happened next",
)
_CID_PATTERN = re.compile(r"\bCID\s*[:#-]?\s*(\d+)\b", re.IGNORECASE)
_PAGE_PATTERN = re.compile(r"(/[A-Za-z0-9._/-]+)")


def has_explicit_debug_scope(question: str) -> bool:
    """Whether the question already carries its own CID or page-path scope."""
    return bool(_CID_PATTERN.search(question) or _PAGE_PATTERN.search(question))


def question_needs_context_resolution(
    question: str, chat_history: list[BaseMessage] | None = None
) -> bool:
    """Heuristic fallback for ambiguous follow-up questions."""
    if not chat_history:
        return False

    text = question.lower().strip()
    if has_explicit_debug_scope(text):
        return False

    if any(marker in text for marker in _FOLLOW_UP_MARKERS):
        return True

    # Very short questions without explicit scope are usually follow-ups.
    return len(text.split()) <= 6


@lru_cache(maxsize=16)
def _build_llm(model_name: str, streaming: bool) -> ChatOpenAI:
    is_reasoning = model_name.startswith(("o1", "o3", "o4"))
    kwargs = {
        "api_key": settings.OPENAI_API_KEY,
        "model": model_name,
        "streaming": streaming,
    }
    kwargs["temperature"] = 1 if is_reasoning else settings.LLM_TEMPERATURE
    return ChatOpenAI(**kwargs)


def get_llm(model: str = "smart", *, streaming: bool = False) -> ChatOpenAI:
    """Return a cached ChatOpenAI instance by preset name or explicit model id."""
    presets = {
        "fast": settings.OPENAI_FAST,
        "smart": settings.OPENAI_SMART,
        "thinking": settings.OPENAI_THINKING,
    }
    model_name = presets.get(model, model)
    return _build_llm(model_name, streaming)

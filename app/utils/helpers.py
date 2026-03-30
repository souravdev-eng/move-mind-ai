"""General-purpose helpers used across the project."""

import logging

from langchain_core.documents import Document
from langchain_openai import ChatOpenAI


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


def _sanitize_value(val):
    """Convert numpy/non-standard types to Python natives for msgpack."""
    if hasattr(val, "item"):  # numpy scalar → Python native
        return val.item()
    if isinstance(val, dict):
        return {k: _sanitize_value(v) for k, v in val.items()}
    if isinstance(val, list):
        return [_sanitize_value(v) for v in val]
    return val


def doc_to_dict(doc: Document) -> dict:
    """Convert a Document to a plain dict for msgpack-safe state storage."""
    return {
        "page_content": doc.page_content,
        "metadata": {k: _sanitize_value(v) for k, v in doc.metadata.items()},
    }


def dict_to_doc(d: dict) -> Document:
    """Convert a plain dict back to a Document."""
    return Document(page_content=d["page_content"], metadata=d.get("metadata", {}))


def format_docs(docs: list[dict | Document], separator: str = "\n\n---\n\n") -> str:
    """Format retrieved documents into a context string with source metadata."""

    def _get(doc):
        if isinstance(doc, dict):
            m = doc.get("metadata", {})
            return f"[{m.get('source', '?')} > {m.get('section', '?')}]\n{doc['page_content']}"
        return f"[{doc.metadata.get('source', '?')} > {doc.metadata.get('section', '?')}]\n{doc.page_content}"

    return separator.join(_get(doc) for doc in docs)


_llm_cache: dict[str, ChatOpenAI] = {}


def get_llm(model: str = "smart") -> ChatOpenAI:
    """Return a cached ChatOpenAI instance by preset name.

    Presets (configured in config.py):
        "fast"     → OPENAI_FAST     (gpt-4o-mini)  — classifier, rewriter
        "smart"    → OPENAI_SMART    (gpt-4o)       — answer generation
        "thinking" → OPENAI_THINKING (o3-mini)       — reasoning-heavy tasks

    You can also pass a model name directly, e.g. get_llm("gpt-4o-mini").
    """
    from app.config import settings

    presets = {
        "fast": settings.OPENAI_FAST,
        "smart": settings.OPENAI_SMART,
        "thinking": settings.OPENAI_THINKING,
    }
    model_name = presets.get(model, model)

    # Reasoning models (o-series) don't support custom temperature
    is_reasoning = model_name.startswith(("o1", "o3", "o4"))

    if model_name not in _llm_cache:
        kwargs = {
            "api_key": settings.OPENAI_API_KEY,
            "model": model_name,
            "streaming": True,
        }
        kwargs["temperature"] = 1 if is_reasoning else settings.LLM_TEMPERATURE
        _llm_cache[model_name] = ChatOpenAI(**kwargs)
    return _llm_cache[model_name]

"""General-purpose helpers used across the project."""

import logging

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


_llm: ChatOpenAI | None = None


def get_llm() -> ChatOpenAI:
    """Return a singleton ChatOpenAI instance configured from app settings."""
    global _llm
    if _llm is None:
        from app.config import settings

        _llm = ChatOpenAI(
            api_key=settings.OPENAI_API_KEY,
            model=settings.LLM_MODEL_NAME,
            temperature=settings.LLM_TEMPERATURE,
            streaming=True,
        )
    return _llm

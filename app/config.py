"""Application configuration and settings."""

import os

from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv()


class Settings(BaseSettings):
    """Central configuration loaded from environment variables / .env file."""

    # --- LLM ---
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY")
    LLM_MODEL_NAME: str = "gpt-5"
    LLM_TEMPERATURE: float = 0

    # --- OpenAI Model Presets ---
    OPENAI_FAST: str = "gpt-4o-mini"       # cheap, fast (classifier, rewriter)
    OPENAI_SMART: str = "gpt-4o"           # powerful (answer generation)
    OPENAI_THINKING: str = "o3"       # reasoning-heavy tasks

    # --- Embeddings ---
    EMBEDDING_MODEL_NAME: str = "text-embedding-3-small"

    # --- Vector Store ---
    VECTORSTORE_PATH: str = "data/vectorstore"
    CHUNK_SIZE: int = 1000
    CHUNK_OVERLAP: int = 200

    # --- RAG ---
    RETRIEVER_TOP_K: int = 5

    # --- Tracing / Observability ---
    LANGCHAIN_TRACING_V2: bool = False
    LANGCHAIN_API_KEY: str = os.getenv("LANGCHAIN_API_KEY")
    LANGCHAIN_PROJECT: str = os.getenv("LANGCHAIN_PROJECT", "move-mind-ai")

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8", "extra": "ignore"}


settings = Settings()

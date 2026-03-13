"""Application configuration and settings."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Central configuration loaded from environment variables / .env file."""

    # --- LLM ---
    OPENAI_API_KEY: str = ""
    LLM_MODEL_NAME: str = "gpt-4o-mini"
    LLM_TEMPERATURE: float = 0.0

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
    LANGCHAIN_API_KEY: str = ""
    LANGCHAIN_PROJECT: str = "move-mind-ai"

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8", "extra": "ignore"}


settings = Settings()

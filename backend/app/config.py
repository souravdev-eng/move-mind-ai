"""Application configuration and settings."""

from pathlib import Path

from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict

PROJECT_ROOT = Path(__file__).resolve().parent.parent
REPO_ROOT = PROJECT_ROOT.parent

# Prefer backend-local .env, fall back to monorepo root .env
_env_path = PROJECT_ROOT / ".env" if (PROJECT_ROOT / ".env").exists() else REPO_ROOT / ".env"

load_dotenv(dotenv_path=_env_path)


class Settings(BaseSettings):
    """Central configuration loaded from environment variables and `.env`."""

    OPENAI_API_KEY: str | None = None
    LLM_TEMPERATURE: float = 0

    # Model presets selected by task type in chains/nodes.
    OPENAI_FAST: str = "gpt-4o-mini"
    OPENAI_SMART: str = "gpt-4o"
    OPENAI_THINKING: str = "o3"

    EMBEDDING_MODEL_NAME: str = "text-embedding-3-small"
    EMBEDDING_DIMENSION: int = 1536

    RAW_LOGS_PATH: str = str(PROJECT_ROOT / "data" / "raw" / "cms3-logs.json")
    PROCESSED_CHUNKS_PATH: str = str(
        PROJECT_ROOT / "data" / "processed" / "cms3_log_chunks.json"
    )

    PINECONE_API_KEY: str | None = None
    PINECONE_INDEX_NAME: str = "move-mind-ai"
    PINECONE_INDEX_HOST: str | None = None
    PINECONE_NAMESPACE: str = "cms3-logs"
    PINECONE_CLOUD: str = "aws"
    PINECONE_REGION: str = "us-east-1"
    PINECONE_METRIC: str = "cosine"

    RETRIEVER_SUMMARY_K: int = 2
    RETRIEVER_EVENT_K: int = 8
    RERANK_TOP_N: int = 5
    FLASHRANK_MODEL_NAME: str = "ms-marco-TinyBERT-L-2-v2"

    LANGCHAIN_TRACING_V2: bool = False
    LANGCHAIN_API_KEY: str | None = None
    LANGCHAIN_PROJECT: str = "move-mind-ai"
    LANGCHAIN_PROJECT_DEV: str | None = None
    LANGCHAIN_PROJECT_EVAL: str | None = None
    LANGCHAIN_PROJECT_PROD: str | None = None

    model_config = SettingsConfigDict(
        env_file=str(_env_path),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    def langsmith_project_for(self, env: str) -> str:
        """Resolve the LangSmith project name for a given env, falling back to LANGCHAIN_PROJECT."""
        per_env = {
            "dev": self.LANGCHAIN_PROJECT_DEV,
            "eval": self.LANGCHAIN_PROJECT_EVAL,
            "prod": self.LANGCHAIN_PROJECT_PROD,
        }.get(env)
        return per_env or self.LANGCHAIN_PROJECT


settings = Settings()

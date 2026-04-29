"""FastAPI application factory."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.dependencies import init_rag_graph, shutdown_rag_graph
from app.api.routes import chat, conversations, health
from app.utils.helpers import get_logger

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup: open Postgres pool + compile graph. Shutdown: close pool."""
    logger.info("Starting up — initialising Postgres + LangGraph RAG graph...")
    await init_rag_graph()
    logger.info("LangGraph RAG graph loaded. API is ready.")
    yield
    logger.info("Shutting down — closing Postgres pool...")
    await shutdown_rag_graph()
    logger.info("Shutdown complete.")


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI(
        title="Move Mind AI",
        version="0.1.0",
        description="GenAI API powered by LangChain, LangGraph, and RAG",
        lifespan=lifespan,
    )

    # ── CORS — allow your frontend to connect ────────────────────────────
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # tighten to your frontend URL in production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(health.router, tags=["health"])
    app.include_router(chat.router, prefix="/api/v1", tags=["chat"])
    app.include_router(conversations.router, prefix="/api/v1", tags=["conversations"])

    return app


app = create_app()

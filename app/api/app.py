"""FastAPI application factory."""

from fastapi import FastAPI

from app.api.routes import chat, health


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI(
        title="Move Mind AI",
        version="0.1.0",
        description="GenAI API powered by LangChain, LangGraph, and RAG",
    )

    app.include_router(health.router, tags=["health"])
    app.include_router(chat.router, prefix="/api/v1", tags=["chat"])

    return app


app = create_app()

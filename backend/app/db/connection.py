"""Async PostgreSQL connection pool and LangGraph checkpointer lifecycle."""

from __future__ import annotations

from pathlib import Path

from psycopg import AsyncConnection
from psycopg_pool import AsyncConnectionPool

from alembic import command
from alembic.config import Config

from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver

from app.config import settings
from app.utils.helpers import get_logger

logger = get_logger(__name__)

_pool: AsyncConnectionPool | None = None
_checkpointer: AsyncPostgresSaver | None = None


def _run_migrations() -> None:
    """Run Alembic migrations synchronously (called from async context)."""
    alembic_dir = Path(__file__).parent.parent.parent / "alembic"
    alembic_ini = Path(__file__).parent.parent.parent / "alembic.ini"

    if not alembic_ini.exists():
        logger.warning("alembic.ini not found, skipping migrations")
        return

    config = Config(str(alembic_ini))
    config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)
    config.set_main_option("script_location", str(alembic_dir))

    try:
        logger.info("Running Alembic migrations...")
        command.upgrade(config, "head")
        logger.info("Migrations completed.")
    except Exception as e:
        logger.warning("Migration run failed (may already be applied): %s", e)


async def init_pool() -> AsyncConnectionPool:
    """Create and open the async connection pool; create checkpoint tables."""
    global _pool, _checkpointer

    logger.info("Opening async Postgres pool → %s", settings.DATABASE_URL.split("@")[-1])
    _pool = AsyncConnectionPool(
        conninfo=settings.DATABASE_URL,
        min_size=2,
        max_size=10,
        open=False,
    )
    await _pool.open()

    # setup() runs CREATE INDEX CONCURRENTLY — needs autocommit, so use a
    # temporary standalone connection for DDL, then hand the pool to the
    # real checkpointer.
    async with await AsyncConnection.connect(
        conninfo=settings.DATABASE_URL, autocommit=True
    ) as setup_conn:
        setup_saver = AsyncPostgresSaver(setup_conn)
        await setup_saver.setup()

    # Run Alembic migrations for application tables (conversations, messages)
    _run_migrations()

    _checkpointer = AsyncPostgresSaver(_pool)
    logger.info("Postgres pool open — checkpoint tables ready.")

    return _pool


async def close_pool() -> None:
    """Gracefully close the connection pool."""
    global _pool, _checkpointer
    if _pool is not None:
        logger.info("Closing async Postgres pool.")
        await _pool.close()
        _pool = None
        _checkpointer = None


def get_checkpointer() -> AsyncPostgresSaver:
    """Return the initialised checkpointer (raises if pool not open)."""
    if _checkpointer is None:
        raise RuntimeError("Checkpointer not initialised — call init_pool() first.")
    return _checkpointer

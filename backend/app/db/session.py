"""Engine / session management and DB session dependency."""

from __future__ import annotations

from collections.abc import Generator

from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)

# SQLite needs check_same_thread off for the threaded test client / uvicorn workers.
_connect_args = {"check_same_thread": False} if settings.is_sqlite else {}

engine = create_engine(
    settings.database_url,
    echo=False,
    future=True,
    pool_pre_ping=True,
    connect_args=_connect_args,
)

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False)


def get_db() -> Generator[Session, None, None]:
    """FastAPI dependency yielding a scoped session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    """Create tables from models. Used for SQLite dev/tests; use Alembic for PostgreSQL."""
    from app.db import (
        base,  # noqa: F401
        models,  # noqa: F401  (registers all models on Base.metadata)
    )

    base.Base.metadata.create_all(bind=engine)


def check_connection() -> bool:
    """Lightweight connectivity probe for /health/ready."""
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except Exception as exc:  # pragma: no cover - exercised only on real failure
        logger.warning("Database connectivity check failed: %s", type(exc).__name__)
        return False

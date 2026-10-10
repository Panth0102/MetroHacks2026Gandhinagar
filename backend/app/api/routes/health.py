from __future__ import annotations

from fastapi import APIRouter

from app.core.config import settings
from app.db.session import check_connection

router = APIRouter(tags=["health"])


@router.get("/health")
def health() -> dict:
    """Liveness probe."""
    return {"status": "ok", "app": settings.app_name, "environment": settings.environment}


@router.get("/health/ready")
def ready() -> dict:
    """Readiness probe: reports actual DB connectivity (does not fabricate success)."""
    db_ok = check_connection()
    return {
        "status": "ready" if db_ok else "degraded",
        "database": "up" if db_ok else "down",
        "database_backend": "sqlite" if settings.is_sqlite else "postgresql",
    }

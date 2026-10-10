from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import api_router
from app.api.routes import health
from app.core.config import settings
from app.core.logging import configure_logging, get_logger

configure_logging()
logger = get_logger(__name__)

app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    description=(
        "Phase 1 backend for Metro Revenue Intelligence (Metro Hacks PS-06: Footfall to "
        "Revenue). All demo data is SYNTHETIC. Pricing is an indicative heuristic, not a "
        "verified market rate."
    ),
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health is unversioned; business endpoints live under /api/v1.
app.include_router(health.router)
app.include_router(api_router, prefix=settings.api_v1_prefix)


@app.get("/", tags=["root"])
def root() -> dict:
    return {
        "name": settings.app_name,
        "docs": "/docs",
        "redoc": "/redoc",
        "api_prefix": settings.api_v1_prefix,
    }

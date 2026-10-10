from __future__ import annotations

from fastapi import APIRouter

from app.api.routes import analytics, footfall, forecasts, inventory, pricing, stations

api_router = APIRouter()
api_router.include_router(stations.router)
api_router.include_router(footfall.router)
api_router.include_router(inventory.router)
api_router.include_router(analytics.router)
api_router.include_router(pricing.router)
api_router.include_router(forecasts.router)

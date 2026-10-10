from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.forecast import ForecastResult
from app.services import forecasting_service

router = APIRouter(prefix="/forecasts", tags=["forecasts"])


@router.get("/revenue", response_model=ForecastResult)
def forecast_revenue(
    db: Session = Depends(get_db), station_id: int | None = None
) -> ForecastResult:
    return forecasting_service.forecast_revenue(db, station_id)


@router.get("/scenarios", response_model=ForecastResult)
def forecast_scenarios(
    db: Session = Depends(get_db), station_id: int | None = None
) -> ForecastResult:
    """Alias of /revenue — the scenario list is the forecast payload."""
    return forecasting_service.forecast_revenue(db, station_id)

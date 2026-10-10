from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.analytics import (
    AnalyticsOverview,
    PeakHoursResult,
    RevenueOpportunity,
    StationFootfallRank,
)
from app.schemas.commercial_space import InventorySummary
from app.services import analytics_service, footfall_service, inventory_service

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/overview", response_model=AnalyticsOverview)
def analytics_overview(db: Session = Depends(get_db)) -> AnalyticsOverview:
    return analytics_service.overview(db)


@router.get("/stations", response_model=list[StationFootfallRank])
def station_rankings(db: Session = Depends(get_db)) -> list[StationFootfallRank]:
    return footfall_service.station_ranking(db)


@router.get("/occupancy", response_model=InventorySummary)
def occupancy(db: Session = Depends(get_db), station_id: int | None = None) -> InventorySummary:
    return inventory_service.inventory_summary(db, station_id)


@router.get("/peak-hours", response_model=PeakHoursResult)
def peak_hours(db: Session = Depends(get_db), station_id: int | None = None) -> PeakHoursResult:
    return analytics_service.peak_hours(db, station_id)


@router.get("/revenue-opportunities", response_model=list[RevenueOpportunity])
def revenue_opportunities(
    db: Session = Depends(get_db),
    station_id: int | None = None,
    limit: int = Query(20, ge=1, le=100),
) -> list[RevenueOpportunity]:
    return analytics_service.revenue_opportunities(db, station_id, limit)

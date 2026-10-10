from __future__ import annotations

from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.db.models.footfall import FootfallRecord
from app.db.models.station import Station
from app.db.session import get_db
from app.schemas.common import Page
from app.schemas.footfall import FootfallOut, FootfallSummary
from app.services import footfall_service

router = APIRouter(prefix="/footfall", tags=["footfall"])


def _validate_range(start: date | None, end: date | None) -> None:
    if start and end and start > end:
        raise HTTPException(status_code=422, detail="start_date must be <= end_date")


@router.get("", response_model=Page[FootfallOut])
def list_footfall(
    db: Session = Depends(get_db),
    station_id: int | None = None,
    start_date: date | None = None,
    end_date: date | None = None,
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
) -> Page[FootfallOut]:
    _validate_range(start_date, end_date)
    conds = footfall_service._filters(station_id, start_date, end_date)
    total = db.scalar(select(func.count(FootfallRecord.id)).where(*conds)) or 0
    rows = db.scalars(
        select(FootfallRecord)
        .where(*conds)
        .order_by(FootfallRecord.observation_date, FootfallRecord.hour)
        .limit(limit)
        .offset(offset)
    ).all()
    return Page(
        items=[FootfallOut.model_validate(r) for r in rows],
        total=int(total),
        limit=limit,
        offset=offset,
    )


@router.get("/summary", response_model=FootfallSummary)
def footfall_summary(
    db: Session = Depends(get_db),
    station_id: int | None = None,
    start_date: date | None = None,
    end_date: date | None = None,
) -> FootfallSummary:
    _validate_range(start_date, end_date)
    return footfall_service.footfall_summary(db, station_id, start_date, end_date)


@router.get("/stations/{station_id}", response_model=FootfallSummary)
def station_footfall(
    station_id: int,
    db: Session = Depends(get_db),
    start_date: date | None = None,
    end_date: date | None = None,
) -> FootfallSummary:
    _validate_range(start_date, end_date)
    if db.get(Station, station_id) is None:
        raise HTTPException(status_code=404, detail="Station not found")
    return footfall_service.footfall_summary(db, station_id, start_date, end_date)

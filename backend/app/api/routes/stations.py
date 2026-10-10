from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.db.models.station import Station
from app.db.session import get_db
from app.schemas.common import Page
from app.schemas.station import StationOut

router = APIRouter(prefix="/stations", tags=["stations"])


@router.get("", response_model=Page[StationOut])
def list_stations(
    db: Session = Depends(get_db),
    active_only: bool = False,
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
) -> Page[StationOut]:
    conds = [Station.is_active.is_(True)] if active_only else []
    total = db.scalar(select(func.count(Station.id)).where(*conds)) or 0
    rows = db.scalars(
        select(Station).where(*conds).order_by(Station.code).limit(limit).offset(offset)
    ).all()
    return Page(
        items=[StationOut.model_validate(r) for r in rows],
        total=int(total),
        limit=limit,
        offset=offset,
    )


@router.get("/{station_id}", response_model=StationOut)
def get_station(station_id: int, db: Session = Depends(get_db)) -> StationOut:
    station = db.get(Station, station_id)
    if station is None:
        raise HTTPException(status_code=404, detail="Station not found")
    return StationOut.model_validate(station)

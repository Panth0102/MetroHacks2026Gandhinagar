from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.db.models.commercial_space import CommercialSpace, SpaceStatus, SpaceType
from app.db.session import get_db
from app.schemas.commercial_space import InventorySummary, SpaceOut
from app.schemas.common import Page
from app.services import inventory_service

router = APIRouter(prefix="/inventory", tags=["inventory"])


@router.get("", response_model=Page[SpaceOut])
def list_inventory(
    db: Session = Depends(get_db),
    station_id: int | None = None,
    status: SpaceStatus | None = None,
    space_type: SpaceType | None = None,
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
) -> Page[SpaceOut]:
    conds = []
    if station_id is not None:
        conds.append(CommercialSpace.station_id == station_id)
    if status is not None:
        conds.append(CommercialSpace.status == status.value)
    if space_type is not None:
        conds.append(CommercialSpace.space_type == space_type.value)
    total = db.scalar(select(func.count(CommercialSpace.id)).where(*conds)) or 0
    rows = db.scalars(
        select(CommercialSpace)
        .where(*conds)
        .order_by(CommercialSpace.id)
        .limit(limit)
        .offset(offset)
    ).all()
    return Page(
        items=[SpaceOut.model_validate(r) for r in rows],
        total=int(total),
        limit=limit,
        offset=offset,
    )


@router.get("/summary", response_model=InventorySummary)
def inventory_summary(
    db: Session = Depends(get_db), station_id: int | None = None
) -> InventorySummary:
    return inventory_service.inventory_summary(db, station_id)


@router.get("/{space_id}", response_model=SpaceOut)
def get_space(space_id: int, db: Session = Depends(get_db)) -> SpaceOut:
    space = db.get(CommercialSpace, space_id)
    if space is None:
        raise HTTPException(status_code=404, detail="Commercial space not found")
    return SpaceOut.model_validate(space)

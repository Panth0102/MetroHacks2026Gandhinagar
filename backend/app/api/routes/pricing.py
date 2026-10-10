from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models.commercial_space import CommercialSpace, SpaceStatus
from app.db.models.station import Station
from app.db.session import get_db
from app.schemas.pricing import PricingEstimate, PricingEstimateRequest, RateCardItem
from app.services import footfall_service, pricing_service

router = APIRouter(prefix="/pricing", tags=["pricing"])


@router.get("/rate-card", response_model=list[RateCardItem])
def rate_card(
    db: Session = Depends(get_db),
    station_id: int | None = None,
    vacant_only: bool = True,
    limit: int = Query(100, ge=1, le=500),
) -> list[RateCardItem]:
    """Data-backed indicative rate card. Defaults to vacant spaces (sellable inventory)."""
    conds = []
    if station_id is not None:
        conds.append(CommercialSpace.station_id == station_id)
    if vacant_only:
        conds.append(CommercialSpace.status == SpaceStatus.vacant.value)
    spaces = db.scalars(
        select(CommercialSpace).where(*conds).order_by(CommercialSpace.id).limit(limit)
    ).all()
    assumptions = pricing_service.get_active_assumptions(db)
    station_names = dict(db.execute(select(Station.id, Station.name)).all())

    items = []
    for sp in spaces:
        daily = footfall_service.observed_daily_footfall(db, sp.station_id)
        est = pricing_service.estimate_price(
            sp.space_type, sp.area_sqm, sp.visibility_score, daily, assumptions
        )
        items.append(
            RateCardItem(
                space_id=sp.id,
                space_code=sp.space_code,
                station_id=sp.station_id,
                station_name=station_names.get(sp.station_id, "?"),
                space_type=sp.space_type,
                status=str(sp.status),
                area_sqm=sp.area_sqm,
                observed_daily_footfall=round(daily, 2) if daily is not None else None,
                indicative_monthly_price=est.indicative_monthly_price,
                data_quality=est.data_quality,
                available=est.available,
            )
        )
    return items


@router.get("/spaces/{space_id}", response_model=PricingEstimate)
def price_space(space_id: int, db: Session = Depends(get_db)) -> PricingEstimate:
    sp = db.get(CommercialSpace, space_id)
    if sp is None:
        raise HTTPException(status_code=404, detail="Commercial space not found")
    assumptions = pricing_service.get_active_assumptions(db)
    daily = footfall_service.observed_daily_footfall(db, sp.station_id)
    return pricing_service.estimate_price(
        sp.space_type,
        sp.area_sqm,
        sp.visibility_score,
        daily,
        assumptions,
        space_id=sp.id,
        space_code=sp.space_code,
        station_id=sp.station_id,
    )


@router.post("/estimate", response_model=PricingEstimate)
def estimate(body: PricingEstimateRequest, db: Session = Depends(get_db)) -> PricingEstimate:
    """Ad-hoc indicative estimate from supplied attributes (no DB space needed)."""
    assumptions = pricing_service.get_active_assumptions(db)
    return pricing_service.estimate_price(
        body.space_type,
        body.area_sqm,
        body.visibility_score,
        body.observed_daily_footfall,
        assumptions,
    )

"""Builds a validated, evidence-grounded proposal context from backend data.

Everything here is deterministic and sourced from the database / pricing engine.
Observed facts (footfall, area) are kept separate from estimates (indicative price)
so the generator can never present an estimate as a guaranteed figure.
"""
from __future__ import annotations

from sqlalchemy.orm import Session

from app.db.models.commercial_space import CommercialSpace
from app.db.models.station import Station
from app.schemas.proposal import ProposalContext, ProposalGenerateRequest
from app.services import footfall_service, pricing_service


def build_context(db: Session, req: ProposalGenerateRequest) -> tuple[ProposalContext, CommercialSpace]:
    space = db.get(CommercialSpace, req.space_id)
    if space is None:
        raise LookupError("Commercial space not found")
    station = db.get(Station, space.station_id)
    if station is None:  # pragma: no cover - FK guarantees a station
        raise LookupError("Station not found")

    summary = footfall_service.footfall_summary(db, station_id=station.id)
    daily = footfall_service.observed_daily_footfall(db, station.id)
    assumptions = pricing_service.get_active_assumptions(db)
    estimate = pricing_service.estimate_price(
        space.space_type,
        space.area_sqm,
        space.visibility_score,
        daily,
        assumptions,
        space_id=space.id,
        space_code=space.space_code,
        station_id=station.id,
    )

    context = ProposalContext(
        station={
            "name": station.name,
            "code": station.code,
            "line": station.line,
            "station_type": station.station_type,
            "location_description": station.location_description,
        },
        space={
            "space_code": space.space_code,
            "space_type": str(space.space_type),
            "area_sqm": str(space.area_sqm) if space.area_sqm is not None else None,
            "floor_description": space.floor_description,
            "visibility_score": str(space.visibility_score)
            if space.visibility_score is not None
            else None,
            "status": str(space.status),
        },
        footfall={
            "metric": "observed passenger entries (boardings)",
            "avg_daily_entries": summary.avg_daily_entries,
            "peak_hour": summary.peak_hour,
            "peak_hours_tied": summary.peak_hours_tied,
            "observation_count": summary.observation_count,
            "start_date": str(summary.start_date) if summary.start_date else None,
            "end_date": str(summary.end_date) if summary.end_date else None,
            "coverage_ratio": summary.coverage_ratio,
        },
        pricing=estimate.model_dump(mode="json"),
        user_input={
            "tenant_category": req.tenant_category,
            "business_name": req.business_name,
            "campaign_objective": req.campaign_objective,
            "target_audience": req.target_audience,
            "budget": req.budget,
            "language": req.language,
        },
    )
    return context, space

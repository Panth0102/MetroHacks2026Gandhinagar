"""Cross-cutting analytics: overview, peak hours, and explainable revenue
opportunity ranking for vacant spaces."""

from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.db.models.commercial_space import CommercialSpace, SpaceStatus
from app.db.models.footfall import FootfallRecord
from app.db.models.station import Station
from app.schemas.analytics import (
    AnalyticsOverview,
    PeakHourBucket,
    PeakHoursResult,
    RevenueOpportunity,
)
from app.schemas.pricing import PricingFactor
from app.services import footfall_service, inventory_service, pricing_service

# Priority score weights (documented, tunable). Revenue dominates so ranking is
# not driven by raw passenger count alone.
W_REVENUE = 0.5
W_FOOTFALL = 0.3
W_QUALITY = 0.2
_QUALITY_SCORE = {"high": 1.0, "medium": 0.6, "low": 0.3}


def overview(db: Session) -> AnalyticsOverview:
    station_count = db.scalar(select(func.count(Station.id))) or 0
    active_count = db.scalar(select(func.count(Station.id)).where(Station.is_active.is_(True))) or 0
    foot = footfall_service.footfall_summary(db)
    inv = inventory_service.inventory_summary(db)
    return AnalyticsOverview(
        station_count=int(station_count),
        active_station_count=int(active_count),
        footfall_observation_count=foot.observation_count,
        footfall_date_range={
            "start": str(foot.start_date) if foot.start_date else None,
            "end": str(foot.end_date) if foot.end_date else None,
        },
        total_entries_observed=foot.total_entries,
        total_spaces=inv.total_spaces,
        occupancy_rate_by_count=inv.occupancy_rate_by_count,
        current_monthly_revenue=inv.current_monthly_revenue,
        potential_vacant_monthly_rent=inv.potential_vacant_monthly_rent,
        notes=["All footfall figures are observed entries; synthetic demo data."],
    )


def peak_hours(db: Session, station_id: int | None = None) -> PeakHoursResult:
    conds = []
    if station_id is not None:
        conds.append(FootfallRecord.station_id == station_id)
    rows = db.execute(
        select(FootfallRecord.hour, func.sum(FootfallRecord.entries))
        .where(*conds)
        .group_by(FootfallRecord.hour)
    ).all()
    obs = db.scalar(select(func.count(FootfallRecord.id)).where(*conds)) or 0
    if not rows:
        return PeakHoursResult(
            station_id=station_id, observation_count=0, notes=["no footfall observations in scope"]
        )
    hourly = {int(h): int(s) for h, s in rows}
    total = sum(hourly.values())
    peak_val = max(hourly.values())
    peak_hours_tied = sorted(h for h, v in hourly.items() if v == peak_val)
    buckets = [
        PeakHourBucket(
            hour=h, total_entries=hourly[h], share=round(hourly[h] / total, 4) if total else 0.0
        )
        for h in sorted(hourly)
    ]
    return PeakHoursResult(
        station_id=station_id,
        observation_count=int(obs),
        peak_hour=peak_hours_tied[0],
        peak_hours_tied=peak_hours_tied,
        buckets=buckets,
    )


def revenue_opportunities(
    db: Session, station_id: int | None = None, limit: int = 20
) -> list[RevenueOpportunity]:
    """Rank VACANT spaces by an explainable priority score. Maintenance/unavailable
    spaces are excluded (not rentable). Annualized asking revenue is asking x 12,
    explicitly NOT a forecast."""
    conds = [CommercialSpace.status == SpaceStatus.vacant.value]
    if station_id is not None:
        conds.append(CommercialSpace.station_id == station_id)
    spaces = db.scalars(select(CommercialSpace).where(*conds).order_by(CommercialSpace.id)).all()
    if not spaces:
        return []

    assumptions = pricing_service.get_active_assumptions(db)
    station_names = dict(db.execute(select(Station.id, Station.name)).all())

    # First pass: compute price + footfall per candidate.
    rows = []
    for sp in spaces:
        daily = footfall_service.observed_daily_footfall(db, sp.station_id)
        est = pricing_service.estimate_price(
            sp.space_type,
            sp.area_sqm,
            sp.visibility_score,
            daily,
            assumptions,
            space_id=sp.id,
            space_code=sp.space_code,
            station_id=sp.station_id,
        )
        rows.append((sp, daily, est))

    max_price = max(
        (float(e.indicative_monthly_price) for _, _, e in rows if e.indicative_monthly_price),
        default=0.0,
    )
    max_foot = max((d for _, d, _ in rows if d is not None), default=0.0)

    results: list[RevenueOpportunity] = []
    for sp, daily, est in rows:
        price = float(est.indicative_monthly_price or 0)
        rev_c = (price / max_price) if max_price else 0.0
        foot_c = (daily / max_foot) if (max_foot and daily is not None) else 0.0
        qual_c = _QUALITY_SCORE.get(est.data_quality, 0.3)
        score = round((W_REVENUE * rev_c + W_FOOTFALL * foot_c + W_QUALITY * qual_c) * 100, 2)

        reasons = []
        if rev_c >= 0.7:
            reasons.append("high indicative asking rent relative to peers")
        if foot_c >= 0.7:
            reasons.append("located at a high-footfall station")
        reasons.append(f"space type: {sp.space_type} (type multiplier applied in price)")
        if not reasons:
            reasons.append("baseline opportunity")

        results.append(
            RevenueOpportunity(
                space_id=sp.id,
                space_code=sp.space_code,
                station_id=sp.station_id,
                station_name=station_names.get(sp.station_id, "?"),
                space_type=str(sp.space_type),
                status=str(sp.status),
                observed_daily_footfall=round(daily, 2) if daily is not None else None,
                indicative_monthly_price=est.indicative_monthly_price,
                estimated_annual_asking_revenue=est.indicative_annual_price,
                priority_score=score,
                score_breakdown=[
                    PricingFactor(
                        name="revenue_component",
                        value=round(rev_c, 4),
                        description=f"weight {W_REVENUE}: price vs max candidate",
                    ),
                    PricingFactor(
                        name="footfall_component",
                        value=round(foot_c, 4),
                        description=f"weight {W_FOOTFALL}: footfall vs max candidate",
                    ),
                    PricingFactor(
                        name="data_quality_component",
                        value=round(qual_c, 4),
                        description=f"weight {W_QUALITY}: input completeness",
                    ),
                ],
                reasons=reasons,
                limitations=est.limitations
                + ([] if est.available else ["indicative price unavailable (missing inputs)"]),
                data_quality=est.data_quality,
            )
        )

    results.sort(key=lambda r: r.priority_score, reverse=True)
    return results[:limit]

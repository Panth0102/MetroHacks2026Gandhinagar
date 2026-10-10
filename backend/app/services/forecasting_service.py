"""Transparent, scenario-based revenue estimation. NOT a trained predictive model.
Potential revenue uses the deterministic pricing engine on eligible VACANT spaces."""

from __future__ import annotations

from decimal import ROUND_HALF_UP, Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models.commercial_space import CommercialSpace, SpaceStatus
from app.schemas.forecast import ForecastResult, RevenueScenario
from app.services import inventory_service, pricing_service

_ZERO = Decimal("0")
SCENARIOS = [("conservative_50pct", 0.5), ("expected_75pct", 0.75), ("full_100pct", 1.0)]


def _money(v: Decimal) -> Decimal:
    return v.quantize(Decimal("1"), rounding=ROUND_HALF_UP)


def forecast_revenue(db: Session, station_id: int | None = None) -> ForecastResult:
    inv = inventory_service.inventory_summary(db, station_id)
    current = inv.current_monthly_revenue

    conds = [CommercialSpace.status == SpaceStatus.vacant.value]
    if station_id is not None:
        conds.append(CommercialSpace.station_id == station_id)
    spaces = db.scalars(select(CommercialSpace).where(*conds)).all()

    assumptions = pricing_service.get_active_assumptions(db)
    from app.services import footfall_service

    potential = _ZERO
    priced = 0
    for sp in spaces:
        daily = footfall_service.observed_daily_footfall(db, sp.station_id)
        est = pricing_service.estimate_price(
            sp.space_type, sp.area_sqm, sp.visibility_score, daily, assumptions
        )
        if est.indicative_monthly_price is not None:
            potential += est.indicative_monthly_price
            priced += 1

    scenarios = []
    for name, frac in SCENARIOS:
        added = _money(potential * Decimal(str(frac)))
        monthly = current + added
        scenarios.append(
            RevenueScenario(
                name=name,
                occupancy_fraction_of_vacant=frac,
                added_monthly_rent=added,
                projected_monthly_revenue=monthly,
                projected_annual_revenue=monthly * 12,
                assumptions=[
                    f"{int(frac * 100)}% of eligible vacant spaces let at indicative asking price",
                    "existing active leases remain in place",
                ],
            )
        )

    return ForecastResult(
        current_monthly_revenue=current,
        current_annual_revenue=current * 12,
        eligible_vacant_potential_monthly_rent=_money(potential),
        eligible_vacant_space_count=priced,
        scenarios=scenarios,
        assumptions=[
            "Potential revenue = indicative pricing-engine output for VACANT spaces only.",
            "Maintenance/unavailable spaces are excluded.",
            "Annualized = monthly x 12 (no churn, seasonality, or ramp-up modelled).",
        ],
        limitations=[
            "Scenario estimates, not a statistically trained forecast.",
            "Assumes asking prices are achieved; real lease-up rates will differ.",
            f"{len(spaces) - priced} vacant space(s) could not be priced (missing inputs).",
        ],
    )

from __future__ import annotations

from decimal import Decimal

from pydantic import BaseModel


class RevenueScenario(BaseModel):
    name: str
    occupancy_fraction_of_vacant: float
    added_monthly_rent: Decimal
    projected_monthly_revenue: Decimal
    projected_annual_revenue: Decimal
    assumptions: list[str] = []


class ForecastResult(BaseModel):
    """Transparent, scenario-based revenue estimate. This is NOT a trained
    predictive model; figures assume the configured asking prices are achieved."""

    method: str = "scenario-baseline"
    is_predictive_model: bool = False
    currency: str = "INR"
    current_monthly_revenue: Decimal
    current_annual_revenue: Decimal
    eligible_vacant_potential_monthly_rent: Decimal
    eligible_vacant_space_count: int
    scenarios: list[RevenueScenario]
    assumptions: list[str] = []
    limitations: list[str] = []

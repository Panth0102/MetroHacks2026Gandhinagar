from __future__ import annotations

from decimal import Decimal

from pydantic import BaseModel, Field

from app.db.models.commercial_space import SpaceType


class PricingFactor(BaseModel):
    name: str
    value: float
    description: str


class PricingEstimate(BaseModel):
    """Indicative monthly asking price from the deterministic v1 heuristic.
    This is NOT a verified market rate and NOT a statistically calibrated figure."""

    available: bool
    is_indicative: bool = True
    currency: str = "INR"
    model_version: str

    space_id: int | None = None
    space_code: str | None = None
    station_id: int | None = None
    space_type: SpaceType

    base_component: Decimal | None = None
    indicative_monthly_price: Decimal | None = None
    indicative_annual_price: Decimal | None = None
    factors: list[PricingFactor] = []

    data_quality: str = Field(
        ..., description="high | medium | low — input completeness, not a probability"
    )
    data_quality_reasons: list[str] = []
    assumptions: dict = {}
    explanation: str
    limitations: list[str] = []


class PricingEstimateRequest(BaseModel):
    space_type: SpaceType
    area_sqm: Decimal | None = Field(None, gt=0)
    visibility_score: Decimal | None = Field(None, ge=1, le=10)
    observed_daily_footfall: float | None = Field(
        None, ge=0, description="Observed avg daily entries at the station; omit if unknown"
    )


class RateCardItem(BaseModel):
    space_id: int
    space_code: str
    station_id: int
    station_name: str
    space_type: SpaceType
    status: str
    area_sqm: Decimal | None = None
    observed_daily_footfall: float | None = None
    indicative_monthly_price: Decimal | None = None
    model_version: str
    data_quality: str
    available: bool

from __future__ import annotations

from decimal import Decimal

from pydantic import BaseModel

from app.schemas.pricing import PricingFactor


class StationFootfallRank(BaseModel):
    station_id: int
    station_name: str
    total_entries: int
    avg_daily_entries: float | None = None
    rank: int


class AnalyticsOverview(BaseModel):
    station_count: int
    active_station_count: int
    footfall_observation_count: int
    footfall_date_range: dict
    total_entries_observed: int
    total_spaces: int
    occupancy_rate_by_count: float | None
    current_monthly_revenue: Decimal
    potential_vacant_monthly_rent: Decimal
    notes: list[str] = []


class PeakHourBucket(BaseModel):
    hour: int
    total_entries: int
    share: float


class PeakHoursResult(BaseModel):
    station_id: int | None = None
    observation_count: int
    peak_hour: int | None = None
    peak_hours_tied: list[int] = []
    buckets: list[PeakHourBucket] = []
    notes: list[str] = []


class RevenueOpportunity(BaseModel):
    space_id: int
    space_code: str
    station_id: int
    station_name: str
    space_type: str
    status: str
    observed_daily_footfall: float | None = None
    indicative_monthly_price: Decimal | None = None
    estimated_annual_asking_revenue: Decimal | None = None
    priority_score: float
    score_breakdown: list[PricingFactor] = []
    reasons: list[str] = []
    limitations: list[str] = []
    data_quality: str

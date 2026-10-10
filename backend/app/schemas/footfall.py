from __future__ import annotations

from datetime import date

from pydantic import BaseModel, ConfigDict


class FootfallOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    station_id: int
    observation_date: date
    hour: int
    entries: int
    exits: int | None = None
    source: str


class FootfallSummary(BaseModel):
    """Aggregated footfall metrics. `entries` is boardings; exits reported separately.
    Missing observations are distinguished from genuine zero counts via
    observation_count / expected observations."""

    station_id: int | None = None
    start_date: date | None = None
    end_date: date | None = None
    observation_count: int
    distinct_days: int
    total_entries: int
    total_exits: int | None = None
    avg_hourly_entries: float | None = None
    avg_daily_entries: float | None = None
    peak_hour: int | None = None
    peak_hour_entries: int | None = None
    peak_hours_tied: list[int] = []
    weekday_avg_daily_entries: float | None = None
    weekend_avg_daily_entries: float | None = None
    hourly_distribution: dict[int, int] = {}
    coverage_ratio: float | None = None  # observed / expected hour-slots in range
    notes: list[str] = []

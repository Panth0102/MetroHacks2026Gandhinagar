from __future__ import annotations

from datetime import date
from decimal import Decimal

from pydantic import BaseModel, ConfigDict

from app.db.models.commercial_space import SpaceStatus, SpaceType


class SpaceOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    station_id: int
    space_code: str
    space_type: SpaceType
    area_sqm: Decimal | None = None
    floor_description: str | None = None
    visibility_score: Decimal | None = None
    status: SpaceStatus
    asking_monthly_rent: Decimal | None = None
    available_from: date | None = None


class InventorySummary(BaseModel):
    """Commercial inventory metrics with explicit definitions.

    occupancy_rate_by_count = occupied / total spaces.
    occupancy_rate_by_area  = occupied area / total known area (spaces w/ known area only).
    current_monthly_revenue = sum of ACTIVE lease rents (contractual, signed).
    potential_vacant_monthly_rent = sum of asking rent on VACANT spaces only
      (excludes maintenance/unavailable); known asking rents only.
    """

    station_id: int | None = None
    total_spaces: int
    count_by_status: dict[str, int]
    count_by_type: dict[str, int]
    occupancy_rate_by_count: float | None = None
    vacancy_rate_by_count: float | None = None
    occupied_area_sqm: Decimal | None = None
    vacant_area_sqm: Decimal | None = None
    occupancy_rate_by_area: float | None = None
    spaces_with_known_area: int
    current_monthly_revenue: Decimal
    current_annual_revenue: Decimal
    potential_vacant_monthly_rent: Decimal
    potential_vacant_rent_known_count: int
    notes: list[str] = []

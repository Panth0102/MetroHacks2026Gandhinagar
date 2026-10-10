from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class StationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    code: str
    name: str
    line: str | None = None
    station_type: str | None = None
    location_description: str | None = None
    is_active: bool

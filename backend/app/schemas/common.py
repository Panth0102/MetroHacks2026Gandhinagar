from __future__ import annotations

from typing import Generic, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class Page(BaseModel, Generic[T]):
    """Generic paginated collection response."""

    items: list[T]
    total: int = Field(..., description="Total matching rows (ignoring pagination)")
    limit: int
    offset: int


class DateRangeInfo(BaseModel):
    start_date: str | None = None
    end_date: str | None = None

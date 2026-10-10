from __future__ import annotations

from datetime import date

from sqlalchemy import (
    CheckConstraint,
    Date,
    ForeignKey,
    Integer,
    SmallInteger,
    String,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class FootfallRecord(Base):
    """One observation = passenger activity at a station for a single hour band.

    `entries` is the primary demand signal (boardings into the station).
    `exits` is recorded separately when available. We deliberately do NOT sum
    entries + exits into a "visitors" field, because that double-counts people.
    """

    __tablename__ = "footfall_records"
    __table_args__ = (
        UniqueConstraint("station_id", "observation_date", "hour", name="uq_footfall_obs"),
        CheckConstraint("hour >= 0 AND hour <= 23", name="ck_footfall_hour"),
        CheckConstraint("entries >= 0", name="ck_footfall_entries_nonneg"),
        CheckConstraint("exits IS NULL OR exits >= 0", name="ck_footfall_exits_nonneg"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    station_id: Mapped[int] = mapped_column(
        ForeignKey("stations.id", ondelete="CASCADE"), nullable=False, index=True
    )
    observation_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    hour: Mapped[int] = mapped_column(SmallInteger, nullable=False)  # 0-23, local time band
    entries: Mapped[int] = mapped_column(Integer, nullable=False)
    exits: Mapped[int | None] = mapped_column(Integer)
    source: Mapped[str] = mapped_column(String(64), nullable=False, default="synthetic")
    created_at: Mapped[date] = mapped_column(Date, server_default=func.current_date())

    station: Mapped[Station] = relationship(back_populates="footfall")  # noqa: F821

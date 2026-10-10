from __future__ import annotations

import enum
from datetime import date
from decimal import Decimal

from sqlalchemy import (
    CheckConstraint,
    Date,
    ForeignKey,
    Integer,
    Numeric,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin


class SpaceType(str, enum.Enum):
    retail = "retail"
    kiosk = "kiosk"
    advertising_panel = "advertising_panel"
    digital_screen = "digital_screen"


class SpaceStatus(str, enum.Enum):
    vacant = "vacant"
    occupied = "occupied"
    under_maintenance = "under_maintenance"
    unavailable = "unavailable"


# Space types priced per-unit (panel) rather than per-sqm. Area is optional for these.
UNIT_PRICED_TYPES = {SpaceType.advertising_panel, SpaceType.digital_screen}


class CommercialSpace(Base, TimestampMixin):
    __tablename__ = "commercial_spaces"
    __table_args__ = (
        UniqueConstraint("station_id", "space_code", name="uq_space_code_per_station"),
        CheckConstraint("area_sqm IS NULL OR area_sqm > 0", name="ck_space_area_positive"),
        CheckConstraint(
            "visibility_score IS NULL OR (visibility_score >= 1 AND visibility_score <= 10)",
            name="ck_space_visibility_range",
        ),
        CheckConstraint(
            "asking_monthly_rent IS NULL OR asking_monthly_rent >= 0",
            name="ck_space_rent_nonneg",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    station_id: Mapped[int] = mapped_column(
        ForeignKey("stations.id", ondelete="CASCADE"), nullable=False, index=True
    )
    space_code: Mapped[str] = mapped_column(String(32), nullable=False)
    space_type: Mapped[SpaceType] = mapped_column(String(32), nullable=False)
    # Nullable on purpose: a missing area stays NULL, it is never coerced to 0.
    area_sqm: Mapped[Decimal | None] = mapped_column(Numeric(10, 2))
    floor_description: Mapped[str | None] = mapped_column(String(128))
    visibility_score: Mapped[Decimal | None] = mapped_column(Numeric(4, 2))  # 1-10 scale
    status: Mapped[SpaceStatus] = mapped_column(String(32), nullable=False)
    asking_monthly_rent: Mapped[Decimal | None] = mapped_column(Numeric(12, 2))
    available_from: Mapped[date | None] = mapped_column(Date)

    station: Mapped[Station] = relationship(back_populates="spaces")  # noqa: F821
    leases: Mapped[list[Lease]] = relationship(  # noqa: F821
        back_populates="space", cascade="all, delete-orphan"
    )

    @property
    def is_unit_priced(self) -> bool:
        return self.space_type in UNIT_PRICED_TYPES

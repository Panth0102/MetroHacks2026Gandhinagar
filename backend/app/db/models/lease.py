from __future__ import annotations

import enum
from datetime import date
from decimal import Decimal

from sqlalchemy import CheckConstraint, Date, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin


class LeaseStatus(str, enum.Enum):
    active = "active"
    expired = "expired"
    terminated = "terminated"


class Lease(Base, TimestampMixin):
    """Occupancy / contract record. Tenant and notes are sensitive and are NOT
    exposed through general analytics endpoints (only aggregate revenue is)."""

    __tablename__ = "leases"
    __table_args__ = (
        CheckConstraint("monthly_rent >= 0", name="ck_lease_rent_nonneg"),
        CheckConstraint("end_date IS NULL OR end_date >= start_date", name="ck_lease_date_order"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    space_id: Mapped[int] = mapped_column(
        ForeignKey("commercial_spaces.id", ondelete="CASCADE"), nullable=False, index=True
    )
    tenant_name: Mapped[str | None] = mapped_column(String(128))
    monthly_rent: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date | None] = mapped_column(Date)
    status: Mapped[LeaseStatus] = mapped_column(String(32), nullable=False)
    notes: Mapped[str | None] = mapped_column(String(255))

    space: Mapped[CommercialSpace] = relationship(back_populates="leases")  # noqa: F821

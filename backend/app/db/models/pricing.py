from __future__ import annotations

from decimal import Decimal

from sqlalchemy import JSON, Boolean, Integer, Numeric, String, text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin


class PricingConfig(Base, TimestampMixin):
    """Configurable, versioned pricing assumptions. The row with is_active=true
    drives the pricing engine. Values are indicative business assumptions, not
    verified market rates; `source_notes` records their rationale."""

    __tablename__ = "pricing_configs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    version: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("false"))

    base_rate_per_sqm: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    base_panel_rate: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    reference_daily_footfall: Mapped[int] = mapped_column(Integer, nullable=False)
    footfall_elasticity: Mapped[Decimal] = mapped_column(Numeric(5, 3), nullable=False)
    min_footfall_factor: Mapped[Decimal] = mapped_column(Numeric(5, 3), nullable=False)
    max_footfall_factor: Mapped[Decimal] = mapped_column(Numeric(5, 3), nullable=False)
    reference_visibility: Mapped[Decimal] = mapped_column(Numeric(4, 2), nullable=False)
    visibility_weight: Mapped[Decimal] = mapped_column(Numeric(5, 3), nullable=False)
    min_visibility_factor: Mapped[Decimal] = mapped_column(Numeric(5, 3), nullable=False)
    max_visibility_factor: Mapped[Decimal] = mapped_column(Numeric(5, 3), nullable=False)
    # Per-space-type multipliers, e.g. {"retail": 1.0, "advertising_panel": 1.2}
    space_type_multipliers: Mapped[dict] = mapped_column(JSON, nullable=False)

    source_notes: Mapped[str | None] = mapped_column(String(512))

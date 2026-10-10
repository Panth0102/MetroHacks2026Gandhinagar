"""Deterministic, explainable pricing engine (v1 heuristic).

Final currency amounts use Decimal arithmetic. Dimensionless adjustment factors
are computed in float (powers/clamps) and converted to Decimal before the money
multiplication, so no binary float ever touches a final rupee amount.

This is an indicative business heuristic, NOT a statistically calibrated or
market-verified model. See README section "Pricing formula".
"""

from __future__ import annotations

from dataclasses import dataclass, field
from decimal import ROUND_HALF_UP, Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.models.commercial_space import UNIT_PRICED_TYPES, SpaceType
from app.db.models.pricing import PricingConfig
from app.schemas.pricing import PricingEstimate, PricingFactor

_CENTS = Decimal("1")  # whole INR


def _money(value: Decimal) -> Decimal:
    return value.quantize(_CENTS, rounding=ROUND_HALF_UP)


def _clamp(value: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, value))


@dataclass(frozen=True)
class PricingAssumptions:
    model_version: str
    base_rate_per_sqm: Decimal
    base_panel_rate: Decimal
    reference_daily_footfall: int
    footfall_elasticity: float
    min_footfall_factor: float
    max_footfall_factor: float
    reference_visibility: float
    visibility_weight: float
    min_visibility_factor: float
    max_visibility_factor: float
    space_type_multipliers: dict[str, float] = field(default_factory=dict)

    def as_public_dict(self) -> dict:
        return {
            "model_version": self.model_version,
            "base_rate_per_sqm": float(self.base_rate_per_sqm),
            "base_panel_rate": float(self.base_panel_rate),
            "reference_daily_footfall": self.reference_daily_footfall,
            "footfall_elasticity": self.footfall_elasticity,
            "footfall_factor_bounds": [self.min_footfall_factor, self.max_footfall_factor],
            "reference_visibility": self.reference_visibility,
            "visibility_weight": self.visibility_weight,
            "visibility_factor_bounds": [self.min_visibility_factor, self.max_visibility_factor],
            "space_type_multipliers": self.space_type_multipliers,
        }


DEFAULT_TYPE_MULTIPLIERS = {
    SpaceType.retail.value: 1.0,
    SpaceType.kiosk.value: 0.85,
    SpaceType.advertising_panel.value: 1.2,
    SpaceType.digital_screen.value: 1.5,
}


def assumptions_from_settings() -> PricingAssumptions:
    """Fallback assumptions from env settings when no DB config row exists."""
    return PricingAssumptions(
        model_version=settings.pricing_model_version,
        base_rate_per_sqm=Decimal(str(settings.base_rate_per_sqm)),
        base_panel_rate=Decimal(str(settings.base_panel_rate)),
        reference_daily_footfall=settings.reference_daily_footfall,
        footfall_elasticity=settings.footfall_elasticity,
        min_footfall_factor=settings.min_footfall_factor,
        max_footfall_factor=settings.max_footfall_factor,
        reference_visibility=settings.reference_visibility,
        visibility_weight=settings.visibility_weight,
        min_visibility_factor=settings.min_visibility_factor,
        max_visibility_factor=settings.max_visibility_factor,
        space_type_multipliers=dict(DEFAULT_TYPE_MULTIPLIERS),
    )


def assumptions_from_config(cfg: PricingConfig) -> PricingAssumptions:
    return PricingAssumptions(
        model_version=cfg.version,
        base_rate_per_sqm=Decimal(cfg.base_rate_per_sqm),
        base_panel_rate=Decimal(cfg.base_panel_rate),
        reference_daily_footfall=int(cfg.reference_daily_footfall),
        footfall_elasticity=float(cfg.footfall_elasticity),
        min_footfall_factor=float(cfg.min_footfall_factor),
        max_footfall_factor=float(cfg.max_footfall_factor),
        reference_visibility=float(cfg.reference_visibility),
        visibility_weight=float(cfg.visibility_weight),
        min_visibility_factor=float(cfg.min_visibility_factor),
        max_visibility_factor=float(cfg.max_visibility_factor),
        space_type_multipliers=dict(cfg.space_type_multipliers or {}),
    )


def get_active_assumptions(db: Session) -> PricingAssumptions:
    cfg = db.scalars(
        select(PricingConfig).where(PricingConfig.is_active.is_(True)).limit(1)
    ).first()
    return assumptions_from_config(cfg) if cfg else assumptions_from_settings()


def validate_assumptions(a: PricingAssumptions) -> None:
    """Raise ValueError on an incoherent pricing configuration."""
    if a.reference_daily_footfall <= 0:
        raise ValueError("reference_daily_footfall must be positive")
    if a.base_rate_per_sqm < 0 or a.base_panel_rate < 0:
        raise ValueError("base rates must be non-negative")
    if a.min_footfall_factor > a.max_footfall_factor:
        raise ValueError("min_footfall_factor exceeds max_footfall_factor")
    if a.min_visibility_factor > a.max_visibility_factor:
        raise ValueError("min_visibility_factor exceeds max_visibility_factor")
    if a.min_footfall_factor < 0 or a.min_visibility_factor < 0:
        raise ValueError("factor bounds must be non-negative")


def estimate_price(
    space_type: SpaceType | str,
    area_sqm: Decimal | None,
    visibility_score: Decimal | None,
    observed_daily_footfall: float | None,
    assumptions: PricingAssumptions,
    *,
    space_id: int | None = None,
    space_code: str | None = None,
    station_id: int | None = None,
) -> PricingEstimate:
    """Pure, deterministic indicative price. No DB, no fabricated inputs."""
    validate_assumptions(assumptions)
    st = SpaceType(space_type) if not isinstance(space_type, SpaceType) else space_type
    unit_priced = st in UNIT_PRICED_TYPES

    limitations: list[str] = []
    quality_hits = 0
    quality_total = 0

    base = PricingEstimate(
        available=False,
        model_version=assumptions.model_version,
        space_id=space_id,
        space_code=space_code,
        station_id=station_id,
        space_type=st,
        data_quality="low",
        assumptions=assumptions.as_public_dict(),
        explanation="",
    )

    # --- Essential input validation ---
    if not unit_priced and (area_sqm is None or area_sqm <= 0):
        base.explanation = (
            f"No indicative price: {st.value} is priced per square metre and its area "
            "is unknown. Area is never fabricated."
        )
        base.limitations = ["missing area for an area-priced space"]
        return base

    # --- Base component (Decimal) ---
    if unit_priced:
        base_component = Decimal(assumptions.base_panel_rate)
        area_note = "unit-priced inventory (area not used)"
    else:
        base_component = _money(Decimal(assumptions.base_rate_per_sqm) * Decimal(area_sqm))
        area_note = f"{area_sqm} sqm x base {assumptions.base_rate_per_sqm}/sqm"
        quality_hits += 1
    quality_total += 1 if not unit_priced else 0

    # --- Footfall factor ---
    quality_total += 1
    if observed_daily_footfall is None:
        footfall_factor = 1.0
        limitations.append("no observed footfall for station; neutral factor 1.0 applied")
    else:
        ratio = observed_daily_footfall / assumptions.reference_daily_footfall
        raw = (
            ratio**assumptions.footfall_elasticity if ratio > 0 else assumptions.min_footfall_factor
        )
        footfall_factor = _clamp(
            raw, assumptions.min_footfall_factor, assumptions.max_footfall_factor
        )
        quality_hits += 1

    # --- Visibility factor ---
    quality_total += 1
    if visibility_score is None:
        visibility_factor = 1.0
        limitations.append("no visibility score; neutral factor 1.0 applied")
    else:
        raw_v = 1.0 + (float(visibility_score) - assumptions.reference_visibility) * (
            assumptions.visibility_weight
        )
        visibility_factor = _clamp(
            raw_v, assumptions.min_visibility_factor, assumptions.max_visibility_factor
        )
        quality_hits += 1

    type_factor = float(assumptions.space_type_multipliers.get(st.value, 1.0))
    if st.value not in assumptions.space_type_multipliers:
        limitations.append(f"no multiplier configured for {st.value}; used 1.0")

    # --- Final currency (Decimal) ---
    price = _money(
        base_component
        * Decimal(str(footfall_factor))
        * Decimal(str(visibility_factor))
        * Decimal(str(type_factor))
    )

    quality = (
        "high"
        if quality_total and quality_hits == quality_total
        else ("medium" if quality_hits >= 1 else "low")
    )

    factors = [
        PricingFactor(name="base_component", value=float(base_component), description=area_note),
        PricingFactor(
            name="footfall_factor",
            value=round(footfall_factor, 4),
            description="demand adjustment (bounded, elasticity-scaled)",
        ),
        PricingFactor(
            name="visibility_factor",
            value=round(visibility_factor, 4),
            description="visibility adjustment (bounded)",
        ),
        PricingFactor(
            name="space_type_factor",
            value=round(type_factor, 4),
            description=f"multiplier for {st.value}",
        ),
    ]

    explanation = (
        f"Indicative monthly asking price INR {price} for a {st.value} space. "
        f"Base {base_component} x footfall {footfall_factor:.3f} x visibility "
        f"{visibility_factor:.3f} x type {type_factor:.3f}. Indicative heuristic "
        f"({assumptions.model_version}), not a verified market rate."
    )

    return PricingEstimate(
        available=True,
        model_version=assumptions.model_version,
        space_id=space_id,
        space_code=space_code,
        station_id=station_id,
        space_type=st,
        base_component=base_component,
        indicative_monthly_price=price,
        indicative_annual_price=_money(price * 12),
        factors=factors,
        data_quality=quality,
        data_quality_reasons=[f"{quality_hits}/{quality_total} key inputs present"],
        assumptions=assumptions.as_public_dict(),
        explanation=explanation,
        limitations=limitations,
    )

"""Transparent, rules-based tenant-category recommendations.

Deterministic and evidence-only: scores come from space type, area, visibility,
and observed footfall. It never infers passenger demographics, income, or buying
intent. An LLM may later narrate these results but must not alter the evidence.
"""
from __future__ import annotations

from sqlalchemy.orm import Session

from app.db.models.commercial_space import CommercialSpace
from app.db.models.station import Station
from app.schemas.proposal import TenantRecommendation, TenantRecommendationResult
from app.services import footfall_service, pricing_service

# category -> rule: applicable space types, footfall sensitivity, inputs it relies on
_CATEGORIES = [
    {"name": "Food & beverage (grab-and-go)", "types": {"retail", "kiosk"},
     "footfall_weight": 0.6, "uses_area": True, "uses_visibility": False},
    {"name": "Convenience retail", "types": {"retail", "kiosk"},
     "footfall_weight": 0.5, "uses_area": True, "uses_visibility": False},
    {"name": "Consumer electronics accessories", "types": {"retail"},
     "footfall_weight": 0.4, "uses_area": True, "uses_visibility": True},
    {"name": "Local brands / specialty retail", "types": {"retail", "kiosk"},
     "footfall_weight": 0.3, "uses_area": True, "uses_visibility": False},
    {"name": "Brand-awareness advertising", "types": {"advertising_panel", "digital_screen"},
     "footfall_weight": 0.7, "uses_area": False, "uses_visibility": True},
    {"name": "Digital / experiential advertising", "types": {"digital_screen"},
     "footfall_weight": 0.8, "uses_area": False, "uses_visibility": True},
]


def _confidence(hits: int, total: int) -> str:
    if total == 0 or hits == total:
        return "high" if total else "low"
    return "medium" if hits >= 1 else "low"


def recommend_tenants(
    db: Session, space_id: int, limit: int = 4
) -> TenantRecommendationResult:
    space = db.get(CommercialSpace, space_id)
    if space is None:
        raise LookupError("Commercial space not found")
    station = db.get(Station, space.station_id)

    daily = footfall_service.observed_daily_footfall(db, space.station_id)
    reference = pricing_service.get_active_assumptions(db).reference_daily_footfall
    footfall_ratio = min(daily / reference, 2.0) / 2.0 if daily else None  # 0..1, None if unknown
    space_type = str(space.space_type)
    area = float(space.area_sqm) if space.area_sqm is not None else None
    visibility = float(space.visibility_score) if space.visibility_score is not None else None

    recs: list[TenantRecommendation] = []
    for cat in _CATEGORIES:
        if space_type not in cat["types"]:
            continue
        evidence: list[str] = [f"Space type '{space_type.replace('_', ' ')}' fits this category"]
        compatibility: list[str] = []
        missing: list[str] = []

        score = 0.4  # base for a type match
        hits, needed = 0, 0

        needed += 1
        if footfall_ratio is not None:
            score += cat["footfall_weight"] * footfall_ratio
            evidence.append(
                f"Observed ~{round(daily):,} daily entries "
                f"({'high' if footfall_ratio > 0.5 else 'moderate'} relative to reference)"
            )
            hits += 1
        else:
            missing.append("No observed footfall for this station")

        if cat["uses_area"]:
            needed += 1
            if area is not None:
                score += 0.15 if area >= 15 else 0.05
                compatibility.append(f"Area {area:g} m² supports an on-site format")
                hits += 1
            else:
                missing.append("Area not recorded")
        if cat["uses_visibility"]:
            needed += 1
            if visibility is not None:
                score += 0.2 * (visibility / 10)
                compatibility.append(f"Visibility {visibility:g}/10")
                hits += 1
            else:
                missing.append("Visibility score not recorded")

        recs.append(
            TenantRecommendation(
                category=cat["name"],
                score=round(min(score, 1.0), 3),
                confidence=_confidence(hits, needed),
                evidence=evidence,
                compatibility=compatibility,
                missing_information=missing,
                limitations=[
                    "Footfall is observed entries, not confirmed customers or impressions.",
                    "No passenger demographic or spending data is used.",
                ],
            )
        )

    recs.sort(key=lambda r: r.score, reverse=True)
    notes = []
    if not recs:
        notes.append(f"No category rules match space type '{space_type}'.")
    return TenantRecommendationResult(
        space_id=space.id,
        space_code=space.space_code,
        station_name=station.name if station else "?",
        recommendations=recs[:limit],
        notes=notes,
    )

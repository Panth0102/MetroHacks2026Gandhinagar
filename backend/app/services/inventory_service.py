"""Commercial inventory analytics with explicit, documented denominators.
Currency uses Decimal. Maintenance/unavailable spaces are never counted as
vacant rentable inventory."""

from __future__ import annotations

from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.db.models.commercial_space import CommercialSpace, SpaceStatus
from app.db.models.lease import Lease, LeaseStatus
from app.schemas.commercial_space import InventorySummary

_ZERO = Decimal("0")


def _space_conds(station_id: int | None):
    return [CommercialSpace.station_id == station_id] if station_id is not None else []


def inventory_summary(db: Session, station_id: int | None = None) -> InventorySummary:
    conds = _space_conds(station_id)

    total_spaces = db.scalar(select(func.count(CommercialSpace.id)).where(*conds)) or 0

    status_rows = db.execute(
        select(CommercialSpace.status, func.count(CommercialSpace.id))
        .where(*conds)
        .group_by(CommercialSpace.status)
    ).all()
    count_by_status = {str(s): int(c) for s, c in status_rows}

    type_rows = db.execute(
        select(CommercialSpace.space_type, func.count(CommercialSpace.id))
        .where(*conds)
        .group_by(CommercialSpace.space_type)
    ).all()
    count_by_type = {str(t): int(c) for t, c in type_rows}

    occupied = count_by_status.get(SpaceStatus.occupied.value, 0)
    vacant = count_by_status.get(SpaceStatus.vacant.value, 0)

    occ_rate_count = round(occupied / total_spaces, 4) if total_spaces else None
    vac_rate_count = round(vacant / total_spaces, 4) if total_spaces else None

    # Area pools (known area only)
    occupied_area = (
        db.scalar(
            select(func.coalesce(func.sum(CommercialSpace.area_sqm), _ZERO)).where(
                *conds, CommercialSpace.status == SpaceStatus.occupied.value
            )
        )
        or _ZERO
    )
    vacant_area = (
        db.scalar(
            select(func.coalesce(func.sum(CommercialSpace.area_sqm), _ZERO)).where(
                *conds, CommercialSpace.status == SpaceStatus.vacant.value
            )
        )
        or _ZERO
    )
    known_area_pool = Decimal(occupied_area) + Decimal(vacant_area)
    occ_rate_area = (
        round(float(Decimal(occupied_area) / known_area_pool), 4) if known_area_pool > 0 else None
    )
    spaces_with_known_area = (
        db.scalar(
            select(func.count(CommercialSpace.id)).where(
                *conds, CommercialSpace.area_sqm.is_not(None)
            )
        )
        or 0
    )

    # Current contractual revenue = active leases only, joined to in-scope spaces.
    current_rev = (
        db.scalar(
            select(func.coalesce(func.sum(Lease.monthly_rent), _ZERO))
            .join(CommercialSpace, CommercialSpace.id == Lease.space_id)
            .where(*conds, Lease.status == LeaseStatus.active.value)
        )
        or _ZERO
    )
    current_rev = Decimal(current_rev)

    # Potential rent from VACANT spaces only, known asking rents.
    potential_rows = db.execute(
        select(
            func.coalesce(func.sum(CommercialSpace.asking_monthly_rent), _ZERO),
            func.count(CommercialSpace.id),
        ).where(
            *conds,
            CommercialSpace.status == SpaceStatus.vacant.value,
            CommercialSpace.asking_monthly_rent.is_not(None),
        )
    ).one()
    potential_rent = Decimal(potential_rows[0] or _ZERO)
    potential_count = int(potential_rows[1] or 0)

    notes = [
        "occupancy_rate_by_count denominator = all spaces (any status).",
        "occupancy_rate_by_area denominator = occupied+vacant known-area pool only.",
        "current_monthly_revenue = signed ACTIVE lease rents; potential = ASKING, not signed.",
    ]
    maintenance = count_by_status.get(SpaceStatus.under_maintenance.value, 0)
    unavailable = count_by_status.get(SpaceStatus.unavailable.value, 0)
    if maintenance or unavailable:
        notes.append(
            f"{maintenance} under-maintenance and {unavailable} unavailable spaces excluded "
            "from vacant/rentable figures."
        )

    return InventorySummary(
        station_id=station_id,
        total_spaces=int(total_spaces),
        count_by_status=count_by_status,
        count_by_type=count_by_type,
        occupancy_rate_by_count=occ_rate_count,
        vacancy_rate_by_count=vac_rate_count,
        occupied_area_sqm=Decimal(occupied_area),
        vacant_area_sqm=Decimal(vacant_area),
        occupancy_rate_by_area=occ_rate_area,
        spaces_with_known_area=int(spaces_with_known_area),
        current_monthly_revenue=current_rev,
        current_annual_revenue=current_rev * 12,
        potential_vacant_monthly_rent=potential_rent,
        potential_vacant_rent_known_count=potential_count,
        notes=notes,
    )

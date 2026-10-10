"""Idempotent synthetic-data seeding.

Running twice does NOT duplicate stations, footfall, spaces, leases, or the
pricing config, and never deletes existing data. Intended for dev/demo DBs only;
it refuses to run against APP_ENV=production unless --force is given.
"""

from __future__ import annotations

import argparse
import sys
from datetime import date
from decimal import Decimal
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from generate_sample_data import build_dataset  # noqa: E402
from sqlalchemy import select  # noqa: E402
from sqlalchemy.orm import Session  # noqa: E402

from app.core.config import settings  # noqa: E402
from app.core.logging import get_logger  # noqa: E402
from app.db.models import (  # noqa: E402
    CommercialSpace,
    FootfallRecord,
    Lease,
    PricingConfig,
    Station,
)
from app.db.session import SessionLocal, init_db  # noqa: E402

logger = get_logger("seed")


def _d(value) -> Decimal | None:
    return None if value is None else Decimal(str(value))


def seed(db: Session) -> dict:
    data = build_dataset()
    created = {"stations": 0, "footfall": 0, "spaces": 0, "leases": 0, "pricing_config": 0}

    # Stations (unique code)
    station_by_code: dict[str, Station] = {s.code: s for s in db.scalars(select(Station)).all()}
    for s in data["stations"]:
        if s["code"] not in station_by_code:
            obj = Station(
                code=s["code"],
                name=s["name"],
                line=s["line"],
                station_type=s["station_type"],
                location_description=s["location_description"],
                is_active=True,
            )
            db.add(obj)
            station_by_code[s["code"]] = obj
            created["stations"] += 1
    db.flush()

    # Footfall (unique station_id, date, hour) — load existing keys once.
    existing_keys = set(
        db.execute(
            select(FootfallRecord.station_id, FootfallRecord.observation_date, FootfallRecord.hour)
        ).all()
    )
    for f in data["footfall"]:
        st = station_by_code[f["station_code"]]
        key = (st.id, date.fromisoformat(f["observation_date"]), f["hour"])
        if key in existing_keys:
            continue
        db.add(
            FootfallRecord(
                station_id=st.id,
                observation_date=key[1],
                hour=f["hour"],
                entries=f["entries"],
                exits=f["exits"],
                source=f["source"],
            )
        )
        existing_keys.add(key)
        created["footfall"] += 1

    # Spaces (unique station_id, space_code)
    existing_space_codes = {
        (sp.station_id, sp.space_code) for sp in db.scalars(select(CommercialSpace)).all()
    }
    space_by_code: dict[str, CommercialSpace] = {}
    for sp in data["spaces"]:
        st = station_by_code[sp["station_code"]]
        if (st.id, sp["space_code"]) in existing_space_codes:
            continue
        obj = CommercialSpace(
            station_id=st.id,
            space_code=sp["space_code"],
            space_type=sp["space_type"],
            area_sqm=_d(sp["area_sqm"]),
            floor_description=sp["floor_description"],
            visibility_score=_d(sp["visibility_score"]),
            status=sp["status"],
            asking_monthly_rent=_d(sp["asking_monthly_rent"]),
            available_from=date.fromisoformat(sp["available_from"])
            if sp["available_from"]
            else None,
        )
        db.add(obj)
        space_by_code[sp["space_code"]] = obj
        created["spaces"] += 1
    db.flush()

    # Leases — idempotent: only add if the space has no lease yet.
    spaces_with_lease = {row[0] for row in db.execute(select(Lease.space_id).distinct()).all()}
    all_spaces = {sp.space_code: sp for sp in db.scalars(select(CommercialSpace)).all()}
    for ls in data["leases"]:
        sp = all_spaces.get(ls["space_code"])
        if sp is None or sp.id in spaces_with_lease:
            continue
        db.add(
            Lease(
                space_id=sp.id,
                tenant_name=ls["tenant_name"],
                monthly_rent=_d(ls["monthly_rent"]),
                start_date=date.fromisoformat(ls["start_date"]),
                end_date=date.fromisoformat(ls["end_date"]) if ls["end_date"] else None,
                status=ls["status"],
                notes=ls["notes"],
            )
        )
        spaces_with_lease.add(sp.id)
        created["leases"] += 1

    # Pricing config (unique version); keep exactly one active.
    pc = data["pricing_config"]
    existing_pc = db.scalars(
        select(PricingConfig).where(PricingConfig.version == pc["version"])
    ).first()
    if existing_pc is None:
        for other in db.scalars(select(PricingConfig)).all():
            other.is_active = False
        db.add(
            PricingConfig(
                version=pc["version"],
                is_active=True,
                base_rate_per_sqm=_d(pc["base_rate_per_sqm"]),
                base_panel_rate=_d(pc["base_panel_rate"]),
                reference_daily_footfall=pc["reference_daily_footfall"],
                footfall_elasticity=_d(pc["footfall_elasticity"]),
                min_footfall_factor=_d(pc["min_footfall_factor"]),
                max_footfall_factor=_d(pc["max_footfall_factor"]),
                reference_visibility=_d(pc["reference_visibility"]),
                visibility_weight=_d(pc["visibility_weight"]),
                min_visibility_factor=_d(pc["min_visibility_factor"]),
                max_visibility_factor=_d(pc["max_visibility_factor"]),
                space_type_multipliers=pc["space_type_multipliers"],
                source_notes=pc["source_notes"],
            )
        )
        created["pricing_config"] += 1

    db.commit()
    return created


def main() -> None:
    parser = argparse.ArgumentParser(description="Seed synthetic data (idempotent).")
    parser.add_argument("--force", action="store_true", help="allow non-development environments")
    parser.add_argument(
        "--create-tables",
        action="store_true",
        help="create tables via metadata (SQLite dev; use Alembic for Postgres)",
    )
    args = parser.parse_args()

    if settings.environment.lower() == "production" and not args.force:
        logger.error("Refusing to seed a production database without --force.")
        sys.exit(1)

    if args.create_tables:
        init_db()

    with SessionLocal() as db:
        created = seed(db)
    logger.info("Seed complete (newly created): %s", created)
    print("Seed complete. Newly created rows:", created)


if __name__ == "__main__":
    main()

from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest
from sqlalchemy.exc import IntegrityError

from app.db.models import CommercialSpace, FootfallRecord, Station
from app.services import inventory_service


def test_inventory_summary_denominators(db_session, small_dataset):
    s = inventory_service.inventory_summary(db_session, station_id=small_dataset.id)
    assert s.total_spaces == 2
    assert s.count_by_status.get("vacant") == 1
    assert s.count_by_status.get("under_maintenance") == 1
    assert s.occupancy_rate_by_count == 0.0
    assert s.vacancy_rate_by_count == 0.5
    assert s.current_monthly_revenue == Decimal("0")
    # Only the vacant space with a known asking rent counts.
    assert s.potential_vacant_monthly_rent == Decimal("50000")
    assert s.spaces_with_known_area == 1


def test_maintenance_space_not_counted_as_vacant(db_session, small_dataset):
    s = inventory_service.inventory_summary(db_session, station_id=small_dataset.id)
    assert any("under-maintenance" in n for n in s.notes)
    # vacant_area excludes the maintenance space (which also has no area)
    assert s.vacant_area_sqm == Decimal("20.00")


def test_footfall_unique_constraint(db_session, small_dataset):
    dup = FootfallRecord(
        station_id=small_dataset.id,
        observation_date=date(2026, 1, 5),
        hour=8,
        entries=1,
        source="dup",
    )
    db_session.add(dup)
    with pytest.raises(IntegrityError):
        db_session.commit()
    db_session.rollback()


def test_space_code_unique_per_station(db_session, small_dataset):
    dup = CommercialSpace(
        station_id=small_dataset.id, space_code="T1-S01", space_type="retail", status="vacant"
    )
    db_session.add(dup)
    with pytest.raises(IntegrityError):
        db_session.commit()
    db_session.rollback()


def test_station_code_unique(db_session):
    db_session.add(Station(code="DUP", name="A"))
    db_session.commit()
    db_session.add(Station(code="DUP", name="B"))
    with pytest.raises(IntegrityError):
        db_session.commit()
    db_session.rollback()


def test_api_inventory_summary(seeded_client):
    r = seeded_client.get("/api/v1/inventory/summary")
    assert r.status_code == 200
    body = r.json()
    assert body["total_spaces"] == 42

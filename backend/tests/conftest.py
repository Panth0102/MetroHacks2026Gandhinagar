from __future__ import annotations

import sys
from datetime import date
from decimal import Decimal
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

# Make scripts/ importable for the seeding helper.
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

import app.db.models  # noqa: F401,E402  (register tables)
from app.db.base import Base  # noqa: E402
from app.db.models import (  # noqa: E402
    CommercialSpace,
    FootfallRecord,
    PricingConfig,
    Station,
)
from app.db.session import get_db  # noqa: E402
from app.main import app  # noqa: E402


@pytest.fixture
def engine():
    eng = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    Base.metadata.create_all(eng)
    yield eng
    Base.metadata.drop_all(eng)
    eng.dispose()


@pytest.fixture
def db_session(engine) -> Session:
    maker = sessionmaker(bind=engine, expire_on_commit=False)
    s = maker()
    try:
        yield s
    finally:
        s.close()


@pytest.fixture
def active_pricing_config(db_session) -> PricingConfig:
    cfg = PricingConfig(
        version="v1.0-heuristic",
        is_active=True,
        base_rate_per_sqm=Decimal("1800"),
        base_panel_rate=Decimal("45000"),
        reference_daily_footfall=20000,
        footfall_elasticity=Decimal("0.3"),
        min_footfall_factor=Decimal("0.6"),
        max_footfall_factor=Decimal("1.8"),
        reference_visibility=Decimal("5"),
        visibility_weight=Decimal("0.08"),
        min_visibility_factor=Decimal("0.7"),
        max_visibility_factor=Decimal("1.4"),
        space_type_multipliers={
            "retail": 1.0,
            "kiosk": 0.85,
            "advertising_panel": 1.2,
            "digital_screen": 1.5,
        },
        source_notes="test",
    )
    db_session.add(cfg)
    db_session.commit()
    return cfg


@pytest.fixture
def small_dataset(db_session):
    """A tiny, hand-verified dataset for deterministic analytics assertions."""
    st = Station(code="T1", name="Test One", line="L1", is_active=True)
    db_session.add(st)
    db_session.flush()
    # Two days: one weekday (Mon 2026-01-05), one weekend (Sat 2026-01-10).
    # hour 8 -> 100, hour 18 -> 100 (tie); hour 12 -> 50.
    for d in (date(2026, 1, 5), date(2026, 1, 10)):
        for hour, entries in ((8, 100), (12, 50), (18, 100)):
            db_session.add(
                FootfallRecord(
                    station_id=st.id,
                    observation_date=d,
                    hour=hour,
                    entries=entries,
                    exits=entries - 10,
                    source="test",
                )
            )
    db_session.add(
        CommercialSpace(
            station_id=st.id,
            space_code="T1-S01",
            space_type="retail",
            area_sqm=Decimal("20"),
            visibility_score=Decimal("6"),
            status="vacant",
            asking_monthly_rent=Decimal("50000"),
        )
    )
    db_session.add(
        CommercialSpace(
            station_id=st.id,
            space_code="T1-S02",
            space_type="kiosk",
            area_sqm=None,
            status="under_maintenance",
        )
    )
    db_session.commit()
    return st


@pytest.fixture
def seeded_client(engine):
    from seed_database import seed

    maker = sessionmaker(bind=engine, expire_on_commit=False)
    with maker() as s:
        seed(s)

    def _override():
        s = maker()
        try:
            yield s
        finally:
            s.close()

    app.dependency_overrides[get_db] = _override
    with TestClient(app) as client:
        yield client
    app.dependency_overrides.clear()

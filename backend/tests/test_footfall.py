from __future__ import annotations

from datetime import date

from app.services import footfall_service


def test_summary_known_values(db_session, small_dataset):
    s = footfall_service.footfall_summary(db_session, station_id=small_dataset.id)
    assert s.observation_count == 6
    assert s.distinct_days == 2
    assert s.total_entries == 500
    assert s.avg_daily_entries == 250.0
    assert s.total_exits == 500 - 6 * 10  # each exits = entries - 10


def test_peak_hour_tie_is_reported(db_session, small_dataset):
    s = footfall_service.footfall_summary(db_session, station_id=small_dataset.id)
    assert s.peak_hours_tied == [8, 18]
    assert s.peak_hour_entries == 200


def test_weekday_vs_weekend_split(db_session, small_dataset):
    s = footfall_service.footfall_summary(db_session, station_id=small_dataset.id)
    assert s.weekday_avg_daily_entries == 250.0  # Mon 2026-01-05
    assert s.weekend_avg_daily_entries == 250.0  # Sat 2026-01-10


def test_date_filter_excludes_out_of_range(db_session, small_dataset):
    s = footfall_service.footfall_summary(
        db_session,
        station_id=small_dataset.id,
        start=date(2026, 1, 5),
        end=date(2026, 1, 5),
    )
    assert s.distinct_days == 1
    assert s.total_entries == 250


def test_empty_dataset_does_not_crash(db_session):
    s = footfall_service.footfall_summary(db_session)
    assert s.observation_count == 0
    assert s.total_entries == 0


def test_percentage_change_zero_baseline_returns_null(db_session, small_dataset):
    out = footfall_service.percentage_change(
        db_session,
        small_dataset.id,
        date(2025, 1, 1),
        date(2025, 1, 2),  # no data -> baseline 0
        date(2026, 1, 5),
        date(2026, 1, 6),
    )
    assert out["baseline_total"] == 0
    assert out["pct_change"] is None


def test_percentage_change_flags_unequal_periods(db_session, small_dataset):
    out = footfall_service.percentage_change(
        db_session,
        small_dataset.id,
        date(2026, 1, 5),
        date(2026, 1, 5),
        date(2026, 1, 9),
        date(2026, 1, 10),
    )
    assert any("differ in length" in n for n in out["notes"])


def test_api_footfall_date_validation(seeded_client):
    r = seeded_client.get("/api/v1/footfall?start_date=2026-10-01&end_date=2026-09-01")
    assert r.status_code == 422

from __future__ import annotations

from decimal import Decimal

from app.services import forecasting_service


def test_scenarios_math(db_session, small_dataset, active_pricing_config):
    f = forecasting_service.forecast_revenue(db_session, station_id=small_dataset.id)
    assert f.current_monthly_revenue == Decimal("0")
    assert len(f.scenarios) == 3
    fracs = [s.occupancy_fraction_of_vacant for s in f.scenarios]
    assert fracs == [0.5, 0.75, 1.0]
    full = next(s for s in f.scenarios if s.occupancy_fraction_of_vacant == 1.0)
    # 100% scenario adds the full eligible vacant potential to current revenue.
    assert full.projected_monthly_revenue == (
        f.current_monthly_revenue + f.eligible_vacant_potential_monthly_rent
    )
    assert full.projected_annual_revenue == full.projected_monthly_revenue * 12
    assert f.is_predictive_model is False


def test_api_forecast_revenue(seeded_client):
    r = seeded_client.get("/api/v1/forecasts/revenue")
    assert r.status_code == 200
    body = r.json()
    assert len(body["scenarios"]) == 3
    assert body["method"] == "scenario-baseline"


def test_api_pricing_estimate_valid(seeded_client):
    r = seeded_client.post(
        "/api/v1/pricing/estimate",
        json={
            "space_type": "retail",
            "area_sqm": 30,
            "visibility_score": 8,
            "observed_daily_footfall": 25000,
        },
    )
    assert r.status_code == 200
    assert r.json()["available"] is True


def test_api_pricing_estimate_rejects_invalid_area(seeded_client):
    r = seeded_client.post(
        "/api/v1/pricing/estimate",
        json={
            "space_type": "retail",
            "area_sqm": -5,
        },
    )
    assert r.status_code == 422


def test_api_pricing_estimate_rejects_bad_visibility(seeded_client):
    r = seeded_client.post(
        "/api/v1/pricing/estimate",
        json={
            "space_type": "retail",
            "area_sqm": 10,
            "visibility_score": 99,
        },
    )
    assert r.status_code == 422

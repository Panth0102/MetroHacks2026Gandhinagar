from __future__ import annotations

from app.services import analytics_service


def test_peak_hours_tie(db_session, small_dataset):
    r = analytics_service.peak_hours(db_session, station_id=small_dataset.id)
    assert r.peak_hours_tied == [8, 18]
    assert abs(sum(b.share for b in r.buckets) - 1.0) < 1e-6


def test_revenue_opportunities_are_explainable(db_session, small_dataset, active_pricing_config):
    ops = analytics_service.revenue_opportunities(db_session, station_id=small_dataset.id)
    assert len(ops) == 1  # only the vacant space; maintenance excluded
    op = ops[0]
    assert op.space_code == "T1-S01"
    assert op.priority_score >= 0
    assert op.score_breakdown  # explanation of the score
    assert op.reasons
    assert op.indicative_monthly_price is not None


def test_opportunities_exclude_non_vacant(db_session, small_dataset, active_pricing_config):
    ops = analytics_service.revenue_opportunities(db_session)
    assert all(o.status == "vacant" for o in ops)


def test_api_overview(seeded_client):
    r = seeded_client.get("/api/v1/analytics/overview")
    assert r.status_code == 200
    body = r.json()
    assert body["station_count"] == 8
    assert body["total_spaces"] == 42


def test_api_station_rankings_sorted(seeded_client):
    r = seeded_client.get("/api/v1/analytics/stations")
    assert r.status_code == 200
    ranks = r.json()
    totals = [x["total_entries"] for x in ranks]
    assert totals == sorted(totals, reverse=True)
    assert ranks[0]["rank"] == 1


def test_api_revenue_opportunities(seeded_client):
    r = seeded_client.get("/api/v1/analytics/revenue-opportunities?limit=5")
    assert r.status_code == 200
    ops = r.json()
    assert len(ops) <= 5
    if ops:
        scores = [o["priority_score"] for o in ops]
        assert scores == sorted(scores, reverse=True)

from __future__ import annotations


def test_health_ok(seeded_client):
    r = seeded_client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_health_ready_reports_database(seeded_client):
    r = seeded_client.get("/health/ready")
    assert r.status_code == 200
    body = r.json()
    assert "database" in body
    assert body["status"] in ("ready", "degraded")

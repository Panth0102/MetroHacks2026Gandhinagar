from __future__ import annotations


def test_list_stations_paginated(seeded_client):
    r = seeded_client.get("/api/v1/stations?limit=3")
    assert r.status_code == 200
    body = r.json()
    assert body["total"] == 8
    assert len(body["items"]) == 3
    assert body["limit"] == 3


def test_get_station_found(seeded_client):
    r = seeded_client.get("/api/v1/stations/1")
    assert r.status_code == 200
    assert r.json()["id"] == 1


def test_get_station_not_found(seeded_client):
    r = seeded_client.get("/api/v1/stations/99999")
    assert r.status_code == 404


def test_active_only_filter(seeded_client):
    r = seeded_client.get("/api/v1/stations?active_only=true")
    assert r.status_code == 200
    assert all(s["is_active"] for s in r.json()["items"])

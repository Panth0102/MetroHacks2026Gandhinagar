from app.services import tenant_recommendation_service
from app.utils.csv_export import to_csv

# ---- CSV export safety ----


def test_csv_neutralizes_formula_injection():
    out = to_csv(["val"], [["=1+2"], ["+cmd"], ["-x"], ["@evil"], ["safe"]])
    lines = out.strip().splitlines()
    assert lines[0] == "val"
    assert "'=1+2" in out
    assert "'+cmd" in out
    assert "'@evil" in out
    assert "safe" in lines  # untouched


def test_csv_escapes_commas_and_quotes():
    out = to_csv(["a", "b"], [["has,comma", 'has"quote']])
    assert '"has,comma"' in out
    assert '"has""quote"' in out


def test_api_rate_card_csv_has_disclaimer_and_data(seeded_client):
    r = seeded_client.get("/api/v1/pricing/rate-card.csv?vacant_only=true")
    assert r.status_code == 200
    assert r.headers["content-type"].startswith("text/csv")
    body = r.text
    assert "Synthetic demonstration data." in body
    assert "Indicative asking prices" in body
    assert "Pricing model version" in body  # header row present


def test_csv_matches_api_rate_card_rows(seeded_client):
    json_rows = seeded_client.get("/api/v1/pricing/rate-card?vacant_only=true&limit=500").json()
    csv_body = seeded_client.get("/api/v1/pricing/rate-card.csv?vacant_only=true").text
    # Every space code in the JSON response appears in the CSV.
    for item in json_rows:
        assert item["space_code"] in csv_body


# ---- tenant recommendations ----


def test_tenant_recommendations_are_ranked_and_evidenced(
    db_session, small_dataset, active_pricing_config
):
    from sqlalchemy import select

    from app.db.models import CommercialSpace

    sp = db_session.scalars(
        select(CommercialSpace).where(CommercialSpace.space_code == "T1-S01")
    ).one()
    res = tenant_recommendation_service.recommend_tenants(db_session, sp.id)
    assert res.recommendations
    scores = [r.score for r in res.recommendations]
    assert scores == sorted(scores, reverse=True)
    assert all(r.confidence in {"high", "medium", "low"} for r in res.recommendations)
    assert all(r.evidence for r in res.recommendations)
    # Retail space must not be offered advertising categories.
    assert not any("advertising" in r.category.lower() for r in res.recommendations)


def test_tenant_recommendations_api(seeded_client):
    inv = seeded_client.get("/api/v1/inventory?status=vacant&limit=1").json()
    sid = inv["items"][0]["id"]
    r = seeded_client.get(f"/api/v1/inventory/{sid}/tenant-recommendations")
    assert r.status_code == 200
    assert "recommendations" in r.json()
    assert seeded_client.get("/api/v1/inventory/99999/tenant-recommendations").status_code == 404

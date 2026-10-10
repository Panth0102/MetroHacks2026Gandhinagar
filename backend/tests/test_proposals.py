import io
import json

import pytest
from pydantic import ValidationError
from pypdf import PdfReader
from sqlalchemy import select

from app.core.config import settings
from app.db.models import CommercialSpace
from app.schemas.proposal import (
    ProposalContent,
    ProposalGenerateRequest,
    ProposalMetric,
    ProposalUpdate,
)
from app.services import (
    pdf_service,
    proposal_context_service,
    proposal_generation_service,
    proposal_service,
)


@pytest.fixture(autouse=True)
def _no_live_ai(monkeypatch):
    # Force the deterministic template path by default so the suite never calls a provider.
    monkeypatch.setattr(settings, "anthropic_api_key", None)


def _vacant_space(db_session, dataset) -> CommercialSpace:
    return db_session.scalars(
        select(CommercialSpace).where(CommercialSpace.space_code == "T1-S01")
    ).one()


def _context(db_session, dataset):
    sp = _vacant_space(db_session, dataset)
    ctx, space = proposal_context_service.build_context(
        db_session, ProposalGenerateRequest(space_id=sp.id, tenant_category="Food & beverage")
    )
    return ctx, space


# ---- schema validation ----


def test_proposal_content_requires_core_fields():
    with pytest.raises(ValidationError):
        ProposalContent(title="x")  # missing required sections


# ---- context construction ----


def test_context_separates_facts_and_estimates(db_session, small_dataset, active_pricing_config):
    ctx, _ = _context(db_session, small_dataset)
    assert ctx.footfall["metric"].startswith("observed")
    assert ctx.footfall["avg_daily_entries"] == 250.0
    assert ctx.pricing["model_version"] == "v1.0-heuristic"
    assert ctx.space["space_code"] == "T1-S01"


# ---- template fallback ----


def test_template_generation_is_valid_and_grounded(
    db_session, small_dataset, active_pricing_config
):
    ctx, _ = _context(db_session, small_dataset)
    content, source, model = proposal_generation_service.generate(ctx, use_ai=False)
    assert source == "template" and model is None
    assert isinstance(content, ProposalContent)
    joined = " ".join(content.assumptions_and_limitations).lower()
    assert "observed" in joined  # footfall described honestly
    assert any("250" in m.value for m in content.verified_metrics)


# ---- AI path (mocked, no network) ----

_GOOD_JSON = json.dumps(
    {
        "title": "AI Proposal for T1-S01",
        "executive_summary": "Summary grounded in observed entries.",
        "location_highlights": ["Central station"],
        "verified_metrics": [{"label": "Avg daily entries", "value": "250"}],
        "commercial_opportunity": "Opportunity text.",
        "pricing_summary": "Indicative price, not a verified rate.",
        "suggested_usage": "Grab-and-go kiosk.",
        "call_to_action": "Contact the commercial team.",
        "assumptions_and_limitations": ["Observed entries, not unique visitors."],
    }
)


def test_ai_generation_parses_structured_json(
    db_session, small_dataset, active_pricing_config, monkeypatch
):
    ctx, _ = _context(db_session, small_dataset)
    monkeypatch.setattr(proposal_generation_service, "_llm_complete", lambda s, u: _GOOD_JSON)
    content, source, model = proposal_generation_service.generate(ctx, use_ai=True)
    assert source == "ai"
    assert content.title == "AI Proposal for T1-S01"


def test_ai_malformed_output_falls_back_to_template(
    db_session, small_dataset, active_pricing_config, monkeypatch
):
    ctx, _ = _context(db_session, small_dataset)
    monkeypatch.setattr(
        proposal_generation_service, "_llm_complete", lambda s, u: "not json at all"
    )
    content, source, _ = proposal_generation_service.generate(ctx, use_ai=True)
    assert source == "template"  # never mislabels a fallback as AI
    assert isinstance(content, ProposalContent)


def test_ai_provider_error_falls_back(
    db_session, small_dataset, active_pricing_config, monkeypatch
):
    ctx, _ = _context(db_session, small_dataset)

    def _boom(s, u):
        raise RuntimeError("provider timeout")

    monkeypatch.setattr(proposal_generation_service, "_llm_complete", _boom)
    _, source, _ = proposal_generation_service.generate(ctx, use_ai=True)
    assert source == "template"


# ---- persistence ----


def test_create_list_get_update(db_session, small_dataset, active_pricing_config):
    ctx, space = _context(db_session, small_dataset)
    content, source, model = proposal_generation_service.generate(ctx, use_ai=False)
    p = proposal_service.create_proposal(
        db_session,
        space=space,
        content=content,
        context=ctx,
        source=source,
        ai_model=model,
        tenant_category="Food & beverage",
    )
    assert p.reference_code.startswith("PROP-")
    rows, total = proposal_service.list_proposals(db_session, limit=10, offset=0)
    assert total == 1 and rows[0].id == p.id

    updated = proposal_service.update_proposal(
        db_session, p, ProposalUpdate(status="approved", title="Edited title")
    )
    assert str(updated.status) == "approved"
    assert updated.title == "Edited title"
    # snapshot is immutable through the update API (no space_id field accepted)
    assert "space_id" not in ProposalUpdate.model_fields


def test_regenerate_uses_frozen_snapshot(db_session, small_dataset, active_pricing_config):
    ctx, space = _context(db_session, small_dataset)
    content, source, model = proposal_generation_service.generate(ctx, use_ai=False)
    p = proposal_service.create_proposal(
        db_session,
        space=space,
        content=content,
        context=ctx,
        source=source,
        ai_model=model,
        tenant_category=None,
    )
    snapshot_before = dict(p.context_snapshot)
    regenerated = proposal_service.replace_content(db_session, p, content, "template", None)
    assert regenerated.context_snapshot == snapshot_before  # evidence frozen


# ---- PDF ----


def _render(content: ProposalContent) -> bytes:
    return pdf_service.render_proposal_pdf(
        content,
        reference_code="PROP-TEST01",
        station_name="Riverfront Central",
        space_code="T1-S01",
    )


def test_pdf_is_one_page_with_expected_text(db_session, small_dataset, active_pricing_config):
    ctx, _ = _context(db_session, small_dataset)
    content, _, _ = proposal_generation_service.generate(ctx, use_ai=False)
    reader = PdfReader(io.BytesIO(_render(content)))
    assert len(reader.pages) == 1
    text = reader.pages[0].extract_text()
    assert "PROP-TEST01" in text
    assert "Riverfront Central" in text


def test_pdf_long_text_stays_one_page():
    long = ("VeryLongBusinessName " * 40).strip()
    content = ProposalContent(
        title=long[:200],
        executive_summary=long[:1190],
        location_highlights=[long[:100]] * 8,
        verified_metrics=[ProposalMetric(label="Metric", value="123") for _ in range(12)],
        commercial_opportunity=long[:1190],
        pricing_summary=long[:790],
        suggested_usage=long[:790],
        call_to_action=long[:590],
        assumptions_and_limitations=[long[:100]] * 10,
    )
    reader = PdfReader(io.BytesIO(_render(content)))
    assert len(reader.pages) == 1


def test_pdf_missing_optional_fields_does_not_crash():
    content = ProposalContent(
        title="Minimal proposal",
        executive_summary="Short.",
        location_highlights=[],
        verified_metrics=[],
        commercial_opportunity="Opp.",
        pricing_summary="Price.",
        suggested_usage="",
        call_to_action="Call.",
        assumptions_and_limitations=[],
    )
    reader = PdfReader(io.BytesIO(_render(content)))
    assert len(reader.pages) == 1


# ---- API flow ----


def test_api_generate_edit_pdf_flow(seeded_client):
    inv = seeded_client.get("/api/v1/inventory?status=vacant&limit=1").json()
    sid = inv["items"][0]["id"]
    r = seeded_client.post(
        "/api/v1/proposals/generate",
        json={"space_id": sid, "tenant_category": "Food & beverage", "business_name": "Chai Point"},
    )
    assert r.status_code == 201
    p = r.json()
    assert p["generation_source"] == "template"  # no AI key in tests
    pid = p["id"]

    assert seeded_client.get(f"/api/v1/proposals/{pid}").status_code == 200
    patched = seeded_client.patch(f"/api/v1/proposals/{pid}", json={"status": "approved"})
    assert patched.json()["status"] == "approved"

    pdf = seeded_client.get(f"/api/v1/proposals/{pid}/pdf")
    assert pdf.status_code == 200
    assert pdf.headers["content-type"] == "application/pdf"
    assert pdf.content[:4] == b"%PDF"

    assert seeded_client.get("/api/v1/proposals/99999").status_code == 404
    assert (
        seeded_client.post("/api/v1/proposals/generate", json={"space_id": 99999}).status_code
        == 404
    )

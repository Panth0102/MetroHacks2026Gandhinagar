from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.db.models.proposal import ProposalStatus


class ProposalMetric(BaseModel):
    label: str = Field(..., max_length=80)
    value: str = Field(..., max_length=120)


class ProposalContent(BaseModel):
    """Structured, editable proposal body. All fields are plain text and are
    escaped when rendered (frontend) or drawn (PDF); no HTML is interpreted."""

    title: str = Field(..., min_length=3, max_length=200)
    executive_summary: str = Field(..., max_length=1200)
    location_highlights: list[str] = Field(default_factory=list, max_length=8)
    verified_metrics: list[ProposalMetric] = Field(default_factory=list, max_length=12)
    commercial_opportunity: str = Field(..., max_length=1200)
    pricing_summary: str = Field(..., max_length=800)
    suggested_usage: str = Field("", max_length=800)
    call_to_action: str = Field(..., max_length=600)
    assumptions_and_limitations: list[str] = Field(default_factory=list, max_length=10)


# ---- Context passed to the generator (observed facts vs estimates kept separate) ----


class ProposalContext(BaseModel):
    station: dict
    space: dict
    footfall: dict
    pricing: dict
    user_input: dict


class ProposalGenerateRequest(BaseModel):
    space_id: int
    tenant_category: str | None = Field(None, max_length=64)
    business_name: str | None = Field(None, max_length=120)
    campaign_objective: str | None = Field(None, max_length=300)
    target_audience: str | None = Field(None, max_length=300)
    budget: float | None = Field(None, ge=0)
    language: str = Field("English", max_length=40)


class ProposalUpdate(BaseModel):
    """Only these fields may be edited on a saved proposal."""

    title: str | None = Field(None, min_length=3, max_length=200)
    tenant_category: str | None = Field(None, max_length=64)
    content: ProposalContent | None = None
    status: ProposalStatus | None = None


class ProposalOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    reference_code: str
    space_id: int
    station_id: int
    title: str
    tenant_category: str | None
    status: ProposalStatus
    content: ProposalContent
    context_snapshot: ProposalContext
    pricing_model_version: str | None
    generation_source: str
    ai_model: str | None
    created_at: datetime
    updated_at: datetime


class ProposalListItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    reference_code: str
    space_id: int
    station_id: int
    title: str
    tenant_category: str | None
    status: ProposalStatus
    generation_source: str
    created_at: datetime
    updated_at: datetime


# ---- Tenant category recommendations (Feature 6) ----


class TenantRecommendation(BaseModel):
    category: str
    score: float
    confidence: str  # high | medium | low
    evidence: list[str]
    compatibility: list[str]
    missing_information: list[str]
    limitations: list[str]


class TenantRecommendationResult(BaseModel):
    space_id: int
    space_code: str
    station_name: str
    recommendations: list[TenantRecommendation]
    notes: list[str] = []

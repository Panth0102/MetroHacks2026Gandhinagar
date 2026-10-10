"""Proposal persistence. Restricts which fields callers may edit and freezes a
context snapshot at generation time so historical proposals never silently change."""
from __future__ import annotations

import uuid

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.db.models.commercial_space import CommercialSpace
from app.db.models.proposal import Proposal
from app.schemas.proposal import (
    ProposalContent,
    ProposalContext,
    ProposalUpdate,
)


def _reference_code() -> str:
    return "PROP-" + uuid.uuid4().hex[:8].upper()


def create_proposal(
    db: Session,
    *,
    space: CommercialSpace,
    content: ProposalContent,
    context: ProposalContext,
    source: str,
    ai_model: str | None,
    tenant_category: str | None,
) -> Proposal:
    proposal = Proposal(
        reference_code=_reference_code(),
        space_id=space.id,
        station_id=space.station_id,
        title=content.title,
        tenant_category=tenant_category,
        status="draft",
        content=content.model_dump(mode="json"),
        context_snapshot=context.model_dump(mode="json"),
        pricing_model_version=context.pricing.get("model_version"),
        generation_source=source,
        ai_model=ai_model,
    )
    db.add(proposal)
    db.commit()
    db.refresh(proposal)
    return proposal


def list_proposals(
    db: Session, *, limit: int, offset: int, space_id: int | None = None
) -> tuple[list[Proposal], int]:
    conds = [Proposal.space_id == space_id] if space_id is not None else []
    total = db.scalar(select(func.count(Proposal.id)).where(*conds)) or 0
    rows = db.scalars(
        select(Proposal)
        .where(*conds)
        .order_by(Proposal.created_at.desc(), Proposal.id.desc())
        .limit(limit)
        .offset(offset)
    ).all()
    return list(rows), int(total)


def get_proposal(db: Session, proposal_id: int) -> Proposal | None:
    return db.get(Proposal, proposal_id)


def update_proposal(db: Session, proposal: Proposal, patch: ProposalUpdate) -> Proposal:
    """Apply only the whitelisted editable fields (title, tenant_category,
    content, status). space/snapshot/provenance are immutable."""
    if patch.title is not None:
        proposal.title = patch.title
    if patch.tenant_category is not None:
        proposal.tenant_category = patch.tenant_category
    if patch.status is not None:
        proposal.status = patch.status.value
    if patch.content is not None:
        proposal.content = patch.content.model_dump(mode="json")
        proposal.title = patch.content.title
    db.commit()
    db.refresh(proposal)
    return proposal


def replace_content(db: Session, proposal: Proposal, content: ProposalContent, source: str,
                    ai_model: str | None) -> Proposal:
    """Used by regeneration: swap body + provenance, keep the same record/snapshot."""
    proposal.content = content.model_dump(mode="json")
    proposal.title = content.title
    proposal.generation_source = source
    proposal.ai_model = ai_model
    db.commit()
    db.refresh(proposal)
    return proposal

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, Response
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.session import get_db
from app.schemas.common import Page
from app.schemas.proposal import (
    ProposalContext,
    ProposalGenerateRequest,
    ProposalListItem,
    ProposalOut,
    ProposalUpdate,
)
from app.services import (
    pdf_service,
    proposal_context_service,
    proposal_generation_service,
    proposal_service,
)

router = APIRouter(prefix="/proposals", tags=["proposals"])


@router.post("/generate", response_model=ProposalOut, status_code=201)
def generate_proposal(body: ProposalGenerateRequest, db: Session = Depends(get_db)) -> ProposalOut:
    """Build a validated, evidence-grounded context from backend data, generate the
    proposal copy (AI when configured, deterministic template otherwise), and save it."""
    try:
        context, space = proposal_context_service.build_context(db, body)
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    content, source, ai_model = proposal_generation_service.generate(
        context, use_ai=settings.ai_enabled
    )
    proposal = proposal_service.create_proposal(
        db, space=space, content=content, context=context, source=source,
        ai_model=ai_model, tenant_category=body.tenant_category,
    )
    return ProposalOut.model_validate(proposal)


@router.get("", response_model=Page[ProposalListItem])
def list_proposals(
    db: Session = Depends(get_db),
    space_id: int | None = None,
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
) -> Page[ProposalListItem]:
    rows, total = proposal_service.list_proposals(db, limit=limit, offset=offset, space_id=space_id)
    return Page(
        items=[ProposalListItem.model_validate(r) for r in rows],
        total=total, limit=limit, offset=offset,
    )


def _get_or_404(db: Session, proposal_id: int):
    proposal = proposal_service.get_proposal(db, proposal_id)
    if proposal is None:
        raise HTTPException(status_code=404, detail="Proposal not found")
    return proposal


@router.get("/{proposal_id}", response_model=ProposalOut)
def get_proposal(proposal_id: int, db: Session = Depends(get_db)) -> ProposalOut:
    return ProposalOut.model_validate(_get_or_404(db, proposal_id))


@router.patch("/{proposal_id}", response_model=ProposalOut)
def update_proposal(
    proposal_id: int, patch: ProposalUpdate, db: Session = Depends(get_db)
) -> ProposalOut:
    proposal = _get_or_404(db, proposal_id)
    return ProposalOut.model_validate(proposal_service.update_proposal(db, proposal, patch))


@router.post("/{proposal_id}/regenerate", response_model=ProposalOut)
def regenerate_proposal(proposal_id: int, db: Session = Depends(get_db)) -> ProposalOut:
    """Regenerate copy from the FROZEN context snapshot (keeps the original evidence)."""
    proposal = _get_or_404(db, proposal_id)
    context = ProposalContext.model_validate(proposal.context_snapshot)
    content, source, ai_model = proposal_generation_service.generate(
        context, use_ai=settings.ai_enabled
    )
    return ProposalOut.model_validate(
        proposal_service.replace_content(db, proposal, content, source, ai_model)
    )


@router.get("/{proposal_id}/pdf")
def download_pdf(proposal_id: int, db: Session = Depends(get_db)) -> Response:
    from app.schemas.proposal import ProposalContent

    proposal = _get_or_404(db, proposal_id)
    content = ProposalContent.model_validate(proposal.content)
    snapshot = ProposalContext.model_validate(proposal.context_snapshot)
    pdf = pdf_service.render_proposal_pdf(
        content,
        reference_code=proposal.reference_code,
        station_name=snapshot.station.get("name", ""),
        space_code=snapshot.space.get("space_code", ""),
    )
    filename = f"{proposal.reference_code}.pdf"
    return Response(
        content=pdf,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )

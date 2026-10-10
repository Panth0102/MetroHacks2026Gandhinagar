from __future__ import annotations

import enum

from sqlalchemy import JSON, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin


class ProposalStatus(str, enum.Enum):
    draft = "draft"
    ready_for_review = "ready_for_review"
    approved = "approved"


class Proposal(Base, TimestampMixin):
    """A generated sales proposal for a commercial space.

    `content` holds the structured, editable proposal sections.
    `context_snapshot` freezes the backend data used at generation time, so later
    footfall/price changes never silently rewrite a historical proposal.
    No AI credentials are ever stored here.
    """

    __tablename__ = "proposals"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    reference_code: Mapped[str] = mapped_column(String(32), unique=True, nullable=False, index=True)
    space_id: Mapped[int] = mapped_column(
        ForeignKey("commercial_spaces.id", ondelete="CASCADE"), nullable=False, index=True
    )
    station_id: Mapped[int] = mapped_column(Integer, nullable=False)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    tenant_category: Mapped[str | None] = mapped_column(String(64))
    status: Mapped[ProposalStatus] = mapped_column(
        String(32), nullable=False, default=ProposalStatus.draft.value
    )

    content: Mapped[dict] = mapped_column(JSON, nullable=False)
    context_snapshot: Mapped[dict] = mapped_column(JSON, nullable=False)

    pricing_model_version: Mapped[str | None] = mapped_column(String(64))
    generation_source: Mapped[str] = mapped_column(String(16), nullable=False, default="template")
    ai_model: Mapped[str | None] = mapped_column(String(64))

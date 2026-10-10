from __future__ import annotations

from sqlalchemy import Boolean, Integer, String, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin


class Station(Base, TimestampMixin):
    __tablename__ = "stations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    code: Mapped[str] = mapped_column(String(32), unique=True, nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    line: Mapped[str | None] = mapped_column(String(64))
    station_type: Mapped[str | None] = mapped_column(String(32))
    location_description: Mapped[str | None] = mapped_column(String(255))
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("true"))

    footfall: Mapped[list[FootfallRecord]] = relationship(  # noqa: F821
        back_populates="station", cascade="all, delete-orphan"
    )
    spaces: Mapped[list[CommercialSpace]] = relationship(  # noqa: F821
        back_populates="station", cascade="all, delete-orphan"
    )

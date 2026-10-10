"""Import all models so they register on Base.metadata (for create_all / Alembic)."""

from app.db.models.commercial_space import (
    UNIT_PRICED_TYPES,
    CommercialSpace,
    SpaceStatus,
    SpaceType,
)
from app.db.models.footfall import FootfallRecord
from app.db.models.lease import Lease, LeaseStatus
from app.db.models.pricing import PricingConfig
from app.db.models.station import Station

__all__ = [
    "Station",
    "FootfallRecord",
    "CommercialSpace",
    "SpaceType",
    "SpaceStatus",
    "UNIT_PRICED_TYPES",
    "Lease",
    "LeaseStatus",
    "PricingConfig",
]

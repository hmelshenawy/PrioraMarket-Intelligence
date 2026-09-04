"""Vehicle Reference Catalog domain validation."""

from __future__ import annotations

from src.models import VehicleReferenceCatalogRow
from src.normalize.canonical import canonical_key


class VehicleReferenceCatalogValidationError(ValueError):
    """Raised when a catalog row violates required source-of-truth rules."""


def validate_vehicle_reference_catalog_row(
    row: VehicleReferenceCatalogRow,
) -> VehicleReferenceCatalogRow:
    required = {
        "market": row.market,
        "make_key": row.make_key,
        "make_display": row.make_display,
        "model_key": row.model_key,
        "model_display": row.model_display,
    }
    missing = [name for name, value in required.items() if not str(value or "").strip()]
    if missing:
        raise VehicleReferenceCatalogValidationError(
            "missing required catalog fields: " + ", ".join(missing)
        )

    if row.make_key != canonical_key(row.make_key):
        raise VehicleReferenceCatalogValidationError("make_key must already be canonical")
    if row.model_key != canonical_key(row.model_key):
        raise VehicleReferenceCatalogValidationError("model_key must already be canonical")
    if row.aliases is not None and not isinstance(row.aliases, dict):
        raise VehicleReferenceCatalogValidationError("aliases must be an object grouped by field")
    if row.confidence not in {"manual", "manual_verified", "imported", "inferred"}:
        raise VehicleReferenceCatalogValidationError("confidence is not supported")
    return row

from __future__ import annotations

import pytest

from src.models import VehicleReferenceCatalogRow
from src.store.catalog_validation import (
    VehicleReferenceCatalogValidationError,
    validate_vehicle_reference_catalog_row,
)


def _row(**overrides) -> VehicleReferenceCatalogRow:
    values = {
        "id": None,
        "market": "global",
        "make_key": "mercedesbenz",
        "make_display": "Mercedes-Benz",
        "model_key": "cclass",
        "model_display": "C-Class",
        "generation": "W206",
        "body_code": "W206",
        "start_year": 2021,
        "aliases": {"make": ["Mercedes"], "model": ["C Class"]},
        "confidence": "manual",
    }
    values.update(overrides)
    return VehicleReferenceCatalogRow(**values)


def test_catalog_row_validation_accepts_required_source_of_truth_fields() -> None:
    row = _row()

    assert validate_vehicle_reference_catalog_row(row) is row


def test_catalog_row_validation_requires_display_values() -> None:
    with pytest.raises(VehicleReferenceCatalogValidationError, match="model_display"):
        validate_vehicle_reference_catalog_row(_row(model_display=""))


def test_catalog_row_validation_rejects_noncanonical_keys() -> None:
    with pytest.raises(VehicleReferenceCatalogValidationError, match="make_key"):
        validate_vehicle_reference_catalog_row(_row(make_key="Mercedes Benz"))

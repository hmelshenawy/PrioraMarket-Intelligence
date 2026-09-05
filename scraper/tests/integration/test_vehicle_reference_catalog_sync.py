from __future__ import annotations

import shutil
from pathlib import Path

from src.store.catalog_sync import synchronize_vehicle_reference_catalog
from tests.integration.catalog_store_stub import CatalogStoreStub

FIXTURE = (
    Path(__file__).parents[1]
    / "fixtures"
    / "vehicle_reference_catalog"
    / "vehicle_reference_catalog.csv"
)


def test_vehicle_reference_catalog_sync_is_idempotent(tmp_path) -> None:
    catalog = tmp_path / "vehicle_reference_catalog.csv"
    shutil.copy(FIXTURE, catalog)
    storage = CatalogStoreStub()

    first = synchronize_vehicle_reference_catalog(storage, catalog)
    second = synchronize_vehicle_reference_catalog(storage, catalog)

    assert first.inserted == 6
    assert second.unchanged == 6
    assert len(storage.vehicle_reference_catalog) == 6

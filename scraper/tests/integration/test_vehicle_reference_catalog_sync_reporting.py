from __future__ import annotations

from dataclasses import replace
from pathlib import Path

from src.store.catalog_sync import synchronize_vehicle_reference_catalog
from tests.fakes import InMemoryStorageAdapter

FIXTURE = (
    Path(__file__).parents[1]
    / "fixtures"
    / "vehicle_reference_catalog"
    / "vehicle_reference_catalog.csv"
)
INVALID = (
    Path(__file__).parents[1]
    / "fixtures"
    / "vehicle_reference_catalog"
    / "vehicle_reference_catalog_invalid.csv"
)


def test_vehicle_reference_catalog_sync_reports_provenance_and_conflicts() -> None:
    storage = InMemoryStorageAdapter()
    first = synchronize_vehicle_reference_catalog(storage, FIXTURE)
    existing = storage.vehicle_reference_catalog[0]
    storage.vehicle_reference_catalog[0] = replace(
        existing, source_file="manual-edit.csv", source_row_hash="manual-hash"
    )

    second = synchronize_vehicle_reference_catalog(storage, FIXTURE)

    assert first.source_file == "vehicle_reference_catalog.csv"
    assert storage.vehicle_reference_catalog[0].last_synced_at is not None
    assert second.unchanged == 5
    assert second.conflicts == 1


def test_vehicle_reference_catalog_sync_reports_rejected_rows() -> None:
    storage = InMemoryStorageAdapter()

    report = synchronize_vehicle_reference_catalog(storage, INVALID)

    assert report.rejected > 0
    assert report.inserted == 0

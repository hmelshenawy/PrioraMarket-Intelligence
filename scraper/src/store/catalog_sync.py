"""Idempotent Vehicle Reference Catalog synchronization service."""

from __future__ import annotations

from pathlib import Path

from src.common.models import CatalogSyncReport, VehicleReferenceCatalogRow
from src.db.vehicle_reference_catalog_csv import read_vehicle_reference_catalog_csv
from src.storage.interface import StorageAdapter


class VehicleReferenceCatalogSyncError(ValueError):
    """Raised when no catalog source can be synchronized safely."""


def read_catalog_sources(
    path: Path,
) -> tuple[list[VehicleReferenceCatalogRow], list[str], list[Path]]:
    files = sorted(path.glob("*.csv")) if path.is_dir() else [path]
    if not files:
        raise VehicleReferenceCatalogSyncError(f"no catalog CSV files found in {path}")
    rows: list[VehicleReferenceCatalogRow] = []
    errors: list[str] = []
    for csv_path in files:
        file_rows, file_errors = read_vehicle_reference_catalog_csv(csv_path)
        rows.extend(file_rows)
        errors.extend(file_errors)
    return rows, errors, files


def synchronize_vehicle_reference_catalog(
    storage: StorageAdapter, path: Path
) -> CatalogSyncReport:
    rows, errors, files = read_catalog_sources(path)
    report = storage.upsert_vehicle_reference_catalog(rows, ",".join(file.name for file in files))
    if errors:
        return CatalogSyncReport(
            source_file=report.source_file,
            inserted=report.inserted,
            updated=report.updated,
            unchanged=report.unchanged,
            rejected=report.rejected + len(errors),
            conflicts=report.conflicts,
            synced_at=report.synced_at,
        )
    return report

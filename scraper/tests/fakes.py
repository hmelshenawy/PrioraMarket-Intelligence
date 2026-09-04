"""Test doubles for the storage boundary.

Production code has exactly two storage implementations (csv_store,
postgres). Tests that are not DB-gated use this in-memory fake.
"""

from __future__ import annotations

from dataclasses import replace
from datetime import datetime, timezone
from typing import Iterable, Iterator

from src.models import (
    BackfillListingCandidate,
    CatalogSyncReport,
    Listing,
    NormalizationStatisticsReport,
    RawListing,
    RunReport,
    VehicleReferenceCatalogRow,
)


class InMemoryStorageAdapter:
    """Minimal storage fake: keeps everything in process memory."""

    def __init__(self):
        self.raw: list[RawListing] = []
        self.listings: list[Listing] = []
        self.report: RunReport | None = None
        self.vehicle_reference_catalog: list[VehicleReferenceCatalogRow] = []
        self.normalization_statistics: list[NormalizationStatisticsReport] = []
        self.backfill_candidates: list[BackfillListingCandidate] = []
        self.backfill_updates: list[tuple[int, dict, str, str, str]] = []

    def write_raw(self, raw_listings: Iterable[RawListing]) -> int:
        items = list(raw_listings)
        self.raw.extend(items)
        return len(items)

    def write_listings(self, listings: Iterable[Listing]) -> int:
        items = list(listings)
        self.listings.extend(items)
        return len(items)

    def write_report(self, report: RunReport) -> None:
        self.report = report

    def find_vehicle_reference_catalog(
        self, market: str, make_key: str, model_key: str | None = None
    ) -> list[VehicleReferenceCatalogRow]:
        return [
            row
            for row in self.vehicle_reference_catalog
            if row.market == market
            and row.make_key == make_key
            and (model_key is None or row.model_key == model_key)
        ]

    def upsert_vehicle_reference_catalog(
        self, rows: Iterable[VehicleReferenceCatalogRow], source_file: str
    ) -> CatalogSyncReport:
        now = datetime.now(timezone.utc)
        inserted = updated = unchanged = conflicts = 0
        for incoming in rows:
            row = replace(incoming, source_file=source_file, last_synced_at=now)
            identity = _catalog_identity(row)
            existing_index = next(
                (
                    index
                    for index, existing in enumerate(self.vehicle_reference_catalog)
                    if _catalog_identity(existing) == identity
                ),
                None,
            )
            if existing_index is None:
                self.vehicle_reference_catalog.append(row)
                inserted += 1
                continue
            existing = self.vehicle_reference_catalog[existing_index]
            if existing.source_row_hash == row.source_row_hash:
                unchanged += 1
                continue
            if existing.source_file and existing.source_file != source_file:
                conflicts += 1
            self.vehicle_reference_catalog[existing_index] = row
            updated += 1
        return CatalogSyncReport(
            source_file=source_file,
            inserted=inserted,
            updated=updated,
            unchanged=unchanged,
            conflicts=conflicts,
            synced_at=now,
        )

    def write_normalization_statistics(self, report: NormalizationStatisticsReport) -> None:
        self.normalization_statistics.append(report)

    def read_listing_backfill_candidates(
        self, batch_size: int, after_id: int | None = None
    ) -> Iterator[BackfillListingCandidate]:
        count = 0
        for candidate in self.backfill_candidates:
            if after_id is not None and candidate.id <= after_id:
                continue
            if count >= batch_size:
                break
            count += 1
            yield candidate

    def update_listing_backfill_payload(
        self,
        listing_id: int,
        canonical_payload: dict,
        canonical_hash: str,
        normalization_version: str,
        canonicalization_version: str,
    ) -> None:
        self.backfill_updates.append(
            (
                listing_id,
                canonical_payload,
                canonical_hash,
                normalization_version,
                canonicalization_version,
            )
        )
        for index, candidate in enumerate(self.backfill_candidates):
            if candidate.id == listing_id:
                self.backfill_candidates[index] = BackfillListingCandidate(
                    id=candidate.id,
                    source=candidate.source,
                    uuid=candidate.uuid,
                    canonical_payload=canonical_payload,
                    normalization_version=normalization_version,
                    current_raw_listing_id=candidate.current_raw_listing_id,
                )
                break


def _catalog_identity(
    row: VehicleReferenceCatalogRow,
) -> tuple[str, str, str, str | None, str | None]:
    return (row.market, row.make_key, row.model_key, row.generation, row.body_code)

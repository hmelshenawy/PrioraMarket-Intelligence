"""StorageAdapter interface (FR-050..052).

The ingestion pipeline depends only on this interface. The CSV
implementation lives in ``csv_storage.py``; a future database adapter can
replace it without touching ingestion logic (SC-008). Contract tests
verify any conforming adapter behaves identically.
"""

from __future__ import annotations

from datetime import datetime
from typing import Iterable, Protocol, runtime_checkable

from src.common.models import (
    BackfillListingCandidate,
    CatalogSyncReport,
    Listing,
    ListingRow,
    MarketplaceSourceRow,
    NormalizationStatisticsReport,
    RawListing,
    RunContext,
    RunReport,
    RunRow,
    SnapshotRow,
    VehicleReferenceCatalogRow,
)


class MarketplaceSourceNotFoundError(Exception):
    """Raised when a seeded marketplace source cannot be resolved."""


@runtime_checkable
class StorageAdapter(Protocol):
    """Persistence boundary for RawListings, Listings, and run reports."""

    def write_raw(self, raw_listings: Iterable[RawListing]) -> int:
        """Persist RawListings (verbatim). Returns number written."""
        ...

    def write_listings(self, listings: Iterable[Listing]) -> int:
        """Persist canonicalized Listings. Returns number written."""
        ...

    def write_report(self, report: RunReport) -> None:
        """Persist a RunReport artifact."""
        ...

    def read_raw(self, dataset_version: str | None = None) -> Iterable[RawListing]:
        """Return stored RawListings (for replay). No marketplace access."""
        ...

    def resolve_marketplace_source_by_code(self, code: str) -> MarketplaceSourceRow:
        """Return an existing seeded MarketplaceSource by code; never create one."""
        raise MarketplaceSourceNotFoundError(code)

    def find_listing_by_source_uuid(self, source: str, uuid: str) -> ListingRow | None:
        return None

    def insert_listing(self, row: ListingRow) -> int:
        return 0

    def insert_raw_listing(self, raw: RawListing, ctx: RunContext) -> int:
        return 0

    def update_listing(self, listing_id: int, row: ListingRow) -> None:
        return None

    def insert_snapshot(self, snap: SnapshotRow) -> int:
        return 0

    def resolve_run(self, run_name_or_id: str) -> RunRow | None:
        return None

    def read_raw_for_run(self, run_name_or_id: str) -> Iterable[RawListing]:
        return ()

    def insert_ingestion_run(self, run: RunRow) -> int:
        return 0

    def finalize_ingestion_run(
        self, run_id: int, report: RunReport, status: str, completed_at: datetime
    ) -> None:
        return None

    def begin_listing_unit(self) -> None:
        return None

    def commit_listing_unit(self) -> None:
        return None

    def rollback_listing_unit(self) -> None:
        return None

    def find_vehicle_reference_catalog(
        self, market: str, make_key: str, model_key: str | None = None
    ) -> list[VehicleReferenceCatalogRow]:
        return []

    def upsert_vehicle_reference_catalog(
        self, rows: Iterable[VehicleReferenceCatalogRow], source_file: str
    ) -> CatalogSyncReport:
        return CatalogSyncReport(source_file=source_file)

    def write_normalization_statistics(self, report: NormalizationStatisticsReport) -> None:
        return None

    def read_listing_backfill_candidates(
        self, batch_size: int, after_id: int | None = None
    ) -> Iterable[BackfillListingCandidate]:
        return ()

    def update_listing_backfill_payload(
        self,
        listing_id: int,
        canonical_payload: dict,
        canonical_hash: str,
        normalization_version: str,
        canonicalization_version: str,
    ) -> None:
        return None

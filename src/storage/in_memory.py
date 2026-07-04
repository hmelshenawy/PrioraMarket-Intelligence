"""In-memory StorageAdapter (US4, T036).

A substitute adapter proving the ingestion pipeline is storage-pluggable
(SC-008): swapping the CSV adapter for this one must not change ingestion
behavior. Also used by tests that need a non-filesystem storage.
"""

from __future__ import annotations

from datetime import datetime
from typing import Iterable, Iterator, List

from src.common.models import (
    Listing,
    ListingRow,
    RawListing,
    RunContext,
    RunReport,
    RunRow,
    SnapshotRow,
)
from src.storage.interface import MarketplaceSourceNotFoundError


class InMemoryStorageAdapter:
    """StorageAdapter that keeps everything in process memory."""

    def __init__(self):
        self.raw: List[RawListing] = []
        self.listings: List[Listing] = []
        self.report: RunReport | None = None

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

    def read_raw(self, dataset_version: str | None = None) -> Iterator[RawListing]:
        # In-memory: dataset_version is ignored (no filesystem layout).
        yield from self.raw

    def resolve_marketplace_source_by_code(self, code: str):
        raise MarketplaceSourceNotFoundError(code)

    def find_listing_by_source_uuid(self, source: str, uuid: str) -> ListingRow | None:
        return None

    def insert_listing(self, row: ListingRow) -> int:
        return len(self.listings) + 1

    def insert_raw_listing(self, raw: RawListing, ctx: RunContext) -> int:
        self.raw.append(raw)
        return len(self.raw)

    def update_listing(self, listing_id: int, row: ListingRow) -> None:
        return None

    def insert_snapshot(self, snap: SnapshotRow) -> int:
        return 0

    def resolve_run(self, run_name_or_id: str) -> RunRow | None:
        return None

    def read_raw_for_run(self, run_name_or_id: str) -> Iterator[RawListing]:
        yield from self.raw

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

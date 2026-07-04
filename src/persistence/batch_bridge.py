"""Batch-to-per-listing bridge for PostgreSQL ingestion persistence.

The Feature 001 pipeline writes storage in batches. This bridge preserves that
boundary while adapting the PostgreSQL backend to PersistenceService's
per-listing transaction flow.
"""

from __future__ import annotations

from datetime import datetime
from typing import Iterable, Iterator

from src.common.models import Listing, RawListing, RunReport, Scope

PairKey = tuple[str, str]


class PersistenceBatchBridge:
    """StorageAdapter-compatible shim used only by the PostgreSQL runner path."""

    def __init__(
        self,
        service,
        scope: Scope,
        config_snapshot: dict,
        run_started_at: datetime,
        marketplace_source_code: str,
    ):
        self._service = service
        self._scope = scope
        self._config_snapshot = dict(config_snapshot)
        self._run_started_at = run_started_at
        self._marketplace_source_code = marketplace_source_code
        self._raw: list[RawListing] = []
        self._listings: list[Listing] = []
        self.unmatched_raw_keys: list[PairKey] = []
        self.unmatched_listing_keys: list[PairKey] = []

    def write_raw(self, raw_listings: Iterable[RawListing]) -> int:
        items = list(raw_listings)
        self._raw.extend(items)
        return len(items)

    def write_listings(self, listings: Iterable[Listing]) -> int:
        items = list(listings)
        self._listings.extend(items)
        return len(items)

    def write_report(self, report: RunReport) -> None:
        ctx = self._service.begin_run(
            self._scope,
            self._config_snapshot,
            self._run_started_at,
            self._marketplace_source_code,
        )
        raw_by_key = {self._raw_key(raw): raw for raw in self._raw if self._raw_key(raw)}
        listing_by_key = {
            self._listing_key(listing): listing
            for listing in self._listings
            if self._listing_key(listing)
        }

        raw_keys = set(raw_by_key)
        listing_keys = set(listing_by_key)
        self.unmatched_raw_keys = sorted(raw_keys - listing_keys)
        self.unmatched_listing_keys = sorted(listing_keys - raw_keys)

        for key in sorted(raw_keys & listing_keys):
            self._service.persist_listing(ctx, raw_by_key[key], listing_by_key[key])

        unmatched_count = len(self.unmatched_raw_keys) + len(self.unmatched_listing_keys)
        if unmatched_count:
            report.listings_skipped += unmatched_count
            report.failures += unmatched_count
        self._service.finalize_run(ctx, report)

    def read_raw(self, dataset_version: str | None = None) -> Iterator[RawListing]:
        yield from self._raw

    @staticmethod
    def _raw_key(raw: RawListing) -> PairKey | None:
        if not raw.marketplace or not raw.uuid:
            return None
        return (raw.marketplace, raw.uuid)

    @staticmethod
    def _listing_key(listing: Listing) -> PairKey | None:
        if not listing.marketplace or not listing.uuid:
            return None
        return (listing.marketplace, listing.uuid)

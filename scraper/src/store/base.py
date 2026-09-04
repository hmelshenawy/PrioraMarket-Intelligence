"""Storage interface (FR-050..052).

The ingestion pipeline and canonicalization engine depend only on these
five methods. PostgreSQL persistence is ``store/postgres.py``; CSV run
artifacts are the debug backend in ``store/csv_store.py``.
"""

from __future__ import annotations

from typing import Iterable, Protocol, runtime_checkable

from src.models import (
    Listing,
    NormalizationStatisticsReport,
    RawListing,
    RunReport,
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

    def find_vehicle_reference_catalog(
        self, market: str, make_key: str, model_key: str | None = None
    ) -> list[VehicleReferenceCatalogRow]:
        """Look up Vehicle Reference Catalog rows for canonicalization."""
        ...

    def write_normalization_statistics(self, report: NormalizationStatisticsReport) -> None:
        """Persist operational normalization statistics."""
        ...

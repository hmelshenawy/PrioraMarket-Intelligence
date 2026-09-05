"""Domain models: raw capture, derived listing, and small row DTOs."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass(frozen=True)
class RawListing:
    """The original marketplace listing exactly as received.

    Immutable. The raw_payload is preserved verbatim — no transformation,
    truncation, or enrichment. Ground truth for all downstream derivation.
    """

    marketplace: str
    marketplace_listing_id: str | None
    uuid: str | None
    raw_payload: dict[str, Any]
    extracted_fields: dict[str, Any]
    fetched_at: datetime
    scrape_run_id: str
    condition: str
    make_slug: str | None


@dataclass
class Listing:
    """Platform-internal, marketplace-independent listing (derived).

    Produced by normalize() from a RawListing; business values arrive
    canonicalized. Never received directly from a marketplace.
    """

    uuid: str | None
    marketplace: str
    marketplace_listing_id: str | None
    make: str | None = None
    model: str | None = None
    trim: str | None = None
    trim_source: str = "unknown"
    condition: str | None = None
    price: float | None = None
    currency: str = "AED"
    year: int | None = None
    kilometers: float | None = None
    fuel_type: str | None = None
    transmission: str | None = None
    regional_spec: str | None = None
    body_type: str | None = None
    seller_type: str | None = None
    vehicle_condition: str | None = None
    specs: str | None = None
    color: str | None = None
    location: str | None = None
    photos_count: int = 0
    source_url: str | None = None
    fetched_at: datetime | None = None
    normalization_version: str | None = None
    canonicalization_version: str | None = None


@dataclass(frozen=True)
class VehicleReferenceCatalogRow:
    """Storage DTO for a Vehicle Reference Catalog row."""

    id: int | None
    market: str
    make_key: str
    make_display: str
    model_key: str
    model_display: str
    generation: str | None = None
    body_code: str | None = None
    start_year: int | None = None
    end_year: int | None = None
    facelift_start_year: int | None = None
    facelift_end_year: int | None = None
    aliases: dict[str, Any] = field(default_factory=dict)
    confidence: str = "manual"
    source_file: str | None = None
    source_row_hash: str | None = None
    last_synced_at: datetime | None = None


@dataclass(frozen=True)
class BackfillListingCandidate:
    """Minimal existing listing data needed for canonical backfill."""

    id: int
    source: str
    uuid: str
    canonical_payload: dict[str, Any]
    normalization_version: str | None = None
    current_raw_listing_id: int | None = None


@dataclass(frozen=True)
class CatalogSyncReport:
    """Summary emitted by Vehicle Reference Catalog synchronization."""

    source_file: str
    inserted: int = 0
    updated: int = 0
    unchanged: int = 0
    rejected: int = 0
    conflicts: int = 0
    synced_at: datetime | None = None

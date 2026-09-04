"""Storage-row models: DTOs exchanged with the persistence layer."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from src.models.run import Scope


@dataclass(frozen=True)
class MarketplaceSourceRow:
    """Seeded marketplace reference data resolved by persistence services."""

    id: int
    code: str
    name: str
    country: str
    base_url: str


@dataclass
class RunRow:
    """Storage DTO for an IngestionRun row."""

    id: int | None
    name: str
    marketplace_source_id: int
    marketplace: str
    condition: str
    make: str
    status: str
    started_at: datetime
    completed_at: datetime | None = None
    pages_scraped: int = 0
    listings_extracted: int = 0
    listings_skipped: int = 0
    failures_count: int = 0
    duration_ms: int | None = None
    config_snapshot: dict[str, Any] = field(default_factory=dict)
    report_json: dict[str, Any] | None = None


@dataclass
class ListingRow:
    """Storage DTO for the current canonical Listing row."""

    id: int | None
    marketplace_source_id: int
    source: str
    uuid: str
    canonical_payload: dict[str, Any]
    canonical_hash: str
    normalization_version: str
    first_seen_at: datetime
    last_seen_at: datetime
    first_seen_run_id: int
    last_seen_run_id: int
    current_raw_listing_id: int | None = None
    status: str = "ACTIVE"


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
class RunContext:
    """Resolved run context used by PersistenceService."""

    run_id: int
    run_name: str
    marketplace_source_id: int
    scope: Scope


@dataclass(frozen=True)
class PersistOutcome:
    """Result of persisting one listing."""

    created: bool = False
    updated: bool = False
    snapshot_created: bool = False
    skipped: bool = False
    reason: str | None = None

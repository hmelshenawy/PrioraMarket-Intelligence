"""Domain models for the Data Ingestion Foundation pipeline.

These types are the platform's marketplace-independent internal
representation. RawListing is immutable and preserved verbatim; Listing
is a derived, canonicalizable projection. See data-model.md.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Optional


class RunState(str, Enum):
    """Pipeline state machine states (spec: Pipeline State Machine)."""

    CREATED = "CREATED"
    RUNNING = "RUNNING"
    FETCHING = "FETCHING"
    NORMALIZING = "NORMALIZING"
    CANONICALIZING = "CANONICALIZING"
    VALIDATING = "VALIDATING"
    STORING = "STORING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    PARTIAL_FAILED = "PARTIAL_FAILED"

    @property
    def is_terminal(self) -> bool:
        return self in {RunState.COMPLETED, RunState.FAILED, RunState.PARTIAL_FAILED}


@dataclass(frozen=True)
class RawListing:
    """The original marketplace listing exactly as received.

    Immutable. The raw_payload is preserved verbatim — no transformation,
    truncation, or enrichment. Ground truth for all downstream derivation.
    """

    marketplace: str
    marketplace_listing_id: Optional[str]
    uuid: Optional[str]
    raw_payload: dict[str, Any]
    extracted_fields: dict[str, Any]
    fetched_at: datetime
    scrape_run_id: str
    condition: str
    make_slug: Optional[str]


@dataclass
class Listing:
    """Platform-internal, marketplace-independent listing (derived).

    Produced by the normalizer from a RawListing; business values are
    canonicalized by the canonicalizer. Never received directly from a
    marketplace.
    """

    uuid: Optional[str]
    marketplace: str
    marketplace_listing_id: Optional[str]
    make: Optional[str] = None
    model: Optional[str] = None
    condition: Optional[str] = None
    price: Optional[float] = None
    currency: str = "AED"
    year: Optional[int] = None
    kilometers: Optional[float] = None
    fuel_type: Optional[str] = None
    transmission: Optional[str] = None
    regional_spec: Optional[str] = None
    body_type: Optional[str] = None
    seller_type: Optional[str] = None
    location: Optional[str] = None
    photos_count: int = 0
    source_url: Optional[str] = None
    fetched_at: Optional[datetime] = None
    normalization_version: Optional[str] = None
    dataset_version: Optional[str] = None
    lineage: dict[str, Any] = field(default_factory=dict)

    def with_canonical(
        self,
        make: Optional[str] = None,
        model: Optional[str] = None,
        fuel_type: Optional[str] = None,
        transmission: Optional[str] = None,
        regional_spec: Optional[str] = None,
        body_type: Optional[str] = None,
    ) -> "Listing":
        """Return a copy with canonicalized business values (FR-043..045)."""
        import dataclasses

        replaced = dataclasses.replace(self)
        if make is not None:
            replaced.make = make
        if model is not None:
            replaced.model = model
        if fuel_type is not None:
            replaced.fuel_type = fuel_type
        if transmission is not None:
            replaced.transmission = transmission
        if regional_spec is not None:
            replaced.regional_spec = regional_spec
        if body_type is not None:
            replaced.body_type = body_type
        return replaced

    def to_record(self) -> dict[str, Any]:
        """Flatten to a CSV/JSON-friendly record."""
        rec = {
            "uuid": self.uuid,
            "marketplace": self.marketplace,
            "marketplace_listing_id": self.marketplace_listing_id,
            "make": self.make,
            "model": self.model,
            "condition": self.condition,
            "price": self.price,
            "currency": self.currency,
            "year": self.year,
            "kilometers": self.kilometers,
            "fuel_type": self.fuel_type,
            "transmission": self.transmission,
            "regional_spec": self.regional_spec,
            "body_type": self.body_type,
            "seller_type": self.seller_type,
            "location": self.location,
            "photos_count": self.photos_count,
            "source_url": self.source_url,
            "fetched_at": self.fetched_at.isoformat() if self.fetched_at else None,
            "normalization_version": self.normalization_version,
            "dataset_version": self.dataset_version,
        }
        rec.update(self.lineage)
        return rec


@dataclass
class ValidationResult:
    """Outcome of validating a canonicalized listing (FR-030..033)."""

    listing_uuid: Optional[str]
    accepted: bool
    reason: Optional[str] = None
    missing_fields: list[str] = field(default_factory=list)
    duplicate: bool = False
    duplicate_of: Optional[str] = None


@dataclass
class IngestionRun:
    """A single execution scoped by marketplace, condition, make."""

    run_id: str
    marketplace: str
    condition: str
    make: str
    normalization_version: str
    dataset_version: Optional[str] = None
    state: RunState = RunState.CREATED
    started_at: Optional[datetime] = None
    ended_at: Optional[datetime] = None
    config_snapshot: dict[str, Any] = field(default_factory=dict)


@dataclass
class DatasetVersion:
    """Identifies the data produced by a successful run (concept only)."""

    identifier: str
    scrape_run_id: str
    marketplace: str
    execution_timestamp: datetime
    ingestion_config: dict[str, Any]
    normalization_version: str

    @staticmethod
    def build(run: IngestionRun, sequence: int) -> "DatasetVersion":
        ts = run.started_at or datetime.utcnow()
        identifier = f"dataset_{ts.strftime('%Y_%m_%d')}_{sequence:03d}"
        return DatasetVersion(
            identifier=identifier,
            scrape_run_id=run.run_id,
            marketplace=run.marketplace,
            execution_timestamp=ts,
            ingestion_config=dict(run.config_snapshot),
            normalization_version=run.normalization_version,
        )


@dataclass
class NormalizationVersion:
    """Identifies the normalization + canonicalization ruleset."""

    identifier: str
    normalizer_ruleset: str
    canonical_mapping_version: str


@dataclass
class FetchMetrics:
    """Per-run fetch counters maintained by the marketplace adapter."""

    pages_processed: int = 0
    retry_count: int = 0
    fetch_duration_seconds: float = 0.0
    failures: int = 0


@dataclass
class RunReport:
    """Structured outcome of a run (FR-061/063/064)."""

    run_id: str
    state: RunState
    marketplace: str
    condition: str
    make: str
    dataset_version: Optional[str]
    normalization_version: str

    # Basic metrics (FR-061)
    pages_processed: int = 0
    listings_extracted: int = 0
    listings_skipped: int = 0
    execution_duration_seconds: float = 0.0
    failures: int = 0

    # Extended metrics (FR-063)
    retry_count: int = 0
    duplicate_count: int = 0
    validation_failures: int = 0
    pages_per_second: float = 0.0
    listings_per_second: float = 0.0
    fetch_duration_seconds: float = 0.0
    processing_duration_seconds: float = 0.0
    storage_duration_seconds: float = 0.0

    # Optional operational metrics (FR-064)
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    total_duration_seconds: Optional[float] = None
    peak_memory: Optional[int] = None
    peak_cpu: Optional[float] = None

    # Failure recovery: where execution stopped
    last_successful_page: Optional[int] = None
    failing_page: Optional[int] = None
    failing_stage: Optional[str] = None

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        d["state"] = self.state.value
        return d


@dataclass
class Scope:
    """An ingestion scope."""

    marketplace: str
    condition: str
    make: str


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


@dataclass
class SnapshotRow:
    """Storage DTO for an append-only ListingSnapshot row."""

    listing_id: int
    ingestion_run_id: int
    raw_listing_id: int | None
    snapshot_hash: str
    canonical_payload: dict[str, Any]
    changed_fields: list[str]
    captured_at: datetime


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

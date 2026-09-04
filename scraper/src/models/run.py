"""Run-domain models: state machine, scope, and run reporting."""

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


@dataclass
class Scope:
    """An ingestion scope."""

    marketplace: str
    condition: str
    make: str


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

    # Failure recovery: where execution stopped
    last_successful_page: Optional[int] = None
    failing_page: Optional[int] = None
    failing_stage: Optional[str] = None

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        d["state"] = self.state.value
        return d

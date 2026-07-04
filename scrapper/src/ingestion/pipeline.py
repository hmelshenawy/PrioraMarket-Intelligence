"""Pipeline orchestration (FR-008, FR-009, FR-023, FR-061).

Drives a single ingestion scope through the domain pipeline:
MarketplaceAdapter -> Normalizer -> Canonicalizer -> Validator ->
StorageAdapter, recording state transitions and basic metrics into a
RunReport. US1 ships the happy-path state machine; US2/US3 harden failure
isolation and the validation gate on top of this structure.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional

from src.common.logger import get_logger
from src.common.models import (
    DatasetVersion,
    IngestionRun,
    Listing,
    RawListing,
    RunReport,
    RunState,
    Scope,
)
from src.common.validation import MinimalValidator, Validator
from src.config.config import Config
from src.ingestion.canonicalizer import Canonicalizer
from src.ingestion.normalizer import Normalizer
from src.marketplaces.adapter_interface import MarketplaceAdapter
from src.reporting.run_report import finalize
from src.storage.interface import StorageAdapter


@dataclass
class PipelineResult:
    report: RunReport
    accepted: list[Listing] = field(default_factory=list)
    raw: list[RawListing] = field(default_factory=list)


class IngestionPipeline:
    """Orchestrates one scoped ingestion run."""

    def __init__(
        self,
        config: Config,
        adapter: MarketplaceAdapter,
        storage: StorageAdapter,
        normalizer: Optional[Normalizer] = None,
        canonicalizer: Optional[Canonicalizer] = None,
        validator: Optional[MinimalValidator] = None,
    ):
        self._config = config
        self._adapter = adapter
        self._storage = storage
        self._normalizer = normalizer or Normalizer(config.normalization_version)
        self._canonicalizer = canonicalizer or Canonicalizer()
        # US3: default to the full validation gate; US1 tests pass a
        # MinimalValidator explicitly where happy-path behavior is needed.
        self._validator = validator or Validator()
        self._log = get_logger("pipeline")

    def run(self, scope: Scope, run_id: str) -> PipelineResult:
        started = datetime.now(timezone.utc)
        t0 = time.monotonic()
        run = IngestionRun(
            run_id=run_id,
            marketplace=scope.marketplace,
            condition=scope.condition,
            make=scope.make,
            normalization_version=self._normalizer.normalization_version,
            started_at=started,
            config_snapshot=self._config.snapshot(),
        )
        if hasattr(self._adapter, "set_run_id"):
            self._adapter.set_run_id(run_id)

        report = RunReport(
            run_id=run_id,
            state=RunState.RUNNING,
            marketplace=scope.marketplace,
            condition=scope.condition,
            make=scope.make,
            dataset_version=None,
            normalization_version=self._normalizer.normalization_version,
        )

        raw_all: list[RawListing] = []
        accepted: list[Listing] = []
        listings_skipped = 0
        failures = 0
        last_successful_page: Optional[int] = None
        failing_page: Optional[int] = None
        failing_stage: Optional[str] = None

        try:
            report.state = RunState.FETCHING
            fetch_t0 = time.monotonic()
            for page_listings, meta in self._adapter.fetch(scope):
                report.pages_processed += 1
                try:
                    if not page_listings and meta.retried:
                        failures += 1
                        failing_page = meta.page
                        self._log.info(
                            "page yielded no listings after retries",
                            extra={"page": meta.page, "stage": "fetching"},
                        )
                        continue
                    raw_all.extend(page_listings)
                    last_successful_page = meta.page
                except Exception as exc:  # isolate per-page failures (US2)
                    failures += 1
                    failing_page = meta.page
                    failing_stage = "fetching"
                    self._log.warning(
                        "page failed, isolating",
                        extra={"page": meta.page, "error": str(exc)},
                    )
            report.fetch_duration_seconds = round(time.monotonic() - fetch_t0, 3)

            report.state = RunState.NORMALIZING
            norm_t0 = time.monotonic()
            normalized: list[Listing] = []
            for r in raw_all:
                try:
                    normalized.append(self._normalizer.normalize(r, scope))
                except Exception as exc:  # isolate per-record failures (US2)
                    listings_skipped += 1
                    failures += 1
                    failing_stage = "normalizing"
                    self._log.warning(
                        "record skipped during normalization",
                        extra={"uuid": r.uuid, "error": str(exc)},
                    )
            report.processing_duration_seconds = round(time.monotonic() - norm_t0, 3)

            report.state = RunState.CANONICALIZING
            if self._config.enable_canonicalization:
                canonicalized: list[Listing] = []
                for listing in normalized:
                    try:
                        canonicalized.append(self._canonicalizer.canonicalize(listing))
                    except Exception as exc:  # isolate per-record failures
                        listings_skipped += 1
                        failures += 1
                        failing_stage = "canonicalizing"
                        self._log.warning(
                            "record skipped during canonicalization",
                            extra={"uuid": listing.uuid, "error": str(exc)},
                        )
                normalized = canonicalized

            report.state = RunState.VALIDATING
            for listing in normalized:
                result = self._validator.validate(listing)
                if result.accepted:
                    accepted.append(listing)
                else:
                    listings_skipped += 1
                    report.validation_failures += 1
                    self._log.info(
                        "listing skipped",
                        extra={
                            "uuid": result.listing_uuid,
                            "reason": result.reason,
                            "stage": "validation",
                        },
                    )

            # Run-level UUID deduplication (FR-033): newest occurrence wins.
            if hasattr(self._validator, "dedup"):
                accepted, dup_count = self._validator.dedup(accepted)
                report.duplicate_count = dup_count
                listings_skipped += dup_count

            report.state = RunState.STORING
            store_t0 = time.monotonic()
            self._storage.write_raw(raw_all)
            if self._config.enable_csv_storage:
                self._storage.write_listings(accepted)
            report.storage_duration_seconds = round(time.monotonic() - store_t0, 3)

            # Dataset version + lineage assignment (FR-023).
            dataset = DatasetVersion.build(run, sequence=1)
            for listing in accepted:
                listing.dataset_version = dataset.identifier
            run.dataset_version = dataset.identifier
            report.dataset_version = dataset.identifier

            report.listings_extracted = len(accepted)
            report.listings_skipped = listings_skipped
            report.failures = failures
            if hasattr(self._adapter, "retry_count"):
                report.retry_count = getattr(self._adapter, "retry_count", 0)
            # Terminal state: PARTIAL_FAILED if some failures but data produced;
            # FAILED if a fatal exception propagated; otherwise COMPLETED.
            if failures > 0 and accepted:
                report.state = RunState.PARTIAL_FAILED
            else:
                report.state = RunState.COMPLETED
        except Exception as exc:
            report.state = RunState.FAILED
            report.failures = failures + 1
            failing_stage = failing_stage or "unknown"
            self._log.error("pipeline failed", extra={"error": str(exc)})
            raise
        finally:
            report.execution_duration_seconds = round(time.monotonic() - t0, 3)
            report.start_time = started.isoformat()
            report.end_time = datetime.now(timezone.utc).isoformat()
            report.last_successful_page = last_successful_page
            report.failing_page = failing_page
            report.failing_stage = failing_stage
            finalize(report)
            self._storage.write_report(report)

        return PipelineResult(report=report, accepted=accepted, raw=raw_all)

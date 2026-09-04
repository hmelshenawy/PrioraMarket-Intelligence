"""Canonical listing backfill using the shared canonicalization engine."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable

from src.hashing import canonical_hash, canonical_payload
from src.models import BackfillListingCandidate, Listing, NormalizationStatisticsReport
from src.normalize.canonical import (
    DEFAULT_CANONICALIZATION_VERSION,
    CanonicalizationEngine,
)
from src.store.base import StorageAdapter


@dataclass
class CanonicalBackfillReport:
    dry_run: bool
    batch_size: int
    resume_after_id: int | None
    canonicalization_version: str
    scanned: int = 0
    changed: int = 0
    unchanged: int = 0
    updated: int = 0
    skipped: int = 0
    failures: int = 0
    last_processed_id: int | None = None
    failed_ids: list[int] = field(default_factory=list)
    progress: list[str] = field(default_factory=list)
    statistics: NormalizationStatisticsReport | None = None


ProgressCallback = Callable[[str], None]


class CanonicalBackfillService:
    """Backfill existing listing canonical fields without touching raw listings."""

    def __init__(
        self,
        storage: StorageAdapter,
        *,
        canonicalization_version: str = DEFAULT_CANONICALIZATION_VERSION,
        market: str = "global",
        progress: ProgressCallback | None = None,
    ):
        self.storage = storage
        self.engine = CanonicalizationEngine(
            storage=storage,
            version=canonicalization_version,
            market=market,
            operation="backfill",
        )
        self.progress = progress

    def run(
        self,
        *,
        dry_run: bool,
        batch_size: int = 500,
        resume_after_id: int | None = None,
    ) -> CanonicalBackfillReport:
        if batch_size < 1:
            raise ValueError("batch_size must be at least 1")

        report = CanonicalBackfillReport(
            dry_run=dry_run,
            batch_size=batch_size,
            resume_after_id=resume_after_id,
            canonicalization_version=self.engine.version,
        )
        after_id = resume_after_id
        while True:
            batch = list(self.storage.read_listing_backfill_candidates(batch_size, after_id))
            if not batch:
                break
            for candidate in batch:
                self._process_candidate(candidate, report, dry_run)
                after_id = candidate.id
                report.last_processed_id = candidate.id
            self._progress(report, f"processed through listing_id={after_id}")
            if len(batch) < batch_size:
                break

        report.statistics = self.engine.report()
        self.storage.write_normalization_statistics(report.statistics)
        self._progress(
            report,
            "backfill complete: "
            f"scanned={report.scanned} changed={report.changed} updated={report.updated} "
            f"unchanged={report.unchanged} skipped={report.skipped} failures={report.failures}",
        )
        return report

    def _process_candidate(
        self, candidate: BackfillListingCandidate, report: CanonicalBackfillReport, dry_run: bool
    ) -> None:
        report.scanned += 1
        try:
            listing = _listing_from_candidate(candidate, self.engine.version)
            canonical = self.engine.canonicalize_listing(listing)
            new_payload = canonical_payload(canonical)
            old_payload = dict(candidate.canonical_payload)
            if _canonical_fields(old_payload) == _canonical_fields(new_payload):
                report.unchanged += 1
                return
            report.changed += 1
            if dry_run:
                return
            self.storage.update_listing_backfill_payload(
                candidate.id,
                old_payload | new_payload,
                canonical_hash(old_payload | new_payload),
                canonical.normalization_version or candidate.normalization_version or "unknown",
                canonical.canonicalization_version or self.engine.version,
            )
            report.updated += 1
        except Exception:
            report.failures += 1
            report.failed_ids.append(candidate.id)

    def _progress(self, report: CanonicalBackfillReport, message: str) -> None:
        report.progress.append(message)
        if self.progress is not None:
            self.progress(message)


def _listing_from_candidate(candidate: BackfillListingCandidate, version: str) -> Listing:
    payload = candidate.canonical_payload
    return Listing(
        uuid=candidate.uuid,
        marketplace=candidate.source,
        marketplace_listing_id=candidate.uuid,
        make=payload.get("make"),
        model=payload.get("model"),
        trim=payload.get("trim"),
        condition=payload.get("condition"),
        fuel_type=payload.get("fuel_type"),
        transmission=payload.get("transmission"),
        regional_spec=payload.get("regional_spec"),
        body_type=payload.get("body_type"),
        seller_type=payload.get("seller_type"),
        vehicle_condition=payload.get("vehicle_condition"),
        specs=payload.get("specs"),
        color=payload.get("color"),
        normalization_version=payload.get("normalization_version")
        or candidate.normalization_version,
        canonicalization_version=version,
    )


def _canonical_fields(payload: dict) -> dict:
    fields = {
        "make",
        "model",
        "trim",
        "condition",
        "fuel_type",
        "transmission",
        "regional_spec",
        "body_type",
        "seller_type",
        "vehicle_condition",
        "specs",
        "color",
        "canonicalization_version",
    }
    return {key: payload.get(key) for key in fields}

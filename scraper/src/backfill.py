"""Canonical listing backfill: re-canonicalize existing listing rows.

Reuses the same canonicalization functions as normalization, applied to
Listing rows already in PostgreSQL. Raw listings are never touched.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from src.hashing import canonical_hash, canonical_payload
from src.models import BackfillListingCandidate, Listing
from src.normalize import DEFAULT_CANONICALIZATION_VERSION, canonicalize_listing
from src.store import backfill_repo, catalog_repo


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


class CanonicalBackfillService:
    """Backfill existing listing canonical fields without touching raw listings."""

    def __init__(
        self,
        conn,
        *,
        canonicalization_version: str = DEFAULT_CANONICALIZATION_VERSION,
        market: str = "global",
    ):
        self.conn = conn
        self.canonicalization_version = canonicalization_version
        self.market = market

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
            canonicalization_version=self.canonicalization_version,
        )

        def catalog(make_key, model_key):
            return catalog_repo.find_vehicle_reference_catalog(
                self.conn, self.market, make_key, model_key
            )

        after_id = resume_after_id
        while True:
            batch = list(
                backfill_repo.read_listing_backfill_candidates(self.conn, batch_size, after_id)
            )
            if not batch:
                break
            for candidate in batch:
                self._process_candidate(candidate, report, dry_run, catalog)
                after_id = candidate.id
                report.last_processed_id = after_id
            if len(batch) < batch_size:
                break

        return report

    def _process_candidate(
        self,
        candidate: BackfillListingCandidate,
        report: CanonicalBackfillReport,
        dry_run: bool,
        catalog,
    ) -> None:
        report.scanned += 1
        try:
            listing = _listing_from_candidate(candidate, self.canonicalization_version)
            canonicalize_listing(listing, catalog)
            new_payload = canonical_payload(listing)
            old_payload = dict(candidate.canonical_payload)
            if _canonical_fields(old_payload) == _canonical_fields(new_payload):
                report.unchanged += 1
                return
            report.changed += 1
            if dry_run:
                return
            merged = old_payload | new_payload
            backfill_repo.update_listing_backfill_payload(
                self.conn,
                candidate.id,
                merged,
                canonical_hash(merged),
                listing.normalization_version or candidate.normalization_version or "unknown",
                listing.canonicalization_version or self.canonicalization_version,
            )
            report.updated += 1
        except Exception:
            report.failures += 1
            report.failed_ids.append(candidate.id)


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

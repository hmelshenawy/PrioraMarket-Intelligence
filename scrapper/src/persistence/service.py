"""Business persistence rules for Feature 002."""

from __future__ import annotations

from datetime import datetime, timezone

from src.common.canonical_hash import canonical_hash, canonical_payload
from src.common.models import (
    Listing,
    ListingRow,
    NormalizationStatisticsReport,
    PersistOutcome,
    RawListing,
    RunContext,
    RunReport,
    RunRow,
    Scope,
)
from src.common.run_naming import build_run_name, collision_disambiguator
from src.storage.interface import MarketplaceSourceNotFoundError, StorageAdapter


class PersistenceError(Exception):
    """Base class for persistence-service domain errors."""


class MarketplaceSourceRequiredError(PersistenceError):
    """Raised when required seeded MarketplaceSource data is missing."""


class PersistenceService:
    """Owns persistence business rules; delegates storage operations to adapters."""

    def __init__(self, storage: StorageAdapter):
        self._storage = storage

    def begin_run(
        self,
        scope: Scope,
        config_snapshot: dict,
        run_started_at: datetime,
        marketplace_source_code: str,
    ) -> RunContext:
        try:
            source = self._storage.resolve_marketplace_source_by_code(marketplace_source_code)
        except MarketplaceSourceNotFoundError as exc:
            raise MarketplaceSourceRequiredError(
                f"MarketplaceSource {marketplace_source_code!r} is not seeded"
            ) from exc

        run_name = build_run_name(scope.marketplace, scope.condition, scope.make, run_started_at)
        if self._storage.resolve_run(run_name) is not None:
            run_name = build_run_name(
                scope.marketplace,
                scope.condition,
                scope.make,
                run_started_at,
                collision_disambiguator(
                    run_name,
                    f"{scope.marketplace}:{scope.condition}:{scope.make}",
                ),
            )

        run_id = self._storage.insert_ingestion_run(
            RunRow(
                id=None,
                name=run_name,
                marketplace_source_id=source.id,
                marketplace=scope.marketplace,
                condition=scope.condition,
                make=scope.make,
                status="RUNNING",
                started_at=run_started_at,
                config_snapshot=config_snapshot,
            )
        )
        return RunContext(
            run_id=run_id,
            run_name=run_name,
            marketplace_source_id=source.id,
            scope=scope,
        )

    def persist_listing(self, ctx: RunContext, raw: RawListing, listing: Listing) -> PersistOutcome:
        if not raw.uuid or not listing.uuid:
            return PersistOutcome(skipped=True, reason="missing uuid")

        self._storage.begin_listing_unit()
        try:
            raw_id = self._storage.insert_raw_listing(raw, ctx)
            existing = self._storage.find_listing_by_source_uuid(listing.marketplace, listing.uuid)
            payload = canonical_payload(listing)
            listing_hash = canonical_hash(payload)
            observed_at = raw.fetched_at or datetime.now(timezone.utc)
            row = ListingRow(
                id=existing.id if existing else None,
                marketplace_source_id=ctx.marketplace_source_id,
                source=listing.marketplace,
                uuid=listing.uuid,
                canonical_payload=payload,
                canonical_hash=listing_hash,
                normalization_version=listing.normalization_version or "unknown",
                first_seen_at=existing.first_seen_at if existing else observed_at,
                last_seen_at=observed_at,
                first_seen_run_id=existing.first_seen_run_id if existing else ctx.run_id,
                last_seen_run_id=ctx.run_id,
                current_raw_listing_id=raw_id,
                status="ACTIVE",
            )
            if existing is None:
                self._storage.insert_listing(row)
                outcome = PersistOutcome(created=True)
            else:
                self._storage.update_listing(existing.id or 0, row)
                outcome = PersistOutcome(updated=True)
            self._storage.commit_listing_unit()
            return outcome
        except Exception:
            self._storage.rollback_listing_unit()
            raise

    def finalize_run(self, ctx: RunContext, report: RunReport) -> None:
        completed_at = datetime.now(timezone.utc)
        self._storage.finalize_ingestion_run(ctx.run_id, report, report.state.value, completed_at)

    def resolve_run(self, run_name_or_id: str) -> RunContext | None:
        run = self._storage.resolve_run(run_name_or_id)
        if run is None or run.id is None:
            return None
        return RunContext(
            run_id=run.id,
            run_name=run.name,
            marketplace_source_id=run.marketplace_source_id,
            scope=Scope(run.marketplace, run.condition, run.make),
        )

    def load_raw_for_run(self, run_name_or_id: str):
        return self._storage.read_raw_for_run(run_name_or_id)

    def write_normalization_statistics(self, report: NormalizationStatisticsReport) -> None:
        self._storage.write_normalization_statistics(report)

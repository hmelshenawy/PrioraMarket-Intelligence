"""PostgreSQL store: run persistence and the ingestion batch facade.

PostgresStore is the only database entry point. The pipeline buffers raw
listings and accepted listings via the StorageAdapter methods, and
``write_report`` persists the whole run in one transactional pass
(resolve marketplace source -> ingestion_run row -> per-listing raw
insert + listing upsert -> finalize). Backfill and catalog sync call the
same store directly.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Iterable

from src.hashing import canonical_hash, canonical_payload
from src.logging_setup import get_logger
from src.models import (
    CatalogSyncReport,
    Listing,
    ListingRow,
    NormalizationStatisticsReport,
    PersistOutcome,
    RawListing,
    RunContext,
    RunReport,
    RunRow,
    RunState,
    Scope,
    VehicleReferenceCatalogRow,
)
from src.run_naming import build_run_name, collision_disambiguator
from src.store import backfill_repo, catalog_repo, listing_repo, run_repo
from src.store.base import MarketplaceSourceNotFoundError

logger = get_logger("prioramarket.store.postgres")


class StorageSchemaError(Exception):
    """Raised when required PostgreSQL schema objects are missing."""


class StorageConstraintError(Exception):
    """Raised for database constraint violations surfaced to services."""


class MarketplaceSourceRequiredError(Exception):
    """Raised when required seeded MarketplaceSource data is missing."""


PairKey = tuple[str, str]


class PostgresStore:
    """Database-only persistence for ingestion, backfill, and catalog sync."""

    def __init__(
        self,
        pool,
        *,
        scope: Scope | None = None,
        config_snapshot: dict | None = None,
        run_started_at: datetime | None = None,
        marketplace_source_code: str | None = None,
    ):
        self._pool = pool
        self._scope = scope
        self._config_snapshot = dict(config_snapshot or {})
        self._run_started_at = run_started_at
        self._marketplace_source_code = marketplace_source_code
        self._raw: list[RawListing] = []
        self._listings: list[Listing] = []
        self._conn_cm = None
        self._conn = None
        self.unmatched_raw_keys: list[PairKey] = []
        self.unmatched_listing_keys: list[PairKey] = []

    # StorageAdapter facade ------------------------------------------------

    def write_raw(self, raw_listings: Iterable[RawListing]) -> int:
        items = list(raw_listings)
        self._raw.extend(items)
        return len(items)

    def write_listings(self, listings: Iterable[Listing]) -> int:
        items = list(listings)
        self._listings.extend(items)
        return len(items)

    def write_report(self, report: RunReport) -> None:
        self.persist_run(report)

    def write_normalization_statistics(self, report: NormalizationStatisticsReport) -> None:
        # Operational statistics stay in-memory; no statistics table exists.
        return None

    def find_vehicle_reference_catalog(
        self, market: str, make_key: str, model_key: str | None = None
    ) -> list[VehicleReferenceCatalogRow]:
        return catalog_repo.find_vehicle_reference_catalog(self, market, make_key, model_key)

    def upsert_vehicle_reference_catalog(
        self, rows: Iterable[VehicleReferenceCatalogRow], source_file: str
    ) -> CatalogSyncReport:
        return catalog_repo.upsert_vehicle_reference_catalog(self, rows, source_file)

    def read_listing_backfill_candidates(self, batch_size: int, after_id: int | None = None):
        return backfill_repo.read_listing_backfill_candidates(self, batch_size, after_id)

    def update_listing_backfill_payload(
        self,
        listing_id: int,
        canonical_payload: dict,
        canonical_hash: str,
        normalization_version: str,
        canonicalization_version: str,
    ) -> None:
        backfill_repo.update_listing_backfill_payload(
            self,
            listing_id,
            canonical_payload,
            canonical_hash,
            normalization_version,
            canonicalization_version,
        )

    # Run persistence ------------------------------------------------------

    def persist_run(self, report: RunReport) -> None:
        """Persist buffered raws + listings, then finalize the run row."""
        ctx = self.begin_run(
            self._scope, self._config_snapshot, self._run_started_at, self._marketplace_source_code
        )
        raw_by_key = {key: raw for raw in self._raw if (key := _pair_key(raw))}
        listing_by_key = {key: listing for listing in self._listings if (key := _pair_key(listing))}
        self.unmatched_raw_keys = sorted(set(raw_by_key) - set(listing_by_key))
        self.unmatched_listing_keys = sorted(set(listing_by_key) - set(raw_by_key))
        try:
            for key in sorted(set(raw_by_key) & set(listing_by_key)):
                self.persist_listing(ctx, raw_by_key[key], listing_by_key[key])
        except Exception:
            # Never leave the run stuck in RUNNING when persistence crashes.
            # Finalize best-effort on a fresh pooled connection; the original
            # error always wins.
            try:
                self._conn = None
                run_repo.finalize_run(
                    self, ctx.run_id, report, RunState.FAILED.value, datetime.now(timezone.utc)
                )
            except Exception:
                logger.exception("could not mark run %s as FAILED", ctx.run_id)
            raise
        unmatched_count = len(self.unmatched_raw_keys) + len(self.unmatched_listing_keys)
        if unmatched_count:
            report.listings_skipped += unmatched_count
            report.failures += unmatched_count
        run_repo.finalize_run(
            self, ctx.run_id, report, report.state.value, datetime.now(timezone.utc)
        )

    def begin_run(
        self,
        scope: Scope,
        config_snapshot: dict,
        run_started_at: datetime,
        marketplace_source_code: str,
    ) -> RunContext:
        try:
            source = run_repo.resolve_marketplace_source(self, marketplace_source_code)
            logger.info("connecting to database")
        except MarketplaceSourceNotFoundError as exc:
            raise MarketplaceSourceRequiredError(
                f"MarketplaceSource {marketplace_source_code!r} is not seeded"
            ) from exc

        run_name = build_run_name(scope.marketplace, scope.condition, scope.make, run_started_at)
        if run_repo.resolve_run(self, run_name) is not None:
            run_name = build_run_name(
                scope.marketplace,
                scope.condition,
                scope.make,
                run_started_at,
                collision_disambiguator(
                    run_name, f"{scope.marketplace}:{scope.condition}:{scope.make}"
                ),
            )

        run_id = run_repo.insert_run(
            self,
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
            ),
        )
        return RunContext(
            run_id=run_id,
            run_name=run_name,
            marketplace_source_id=source.id,
            scope=scope,
        )

    def resolve_run(self, run_name_or_id: str) -> RunRow | None:
        return run_repo.resolve_run(self, run_name_or_id)

    def persist_listing(self, ctx: RunContext, raw: RawListing, listing: Listing) -> PersistOutcome:
        """Insert the verbatim raw payload and upsert the current listing row."""
        if not raw.uuid or not listing.uuid:
            return PersistOutcome(skipped=True, reason="missing uuid")

        self.begin_listing_unit()
        try:
            raw_id = listing_repo.insert_raw_listing(self, raw, ctx)
            existing = listing_repo.find_by_source_uuid(self, listing.marketplace, listing.uuid)
            payload = canonical_payload(listing)
            observed_at = raw.fetched_at or datetime.now(timezone.utc)
            row = ListingRow(
                id=existing.id if existing else None,
                marketplace_source_id=ctx.marketplace_source_id,
                source=listing.marketplace,
                uuid=listing.uuid,
                canonical_payload=payload,
                canonical_hash=canonical_hash(payload),
                normalization_version=listing.normalization_version or "unknown",
                first_seen_at=existing.first_seen_at if existing else observed_at,
                last_seen_at=observed_at,
                first_seen_run_id=existing.first_seen_run_id if existing else ctx.run_id,
                last_seen_run_id=ctx.run_id,
                current_raw_listing_id=raw_id,
                status="ACTIVE",
            )
            if existing is None:
                listing_repo.insert_listing(self, row)
                outcome = PersistOutcome(created=True)
            else:
                listing_repo.update_listing(self, existing.id or 0, row)
                outcome = PersistOutcome(updated=True)
            self.commit_listing_unit()
            print("outcome!!:", outcome)
            return outcome
        except Exception:
            self.rollback_listing_unit()
            raise

    # Transaction + cursor plumbing ----------------------------------------

    def begin_listing_unit(self) -> None:
        if self._conn is not None:
            return
        self._conn_cm = self._pool.connection()
        self._conn = self._conn_cm.__enter__()
        self._conn.execute("BEGIN")

    def commit_listing_unit(self) -> None:
        if self._conn is None:
            return
        self._conn.commit()
        self._close_transaction_connection()

    def rollback_listing_unit(self) -> None:
        if self._conn is None:
            return
        self._conn.rollback()
        self._close_transaction_connection()

    def _close_transaction_connection(self) -> None:
        if self._conn_cm is not None:
            self._conn_cm.__exit__(None, None, None)
        self._conn_cm = None
        self._conn = None

    def _fetchone(self, sql: str, params: tuple = ()):
        return self._with_cursor(lambda cur: cur.execute(sql, params).fetchone())

    def _fetchall(self, sql: str, params: tuple = ()):
        return self._with_cursor(lambda cur: cur.execute(sql, params).fetchall())

    def _execute(self, sql: str, params: tuple = ()) -> None:
        self._with_cursor(lambda cur: cur.execute(sql, params))

    def _with_cursor(self, operation):
        try:
            from psycopg import errors
            from psycopg.rows import dict_row
        except Exception as exc:  # pragma: no cover - dependency/environment failure
            raise StorageSchemaError("psycopg is not installed") from exc

        try:
            if self._conn is not None:
                with self._conn.cursor(row_factory=dict_row) as cur:
                    return operation(cur)
            with self._pool.connection() as conn:
                with conn.cursor(row_factory=dict_row) as cur:
                    return operation(cur)
        except errors.UndefinedTable as exc:
            raise StorageSchemaError("PostgreSQL schema is missing; run migrations") from exc
        except errors.UniqueViolation as exc:
            raise StorageConstraintError(str(exc)) from exc

    @staticmethod
    def _json(value):
        from psycopg.types.json import Jsonb

        return Jsonb(value)


def _pair_key(obj) -> PairKey | None:
    """Reconciliation key shared by RawListing and Listing."""
    if not obj.marketplace or not obj.uuid:
        return None
    return (obj.marketplace, obj.uuid)

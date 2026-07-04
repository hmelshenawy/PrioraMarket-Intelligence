"""PostgreSQL StorageAdapter implementation for Feature 002."""

from __future__ import annotations

from datetime import datetime
from typing import Iterable, Iterator

from src.common.canonical_hash import canonical_hash
from src.common.models import (
    Listing,
    ListingRow,
    MarketplaceSourceRow,
    RawListing,
    RunContext,
    RunReport,
    RunRow,
    SnapshotRow,
)
from src.storage.interface import MarketplaceSourceNotFoundError


class StorageSchemaError(Exception):
    """Raised when required PostgreSQL schema objects are missing."""


class StorageConstraintError(Exception):
    """Raised for database constraint violations surfaced to services."""


class PostgresStorageAdapter:
    """Database-only adapter. Business persistence rules live in PersistenceService."""

    def __init__(self, pool):
        self._pool = pool
        self._conn_cm = None
        self._conn = None

    def write_raw(self, raw_listings: Iterable[RawListing]) -> int:
        return 0

    def write_listings(self, listings: Iterable[Listing]) -> int:
        return 0

    def write_report(self, report: RunReport) -> None:
        return None

    def read_raw(self, dataset_version: str | None = None) -> Iterator[RawListing]:
        return iter(())

    def resolve_marketplace_source_by_code(self, code: str) -> MarketplaceSourceRow:
        row = self._fetchone(
            """
            SELECT id, code, name, country, base_url
            FROM marketplace_source
            WHERE code = %s
            """,
            (code,),
        )
        if row is None:
            raise MarketplaceSourceNotFoundError(code)
        return MarketplaceSourceRow(
            id=row["id"],
            code=row["code"],
            name=row["name"],
            country=row["country"],
            base_url=row["base_url"],
        )

    def insert_ingestion_run(self, run: RunRow) -> int:
        row = self._fetchone(
            """
            INSERT INTO ingestion_run (
                name, marketplace_source_id, marketplace, condition, make, status,
                started_at, completed_at, pages_scraped, listings_extracted,
                listings_skipped, failures_count, duration_ms, config_snapshot, report_json
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id
            """,
            (
                run.name,
                run.marketplace_source_id,
                run.marketplace,
                run.condition,
                run.make,
                run.status,
                run.started_at,
                run.completed_at,
                run.pages_scraped,
                run.listings_extracted,
                run.listings_skipped,
                run.failures_count,
                run.duration_ms,
                self._json(run.config_snapshot),
                self._json(run.report_json) if run.report_json is not None else None,
            ),
        )
        return int(row["id"])

    def finalize_ingestion_run(
        self, run_id: int, report: RunReport, status: str, completed_at: datetime
    ) -> None:
        duration_ms = int((report.execution_duration_seconds or 0) * 1000)
        self._execute(
            """
            UPDATE ingestion_run
            SET status = %s,
                completed_at = %s,
                pages_scraped = %s,
                listings_extracted = %s,
                listings_skipped = %s,
                failures_count = %s,
                duration_ms = %s,
                report_json = %s
            WHERE id = %s
            """,
            (
                status,
                completed_at,
                report.pages_processed,
                report.listings_extracted,
                report.listings_skipped,
                report.failures,
                duration_ms,
                self._json(report.to_dict()),
                run_id,
            ),
        )

    def insert_raw_listing(self, raw: RawListing, ctx: RunContext) -> int:
        row = self._fetchone(
            """
            INSERT INTO raw_listing (
                marketplace_source_id, ingestion_run_id, source, uuid, raw_payload,
                raw_hash, adapter_version, marketplace_schema_version,
                marketplace_payload_version, extracted_at
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id
            """,
            (
                ctx.marketplace_source_id,
                ctx.run_id,
                raw.marketplace,
                raw.uuid,
                self._json(raw.raw_payload),
                canonical_hash(raw.raw_payload),
                raw.extracted_fields.get("adapter_version", "unknown"),
                raw.extracted_fields.get("marketplace_schema_version"),
                raw.extracted_fields.get("marketplace_payload_version"),
                raw.fetched_at,
            ),
        )
        return int(row["id"])

    def find_listing_by_source_uuid(self, source: str, uuid: str) -> ListingRow | None:
        row = self._fetchone(
            """
            SELECT *
            FROM listing
            WHERE source = %s AND uuid = %s
            """,
            (source, uuid),
        )
        if row is None:
            return None
        return self._listing_row(row)

    def insert_listing(self, row: ListingRow) -> int:
        payload = row.canonical_payload
        inserted = self._fetchone(
            """
            INSERT INTO listing (
                marketplace_source_id, source, uuid, title, make, model, trim, year,
                price, mileage, condition, location, seller_type, url, status,
                first_seen_at, last_seen_at, first_seen_run_id, last_seen_run_id,
                current_raw_listing_id, canonical_hash, normalization_version
            )
            VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
            )
            RETURNING id
            """,
            (
                row.marketplace_source_id,
                row.source,
                row.uuid,
                payload.get("title"),
                payload.get("make"),
                payload.get("model"),
                payload.get("trim"),
                payload.get("year"),
                payload.get("price"),
                payload.get("kilometers"),
                payload.get("condition"),
                payload.get("location"),
                payload.get("seller_type"),
                payload.get("source_url"),
                row.status,
                row.first_seen_at,
                row.last_seen_at,
                row.first_seen_run_id,
                row.last_seen_run_id,
                row.current_raw_listing_id,
                row.canonical_hash,
                row.normalization_version,
            ),
        )
        return int(inserted["id"])

    def update_listing(self, listing_id: int, row: ListingRow) -> None:
        payload = row.canonical_payload
        self._execute(
            """
            UPDATE listing
            SET title = %s, make = %s, model = %s, trim = %s, year = %s,
                price = %s, mileage = %s, condition = %s, location = %s,
                seller_type = %s, url = %s, status = %s, last_seen_at = %s,
                last_seen_run_id = %s, current_raw_listing_id = %s,
                canonical_hash = %s, normalization_version = %s, updated_at = now()
            WHERE id = %s
            """,
            (
                payload.get("title"),
                payload.get("make"),
                payload.get("model"),
                payload.get("trim"),
                payload.get("year"),
                payload.get("price"),
                payload.get("kilometers"),
                payload.get("condition"),
                payload.get("location"),
                payload.get("seller_type"),
                payload.get("source_url"),
                row.status,
                row.last_seen_at,
                row.last_seen_run_id,
                row.current_raw_listing_id,
                row.canonical_hash,
                row.normalization_version,
                listing_id,
            ),
        )

    def insert_snapshot(self, snap: SnapshotRow) -> int:
        row = self._fetchone(
            """
            INSERT INTO listing_snapshot (
                listing_id, ingestion_run_id, raw_listing_id, snapshot_hash,
                canonical_payload, changed_fields, captured_at
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            RETURNING id
            """,
            (
                snap.listing_id,
                snap.ingestion_run_id,
                snap.raw_listing_id,
                snap.snapshot_hash,
                self._json(snap.canonical_payload),
                self._json(snap.changed_fields),
                snap.captured_at,
            ),
        )
        return int(row["id"])

    def resolve_run(self, run_name_or_id: str) -> RunRow | None:
        if run_name_or_id.isdigit():
            row = self._fetchone(
                "SELECT * FROM ingestion_run WHERE id = %s",
                (int(run_name_or_id),),
            )
        else:
            row = self._fetchone("SELECT * FROM ingestion_run WHERE name = %s", (run_name_or_id,))
        if row is None:
            return None
        return self._run_row(row)

    def read_raw_for_run(self, run_name_or_id: str) -> Iterator[RawListing]:
        run = self.resolve_run(run_name_or_id)
        if run is None or run.id is None:
            return iter(())
        rows = self._fetchall(
            """
            SELECT source, uuid, raw_payload, extracted_at, ingestion_run_id
            FROM raw_listing
            WHERE ingestion_run_id = %s
            ORDER BY id
            """,
            (run.id,),
        )
        return (
            RawListing(
                marketplace=row["source"],
                marketplace_listing_id=row["uuid"],
                uuid=row["uuid"],
                raw_payload=row["raw_payload"],
                extracted_fields={},
                fetched_at=row["extracted_at"],
                scrape_run_id=str(row["ingestion_run_id"]),
                condition=run.condition,
                make_slug=run.make,
            )
            for row in rows
        )

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

    def _fetchone(self, sql: str, params: tuple = {}):
        return self._with_cursor(lambda cur: cur.execute(sql, params).fetchone())

    def _fetchall(self, sql: str, params: tuple = {}):
        return self._with_cursor(lambda cur: cur.execute(sql, params).fetchall())

    def _execute(self, sql: str, params: tuple = {}) -> None:
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

    @staticmethod
    def _listing_row(row) -> ListingRow:
        payload = {
            "title": row.get("title"),
            "make": row.get("make"),
            "model": row.get("model"),
            "trim": row.get("trim"),
            "year": row.get("year"),
            "price": row.get("price"),
            "kilometers": row.get("mileage"),
            "condition": row.get("condition"),
            "location": row.get("location"),
            "seller_type": row.get("seller_type"),
            "source_url": row.get("url"),
            "normalization_version": row.get("normalization_version"),
        }
        return ListingRow(
            id=row["id"],
            marketplace_source_id=row["marketplace_source_id"],
            source=row["source"],
            uuid=row["uuid"],
            canonical_payload=payload,
            canonical_hash=row["canonical_hash"],
            normalization_version=row["normalization_version"],
            first_seen_at=row["first_seen_at"],
            last_seen_at=row["last_seen_at"],
            first_seen_run_id=row["first_seen_run_id"],
            last_seen_run_id=row["last_seen_run_id"],
            current_raw_listing_id=row["current_raw_listing_id"],
            status=row["status"],
        )

    @staticmethod
    def _run_row(row) -> RunRow:
        return RunRow(
            id=row["id"],
            name=row["name"],
            marketplace_source_id=row["marketplace_source_id"],
            marketplace=row["marketplace"],
            condition=row["condition"],
            make=row["make"],
            status=row["status"],
            started_at=row["started_at"],
            completed_at=row["completed_at"],
            pages_scraped=row["pages_scraped"],
            listings_extracted=row["listings_extracted"],
            listings_skipped=row["listings_skipped"],
            failures_count=row["failures_count"],
            duration_ms=row["duration_ms"],
            config_snapshot=row["config_snapshot"],
            report_json=row["report_json"],
        )

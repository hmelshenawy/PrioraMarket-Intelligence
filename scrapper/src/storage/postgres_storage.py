"""PostgreSQL StorageAdapter implementation for Feature 002."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Iterable, Iterator

from src.common.canonical_hash import canonical_hash
from src.common.models import (
    BackfillListingCandidate,
    CatalogSyncReport,
    Listing,
    ListingRow,
    MarketplaceSourceRow,
    NormalizationStatisticsReport,
    RawListing,
    RunContext,
    RunReport,
    RunRow,
    SnapshotRow,
    VehicleReferenceCatalogRow,
)
from src.normalization.canonical_key import canonical_key
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
        if dataset_version is None:
            return iter(())
        return self.read_raw_for_run(dataset_version)

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
                price, mileage, condition, fuel_type, transmission, regional_spec,
                body_type, seller_type, vehicle_condition, specs, color, location, url, status,
                first_seen_at, last_seen_at, first_seen_run_id, last_seen_run_id,
                current_raw_listing_id, canonical_hash, normalization_version,
                canonicalization_version
            )
            VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                %s, %s
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
                payload.get("fuel_type"),
                payload.get("transmission"),
                payload.get("regional_spec"),
                payload.get("body_type"),
                payload.get("seller_type"),
                payload.get("vehicle_condition"),
                payload.get("specs"),
                payload.get("color"),
                payload.get("location"),
                payload.get("source_url"),
                row.status,
                row.first_seen_at,
                row.last_seen_at,
                row.first_seen_run_id,
                row.last_seen_run_id,
                row.current_raw_listing_id,
                row.canonical_hash,
                row.normalization_version,
                payload.get("canonicalization_version"),
            ),
        )
        return int(inserted["id"])

    def update_listing(self, listing_id: int, row: ListingRow) -> None:
        payload = row.canonical_payload
        self._execute(
            """
            UPDATE listing
            SET title = %s, make = %s, model = %s, trim = %s, year = %s,
                price = %s, mileage = %s, condition = %s, fuel_type = %s,
                transmission = %s, regional_spec = %s, body_type = %s,
                seller_type = %s, vehicle_condition = %s, specs = %s, color = %s,
                location = %s, url = %s, status = %s, last_seen_at = %s,
                last_seen_run_id = %s, current_raw_listing_id = %s,
                canonical_hash = %s, normalization_version = %s,
                canonicalization_version = %s, updated_at = now()
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
                payload.get("fuel_type"),
                payload.get("transmission"),
                payload.get("regional_spec"),
                payload.get("body_type"),
                payload.get("seller_type"),
                payload.get("vehicle_condition"),
                payload.get("specs"),
                payload.get("color"),
                payload.get("location"),
                payload.get("source_url"),
                row.status,
                row.last_seen_at,
                row.last_seen_run_id,
                row.current_raw_listing_id,
                row.canonical_hash,
                row.normalization_version,
                payload.get("canonicalization_version"),
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

    def find_vehicle_reference_catalog(
        self, market: str, make_key: str, model_key: str | None = None
    ) -> list[VehicleReferenceCatalogRow]:
        rows = self._fetchall(
            """
            SELECT *
            FROM vehicle_reference_catalog
            WHERE market = %s AND make_key = %s
            ORDER BY model_key, generation NULLS LAST, body_code NULLS LAST
            """,
            (market, make_key),
        )
        catalog_rows = [self._vehicle_reference_catalog_row(row) for row in rows]
        if model_key is None:
            return catalog_rows
        key = canonical_key(model_key)
        return [
            row
            for row in catalog_rows
            if row.model_key == key or key in _catalog_aliases(row, "model")
        ]

    def upsert_vehicle_reference_catalog(
        self, rows: Iterable[VehicleReferenceCatalogRow], source_file: str
    ) -> CatalogSyncReport:
        inserted = updated = unchanged = conflicts = 0
        synced_at = datetime.now(timezone.utc)
        for row in rows:
            existing = self._fetchone(
                """
                SELECT *
                FROM vehicle_reference_catalog
                WHERE market = %s
                  AND make_key = %s
                  AND model_key = %s
                  AND generation IS NOT DISTINCT FROM %s
                  AND body_code IS NOT DISTINCT FROM %s
                """,
                (row.market, row.make_key, row.model_key, row.generation, row.body_code),
            )
            params = {
                "market": row.market,
                "make_key": row.make_key,
                "make_display": row.make_display,
                "model_key": row.model_key,
                "model_display": row.model_display,
                "generation": row.generation,
                "body_code": row.body_code,
                "start_year": row.start_year,
                "end_year": row.end_year,
                "facelift_start_year": row.facelift_start_year,
                "facelift_end_year": row.facelift_end_year,
                "aliases": self._json(row.aliases),
                "confidence": row.confidence,
                "source_file": source_file,
                "source_row_hash": row.source_row_hash,
                "last_synced_at": synced_at,
            }
            if existing is None:
                self._execute(
                    """
                    INSERT INTO vehicle_reference_catalog (
                        market, make_key, make_display, model_key, model_display,
                        generation, body_code, start_year, end_year, facelift_start_year,
                        facelift_end_year, aliases, confidence, source_file,
                        source_row_hash, last_synced_at, updated_at
                    )
                    VALUES (
                        %(market)s, %(make_key)s, %(make_display)s, %(model_key)s,
                        %(model_display)s, %(generation)s, %(body_code)s, %(start_year)s,
                        %(end_year)s, %(facelift_start_year)s, %(facelift_end_year)s,
                        %(aliases)s, %(confidence)s, %(source_file)s, %(source_row_hash)s,
                        %(last_synced_at)s, now()
                    )
                    """,
                    params,
                )
                inserted += 1
                continue
            if existing.get("source_row_hash") == row.source_row_hash:
                unchanged += 1
                continue
            if existing.get("source_file") and existing.get("source_file") != source_file:
                conflicts += 1
            self._execute(
                """
                UPDATE vehicle_reference_catalog
                SET make_display = %(make_display)s,
                    model_display = %(model_display)s,
                    start_year = %(start_year)s,
                    end_year = %(end_year)s,
                    facelift_start_year = %(facelift_start_year)s,
                    facelift_end_year = %(facelift_end_year)s,
                    aliases = %(aliases)s,
                    confidence = %(confidence)s,
                    source_file = %(source_file)s,
                    source_row_hash = %(source_row_hash)s,
                    last_synced_at = %(last_synced_at)s,
                    updated_at = now()
                WHERE id = %(id)s
                """,
                params | {"id": existing["id"]},
            )
            updated += 1
        return CatalogSyncReport(
            source_file=source_file,
            inserted=inserted,
            updated=updated,
            unchanged=unchanged,
            conflicts=conflicts,
            synced_at=synced_at,
        )

    def write_normalization_statistics(self, report: NormalizationStatisticsReport) -> None:
        # Persistence of statistics is implemented with canonicalization integration.
        return None

    def read_listing_backfill_candidates(
        self, batch_size: int, after_id: int | None = None
    ) -> Iterator[BackfillListingCandidate]:
        where = "WHERE id > %s" if after_id is not None else ""
        params = (after_id, batch_size) if after_id is not None else (batch_size,)
        rows = self._fetchall(
            f"""
            SELECT id, source, uuid, make, model, trim, condition, fuel_type,
                   transmission, regional_spec, body_type, seller_type,
                   vehicle_condition, specs, color, canonical_hash,
                   normalization_version, canonicalization_version, current_raw_listing_id
            FROM listing
            {where}
            ORDER BY id
            LIMIT %s
            """,
            params,
        )
        return (
            BackfillListingCandidate(
                id=row["id"],
                source=row["source"],
                uuid=row["uuid"],
                canonical_payload={
                    "make": row.get("make"),
                    "model": row.get("model"),
                    "trim": row.get("trim"),
                    "condition": row.get("condition"),
                    "fuel_type": row.get("fuel_type"),
                    "transmission": row.get("transmission"),
                    "regional_spec": row.get("regional_spec"),
                    "body_type": row.get("body_type"),
                    "seller_type": row.get("seller_type"),
                    "vehicle_condition": row.get("vehicle_condition"),
                    "specs": row.get("specs"),
                    "color": row.get("color"),
                    "canonicalization_version": row.get("canonicalization_version"),
                },
                normalization_version=row.get("normalization_version"),
                current_raw_listing_id=row.get("current_raw_listing_id"),
            )
            for row in rows
        )

    def update_listing_backfill_payload(
        self,
        listing_id: int,
        canonical_payload: dict,
        canonical_hash: str,
        normalization_version: str,
        canonicalization_version: str,
    ) -> None:
        self._execute(
            """
            UPDATE listing
            SET make = %(make)s,
                model = %(model)s,
                trim = %(trim)s,
                condition = %(condition)s,
                fuel_type = %(fuel_type)s,
                transmission = %(transmission)s,
                regional_spec = %(regional_spec)s,
                body_type = %(body_type)s,
                seller_type = %(seller_type)s,
                vehicle_condition = %(vehicle_condition)s,
                specs = %(specs)s,
                color = %(color)s,
                canonical_hash = %(canonical_hash)s,
                normalization_version = %(normalization_version)s,
                canonicalization_version = %(canonicalization_version)s,
                updated_at = now()
            WHERE id = %(listing_id)s
            """,
            {
                "listing_id": listing_id,
                "make": canonical_payload.get("make"),
                "model": canonical_payload.get("model"),
                "trim": canonical_payload.get("trim"),
                "condition": canonical_payload.get("condition"),
                "fuel_type": canonical_payload.get("fuel_type"),
                "transmission": canonical_payload.get("transmission"),
                "regional_spec": canonical_payload.get("regional_spec"),
                "body_type": canonical_payload.get("body_type"),
                "seller_type": canonical_payload.get("seller_type"),
                "vehicle_condition": canonical_payload.get("vehicle_condition"),
                "specs": canonical_payload.get("specs"),
                "color": canonical_payload.get("color"),
                "canonical_hash": canonical_hash,
                "normalization_version": normalization_version,
                "canonicalization_version": canonicalization_version,
            },
        )

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
            "fuel_type": row.get("fuel_type"),
            "transmission": row.get("transmission"),
            "regional_spec": row.get("regional_spec"),
            "body_type": row.get("body_type"),
            "seller_type": row.get("seller_type"),
            "vehicle_condition": row.get("vehicle_condition"),
            "specs": row.get("specs"),
            "color": row.get("color"),
            "location": row.get("location"),
            "source_url": row.get("url"),
            "normalization_version": row.get("normalization_version"),
            "canonicalization_version": row.get("canonicalization_version"),
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

    @staticmethod
    def _vehicle_reference_catalog_row(row) -> VehicleReferenceCatalogRow:
        return VehicleReferenceCatalogRow(
            id=row.get("id"),
            market=row["market"],
            make_key=row["make_key"],
            make_display=row["make_display"],
            model_key=row["model_key"],
            model_display=row["model_display"],
            generation=row.get("generation"),
            body_code=row.get("body_code"),
            start_year=row.get("start_year"),
            end_year=row.get("end_year"),
            facelift_start_year=row.get("facelift_start_year"),
            facelift_end_year=row.get("facelift_end_year"),
            aliases=row.get("aliases") or {},
            confidence=row.get("confidence") or "manual",
            source_file=row.get("source_file"),
            source_row_hash=row.get("source_row_hash"),
            last_synced_at=row.get("last_synced_at"),
        )


def _catalog_aliases(row: VehicleReferenceCatalogRow, field_name: str) -> set[str]:
    aliases = row.aliases.get(field_name, []) if isinstance(row.aliases, dict) else []
    if isinstance(aliases, str):
        aliases = [aliases]
    if not isinstance(aliases, list):
        return set()
    return {key for alias in aliases if (key := canonical_key(alias)) is not None}

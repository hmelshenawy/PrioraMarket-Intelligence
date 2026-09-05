from __future__ import annotations

import os
from datetime import datetime, timezone

import pytest

from src.migrate import apply as apply_migrations
from src.models import Listing, RawListing, RunReport, RunState, Scope
from src.store.postgres import PostgresStore

pytestmark = pytest.mark.skipif(
    os.environ.get("PRIORAMARKET_RUN_DB_TESTS") != "1" or not os.environ.get("DATABASE_URL"),
    reason="set PRIORAMARKET_RUN_DB_TESTS=1 and DATABASE_URL to run PostgreSQL integration tests",
)


def test_full_run_persistence_to_postgresql_counts_reconcile() -> None:
    database_url = os.environ["DATABASE_URL"]
    apply_migrations(database_url)

    from psycopg_pool import ConnectionPool

    pool = ConnectionPool(database_url, min_size=1, max_size=2)
    try:
        scope = Scope("dubizzle", "used", "toyota")
        started = datetime.now(timezone.utc)
        store = PostgresStore(
            pool,
            scope=scope,
            config_snapshot={"storage_backend": "postgres"},
            run_started_at=started,
            marketplace_source_code="dubizzle_uae",
        )
        uuid = f"integration-{started.timestamp()}"
        raw = RawListing(
            marketplace="dubizzle",
            marketplace_listing_id=uuid,
            uuid=uuid,
            raw_payload={"id": uuid, "price": 10000},
            extracted_fields={"adapter_version": "test"},
            fetched_at=started,
            scrape_run_id="integration-run",
            condition="used",
            make_slug="toyota",
        )
        listing = Listing(
            uuid=uuid,
            marketplace="dubizzle",
            marketplace_listing_id=uuid,
            make="Toyota",
            model="Camry",
            price=10000,
            normalization_version="norm-1",
        )
        report = RunReport(
            run_id="integration-run",
            state=RunState.COMPLETED,
            marketplace="dubizzle",
            condition="used",
            make="toyota",
            dataset_version=None,
            normalization_version="norm-1",
            pages_processed=1,
            listings_extracted=1,
        )

        store.write_raw([raw])
        store.write_listings([listing])
        store.write_report(report)

        with pool.connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT COUNT(*) FROM raw_listing WHERE uuid = %s", (uuid,))
                assert cur.fetchone()[0] == 1
                cur.execute("SELECT COUNT(*) FROM listing WHERE uuid = %s", (uuid,))
                assert cur.fetchone()[0] == 1
                cur.execute(
                    """
                    SELECT report_json->>'run_id', report_json->>'state'
                    FROM ingestion_run
                    WHERE id = (SELECT ingestion_run_id FROM raw_listing WHERE uuid = %s)
                    """,
                    (uuid,),
                )
                report_run_id, report_state = cur.fetchone()
                assert report_run_id == "integration-run"
                assert report_state == "COMPLETED"
                cur.execute(
                    """
                    SELECT COUNT(*)
                    FROM listing_snapshot
                    WHERE raw_listing_id IN (SELECT id FROM raw_listing WHERE uuid = %s)
                    """,
                    (uuid,),
                )
                assert cur.fetchone()[0] == 0
    finally:
        pool.close()


def test_persist_run_marks_run_failed_when_listing_persistence_crashes() -> None:
    database_url = os.environ["DATABASE_URL"]
    apply_migrations(database_url)

    from psycopg_pool import ConnectionPool

    pool = ConnectionPool(database_url, min_size=1, max_size=2)
    try:
        scope = Scope("dubizzle", "used", "toyota")
        started = datetime.now(timezone.utc)
        store = PostgresStore(
            pool,
            scope=scope,
            config_snapshot={"storage_backend": "postgres"},
            run_started_at=started,
            marketplace_source_code="dubizzle_uae",
        )
        raw = RawListing(
            marketplace="dubizzle",
            marketplace_listing_id="crash-run",
            uuid="crash-run",
            raw_payload={"id": "crash-run"},
            extracted_fields={},
            fetched_at=started,
            scrape_run_id="integration-run-crash",
            condition="used",
            make_slug="toyota",
        )
        listing = Listing(
            uuid="crash-run",
            marketplace="dubizzle",
            marketplace_listing_id="crash-run",
            make="Toyota",
            model="Camry",
            price=10000,
            normalization_version="norm-1",
        )
        store.write_raw([raw])
        store.write_listings([listing])

        original_begin_run = store.begin_run
        run_ids = []

        def _capture_run_id(scope, config_snapshot, run_started_at, marketplace_source_code):
            ctx = original_begin_run(
                scope, config_snapshot, run_started_at, marketplace_source_code
            )
            run_ids.append(ctx.run_id)
            return ctx

        def _crash(ctx, raw, listing):
            raise RuntimeError("simulated persistence crash")

        store.begin_run = _capture_run_id
        store.persist_listing = _crash
        report = RunReport(
            run_id="integration-run-crash",
            state=RunState.COMPLETED,
            marketplace="dubizzle",
            condition="used",
            make="toyota",
            dataset_version=None,
            normalization_version="norm-1",
            pages_processed=1,
            listings_extracted=1,
        )

        with pytest.raises(RuntimeError, match="simulated persistence crash"):
            store.write_report(report)

        with pool.connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT status FROM ingestion_run WHERE id = %s", (run_ids[0],))
                assert cur.fetchone()[0] == "FAILED"
                cur.execute("DELETE FROM ingestion_run WHERE id = %s", (run_ids[0],))
            conn.commit()
    finally:
        pool.close()

from __future__ import annotations

import os
from datetime import datetime, timezone

import pytest

from src.common.models import Listing, RawListing, RunReport, RunState, Scope
from src.db.migrate import apply as apply_migrations
from src.persistence.batch_bridge import PersistenceBatchBridge
from src.persistence.service import PersistenceService
from src.storage.postgres_storage import PostgresStorageAdapter

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
        service = PersistenceService(PostgresStorageAdapter(pool))
        scope = Scope("dubizzle", "used", "toyota")
        started = datetime.now(timezone.utc)
        bridge = PersistenceBatchBridge(
            service=service,
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

        bridge.write_raw([raw])
        bridge.write_listings([listing])
        bridge.write_report(report)

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

from __future__ import annotations

import os
from datetime import datetime, timezone

import psycopg
import pytest
from psycopg.rows import dict_row

from src.migrate import apply as apply_migrations
from src.models import Listing, RawListing
from src.store.postgres import PostgresStore

pytestmark = pytest.mark.skipif(
    os.environ.get("PRIORAMARKET_RUN_DB_TESTS") != "1" or not os.environ.get("DATABASE_URL"),
    reason="set PRIORAMARKET_RUN_DB_TESTS=1 and DATABASE_URL to run PostgreSQL integration tests",
)


def _pair(uuid, fetched_at):
    raw = RawListing(
        marketplace="dubizzle",
        marketplace_listing_id=uuid,
        uuid=uuid,
        raw_payload={"id": uuid, "price": 10000},
        extracted_fields={"adapter_version": "test"},
        fetched_at=fetched_at,
        scrape_run_id="integration-run",
        condition="used",
        make_slug="toyota",
    )
    listing = Listing(
        uuid=uuid,
        marketplace="dubizzle",
        marketplace_listing_id=uuid,
        make="toyota",
        model="camry",
        price=10000,
        normalization_version="norm-1",
    )
    return raw, listing


def test_save_listing_inserts_then_updates_preserving_first_seen() -> None:
    database_url = os.environ["DATABASE_URL"]
    apply_migrations(database_url)

    conn = psycopg.connect(database_url, row_factory=dict_row)
    try:
        store = PostgresStore(conn)
        uuid = f"integration-{datetime.now(timezone.utc).timestamp()}"
        raw, listing = _pair(uuid, datetime.now(timezone.utc))

        # New listing is created; data is only durable once the caller commits.
        assert store.save_listing(raw, listing) == "created"
        conn.commit()

        with conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) FROM raw_listing WHERE uuid = %s", (uuid,))
            assert cur.fetchone()["count"] == 1
            cur.execute("SELECT COUNT(*) FROM listing WHERE uuid = %s", (uuid,))
            assert cur.fetchone()["count"] == 1

        # Second save of the same listing is an UPDATE, first_seen preserved.
        assert store.save_listing(raw, listing) == "updated"
        conn.commit()

        with conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) FROM raw_listing WHERE uuid = %s", (uuid,))
            assert cur.fetchone()["count"] == 2  # raw payloads append per observation
            cur.execute(
                """
                SELECT first_seen_at = last_seen_at AS same_ts, status
                FROM listing WHERE uuid = %s
                """,
                (uuid,),
            )
            row = cur.fetchone()
            first_equals_last, status = row["same_ts"], row["status"]
            assert first_equals_last is False
            assert status == "ACTIVE"
    finally:
        conn.close()


def test_failed_save_is_rolled_back_by_the_caller() -> None:
    database_url = os.environ["DATABASE_URL"]
    apply_migrations(database_url)

    conn = psycopg.connect(database_url, row_factory=dict_row)
    try:
        store = PostgresStore(conn)
        uuid = f"rollback-{datetime.now(timezone.utc).timestamp()}"
        # uuid is NOT NULL in raw_listing — the save must fail.
        raw, listing = _pair(uuid, datetime.now(timezone.utc))
        bad_raw = RawListing(
            marketplace=raw.marketplace,
            marketplace_listing_id=None,
            uuid=None,
            raw_payload=raw.raw_payload,
            extracted_fields=raw.extracted_fields,
            fetched_at=raw.fetched_at,
            scrape_run_id=raw.scrape_run_id,
            condition=raw.condition,
            make_slug=raw.make_slug,
        )

        with pytest.raises(psycopg.errors.NotNullViolation):
            store.save_listing(bad_raw, listing)
        conn.rollback()

        with conn.cursor() as cur:
            cur.execute(
                "SELECT COUNT(*) FROM listing WHERE source = 'dubizzle' AND uuid = %s", (uuid,)
            )
            assert cur.fetchone()["count"] == 0
            cur.execute("SELECT COUNT(*) FROM raw_listing WHERE uuid IS NULL")
            assert cur.fetchone()["count"] == 0
    finally:
        conn.close()

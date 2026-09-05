from __future__ import annotations

import csv
import os
from urllib.parse import quote, unquote, urlsplit, urlunsplit

import pytest

from src.migrate import apply as apply_migrations
from src.store.catalog_sync import synchronize_vehicle_reference_catalog
from src.store.pool import DatabaseSettings, create_pool
from src.store.postgres import PostgresStore


def _import_vehicle_catalog(path, database_url):
    """Apply migrations, then sync a catalog CSV directory (ex-migrate sync-catalog)."""
    apply_migrations(database_url)
    pool = create_pool(DatabaseSettings(database_url=database_url))
    return synchronize_vehicle_reference_catalog(PostgresStore(pool), path)


pytestmark = pytest.mark.skipif(
    os.environ.get("PRIORAMARKET_RUN_DB_TESTS") != "1" or not os.environ.get("DATABASE_URL"),
    reason="set PRIORAMARKET_RUN_DB_TESTS=1 and DATABASE_URL to run PostgreSQL integration tests",
)


def _safe_database_url(database_url: str) -> str:
    """Quote userinfo so local passwords with reserved characters work in tests."""
    parts = urlsplit(database_url)
    if not parts.username:
        return database_url

    username = quote(unquote(parts.username), safe="")
    password = quote(unquote(parts.password or ""), safe="")
    host = parts.hostname or ""
    if ":" in host and not host.startswith("["):
        host = f"[{host}]"
    port = f":{parts.port}" if parts.port else ""
    userinfo = username if parts.password is None else f"{username}:{password}"
    netloc = f"{userinfo}@{host}{port}"
    return urlunsplit((parts.scheme, netloc, parts.path, parts.query, parts.fragment))


def test_vehicle_generation_catalog_migration_creates_expected_schema() -> None:
    database_url = _safe_database_url(os.environ["DATABASE_URL"])
    apply_migrations(database_url)

    from psycopg import connect

    with connect(database_url) as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT EXISTS (
                    SELECT 1
                    FROM information_schema.tables
                    WHERE table_schema = 'public'
                      AND table_name = 'vehicle_generation_catalog'
                )
                """)
            assert cur.fetchone()[0] is True

            cur.execute("""
                SELECT column_name, data_type, is_nullable, column_default
                FROM information_schema.columns
                WHERE table_schema = 'public'
                  AND table_name = 'vehicle_generation_catalog'
                """)
            columns = {row[0]: row[1:] for row in cur.fetchall()}

            expected_columns = {
                "id": ("bigint", "NO"),
                "slug": ("text", "NO"),
                "market": ("text", "NO"),
                "make_key": ("text", "NO"),
                "model_key": ("text", "NO"),
                "generation": ("text", "NO"),
                "body_code": ("text", "YES"),
                "marketing_name": ("text", "YES"),
                "start_year": ("integer", "NO"),
                "end_year": ("integer", "YES"),
                "facelift_start_year": ("integer", "YES"),
                "facelift_end_year": ("integer", "YES"),
                "aliases": ("jsonb", "NO"),
                "confidence": ("text", "NO"),
                "created_at": ("timestamp with time zone", "NO"),
                "updated_at": ("timestamp with time zone", "NO"),
            }
            assert set(expected_columns).issubset(columns)
            for column_name, (data_type, is_nullable) in expected_columns.items():
                assert columns[column_name][0] == data_type
                assert columns[column_name][1] == is_nullable

            assert "nextval" in columns["id"][2]
            assert "'global'::text" in columns["market"][2]
            assert "'[]'::jsonb" in columns["aliases"][2]
            assert "'manual'::text" in columns["confidence"][2]
            assert "now()" in columns["created_at"][2]
            assert "now()" in columns["updated_at"][2]

            cur.execute("""
                SELECT conname, contype, pg_get_constraintdef(oid)
                FROM pg_constraint
                WHERE conrelid = 'public.vehicle_generation_catalog'::regclass
                """)
            constraints = {row[0]: (row[1], row[2]) for row in cur.fetchall()}
            assert any(
                contype == "p" and "PRIMARY KEY (id)" in definition
                for contype, definition in constraints.values()
            )
            assert constraints["uq_vehicle_generation_catalog_slug"] == (
                "u",
                "UNIQUE (slug)",
            )
            assert constraints["uq_vehicle_generation_catalog_market_identity"] == (
                "u",
                "UNIQUE (market, make_key, model_key, generation, body_code)",
            )

            cur.execute("""
                SELECT indexname, indexdef
                FROM pg_indexes
                WHERE schemaname = 'public'
                  AND tablename = 'vehicle_generation_catalog'
                """)
            indexes = {row[0]: row[1] for row in cur.fetchall()}
            assert "idx_vehicle_generation_catalog_market_make_model" in indexes
            assert (
                "(market, make_key, model_key)"
                in indexes["idx_vehicle_generation_catalog_market_make_model"]
            )
            assert "idx_vehicle_generation_catalog_market_make_model_years" in indexes
            assert (
                "(market, make_key, model_key, start_year, end_year)"
                in indexes["idx_vehicle_generation_catalog_market_make_model_years"]
            )


def _write_catalog_csv(path, rows) -> None:
    fieldnames = [
        "market",
        "make_key",
        "make_display",
        "model_key",
        "model_display",
        "generation",
        "body_code",
        "start_year",
        "end_year",
        "facelift_start_year",
        "facelift_end_year",
        "aliases",
        "confidence",
    ]
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, quotechar="'")
        writer.writeheader()
        writer.writerows(rows)


def _catalog_row(market: str, start_year: str = "2014") -> dict[str, str]:
    return {
        "market": market,
        "make_key": "prioratest",
        "make_display": "Prioratest",
        "model_key": "catalog",
        "model_display": "Catalog",
        "generation": "T1",
        "body_code": "T1",
        "start_year": start_year,
        "end_year": "",
        "facelift_start_year": "",
        "facelift_end_year": "",
        "aliases": '{"model": ["Catalog", "T1"]}',
        "confidence": "manual",
    }


def test_vehicle_catalog_sync_upserts_and_allows_market_specific_duplicates(tmp_path) -> None:
    database_url = _safe_database_url(os.environ["DATABASE_URL"])
    apply_migrations(database_url)

    from psycopg import connect

    with connect(database_url) as conn:
        with conn.cursor() as cur:
            cur.execute("""
                DELETE FROM vehicle_reference_catalog
                WHERE make_key = 'prioratest' AND model_key = 'catalog'
                """)
        conn.commit()

    _write_catalog_csv(
        tmp_path / "prioratest.csv",
        [
            _catalog_row("global", "2014"),
            _catalog_row("uae", "2015"),
        ],
    )
    summary = _import_vehicle_catalog(tmp_path, database_url)

    assert (summary.inserted, summary.updated, summary.unchanged, summary.conflicts) == (2, 0, 0, 0)

    _write_catalog_csv(
        tmp_path / "prioratest.csv",
        [
            _catalog_row("global", "2016"),
            _catalog_row("uae", "2015"),
        ],
    )
    summary = _import_vehicle_catalog(tmp_path, database_url)

    assert (summary.inserted, summary.updated, summary.unchanged) == (0, 1, 1)

    with connect(database_url) as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT market, start_year
                FROM vehicle_reference_catalog
                WHERE make_key = 'prioratest' AND model_key = 'catalog'
                ORDER BY market
                """)
            rows = cur.fetchall()
            cur.execute("""
                DELETE FROM vehicle_reference_catalog
                WHERE make_key = 'prioratest' AND model_key = 'catalog'
                """)
        conn.commit()

    assert rows == [("global", 2016), ("uae", 2015)]

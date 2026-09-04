from __future__ import annotations

import os
from urllib.parse import quote, unquote, urlsplit, urlunsplit

import pytest

from src.migrate import apply as apply_migrations

pytestmark = pytest.mark.skipif(
    os.environ.get("PRIORAMARKET_RUN_DB_TESTS") != "1" or not os.environ.get("DATABASE_URL"),
    reason="set PRIORAMARKET_RUN_DB_TESTS=1 and DATABASE_URL to run PostgreSQL integration tests",
)


def _safe_database_url(database_url: str) -> str:
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
    return urlunsplit(
        (parts.scheme, f"{userinfo}@{host}{port}", parts.path, parts.query, parts.fragment)
    )


def test_vehicle_reference_catalog_migration_creates_foundation_schema() -> None:
    database_url = _safe_database_url(os.environ["DATABASE_URL"])
    apply_migrations(database_url)

    from psycopg import connect

    with connect(database_url) as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT column_name
                FROM information_schema.columns
                WHERE table_schema = 'public'
                  AND table_name = 'vehicle_reference_catalog'
                """)
            catalog_columns = {row[0] for row in cur.fetchall()}
            assert {
                "market",
                "make_key",
                "make_display",
                "model_key",
                "model_display",
                "aliases",
                "confidence",
                "last_synced_at",
                "source_file",
                "source_row_hash",
            }.issubset(catalog_columns)

            cur.execute("""
                SELECT column_name
                FROM information_schema.columns
                WHERE table_schema = 'public'
                  AND table_name = 'listing'
                """)
            listing_columns = {row[0] for row in cur.fetchall()}
            assert {
                "fuel_type",
                "transmission",
                "body_type",
                "regional_spec",
                "specs",
                "color",
                "vehicle_condition",
                "canonicalization_version",
            }.issubset(listing_columns)

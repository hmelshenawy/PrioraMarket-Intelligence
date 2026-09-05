"""Listing persistence: raw capture and current-listing upsert SQL.

Every function takes a psycopg connection and runs exactly one SQL
statement. The column constants pin the exact ``listing`` table columns
the NestJS backend reads via Prisma (make/model/trim/year/price/status,
canonical_hash, normalization_version, last_seen_at,
current_raw_listing_id) — do not rename or reorder without checking the
backend.
"""

from __future__ import annotations

from datetime import datetime, timezone

from psycopg.types.json import Jsonb

from src.hashing import canonical_hash, canonical_payload
from src.models import Listing, RawListing

LISTING_INSERT_COLUMNS = (
    "source",
    "uuid",
    "title",
    "make",
    "model",
    "trim",
    "year",
    "price",
    "mileage",
    "condition",
    "fuel_type",
    "transmission",
    "regional_spec",
    "body_type",
    "seller_type",
    "vehicle_condition",
    "specs",
    "color",
    "location",
    "url",
    "status",
    "first_seen_at",
    "last_seen_at",
    "current_raw_listing_id",
    "canonical_hash",
    "normalization_version",
    "canonicalization_version",
)

LISTING_UPDATE_COLUMNS = (
    "title",
    "make",
    "model",
    "trim",
    "year",
    "price",
    "mileage",
    "condition",
    "fuel_type",
    "transmission",
    "regional_spec",
    "body_type",
    "seller_type",
    "vehicle_condition",
    "specs",
    "color",
    "location",
    "url",
    "status",
    "last_seen_at",
    "current_raw_listing_id",
    "canonical_hash",
    "normalization_version",
    "canonicalization_version",
)

# Listing attribute per SQL column when the names differ (None -> always NULL).
_COLUMN_ATTR = {
    "title": None,
    "mileage": "kilometers",
    "url": "source_url",
}


def insert_raw_listing(conn, raw: RawListing) -> int:
    """Insert the raw payload exactly as received; return its row id."""
    with conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO raw_listing (
                source, uuid, raw_payload, raw_hash, adapter_version,
                marketplace_schema_version, marketplace_payload_version, extracted_at
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id
            """,
            (
                raw.marketplace,
                raw.uuid,
                Jsonb(raw.raw_payload),
                canonical_hash(raw.raw_payload),
                raw.extracted_fields.get("adapter_version", "unknown"),
                raw.extracted_fields.get("marketplace_schema_version"),
                raw.extracted_fields.get("marketplace_payload_version"),
                raw.fetched_at,
            ),
        )
        return int(cur.fetchone()["id"])


def find_by_source_uuid(conn, source: str, uuid: str) -> dict | None:
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT id, first_seen_at
            FROM listing
            WHERE source = %s AND uuid = %s
            """,
            (source, uuid),
        )
        return cur.fetchone()


def insert_listing(conn, listing: Listing, *, raw_id: int) -> int:
    """Insert a new current listing row; first/last seen = observation time."""
    values = _column_values(listing, raw_id=raw_id)
    seen_at = listing.fetched_at or datetime.now(timezone.utc)
    values["first_seen_at"] = seen_at
    values["last_seen_at"] = seen_at
    columns = ", ".join(LISTING_INSERT_COLUMNS)
    placeholders = ", ".join(["%s"] * len(LISTING_INSERT_COLUMNS))
    with conn.cursor() as cur:
        cur.execute(
            f"INSERT INTO listing ({columns}) VALUES ({placeholders}) RETURNING id",
            tuple(values[column] for column in LISTING_INSERT_COLUMNS),
        )
        return int(cur.fetchone()["id"])


def update_listing(conn, listing_id: int, listing: Listing, *, raw_id: int) -> None:
    """Refresh the current listing row from a new observation.

    first_seen_at is intentionally absent: the original first-seen
    provenance is preserved on update.
    """
    values = _column_values(listing, raw_id=raw_id)
    values["last_seen_at"] = datetime.now(timezone.utc)
    assignments = ", ".join(f"{column} = %s" for column in LISTING_UPDATE_COLUMNS)
    with conn.cursor() as cur:
        cur.execute(
            f"UPDATE listing SET {assignments}, updated_at = now() WHERE id = %s",
            (*(values[column] for column in LISTING_UPDATE_COLUMNS), listing_id),
        )


def _column_values(listing: Listing, *, raw_id: int) -> dict:
    """Map one Listing to the pinned SQL column values."""
    values = {}
    for column in LISTING_INSERT_COLUMNS:
        if column in ("first_seen_at", "last_seen_at"):
            values[column] = None  # supplied by the caller
        elif column == "source":
            values[column] = listing.marketplace
        elif column == "uuid":
            values[column] = listing.uuid
        elif column == "status":
            values[column] = "ACTIVE"
        elif column == "current_raw_listing_id":
            values[column] = raw_id
        elif column == "canonical_hash":
            values[column] = canonical_hash(canonical_payload(listing))
        else:
            attr = _COLUMN_ATTR.get(column, column)
            values[column] = getattr(listing, attr) if attr else None
    return values

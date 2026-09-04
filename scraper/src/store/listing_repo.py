"""Listing persistence: raw capture and current-listing upsert columns.

The column constants here pin the exact ``listing`` table columns the
NestJS backend reads via Prisma (make/model/trim/year/price/status,
canonical_hash, normalization_version, last_seen_at, last_seen_run_id,
first_seen_run_id, current_raw_listing_id) — do not rename or reorder
without checking the backend.
"""

from __future__ import annotations

from src.hashing import canonical_hash
from src.models import ListingRow, RawListing, RunContext

LISTING_INSERT_COLUMNS = (
    "marketplace_source_id",
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
    "first_seen_run_id",
    "last_seen_run_id",
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
    "last_seen_run_id",
    "current_raw_listing_id",
    "canonical_hash",
    "normalization_version",
    "canonicalization_version",
)

# Canonical payload key per listing column (None -> column name itself).
_PAYLOAD_KEY = {"mileage": "kilometers", "url": "source_url"}
_ROW_FIELDS = frozenset(
    {
        "marketplace_source_id",
        "source",
        "uuid",
        "status",
        "first_seen_at",
        "last_seen_at",
        "first_seen_run_id",
        "last_seen_run_id",
        "current_raw_listing_id",
        "canonical_hash",
        "normalization_version",
    }
)


def insert_raw_listing(store, raw: RawListing, ctx: RunContext) -> int:
    row = store._fetchone(
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
            store._json(raw.raw_payload),
            canonical_hash(raw.raw_payload),
            raw.extracted_fields.get("adapter_version", "unknown"),
            raw.extracted_fields.get("marketplace_schema_version"),
            raw.extracted_fields.get("marketplace_payload_version"),
            raw.fetched_at,
        ),
    )
    return int(row["id"])


def find_by_source_uuid(store, source: str, uuid: str) -> ListingRow | None:
    row = store._fetchone(
        """
        SELECT *
        FROM listing
        WHERE source = %s AND uuid = %s
        """,
        (source, uuid),
    )
    if row is None:
        return None
    return _listing_row(row)


def insert_listing(store, row: ListingRow) -> int:
    columns = ", ".join(LISTING_INSERT_COLUMNS)
    placeholders = ", ".join(["%s"] * len(LISTING_INSERT_COLUMNS))
    inserted = store._fetchone(
        f"INSERT INTO listing ({columns}) VALUES ({placeholders}) RETURNING id",
        _listing_values(LISTING_INSERT_COLUMNS, row),
    )
    return int(inserted["id"])


def update_listing(store, listing_id: int, row: ListingRow) -> None:
    assignments = ", ".join(f"{column} = %s" for column in LISTING_UPDATE_COLUMNS)
    store._execute(
        f"UPDATE listing SET {assignments}, updated_at = now() WHERE id = %s",
        (*_listing_values(LISTING_UPDATE_COLUMNS, row), listing_id),
    )


def _listing_values(columns, row: ListingRow) -> tuple:
    payload = row.canonical_payload
    values = []
    for column in columns:
        if column in _ROW_FIELDS:
            values.append(getattr(row, column))
        else:
            values.append(payload.get(_PAYLOAD_KEY.get(column, column)))
    return tuple(values)


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

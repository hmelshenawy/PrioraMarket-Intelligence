"""Backend-contract guard: pin the listing columns the NestJS backend reads.

The backend's Prisma models read canonical columns (make/model/trim/year/
price/status, canonical_hash, normalization_version) and freshness
metadata (last_seen_at, current_raw_listing_id) from the scraper-owned
``listing`` table. These tests fail if an insert or update stops
populating any of them.
"""

from __future__ import annotations

from src.store.listing_repo import LISTING_INSERT_COLUMNS, LISTING_UPDATE_COLUMNS

BACKEND_READ_COLUMNS = {
    "make",
    "model",
    "trim",
    "year",
    "price",
    "status",
    "canonical_hash",
    "normalization_version",
    "canonicalization_version",
    "last_seen_at",
    "current_raw_listing_id",
    "mileage",
}

INSERT_ONLY_COLUMNS = {
    "source",
    "uuid",
    "first_seen_at",
}


def test_insert_writes_every_backend_read_column() -> None:
    missing = BACKEND_READ_COLUMNS - set(LISTING_INSERT_COLUMNS)
    assert not missing, f"listing INSERT stopped writing: {sorted(missing)}"


def test_update_writes_every_backend_read_column() -> None:
    missing = BACKEND_READ_COLUMNS - set(LISTING_UPDATE_COLUMNS)
    assert not missing, f"listing UPDATE stopped writing: {sorted(missing)}"


def test_insert_is_update_plus_first_seen_columns() -> None:
    assert set(LISTING_INSERT_COLUMNS) == set(LISTING_UPDATE_COLUMNS) | INSERT_ONLY_COLUMNS

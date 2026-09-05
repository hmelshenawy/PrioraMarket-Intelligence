"""Validation gate (plain functions).

The only important behavior: a valid listing is saved, an invalid one
is skipped. Required fields are uuid, make, and price; numeric values
get basic sanity bounds. `dedup` collapses run-level duplicates so the
newest occurrence wins.
"""

from __future__ import annotations

from datetime import datetime, timezone

from src.models import Listing

# Required fields for a listing to be persisted.
REQUIRED_FIELDS = ("uuid", "make", "price")

# Sanity bounds for basic consistency checks.
_MIN_YEAR = 1900
_MAX_YEAR = datetime.now(timezone.utc).year + 1
_MAX_KILOMETERS = 1_000_000  # 1M km sanity ceiling
_MAX_PRICE = 100_000_000  # 100M AED sanity ceiling


def validate(listing: Listing) -> bool:
    """Return True when the listing has its required fields and sane numbers."""
    for field_name in REQUIRED_FIELDS:
        if getattr(listing, field_name, None) is None or getattr(listing, field_name) == "":
            return False

    if listing.price <= 0 or listing.price > _MAX_PRICE:
        return False
    if listing.kilometers is not None and listing.kilometers > _MAX_KILOMETERS:
        return False
    if listing.year is not None and not (_MIN_YEAR <= listing.year <= _MAX_YEAR):
        return False
    return True


def dedup(listings: list[Listing]) -> tuple[list[Listing], int]:
    """Run-level UUID deduplication: the newest (last) occurrence wins.

    Returns the deduplicated list (in first-seen order) and the number
    of duplicates dropped.
    """
    winner: dict[str, Listing] = {}
    first_seen_order: list[str] = []
    duplicates = 0
    for listing in listings:
        if listing.uuid in winner:
            duplicates += 1
        else:
            first_seen_order.append(listing.uuid)
        winner[listing.uuid] = listing  # newest wins
    deduped = [winner[key] for key in first_seen_order]
    return deduped, duplicates

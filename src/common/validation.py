"""Listing validation gate (FR-030..033, US3).

The full validator checks: uuid presence, required fields, numeric
values, and basic data consistency, producing a ValidationResult. Run-
level UUID deduplication keeps the newest occurrence and counts the rest
as duplicates. Validation is NEVER fatal: invalid/duplicate records are
logged and counted as skipped (the pipeline enforces this).

US1's MinimalValidator is retained as a thin alias for the happy-path
story; US3 swaps the pipeline default to Validator.
"""

from __future__ import annotations

from datetime import datetime, timezone

from src.common.models import Listing, ValidationResult

# Required fields for a listing to be persisted (FR-031).
REQUIRED_FIELDS = ("uuid", "make", "price")

# Sanity bounds for basic consistency checks (FR-032).
_MIN_YEAR = 1900
_MAX_YEAR = datetime.now(timezone.utc).year + 1
_MAX_KILOMETERS = 1_000_000  # 1M km sanity ceiling
_MAX_PRICE = 100_000_000  # 100M AED sanity ceiling


class Validator:
    """Full validation gate producing ValidationResult (US3, T029)."""

    def __init__(self, required_fields=REQUIRED_FIELDS):
        self._required = tuple(required_fields)

    def validate(self, listing: Listing) -> ValidationResult:
        missing: list[str] = []

        # uuid presence (FR-030).
        if not listing.uuid:
            missing.append("uuid")
            return ValidationResult(
                listing_uuid=None,
                accepted=False,
                reason="missing uuid",
                missing_fields=missing,
            )

        # required fields (FR-031).
        for field in self._required:
            if field == "uuid":
                continue
            value = getattr(listing, field, None)
            if value is None or value == "":
                missing.append(field)

        # numeric sanity (FR-032).
        if listing.price is not None and listing.price > _MAX_PRICE:
            return ValidationResult(
                listing_uuid=listing.uuid,
                accepted=False,
                reason=f"price exceeds sanity ceiling ({_MAX_PRICE})",
                missing_fields=missing,
            )
        if listing.kilometers is not None and listing.kilometers > _MAX_KILOMETERS:
            return ValidationResult(
                listing_uuid=listing.uuid,
                accepted=False,
                reason=f"kilometers exceeds sanity ceiling ({_MAX_KILOMETERS})",
                missing_fields=missing,
            )

        # basic consistency (FR-032).
        if listing.year is not None and not (_MIN_YEAR <= listing.year <= _MAX_YEAR):
            return ValidationResult(
                listing_uuid=listing.uuid,
                accepted=False,
                reason=f"year out of consistency bounds [{_MIN_YEAR}, {_MAX_YEAR}]",
                missing_fields=missing,
            )

        if missing:
            return ValidationResult(
                listing_uuid=listing.uuid,
                accepted=False,
                reason="missing required fields: " + ", ".join(missing),
                missing_fields=missing,
            )

        return ValidationResult(listing_uuid=listing.uuid, accepted=True)

    def dedup(self, listings: list[Listing]) -> tuple[list[Listing], int]:
        """Run-level UUID deduplication (FR-033, T030).

        Newest occurrence wins: for listings sharing a uuid, the LAST one
        in iteration order (most recently fetched) is kept. Returns the
        deduplicated list (in first-seen order) and the duplicate count.
        """
        winner: dict[str, Listing] = {}
        first_seen_order: list[str] = []
        counts: dict[str, int] = {}
        for listing in listings:
            key = listing.uuid
            if key not in winner:
                first_seen_order.append(key)
                counts[key] = 0
            else:
                counts[key] += 1
            winner[key] = listing  # newest wins
        deduped = [winner[k] for k in first_seen_order]
        duplicate_count = sum(counts.values())
        return deduped, duplicate_count


class MinimalValidator(Validator):
    """US1 happy-path validator (T017). US3 replaces it with Validator.

    Kept as an alias so US1 tests remain independently meaningful; the
    full ruleset lives in the base class.
    """

    def __init__(self):
        super().__init__(required_fields=("uuid",))

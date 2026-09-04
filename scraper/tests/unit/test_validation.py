"""Unit test for the full validation gate (T028, US3).

Covers: uuid presence, required fields, numeric values, basic
consistency, and run-level UUID deduplication (newest occurrence wins).
"""

from __future__ import annotations

from datetime import datetime, timezone

from src.models import Listing
from src.validation import Validator


def _listing(**overrides) -> Listing:
    base = dict(
        uuid="uuid-1",
        marketplace="dubizzle",
        marketplace_listing_id="1",
        make="Toyota",
        model="Camry",
        condition="used",
        price=85000.0,
        currency="AED",
        year=2021,
        kilometers=45000.0,
        fuel_type="Petrol",
        transmission="Automatic",
        seller_type="dealer",
        location="Dubai",
        photos_count=1,
        source_url="https://dubai.dubizzle.com/x",
        fetched_at=datetime.now(timezone.utc),
        normalization_version="norm-1",
    )
    base.update(overrides)
    return Listing(**base)


def test_accepts_valid_listing():
    v = Validator()
    r = v.validate(_listing())
    assert r.accepted is True
    assert r.reason is None


def test_rejects_missing_uuid():
    v = Validator()
    r = v.validate(_listing(uuid=None))
    assert r.accepted is False
    assert "uuid" in r.missing_fields


def test_rejects_missing_required_fields():
    v = Validator()
    r = v.validate(_listing(make=None, price=None))
    assert r.accepted is False
    assert "make" in r.missing_fields
    assert "price" in r.missing_fields


def test_rejects_non_numeric_price():
    v = Validator()
    # price is typed float; a non-numeric surfaces as None from normalizer.
    r = v.validate(_listing(price=None))
    assert r.accepted is False
    assert "price" in r.missing_fields


def test_rejects_inconsistent_year():
    v = Validator()
    # Year far in the future fails basic consistency.
    r = v.validate(_listing(year=2100))
    assert r.accepted is False
    assert r.reason is not None
    assert "year" in (r.reason or "").lower() or "consistency" in (r.reason or "").lower()


def test_dedup_newest_occurrence_wins():
    v = Validator()
    listings = [
        _listing(uuid="dup", price=100.0),
        _listing(uuid="dup", price=200.0),  # newest
        _listing(uuid="dup", price=150.0),  # last occurrence is newest
        _listing(uuid="other", price=999.0),
    ]
    deduped, dup_count = v.dedup(listings)
    # Newest (last) occurrence of dup wins.
    assert len(deduped) == 2
    dup = next(item for item in deduped if item.uuid == "dup")
    assert dup.price == 150.0
    assert dup_count == 2


def test_dedup_no_duplicates():
    v = Validator()
    listings = [_listing(uuid="a"), _listing(uuid="b")]
    deduped, dup_count = v.dedup(listings)
    assert len(deduped) == 2
    assert dup_count == 0


def test_validator_is_stateless_across_runs():
    v = Validator()
    assert v.validate(_listing()).accepted
    # A fresh validator has no carryover state.
    v2 = Validator()
    assert v2.validate(_listing()).accepted

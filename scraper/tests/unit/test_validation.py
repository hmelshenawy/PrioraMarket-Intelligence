"""Unit tests for the validation gate functions."""

from __future__ import annotations

from datetime import datetime, timezone

from src.models import Listing
from src.validation import dedup, validate


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
        fuel_type="petrol",
        transmission="automatic",
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
    assert validate(_listing()) is True


def test_rejects_missing_uuid():
    assert validate(_listing(uuid=None)) is False


def test_rejects_missing_make_or_price():
    assert validate(_listing(make=None)) is False
    assert validate(_listing(price=None)) is False


def test_rejects_non_positive_price():
    assert validate(_listing(price=0.0)) is False


def test_rejects_inconsistent_year():
    # Year far in the future fails basic consistency.
    assert validate(_listing(year=2100)) is False


def test_rejects_insane_price_and_mileage():
    assert validate(_listing(price=200_000_000.0)) is False
    assert validate(_listing(kilometers=2_000_000.0)) is False


def test_dedup_newest_occurrence_wins():
    listings = [
        _listing(uuid="dup", price=100.0),
        _listing(uuid="dup", price=200.0),
        _listing(uuid="dup", price=150.0),  # last occurrence is newest
        _listing(uuid="other", price=999.0),
    ]
    deduped, dup_count = dedup(listings)
    # Newest (last) occurrence of dup wins.
    assert len(deduped) == 2
    dup = next(item for item in deduped if item.uuid == "dup")
    assert dup.price == 150.0
    assert dup_count == 2


def test_dedup_no_duplicates():
    deduped, dup_count = dedup([_listing(uuid="a"), _listing(uuid="b")])
    assert len(deduped) == 2
    assert dup_count == 0

from __future__ import annotations

from datetime import datetime, timezone

from src.common.canonical_hash import canonical_hash
from src.common.models import Listing


def test_canonical_hash_is_order_independent() -> None:
    left = {"uuid": "1", "features": ["b", "a"], "nested": {"z": 1, "a": 2}}
    right = {"nested": {"a": 2, "z": 1}, "features": ["a", "b"], "uuid": "1"}

    assert canonical_hash(left) == canonical_hash(right)


def test_canonical_hash_excludes_volatile_metadata() -> None:
    listing = Listing(
        uuid="listing-1",
        marketplace="dubizzle",
        marketplace_listing_id="native-1",
        make="Toyota",
        model="Camry",
        price=10000,
        fetched_at=datetime(2026, 7, 4, tzinfo=timezone.utc),
        lineage={"first_seen_run_id": 1, "last_seen_run_id": 1},
    )
    changed_metadata = Listing(
        uuid="listing-1",
        marketplace="dubizzle",
        marketplace_listing_id="native-1",
        make="Toyota",
        model="Camry",
        price=10000,
        fetched_at=datetime(2026, 7, 5, tzinfo=timezone.utc),
        lineage={"first_seen_run_id": 99, "last_seen_run_id": 100},
    )

    assert canonical_hash(listing) == canonical_hash(changed_metadata)


def test_canonical_hash_changes_for_business_state_change() -> None:
    base = {"uuid": "listing-1", "price": 10000, "make": "Toyota"}
    changed = {"uuid": "listing-1", "price": 11000, "make": "Toyota"}

    assert canonical_hash(base) != canonical_hash(changed)


def test_canonical_hash_includes_categorical_fields_and_canonicalization_version() -> None:
    base = Listing(
        uuid="listing-1",
        marketplace="dubizzle",
        marketplace_listing_id="native-1",
        make="mercedesbenz",
        model="cclass",
        fuel_type="petrol",
        canonicalization_version="canonical-key-1",
    )
    changed_version = Listing(
        uuid="listing-1",
        marketplace="dubizzle",
        marketplace_listing_id="native-1",
        make="mercedesbenz",
        model="cclass",
        fuel_type="petrol",
        canonicalization_version="canonical-key-2",
    )
    changed_field = Listing(
        uuid="listing-1",
        marketplace="dubizzle",
        marketplace_listing_id="native-1",
        make="mercedesbenz",
        model="cclass",
        fuel_type="diesel",
        canonicalization_version="canonical-key-1",
    )

    assert canonical_hash(base) != canonical_hash(changed_version)
    assert canonical_hash(base) != canonical_hash(changed_field)

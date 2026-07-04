"""Unit test for the offline replayer (T038, US5).

Verifies: replayer reads stored RawListings via StorageAdapter.read_raw
(no marketplace access), applies an explicit Normalization Version, never
modifies RawListings, and is deterministic across runs.
"""

from __future__ import annotations

import copy
from datetime import datetime, timezone

import pytest
from conftest import load_fixture

from src.common.models import RawListing, Scope
from src.common.validation import Validator
from src.replay.replayer import Replayer
from src.storage.in_memory import InMemoryStorageAdapter


def _raw(condition="used"):
    hit = copy.deepcopy(load_fixture("sample_hit.json"))
    return RawListing(
        marketplace="dubizzle",
        marketplace_listing_id="1",
        uuid="sample-uuid-aaaa-bbbb-cccc",
        raw_payload=hit,
        extracted_fields={
            "uuid": "sample-uuid-aaaa-bbbb-cccc",
            "make": "Toyota",
            "model": "Camry",
            "price_aed": 85000,
            "year": 2021,
            "km": 45000,
            "fuel": "Petrol",
            "specs": "GCC Specs",
            "body_type": "Sedan",
            "transmission": "Automatic",
            "url": "https://dubai.dubizzle.com/x",
            "photos_count": 12,
        },
        fetched_at=datetime.now(timezone.utc),
        scrape_run_id="run-orig",
        condition=condition,
        make_slug="toyota",
    )


@pytest.fixture
def storage():
    s = InMemoryStorageAdapter()
    s.write_raw([_raw()])
    return s


def test_replayer_uses_read_raw_no_marketplace(storage):
    replayer = Replayer(
        storage=storage,
        normalizer_version="norm-1",
        scope=Scope("dubizzle", "used", "toyota"),
    )
    # Sanity: no adapter is constructed; replayer only touches storage.
    listings = replayer.replay(dataset_version=None)
    assert len(listings) == 1
    assert listings[0].make == "Toyota"
    assert listings[0].fuel_type == "Petrol"  # canonicalized


def test_replayer_never_modifies_raw(storage):
    before = copy.deepcopy(storage.raw[0].raw_payload)
    before_ef = copy.deepcopy(storage.raw[0].extracted_fields)
    replayer = Replayer(
        storage=storage,
        normalizer_version="norm-1",
        scope=Scope("dubizzle", "used", "toyota"),
    )
    replayer.replay(dataset_version=None)
    # RawListing is immutable and untouched.
    assert storage.raw[0].raw_payload == before
    assert storage.raw[0].extracted_fields == before_ef
    assert storage.raw[0].scrape_run_id == "run-orig"


def test_replayer_is_deterministic_across_runs(storage):
    replayer = Replayer(
        storage=storage,
        normalizer_version="norm-1",
        scope=Scope("dubizzle", "used", "toyota"),
    )
    first = replayer.replay(dataset_version=None)
    second = replayer.replay(dataset_version=None)
    assert len(first) == len(second) == 1
    a, b = first[0], second[0]
    for attr in (
        "uuid",
        "make",
        "model",
        "price",
        "year",
        "kilometers",
        "fuel_type",
        "regional_spec",
        "body_type",
        "normalization_version",
    ):
        assert getattr(a, attr) == getattr(b, attr)


def test_replayer_applies_explicit_normalization_version(storage):
    replayer = Replayer(
        storage=storage,
        normalizer_version="norm-explicit",
        scope=Scope("dubizzle", "used", "toyota"),
    )
    listings = replayer.replay(dataset_version=None)
    assert listings[0].normalization_version == "norm-explicit"


def test_replayer_validates_and_skips_invalid(storage):
    # Corrupt one raw: missing uuid in extracted_fields and raw_payload.
    bad = copy.deepcopy(_raw())
    bad = RawListing(
        marketplace=bad.marketplace,
        marketplace_listing_id="2",
        uuid=None,
        raw_payload={"id": 2},
        extracted_fields={},
        fetched_at=bad.fetched_at,
        scrape_run_id="run-orig",
        condition="used",
        make_slug="toyota",
    )
    storage.write_raw([bad])
    replayer = Replayer(
        storage=storage,
        normalizer_version="norm-1",
        scope=Scope("dubizzle", "used", "toyota"),
        validator=Validator(),
    )
    listings = replayer.replay(dataset_version=None)
    # Only the valid one survives; the invalid one is skipped, not fatal.
    assert len(listings) == 1
    assert listings[0].uuid == "sample-uuid-aaaa-bbbb-cccc"


def test_replayer_empty_when_no_raw():
    storage = InMemoryStorageAdapter()
    replayer = Replayer(
        storage=storage,
        normalizer_version="norm-1",
        scope=Scope("dubizzle", "used", "toyota"),
    )
    assert replayer.replay(dataset_version=None) == []

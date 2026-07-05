from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone

from conftest import load_fixture

from src.common.canonical_hash import canonical_payload
from src.common.models import RawListing, Scope
from src.ingestion.normalizer import Normalizer
from src.marketplaces.dubizzle.extractor import derive_trim_from_title, extract
from src.replay.replayer import Replayer
from src.storage.in_memory import InMemoryStorageAdapter


def _hit(name: str, *, structured_trim=None, year=2021, price=95000, km=45000):
    hit = deepcopy(load_fixture("sample_hit.json"))
    hit["name"] = {"en": name}
    hit["year"] = year
    hit["price"] = price
    hit["kilometers"] = km
    hit["motors_trim"] = {"name": structured_trim} if structured_trim is not None else None
    return hit


def _extract(hit):
    return extract(
        hit,
        condition="used",
        scrape_run_id="run-trim",
        fetched_at=datetime(2026, 7, 4, tzinfo=timezone.utc),
    )


def test_structured_trim_wins_over_title_candidate():
    raw = _extract(_hit("Mercedes-Benz E 300 AMG", structured_trim="Exclusive"))

    assert raw.extracted_fields["trim"] == "Exclusive"
    assert raw.extracted_fields["trim_source"] == "structured"


def test_derives_e_300_from_title_when_structured_trim_missing():
    raw = _extract(_hit("Mercedes-Benz E 300 GCC Specs"))

    assert raw.extracted_fields["trim"] == "300"
    assert raw.extracted_fields["trim_source"] == "derived_title"


def test_derives_c_200_from_title_when_structured_trim_missing():
    raw = _extract(_hit("Mercedes-Benz C 200 2021"))

    assert raw.extracted_fields["trim"] == "200"
    assert raw.extracted_fields["trim_source"] == "derived_title"


def test_derives_gle_450_from_title_when_structured_trim_missing():
    raw = _extract(_hit("Mercedes-Benz GLE 450 4Matic"))

    assert raw.extracted_fields["trim"] == "450"
    assert raw.extracted_fields["trim_source"] == "derived_title"


def test_derives_amg_known_trim_token_from_title():
    raw = _extract(_hit("Mercedes-Benz AMG GT Coupe"))

    assert raw.extracted_fields["trim"] == "AMG"
    assert raw.extracted_fields["trim_source"] == "derived_title"


def test_no_trim_found_when_title_has_no_safe_candidate():
    raw = _extract(_hit("Toyota Camry GCC Specs"))

    assert raw.extracted_fields["trim"] is None
    assert raw.extracted_fields["trim_source"] == "unknown"


def test_avoids_false_positives_from_year_mileage_price_and_phone_numbers():
    title = "Toyota Camry 2021 45,000 km AED 95,000 call 050 300 4500"

    assert derive_trim_from_title(title) is None


def test_normalized_listing_promotes_trim_into_canonical_payload():
    raw = _extract(_hit("Mercedes-Benz GLE 450 4Matic"))
    listing = Normalizer("norm-trim").normalize(raw, Scope("dubizzle", "used", "mercedes-benz"))

    assert listing.trim == "450"
    assert listing.trim_source == "derived_title"
    assert canonical_payload(listing)["trim"] == "450"
    assert canonical_payload(listing)["trim_source"] == "derived_title"


def test_replay_backfills_trim_from_preserved_raw_payload_when_extracted_trim_is_missing():
    hit = _hit("Mercedes-Benz E 300 GCC Specs")
    raw = RawListing(
        marketplace="dubizzle",
        marketplace_listing_id="listing-1",
        uuid=hit["uuid"],
        raw_payload=hit,
        extracted_fields={"uuid": hit["uuid"], "trim": None},
        fetched_at=datetime(2026, 7, 4, tzinfo=timezone.utc),
        scrape_run_id="run-old",
        condition="used",
        make_slug="mercedes-benz",
    )
    storage = InMemoryStorageAdapter()
    storage.write_raw([raw])

    listings = Replayer(
        storage=storage,
        normalizer_version="norm-trim",
        scope=Scope("dubizzle", "used", "mercedes-benz"),
    ).replay()

    assert listings[0].trim == "300"
    assert listings[0].trim_source == "derived_title"
    assert storage.raw[0].extracted_fields == {"uuid": hit["uuid"], "trim": None}


def test_replay_does_not_overwrite_existing_structured_trim():
    hit = _hit("Mercedes-Benz E 300 AMG")
    extracted = _extract(
        _hit("Mercedes-Benz E 300 AMG", structured_trim="Exclusive")
    ).extracted_fields
    raw = RawListing(
        marketplace="dubizzle",
        marketplace_listing_id="listing-1",
        uuid=hit["uuid"],
        raw_payload=hit,
        extracted_fields=extracted,
        fetched_at=datetime(2026, 7, 4, tzinfo=timezone.utc),
        scrape_run_id="run-old",
        condition="used",
        make_slug="mercedes-benz",
    )
    storage = InMemoryStorageAdapter()
    storage.write_raw([raw])

    listings = Replayer(
        storage=storage,
        normalizer_version="norm-trim",
        scope=Scope("dubizzle", "used", "mercedes-benz"),
    ).replay()

    assert listings[0].trim == "exclusive"
    assert listings[0].trim_source == "structured"

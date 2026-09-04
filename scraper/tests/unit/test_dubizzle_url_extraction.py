from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone

from conftest import load_fixture

from src.fetch.dubizzle_extract import canonical_listing_url, extract
from src.models import Scope
from src.normalize.normalizer import Normalizer


def _extract(hit):
    return extract(
        hit,
        condition="used",
        scrape_run_id="run-url",
        fetched_at=datetime(2026, 7, 4, tzinfo=timezone.utc),
    )


def test_prefers_canonical_url_supplied_by_payload():
    hit = deepcopy(load_fixture("sample_hit.json"))
    hit["canonical_url"] = "https://dubai.dubizzle.com/motors/used-cars/toyota/camry/1234567/"
    hit["uri"] = "/countries/4/listings/aXRlbTo0OjI6MTQ3NjoxNjc5MjM4NQ==/"

    assert _extract(hit).extracted_fields["url"] == hit["canonical_url"]


def test_encoded_listing_id_uri_falls_back_to_public_category_route():
    hit = deepcopy(load_fixture("sample_hit.json"))
    hit["id"] = 16792385
    hit["uri"] = "/countries/4/listings/aXRlbTo0OjI6MTQ3NjoxNjc5MjM4NQ==/"
    hit["category_v2"]["slug_paths"] = [
        "motors",
        "motors/used-cars",
        "motors/used-cars/mercedes-benz",
        "motors/used-cars/mercedes-benz/g-class",
    ]

    assert (
        _extract(hit).extracted_fields["url"]
        == "https://dubai.dubizzle.com/motors/used-cars/mercedes-benz/g-class/16792385/"
    )


def test_missing_optional_url_fields_returns_none_when_no_public_route_can_be_derived():
    hit = deepcopy(load_fixture("edge_hit.json"))
    hit["id"] = None
    hit["uri"] = None
    hit["category_v2"] = {"slug_paths": []}

    assert canonical_listing_url(hit) is None
    assert _extract(hit).extracted_fields["url"] is None


def test_url_normalization_accepts_existing_public_uri_without_changing_consumers():
    hit = deepcopy(load_fixture("sample_hit.json"))
    hit["uri"] = " /motors/used-cars/toyota/camry/1234567/ "

    assert (
        _extract(hit).extracted_fields["url"]
        == "https://dubai.dubizzle.com/motors/used-cars/toyota/camry/1234567/"
    )


def test_normalizer_carries_canonical_url_to_source_url():
    hit = deepcopy(load_fixture("sample_hit.json"))
    hit["canonical_url"] = "https://dubai.dubizzle.com/motors/used-cars/toyota/camry/1234567/"

    raw = _extract(hit)
    listing = Normalizer("norm-url").normalize(raw, Scope("dubizzle", "used", "toyota"))

    assert listing.source_url == "https://dubai.dubizzle.com/motors/used-cars/toyota/camry/1234567/"

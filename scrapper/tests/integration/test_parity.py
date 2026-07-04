"""Parity regression: refactored pipeline vs. prototype (SC-001, T044).

Asserts the refactored pipeline reproduces the prototype scraper's
``extract()`` projection field-for-field for the same hit, and that the
normalized+canonicalized Listing carries the same identity values. The
prototype's extract() logic is embedded here as the reference oracle.
"""

from __future__ import annotations

from datetime import datetime, timezone

import pytest
from conftest import load_fixture

from src.common.models import Scope
from src.ingestion.normalizer import Normalizer
from src.marketplaces.dubizzle.extractor import extract


def _prototype_extract(hit: dict) -> dict:
    """Verbatim copy of dubizzle_full_scrape_v2.extract (reference oracle)."""
    raw_details = hit.get("details") or {}

    def dval(key):
        entry = raw_details.get(key, {})
        if isinstance(entry, dict):
            return (entry.get("en") or {}).get("value")
        return None

    places = hit.get("places") or {}
    place_en = places.get("en", []) if isinstance(places, dict) else []
    location_str = ", ".join(place_en) if place_en else None

    cats = (hit.get("category_v2") or {}).get("slug_paths", [])
    make_slug = next((c.split("/")[2] for c in cats if c.count("/") == 2), None)
    model_slug = next((c.split("/")[3] for c in cats if c.count("/") == 3), None)

    name = hit.get("name") or {}
    name_en = name.get("en") if isinstance(name, dict) else name
    nbhd = hit.get("neighbourhood") or {}
    nbhd_en = nbhd.get("en") if isinstance(nbhd, dict) else nbhd

    return {
        "id": hit.get("id"),
        "uuid": hit.get("uuid"),
        "name": name_en,
        "price_aed": hit.get("price"),
        "year": hit.get("year"),
        "km": hit.get("kilometers"),
        "make": make_slug.replace("-", " ").title() if make_slug else None,
        "model": model_slug.replace("-", " ").title() if model_slug else None,
        "trim": (hit.get("motors_trim") or {}).get("name"),
        "body_type": dval("Body Type"),
        "fuel": dval("Fuel Type"),
        "transmission": dval("Transmission Type"),
        "color": dval("Exterior Color"),
        "specs": dval("Regional Specs"),
        "seller_type": hit.get("seller_type"),
        "seller": (hit.get("user") or {}).get("name"),
        "is_verified": hit.get("is_verified_user"),
        "is_agent": hit.get("seller_account_type") == "AG",
        "neighbourhood": nbhd_en,
        "location": location_str,
        "added": hit.get("added"),
        "url": f"https://dubai.dubizzle.com{hit.get('uri', '')}",
        "photos_count": hit.get("photos_count", 0),
    }


@pytest.mark.parametrize(
    "fixture_name",
    [
        "sample_hit.json",
        "new_car_hit.json",
        "edge_hit.json",
    ],
)
def test_extracted_fields_match_prototype(fixture_name):
    hit = load_fixture(fixture_name)
    raw = extract(
        hit,
        condition="used",
        scrape_run_id="run-parity",
        fetched_at=datetime.now(timezone.utc),
    )
    proto = _prototype_extract(hit)
    ef = raw.extracted_fields
    # Every prototype field maps to the same value in our projection.
    assert ef["id"] == proto["id"]
    assert ef["uuid"] == proto["uuid"]
    assert ef["name"] == proto["name"]
    assert ef["price_aed"] == proto["price_aed"]
    assert ef["year"] == proto["year"]
    assert ef["km"] == proto["km"]
    assert ef["make"] == proto["make"]
    assert ef["model"] == proto["model"]
    assert ef["trim"] == proto["trim"]
    assert ef["body_type"] == proto["body_type"]
    assert ef["fuel"] == proto["fuel"]
    assert ef["transmission"] == proto["transmission"]
    assert ef["color"] == proto["color"]
    assert ef["specs"] == proto["specs"]
    assert ef["seller_type"] == proto["seller_type"]
    assert ef["seller"] == proto["seller"]
    assert ef["is_verified"] == proto["is_verified"]
    assert ef["is_agent"] == proto["is_agent"]
    assert ef["neighbourhood"] == proto["neighbourhood"]
    assert ef["location"] == proto["location"]
    assert ef["added"] == proto["added"]
    assert ef["url"] == proto["url"]
    assert ef["photos_count"] == proto["photos_count"]
    # Verbatim raw payload preserved.
    assert raw.raw_payload is hit


def test_normalized_listing_identity_matches_prototype():
    hit = load_fixture("sample_hit.json")
    raw = extract(
        hit,
        condition="used",
        scrape_run_id="run-parity",
        fetched_at=datetime.now(timezone.utc),
    )
    norm = Normalizer("norm-1").normalize(raw, Scope("dubizzle", "used", "toyota"))
    proto = _prototype_extract(hit)
    # Listing identity fields equal the prototype projection (pre-canonical).
    assert norm.uuid == proto["uuid"]
    assert norm.make == proto["make"]
    assert norm.model == proto["model"]
    assert norm.price == float(proto["price_aed"])
    assert norm.year == proto["year"]
    assert norm.kilometers == float(proto["km"])
    assert norm.body_type == proto["body_type"]
    assert norm.fuel_type == proto["fuel"]
    assert norm.transmission == proto["transmission"]
    assert norm.regional_spec == proto["specs"]
    assert norm.source_url == proto["url"]
    assert norm.photos_count == proto["photos_count"]

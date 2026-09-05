from __future__ import annotations

from datetime import datetime, timezone

from src.models import RawListing
from src.normalize import normalize


def _raw(**fields) -> RawListing:
    extracted = {
        "uuid": "1",
        "make": "Mercedes-Benz",
        "model": "E53 AMG",
        "trim": "AMG Night Package",
        "fuel": "Gasoline",
        "transmission": "Auto",
        "specs": "GCC Specs",
        "body_type": "Crossover SUV",
        "seller_type": "Dealer",
        "color": "Obsidian Black Metallic",
    }
    extracted.update(fields)
    return RawListing(
        marketplace="dubizzle",
        marketplace_listing_id="1",
        uuid="1",
        raw_payload={},
        extracted_fields=extracted,
        fetched_at=datetime.now(timezone.utc),
        scrape_run_id="run-1",
        condition="Used",
        make_slug="mercedes-benz",
    )


def test_supported_categorical_fields_are_canonicalized_to_keys() -> None:
    listing = normalize(_raw())

    assert listing.make == "mercedesbenz"
    assert listing.model == "e53amg"
    assert listing.trim == "amgnightpackage"
    assert listing.condition == "used"
    assert listing.fuel_type == "petrol"
    assert listing.transmission == "automatic"
    assert listing.regional_spec == "gcc"
    assert listing.body_type == "suv"
    assert listing.seller_type == "dealer"
    assert listing.vehicle_condition == "used"
    assert listing.specs == "gccspecs"
    assert listing.color == "obsidianblackmetallic"
    assert listing.canonicalization_version == "canonical-key-1"


def test_normalize_maps_raw_identity_and_numbers() -> None:
    raw = _raw(price_aed="45000", year="2022", km="12,500")
    listing = normalize(raw)

    assert listing.uuid == "1"
    assert listing.marketplace == "dubizzle"
    assert listing.price == 45000.0
    assert listing.year == 2022
    assert listing.kilometers is None  # non-numeric km string is dropped
    assert listing.currency == "AED"


def test_normalize_uses_catalog_for_model_resolution() -> None:
    class _Row:
        model_key = "eclass"
        aliases = {"model": ["E53 AMG"]}

    listing = normalize(
        _raw(model="E53 AMG"),
        catalog=lambda make, model: [_Row()],
    )

    assert listing.model == "eclass"

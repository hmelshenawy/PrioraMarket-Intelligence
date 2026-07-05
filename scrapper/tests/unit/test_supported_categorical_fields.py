from __future__ import annotations

from src.common.models import Listing
from src.ingestion.canonicalizer import Canonicalizer


def test_supported_categorical_fields_are_canonicalized_to_keys() -> None:
    listing = Listing(
        uuid="1",
        marketplace="dubizzle",
        marketplace_listing_id="1",
        make="Mercedes-Benz",
        model="E53 AMG",
        trim="AMG Night Package",
        condition="Used",
        fuel_type="Gasoline",
        transmission="Auto",
        regional_spec="GCC Specs",
        body_type="Crossover SUV",
        seller_type="Dealer",
        vehicle_condition="Used",
        specs="GCC Specs",
        color="Obsidian Black Metallic",
    )

    canonical = Canonicalizer().canonicalize(listing)

    assert canonical.make == "mercedesbenz"
    assert canonical.model == "e53amg"
    assert canonical.trim == "amgnightpackage"
    assert canonical.condition == "used"
    assert canonical.fuel_type == "petrol"
    assert canonical.transmission == "automatic"
    assert canonical.regional_spec == "gcc"
    assert canonical.body_type == "suv"
    assert canonical.seller_type == "dealer"
    assert canonical.vehicle_condition == "used"
    assert canonical.specs == "gccspecs"
    assert canonical.color == "obsidianblackmetallic"
    assert canonical.canonicalization_version == "canonical-key-1"

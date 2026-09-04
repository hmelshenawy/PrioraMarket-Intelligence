from __future__ import annotations

from src.models import Listing, VehicleReferenceCatalogRow
from src.normalize.canonical import CanonicalizationEngine
from tests.fakes import InMemoryStorageAdapter


def test_canonicalization_records_alias_and_catalog_statistics() -> None:
    storage = InMemoryStorageAdapter()
    storage.vehicle_reference_catalog.append(
        VehicleReferenceCatalogRow(
            id=1,
            market="global",
            make_key="mercedesbenz",
            make_display="Mercedes-Benz",
            model_key="cclass",
            model_display="C-Class",
            aliases={"make": ["Mercedes"], "model": ["C Class"]},
        )
    )
    canonicalizer = CanonicalizationEngine(storage=storage)

    listing = canonicalizer.canonicalize_listing(
        Listing(
            uuid="1",
            marketplace="dubizzle",
            marketplace_listing_id="1",
            make="Mercedes",
            model="C Class",
        )
    )

    assert listing.make == "mercedesbenz"
    assert listing.model == "cclass"
    stats = canonicalizer.report().stats
    assert any(s.field_name == "make" and s.alias_matched and s.catalog_matched for s in stats)
    assert any(s.field_name == "model" and s.alias_matched and s.catalog_matched for s in stats)


def test_canonicalization_records_unknown_values_without_blocking() -> None:
    canonicalizer = CanonicalizationEngine()

    listing = canonicalizer.canonicalize_listing(
        Listing(
            uuid="1",
            marketplace="dubizzle",
            marketplace_listing_id="1",
            make="Mystery Brand",
            model="Mystery Model",
            fuel_type="Solar",
        )
    )

    assert listing.make == "mysterybrand"
    assert listing.model == "mysterymodel"
    assert listing.fuel_type == "solar"
    report = canonicalizer.report()
    assert report.unknown_count >= 3
    assert any(s.field_name == "fuel_type" and not s.known for s in report.stats)

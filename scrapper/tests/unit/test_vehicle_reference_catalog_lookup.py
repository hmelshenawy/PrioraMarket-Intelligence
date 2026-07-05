from __future__ import annotations

from src.common.models import VehicleReferenceCatalogRow
from src.normalization.catalog_lookup import VehicleReferenceCatalogLookup
from src.storage.in_memory import InMemoryStorageAdapter


def test_catalog_lookup_resolves_identity_display_values_aliases_and_market_scope() -> None:
    storage = InMemoryStorageAdapter()
    storage.vehicle_reference_catalog.extend(
        [
            VehicleReferenceCatalogRow(
                id=1,
                market="global",
                make_key="mercedesbenz",
                make_display="Mercedes-Benz",
                model_key="cclass",
                model_display="C-Class",
                aliases={"model": ["C Class"]},
            ),
            VehicleReferenceCatalogRow(
                id=2,
                market="uae",
                make_key="mercedesbenz",
                make_display="Mercedes-Benz UAE",
                model_key="cclass",
                model_display="C-Class UAE",
                aliases={"model": ["C Class"]},
            ),
        ]
    )

    global_row = VehicleReferenceCatalogLookup(storage, "global").resolve("mercedesbenz", "C Class")
    uae_row = VehicleReferenceCatalogLookup(storage, "uae").resolve("mercedesbenz", "cclass")

    assert global_row is not None
    assert global_row.model_key == "cclass"
    assert global_row.model_display == "C-Class"
    assert uae_row is not None
    assert uae_row.make_display == "Mercedes-Benz UAE"

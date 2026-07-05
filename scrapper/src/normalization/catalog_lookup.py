"""Storage-backed Vehicle Reference Catalog lookup provider."""

from __future__ import annotations

from collections.abc import Iterable
from typing import Any

from src.common.models import VehicleReferenceCatalogRow
from src.normalization.canonical_key import canonical_key
from src.storage.interface import StorageAdapter


class VehicleReferenceCatalogLookup:
    """Resolve catalog rows by canonical identity or catalog-owned aliases."""

    def __init__(self, storage: StorageAdapter, market: str = "global"):
        self.storage = storage
        self.market = market

    def find(
        self, make_key: str, model_key: str | None = None
    ) -> list[VehicleReferenceCatalogRow]:
        return list(self.storage.find_vehicle_reference_catalog(self.market, make_key, model_key))

    def resolve(
        self, make_value: str, model_value: str | None = None
    ) -> VehicleReferenceCatalogRow | None:
        make_key = canonical_key(make_value)
        model_key = canonical_key(model_value)
        if make_key is None:
            return None

        direct = self.find(make_key, model_key)
        if direct:
            return direct[0]

        for row in self.find(make_key):
            if model_key is None:
                return row
            if model_key == row.model_key or model_key in _aliases(row.aliases, "model"):
                return row
        return None


def _aliases(value: dict[str, Any], field_name: str) -> set[str]:
    raw_aliases = value.get(field_name, []) if isinstance(value, dict) else []
    if isinstance(raw_aliases, str):
        raw_aliases = [raw_aliases]
    if not isinstance(raw_aliases, Iterable):
        return set()
    return {key for alias in raw_aliases if (key := canonical_key(alias)) is not None}

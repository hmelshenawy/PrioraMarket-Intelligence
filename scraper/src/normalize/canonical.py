"""Deterministic canonical keys and the catalog-aware canonicalization engine."""

from __future__ import annotations

import re
from collections.abc import Iterable
from typing import Any

from src.models import Listing, VehicleReferenceCatalogRow
from src.normalize.stats import NormalizationStatisticsCollector
from src.store.base import StorageAdapter

DEFAULT_CANONICALIZATION_VERSION = "canonical-key-1"

MAKE_ALIASES = {
    "mercedes": "mercedesbenz",
    "mercedesbenz": "mercedesbenz",
    "vw": "volkswagen",
    "volkswagen": "volkswagen",
    "chevy": "chevrolet",
    "chevrolet": "chevrolet",
    "landrover": "landrover",
}

FIELD_ALIASES = {
    "fuel_type": {
        "gasoline": "petrol",
        "gas": "petrol",
        "ev": "electric",
        "compressednaturalgas": "cng",
        "liquefiedpetroleumgas": "lpg",
        "pluginhybridpetrolelectric": "pluginhybrid",
    },
    "transmission": {"auto": "automatic", "tiptronic": "automatic", "standard": "manual"},
    "regional_spec": {
        "gccspecs": "gcc",
        "gulfspecs": "gcc",
        "americanspecs": "american",
        "usspecs": "american",
        "japanesespecs": "japanese",
        "japanspecs": "japanese",
        "europeanspecs": "european",
        "eurospecs": "european",
        "koreanspecs": "korean",
    },
    "body_type": {
        "crossover": "suv",
        "crossoversuv": "suv",
        "saloon": "sedan",
        "cabriolet": "convertible",
        "pickuptruck": "pickup",
        "minivan": "van",
        "mpv": "van",
        "estate": "wagon",
    },
}

KNOWN_FIELD_KEYS = {
    "fuel_type": {"petrol", "diesel", "hybrid", "electric", "cng", "lpg", "pluginhybrid"},
    "transmission": {"automatic", "manual"},
    "regional_spec": {"gcc", "american", "japanese", "european", "korean"},
    "body_type": {"suv", "sedan", "coupe", "hatchback", "convertible", "pickup", "van", "wagon"},
}


class CanonicalizationEngine:
    """Canonicalize supported categorical fields and collect operational stats."""

    def __init__(
        self,
        storage: StorageAdapter | None = None,
        version: str = DEFAULT_CANONICALIZATION_VERSION,
        market: str = "global",
        operation: str = "ingestion",
    ):
        self.storage = storage
        self.version = version
        self.market = market
        self.statistics = NormalizationStatisticsCollector(market, version, operation)

    def canonicalize_listing(self, listing: Listing) -> Listing:
        make_key = self._canonicalize_make(listing.make)
        model_key = self._canonicalize_model(make_key, listing.model)
        regional_spec = self._canonicalize_field("regional_spec", listing.regional_spec)
        condition = self._canonicalize_field("condition", listing.condition)
        return listing.with_canonical(
            make=make_key,
            model=model_key,
            trim=self._canonicalize_field("trim", listing.trim),
            condition=condition,
            fuel_type=self._canonicalize_field("fuel_type", listing.fuel_type),
            transmission=self._canonicalize_field("transmission", listing.transmission),
            regional_spec=regional_spec,
            body_type=self._canonicalize_field("body_type", listing.body_type),
            seller_type=self._canonicalize_field("seller_type", listing.seller_type),
            vehicle_condition=self._canonicalize_field(
                "vehicle_condition", listing.vehicle_condition or listing.condition
            ),
            specs=self._canonicalize_field("specs", listing.specs or listing.regional_spec),
            color=self._canonicalize_field("color", listing.color),
            canonicalization_version=self.version,
        )

    def report(self):
        return self.statistics.report()

    def reset_statistics(self) -> None:
        self.statistics.reset()

    def _canonicalize_make(self, value: Any) -> str | None:
        key = canonical_key(value)
        if key is None:
            self.statistics.record("make", None, None, known=False)
            return None
        resolved = MAKE_ALIASES.get(key, key)
        catalog_matched = bool(self._catalog_rows(resolved, None))
        known = catalog_matched or resolved != key or key in MAKE_ALIASES.values()
        self.statistics.record(
            "make",
            str(value),
            resolved,
            known=known,
            alias_matched=resolved != key,
            catalog_matched=catalog_matched,
        )
        return resolved

    def _canonicalize_model(self, make_key: str | None, value: Any) -> str | None:
        key = canonical_key(value)
        if key is None:
            self.statistics.record("model", None, None, known=False)
            return None
        resolved = key
        alias_matched = False
        catalog_matched = False
        rows = self._catalog_rows(make_key, key) if make_key else []
        if rows:
            catalog_matched = True
            resolved = rows[0].model_key
            alias_matched = key in _aliases(rows[0].aliases, "model")
        elif make_key:
            for row in self._catalog_rows(make_key, None):
                aliases = _aliases(row.aliases, "model")
                if key == row.model_key or key in aliases:
                    resolved = row.model_key
                    catalog_matched = True
                    alias_matched = key in aliases and key != row.model_key
                    break
        self.statistics.record(
            "model",
            str(value),
            resolved,
            known=catalog_matched,
            alias_matched=alias_matched,
            catalog_matched=catalog_matched,
        )
        return resolved

    def _canonicalize_field(self, field_name: str, value: Any) -> str | None:
        key = canonical_key(value)
        if key is None:
            self.statistics.record(field_name, None, None, known=False)
            return None
        alias_table = FIELD_ALIASES.get(field_name, {})
        resolved = alias_table.get(key, key)
        known_values = KNOWN_FIELD_KEYS.get(field_name)
        known = known_values is None or resolved in known_values
        self.statistics.record(
            field_name,
            str(value),
            resolved,
            known=known,
            alias_matched=resolved != key,
            catalog_matched=False,
        )
        return resolved

    def _catalog_rows(
        self, make_key: str | None, model_key: str | None
    ) -> list[VehicleReferenceCatalogRow]:
        if self.storage is None or make_key is None:
            return []
        try:
            return list(
                self.storage.find_vehicle_reference_catalog(self.market, make_key, model_key)
            )
        except Exception:
            return []


def _aliases(value: dict[str, Any], field_name: str) -> set[str]:
    raw_aliases = value.get(field_name, []) if isinstance(value, dict) else []
    if isinstance(raw_aliases, str):
        raw_aliases = [raw_aliases]
    if not isinstance(raw_aliases, Iterable):
        return set()
    return {key for alias in raw_aliases if (key := canonical_key(alias)) is not None}


_NON_ALNUM = re.compile(r"[^a-z0-9]+")


def canonical_key(value: Any) -> str | None:
    """Return the immutable key form while preserving semantic letters/numbers."""
    if value is None:
        return None
    text = str(value).strip().lower()
    if not text:
        return None
    key = _NON_ALNUM.sub("", text)
    return key or None

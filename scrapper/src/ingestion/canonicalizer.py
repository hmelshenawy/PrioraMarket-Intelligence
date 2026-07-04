"""Listing canonicalizer (FR-043..045).

Standardizes business values (make, model, fuel, transmission, regional
spec, body type) into canonical platform enums using versioned mappings.
Separate from the normalizer: normalization is object mapping;
canonicalization is business-value standardization (Constitution
"separation of responsibilities"). The canonical mapping version is part
of the Normalization Version so replay is deterministic.
"""

from __future__ import annotations

from typing import Optional

from src.common.models import Listing

CANONICAL_MAPPING_VERSION = "canonical-map-1"

# Lowercased, whitespace-collapsed canonical maps. New aliases extend
# without changing existing entries; bump CANONICAL_MAPPING_VERSION on
# any semantic change.
FUEL_MAP = {
    "petrol": "Petrol",
    "gasoline": "Petrol",
    "gas": "Petrol",
    "diesel": "Diesel",
    "hybrid": "Hybrid",
    "hybrid (petrol/electric)": "Hybrid",
    "electric": "Electric",
    "ev": "Electric",
    "cng": "CNG",
    "compressed natural gas": "CNG",
    "lpg": "LPG",
    "liquefied petroleum gas": "LPG",
    "plug-in hybrid": "Plug-in Hybrid",
    "plug-in hybrid (petrol/electric)": "Plug-in Hybrid",
}

TRANSMISSION_MAP = {
    "automatic": "Automatic",
    "auto": "Automatic",
    "tiptronic": "Automatic",
    "manual": "Manual",
    "standard": "Manual",
}

REGIONAL_SPEC_MAP = {
    "gcc": "GCC",
    "gulf specs": "GCC",
    "gcc specs": "GCC",
    "american": "American",
    "american specs": "American",
    "us specs": "American",
    "japanese": "Japanese",
    "japanese specs": "Japanese",
    "japan specs": "Japanese",
    "european": "European",
    "european specs": "European",
    "euro specs": "European",
    "korean": "Korean",
    "korean specs": "Korean",
}

BODY_TYPE_MAP = {
    "suv": "SUV",
    "crossover": "SUV",
    "crossover suv": "SUV",
    "sedan": "Sedan",
    "saloon": "Sedan",
    "coupe": "Coupe",
    "coupÃ©": "Coupe",
    "hatchback": "Hatchback",
    "convertible": "Convertible",
    "cabriolet": "Convertible",
    "pickup": "Pickup",
    "pickup truck": "Pickup",
    "van": "Van",
    "minivan": "Van",
    "mpv": "Van",
    "wagon": "Wagon",
    "estate": "Wagon",
}


def _canonical(value: Optional[str], table: dict[str, str]) -> Optional[str]:
    if value is None:
        return None
    key = str(value).strip().lower()
    if not key:
        return None
    return table.get(key, str(value).strip())


class Canonicalizer:
    """Apply versioned canonical-value mappings to a Listing."""

    def __init__(self, mapping_version: str = CANONICAL_MAPPING_VERSION):
        self.mapping_version = mapping_version

    def canonicalize(self, listing: Listing) -> Listing:
        return listing.with_canonical(
            make=_canonical_make(listing.make),
            model=_canonical_model(listing.model),
            fuel_type=_canonical(listing.fuel_type, FUEL_MAP),
            transmission=_canonical(listing.transmission, TRANSMISSION_MAP),
            regional_spec=_canonical(listing.regional_spec, REGIONAL_SPEC_MAP),
            body_type=_canonical(listing.body_type, BODY_TYPE_MAP),
        )


def _canonical_make(value: Optional[str]) -> Optional[str]:
    if value is None:
        return None
    # The normalizer already title-cases from the slug; keep that as the
    # canonical form but collapse internal spacing.
    return " ".join(str(value).split())


def _canonical_model(value: Optional[str]) -> Optional[str]:
    if value is None:
        return None
    return " ".join(str(value).split())

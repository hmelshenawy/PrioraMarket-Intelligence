"""Normalization: RawListing -> canonicalized Listing (plain functions).

`canonicalize` reduces any value to its canonical key form (lowercase,
alphanumeric only). Fixed alias tables standardize known variants
(fuel types, transmissions, makes, ...). `normalize` maps a RawListing
to a Listing and applies canonicalization to every categorical field.
"""

from __future__ import annotations

import re
from collections.abc import Callable

from src.models import Listing, RawListing

NORMALIZATION_VERSION = "norm-1"
DEFAULT_CANONICALIZATION_VERSION = "canonical-key-1"

# Lookup signature: (make_key, model_key | None) -> catalog rows.
CatalogLookup = Callable[[str | None, str | None], list]

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

_NON_ALNUM = re.compile(r"[^a-z0-9]+")


def canonicalize(value: str | None) -> str | None:
    """Return the canonical key form: trimmed, lowercase, alphanumeric."""
    if not value:
        return None
    key = _NON_ALNUM.sub("", str(value).strip().lower())
    return key or None


def canonicalize_make(value: str | None) -> str | None:
    """Canonicalize a make, mapping known aliases to one key."""
    key = canonicalize(value)
    if key is None:
        return None
    return MAKE_ALIASES.get(key, key)


def canonicalize_field(field_name: str, value: str | None) -> str | None:
    """Canonicalize one categorical field via its alias table."""
    key = canonicalize(value)
    if key is None:
        return None
    return FIELD_ALIASES.get(field_name, {}).get(key, key)


def normalize(raw: RawListing, catalog: CatalogLookup | None = None) -> Listing:
    """Map a RawListing to a canonicalized Listing."""
    ef = raw.extracted_fields
    make = canonicalize_make(ef.get("make"))
    listing = Listing(
        uuid=ef.get("uuid") or raw.uuid,
        marketplace=raw.marketplace,
        marketplace_listing_id=raw.marketplace_listing_id,
        make=make,
        model=_model_key(make, ef.get("model"), catalog),
        trim=canonicalize(ef.get("trim")),
        trim_source=ef.get("trim_source") or "unknown",
        condition=canonicalize(raw.condition),
        price=_to_float(ef.get("price_aed")),
        currency="AED",
        year=_to_int(ef.get("year")),
        kilometers=_to_float(ef.get("km")),
        fuel_type=canonicalize_field("fuel_type", ef.get("fuel")),
        transmission=canonicalize_field("transmission", ef.get("transmission")),
        regional_spec=canonicalize_field("regional_spec", ef.get("specs")),
        body_type=canonicalize_field("body_type", ef.get("body_type")),
        seller_type=canonicalize(ef.get("seller_type")),
        vehicle_condition=canonicalize(raw.condition),
        specs=canonicalize(ef.get("specs")),
        color=canonicalize(ef.get("color")),
        location=ef.get("location"),
        photos_count=int(ef.get("photos_count") or 0),
        source_url=ef.get("url"),
        fetched_at=raw.fetched_at,
        normalization_version=NORMALIZATION_VERSION,
        canonicalization_version=DEFAULT_CANONICALIZATION_VERSION,
    )
    return listing


def canonicalize_listing(listing: Listing, catalog: CatalogLookup | None = None) -> Listing:
    """Re-canonicalize the categorical fields of an existing Listing.

    Used by the canonical backfill so stored rows follow exactly the
    same rules as fresh normalization.
    """
    listing.make = canonicalize_make(listing.make)
    listing.model = _model_key(listing.make, listing.model, catalog)
    listing.trim = canonicalize(listing.trim)
    listing.condition = canonicalize(listing.condition)
    listing.fuel_type = canonicalize_field("fuel_type", listing.fuel_type)
    listing.transmission = canonicalize_field("transmission", listing.transmission)
    listing.regional_spec = canonicalize_field("regional_spec", listing.regional_spec)
    listing.body_type = canonicalize_field("body_type", listing.body_type)
    listing.seller_type = canonicalize(listing.seller_type)
    listing.vehicle_condition = canonicalize(listing.vehicle_condition or listing.condition)
    listing.specs = canonicalize(listing.specs or listing.regional_spec)
    listing.color = canonicalize(listing.color)
    listing.canonicalization_version = DEFAULT_CANONICALIZATION_VERSION
    return listing


def _model_key(make: str | None, value, catalog: CatalogLookup | None) -> str | None:
    """Canonicalize a model, preferring the reference catalog for the make."""
    key = canonicalize(value)
    if key is None:
        return None
    if catalog is not None and make:
        try:
            rows = catalog(make, key)
        except Exception:
            rows = []
        for row in rows:
            if key == row.model_key or key in _aliases(row.aliases):
                return row.model_key
    return key


def _aliases(row_aliases) -> set[str]:
    raw = row_aliases.get("model", []) if isinstance(row_aliases, dict) else []
    if isinstance(raw, str):
        raw = [raw]
    return {key for alias in raw if (key := canonicalize(alias)) is not None}


def _to_float(value) -> float | None:
    if value is None or value == "":
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _to_int(value) -> int | None:
    if value is None or value == "":
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None

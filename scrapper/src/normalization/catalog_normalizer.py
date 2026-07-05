"""Deterministic make/model key normalization for catalog lookups.

This module intentionally avoids fuzzy matching. It only canonicalizes known
separator/case variants and then applies explicit alias dictionaries.
"""

from __future__ import annotations

import re
import string

_SEPARATORS = re.compile(r"[\s\-_]+")

MAKE_ALIASES = {
    "mercedes": "mercedesbenz",
    "mercedesbenz": "mercedesbenz",
    "vw": "volkswagen",
    "volkswagen": "volkswagen",
    "landrover": "landrover",
    "chevy": "chevrolet",
    "chevrolet": "chevrolet",
}

MODEL_ALIASES = {
    "mercedesbenz": {
        "cclass": "cclass",
        "eclass": "eclass",
        "gle": "gleclass",
        "gleclass": "gleclass",
        "glc": "glcclass",
        "glcclass": "glcclass",
    },
    "bmw": {
        "3series": "3series",
        "5series": "5series",
        "7series": "7series",
    },
    "audi": {
        "a4": "a4",
        "a6": "a6",
    },
}


def canonicalize_key(value: str) -> str:
    """Return the stable key form used before alias resolution."""
    normalized = _SEPARATORS.sub("", value.strip().lower())
    return normalized.strip(string.punctuation)


def normalize_make(make: str) -> str:
    """Normalize a make to the catalog make key."""
    key = canonicalize_key(make)
    return MAKE_ALIASES.get(key, key)


def normalize_model(make_key: str, model: str) -> str:
    """Normalize a model to the catalog model key for a known make key."""
    canonical_make = normalize_make(make_key)
    model_key = canonicalize_key(model)
    return MODEL_ALIASES.get(canonical_make, {}).get(model_key, model_key)

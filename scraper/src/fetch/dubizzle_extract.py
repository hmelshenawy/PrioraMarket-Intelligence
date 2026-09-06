"""Dubizzle listing extraction (FR-020..022).

Parses a single Algolia hit into a RawListing. The raw payload is
preserved verbatim; extracted_fields holds the projection that the
normalizer consumes. This is the only module that knows Dubizzle field
names, keeping marketplace-specific logic isolated (Constitution III/V).
"""

from __future__ import annotations

import re
from datetime import datetime
from typing import Any, Optional
from urllib.parse import urlparse

from src.models import RawListing

NUMERIC_TRIMS = ("200", "250", "300", "350", "400", "450", "500", "550", "560", "580", "63")
MODEL_CUES = (
    "A",
    "B",
    "C",
    "E",
    "S",
    "CLA",
    "CLS",
    "GLA",
    "GLB",
    "GLC",
    "GLE",
    "GLS",
    "SL",
    "SLC",
    "SLK",
    "G",
    "EQE",
    "EQS",
    "RX",
    "LX",
    "ES",
    "GS",
    "IS",
    "LS",
    "NX",
    "GX",
    "X1",
    "X2",
    "X3",
    "X4",
    "X5",
    "X6",
    "X7",
    "M2",
    "M3",
    "M4",
    "M5",
    "M6",
    "M8",
)
PHRASE_TRIMS = (
    (re.compile(r"\bM\s+SPORT\b", re.IGNORECASE), "M Sport"),
    (re.compile(r"\bS\s+LINE\b", re.IGNORECASE), "S Line"),
)
TOKEN_TRIMS = {
    "AMG": "AMG",
    "AUTOBIOGRAPHY": "Autobiography",
    "HSE": "HSE",
    "SVR": "SVR",
    "VXR": "VXR",
    "SPORT": "Sport",
    "PREMIUM": "Premium",
    "LUXURY": "Luxury",
    "SEL": "SEL",
    "SE": "SE",
    "GT": "GT",
    "S": "S",
}
NUMERIC_TRIM_PATTERN = re.compile(
    rf"\b(?:{'|'.join(re.escape(cue) for cue in MODEL_CUES)})[\s-]+"
    rf"({'|'.join(re.escape(trim) for trim in NUMERIC_TRIMS)})\b",
    re.IGNORECASE,
)
DUBIZZLE_BASE_URL = "https://dubai.dubizzle.com"
CANONICAL_URL_FIELDS = (
    "canonical_url",
    "absolute_url",
    "web_url",
    "share_url",
    "permalink",
    "url",
)


def _dval(details: dict[str, Any], key: str) -> Optional[Any]:
    entry = details.get(key, {})
    if isinstance(entry, dict):
        return (entry.get("en") or {}).get("value")
    return None


def _clean_trim(value: Any) -> Optional[str]:
    if not isinstance(value, str):
        return None
    value = " ".join(value.split()).strip(" -/")
    return value or None


def _structured_trim(hit: dict[str, Any]) -> Optional[str]:
    motors_trim = hit.get("motors_trim") or {}
    if not isinstance(motors_trim, dict):
        return None
    return _clean_trim(motors_trim.get("name"))


def derive_trim_from_title(title: Any) -> Optional[str]:
    """Return a conservative trim candidate from a listing title.

    Numeric trims are accepted only when adjacent to a model/class cue, which
    avoids turning years, mileage, prices, or phone numbers into trims.
    """
    if not isinstance(title, str) or not title.strip():
        return None

    match = NUMERIC_TRIM_PATTERN.search(title)
    if match:
        return match.group(1)

    for pattern, trim in PHRASE_TRIMS:
        if pattern.search(title):
            return trim

    tokens = re.findall(r"[A-Za-z0-9]+", title.upper())
    for token in tokens:
        trim = TOKEN_TRIMS.get(token)
        if trim:
            return trim

    return None


def _public_url(value: Any) -> Optional[str]:
    if not isinstance(value, str):
        return None
    value = value.strip()
    if not value:
        return None
    if value.startswith("//"):
        value = f"https:{value}"
    elif value.startswith("dubizzle.com") or value.startswith("dubai.dubizzle.com"):
        value = f"https://{value}"
    elif value.startswith("/"):
        value = f"{DUBIZZLE_BASE_URL}{value}"

    parsed = urlparse(value)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        return None
    if not parsed.netloc.endswith("dubizzle.com"):
        return None
    return value


def _deepest_category_path(hit: dict[str, Any]) -> Optional[str]:
    slug_paths = (hit.get("category_v2") or {}).get("slug_paths", []) or []
    paths = [
        str(path).strip("/")
        for path in slug_paths
        if isinstance(path, str) and path.strip("/").startswith("motors/")
    ]
    if not paths:
        return None
    return max(paths, key=lambda path: path.count("/"))


def canonical_listing_url(hit: dict[str, Any]) -> Optional[str]:
    """Resolve the usable public Dubizzle listing URL for one Algolia hit.

    Dubizzle may expose a public URL directly. If not, some hits only expose an
    internal encoded route like /countries/4/listings/...; for those, derive the
    public route from the preserved category slug path and numeric listing id.
    """
    for field in CANONICAL_URL_FIELDS:
        url = _public_url(hit.get(field))
        if url:
            return url

    uri = hit.get("uri")
    if isinstance(uri, str) and "/countries/" not in uri:
        url = _public_url(uri)
        if url:
            return url

    category_path = _deepest_category_path(hit)
    listing_id = hit.get("id")
    if category_path and listing_id is not None:
        return f"{DUBIZZLE_BASE_URL}/{category_path}/{listing_id}/"

    return None


def extract(
    hit: dict[str, Any],
    *,
    condition: str,
    scrape_run_id: str,
    fetched_at: datetime,
    marketplace: str = "dubizzle",
) -> RawListing:
    """Build a verbatim RawListing from one Algolia hit.

    Mirrors the prototype ``extract()`` so parity (SC-001) holds, but the
    projection is stored in extracted_fields rather than flattened to CSV.
    """
    raw_details = hit.get("details") or {}

    places = hit.get("places") or {}
    place_en = places.get("en", []) if isinstance(places, dict) else []
    location_str = ", ".join(place_en) if place_en else None

    cats = (hit.get("category_v2") or {}).get("slug_paths", []) or []
    make_slug = next((c.split("/")[2] for c in cats if c.count("/") == 2), None)
    model_slug = next((c.split("/")[3] for c in cats if c.count("/") == 3), None)

    name = hit.get("name") or {}
    name_en = name.get("en") if isinstance(name, dict) else name
    nbhd = hit.get("neighbourhood") or {}
    nbhd_en = nbhd.get("en") if isinstance(nbhd, dict) else nbhd
    trim = _structured_trim(hit)
    trim_source = "structured" if trim else "unknown"
    if trim is None:
        trim = derive_trim_from_title(name_en)
        trim_source = "derived_title" if trim else "unknown"

    extracted_fields: dict[str, Any] = {
        "id": hit.get("id"),
        "uuid": hit.get("uuid"),
        "name": name_en,
        "price_aed": hit.get("price"),
        "year": hit.get("year"),
        "km": hit.get("kilometers"),
        "make_slug": make_slug,
        "model_slug": model_slug,
        "make": make_slug.replace("-", " ").title() if make_slug else None,
        "model": model_slug.replace("-", " ").title() if model_slug else None,
        "trim": trim,
        "trim_source": trim_source,
        "body_type": _dval(raw_details, "Body Type"),
        "fuel": _dval(raw_details, "Fuel Type"),
        "transmission": _dval(raw_details, "Transmission Type"),
        "color": _dval(raw_details, "Exterior Color"),
        "specs": _dval(raw_details, "Regional Specs"),
        "seller_type": hit.get("seller_type"),
        "seller": (hit.get("user") or {}).get("name"),
        "is_verified": hit.get("is_verified_user"),
        "is_agent": hit.get("seller_account_type") == "AG",
        "neighbourhood": nbhd_en,
        "location": location_str,
        "added": hit.get("added"),
        "uri": hit.get("uri"),
        "url": canonical_listing_url(hit),
        "photos_count": hit.get("photos_count", 0),
    }

    extracted =  RawListing(
        marketplace=marketplace,
        marketplace_listing_id=str(hit.get("id")) if hit.get("id") is not None else None,
        uuid=hit.get("uuid"),
        raw_payload=hit,  # verbatim — no copy/truncation
        extracted_fields=extracted_fields,
        fetched_at=fetched_at,
        scrape_run_id=scrape_run_id,
        condition=condition,
        make_slug=make_slug,
    )
    print("extracted value!!", extracted.extracted_fields )
    return extracted 

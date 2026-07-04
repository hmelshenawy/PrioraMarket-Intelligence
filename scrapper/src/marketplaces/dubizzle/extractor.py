"""Dubizzle listing extraction (FR-020..022).

Parses a single Algolia hit into a RawListing. The raw payload is
preserved verbatim; extracted_fields holds the projection that the
normalizer consumes. This is the only module that knows Dubizzle field
names, keeping marketplace-specific logic isolated (Constitution III/V).
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Optional

from src.common.models import RawListing


def _dval(details: dict[str, Any], key: str) -> Optional[Any]:
    entry = details.get(key, {})
    if isinstance(entry, dict):
        return (entry.get("en") or {}).get("value")
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
        "trim": (hit.get("motors_trim") or {}).get("name"),
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
        "url": f"https://dubai.dubizzle.com{hit.get('uri', '')}",
        "photos_count": hit.get("photos_count", 0),
    }

    return RawListing(
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

"""Listing normalizer (FR-024..029).

Maps a RawListing (verbatim, marketplace-specific) into a Listing
(platform-internal, marketplace-independent). This is pure object mapping
— no business-value standardization (that is the canonicalizer's job).
Deterministic and versioned via Normalization Version so the same
RawListing always yields the same Listing for a given version (replay).
"""

from __future__ import annotations

from typing import Optional

from src.common.models import Listing, RawListing, Scope

# The normalizer ruleset version. Bump when mapping logic changes; replay
# uses this to select which ruleset to apply.
NORMALIZER_RULESET = "norm-ruleset-1"


class Normalizer:
    """RawListing -> Listing object mapping."""

    def __init__(self, normalization_version: str = "norm-1"):
        self.normalization_version = normalization_version

    def normalize(self, raw: RawListing, scope: Scope) -> Listing:
        ef = raw.extracted_fields
        uuid = ef.get("uuid") or raw.uuid
        return Listing(
            uuid=uuid,
            marketplace=raw.marketplace,
            marketplace_listing_id=raw.marketplace_listing_id,
            make=ef.get("make"),
            model=ef.get("model"),
            condition=scope.condition,
            price=_to_float(ef.get("price_aed")),
            currency="AED",
            year=_to_int(ef.get("year")),
            kilometers=_to_float(ef.get("km")),
            fuel_type=ef.get("fuel"),
            transmission=ef.get("transmission"),
            regional_spec=ef.get("specs"),
            body_type=ef.get("body_type"),
            seller_type=ef.get("seller_type"),
            location=ef.get("location"),
            photos_count=int(ef.get("photos_count") or 0),
            source_url=ef.get("url"),
            fetched_at=raw.fetched_at,
            normalization_version=self.normalization_version,
            lineage={
                "scrape_run_id": raw.scrape_run_id,
                "marketplace_listing_id": raw.marketplace_listing_id,
                "raw_uuid": raw.uuid,
                "condition": raw.condition,
                "make_slug": raw.make_slug,
                "trim": ef.get("trim"),
                "color": ef.get("color"),
                "seller": ef.get("seller"),
                "is_verified": ef.get("is_verified"),
                "is_agent": ef.get("is_agent"),
                "neighbourhood": ef.get("neighbourhood"),
                "added": ef.get("added"),
            },
        )


def _to_float(value) -> Optional[float]:
    if value is None or value == "":
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _to_int(value) -> Optional[int]:
    if value is None or value == "":
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None

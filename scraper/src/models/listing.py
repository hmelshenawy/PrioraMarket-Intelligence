"""Listing-domain models: raw capture and the derived canonical projection.

RawListing is immutable and preserved verbatim; Listing is a derived,
canonicalizable projection. See data-model.md.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Optional


@dataclass(frozen=True)
class RawListing:
    """The original marketplace listing exactly as received.

    Immutable. The raw_payload is preserved verbatim — no transformation,
    truncation, or enrichment. Ground truth for all downstream derivation.
    """

    marketplace: str
    marketplace_listing_id: Optional[str]
    uuid: Optional[str]
    raw_payload: dict[str, Any]
    extracted_fields: dict[str, Any]
    fetched_at: datetime
    scrape_run_id: str
    condition: str
    make_slug: Optional[str]


@dataclass
class Listing:
    """Platform-internal, marketplace-independent listing (derived).

    Produced by the normalizer from a RawListing; business values are
    canonicalized by the canonicalizer. Never received directly from a
    marketplace.
    """

    uuid: Optional[str]
    marketplace: str
    marketplace_listing_id: Optional[str]
    make: Optional[str] = None
    model: Optional[str] = None
    trim: Optional[str] = None
    trim_source: str = "unknown"
    condition: Optional[str] = None
    price: Optional[float] = None
    currency: str = "AED"
    year: Optional[int] = None
    kilometers: Optional[float] = None
    fuel_type: Optional[str] = None
    transmission: Optional[str] = None
    regional_spec: Optional[str] = None
    body_type: Optional[str] = None
    seller_type: Optional[str] = None
    vehicle_condition: Optional[str] = None
    specs: Optional[str] = None
    color: Optional[str] = None
    location: Optional[str] = None
    photos_count: int = 0
    source_url: Optional[str] = None
    fetched_at: Optional[datetime] = None
    normalization_version: Optional[str] = None
    canonicalization_version: Optional[str] = None
    dataset_version: Optional[str] = None
    lineage: dict[str, Any] = field(default_factory=dict)

    def with_canonical(
        self,
        make: Optional[str] = None,
        model: Optional[str] = None,
        trim: Optional[str] = None,
        condition: Optional[str] = None,
        fuel_type: Optional[str] = None,
        transmission: Optional[str] = None,
        regional_spec: Optional[str] = None,
        body_type: Optional[str] = None,
        seller_type: Optional[str] = None,
        vehicle_condition: Optional[str] = None,
        specs: Optional[str] = None,
        color: Optional[str] = None,
        canonicalization_version: Optional[str] = None,
    ) -> "Listing":
        """Return a copy with canonicalized business values (FR-043..045)."""
        import dataclasses

        replaced = dataclasses.replace(self)
        if make is not None:
            replaced.make = make
        if model is not None:
            replaced.model = model
        if trim is not None:
            replaced.trim = trim
        if condition is not None:
            replaced.condition = condition
        if fuel_type is not None:
            replaced.fuel_type = fuel_type
        if transmission is not None:
            replaced.transmission = transmission
        if regional_spec is not None:
            replaced.regional_spec = regional_spec
        if body_type is not None:
            replaced.body_type = body_type
        if seller_type is not None:
            replaced.seller_type = seller_type
        if vehicle_condition is not None:
            replaced.vehicle_condition = vehicle_condition
        if specs is not None:
            replaced.specs = specs
        if color is not None:
            replaced.color = color
        if canonicalization_version is not None:
            replaced.canonicalization_version = canonicalization_version
        return replaced

    def to_record(self) -> dict[str, Any]:
        """Flatten to a CSV/JSON-friendly record."""
        rec = {
            "uuid": self.uuid,
            "marketplace": self.marketplace,
            "marketplace_listing_id": self.marketplace_listing_id,
            "make": self.make,
            "model": self.model,
            "trim": self.trim,
            "trim_source": self.trim_source,
            "condition": self.condition,
            "price": self.price,
            "currency": self.currency,
            "year": self.year,
            "kilometers": self.kilometers,
            "fuel_type": self.fuel_type,
            "transmission": self.transmission,
            "regional_spec": self.regional_spec,
            "body_type": self.body_type,
            "seller_type": self.seller_type,
            "vehicle_condition": self.vehicle_condition,
            "specs": self.specs,
            "color": self.color,
            "location": self.location,
            "photos_count": self.photos_count,
            "source_url": self.source_url,
            "fetched_at": self.fetched_at.isoformat() if self.fetched_at else None,
            "normalization_version": self.normalization_version,
            "canonicalization_version": self.canonicalization_version,
            "dataset_version": self.dataset_version,
        }
        rec.update(self.lineage)
        return rec


@dataclass
class ValidationResult:
    """Outcome of validating a canonicalized listing (FR-030..033)."""

    listing_uuid: Optional[str]
    accepted: bool
    reason: Optional[str] = None
    missing_fields: list[str] = field(default_factory=list)
    duplicate: bool = False
    duplicate_of: Optional[str] = None

"""Deterministic canonical hash generation for Listing business state."""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, is_dataclass
from datetime import date, datetime
from decimal import Decimal
from typing import Any

EXCLUDED_FIELDS = {
    "id",
    "created_at",
    "updated_at",
    "first_seen_at",
    "last_seen_at",
    "first_seen_run_id",
    "last_seen_run_id",
    "ingestion_run_id",
    "current_raw_listing_id",
    "fetched_at",
    "scrape_run_id",
    "dataset_version",
    "lineage",
}


def _normalize(value: Any) -> Any:
    if is_dataclass(value):
        value = asdict(value)
    if isinstance(value, dict):
        return {str(k): _normalize(v) for k, v in sorted(value.items()) if k not in EXCLUDED_FIELDS}
    if isinstance(value, (list, tuple, set)):
        normalized = [_normalize(item) for item in value]
        return sorted(normalized, key=lambda item: json.dumps(item, sort_keys=True, default=str))
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    if isinstance(value, Decimal):
        return str(value)
    return value


def canonical_payload(value: Any) -> dict[str, Any]:
    """Return a stable business-state payload with volatile metadata removed."""
    normalized = _normalize(value)
    if not isinstance(normalized, dict):
        raise TypeError("canonical payload source must normalize to a mapping")
    return normalized


def canonical_hash(value: Any) -> str:
    """Return a sha256 hex digest of the complete canonical business state."""
    payload = canonical_payload(value)
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()

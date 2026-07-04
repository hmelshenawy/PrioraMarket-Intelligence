"""Run-name generation for IngestionRun replay handles."""

from __future__ import annotations

import hashlib
import re
import unicodedata
from datetime import datetime, timezone
from typing import Iterable


def slug_segment(value: str | None) -> str:
    """Lowercase ASCII slug; empty results become 'unknown'."""
    text = unicodedata.normalize("NFKD", value or "").encode("ascii", "ignore").decode("ascii")
    text = re.sub(r"[^a-zA-Z0-9]+", "-", text.lower()).strip("-")
    return text or "unknown"


def scope_digest(parts: Iterable[str | None]) -> str:
    raw = "|".join(part or "" for part in parts)
    return hashlib.sha1(raw.encode("utf-8")).hexdigest()[:8]


def build_run_name(
    marketplace: str,
    condition: str,
    make: str | None,
    started_at: datetime,
    disambiguator: str | None = None,
) -> str:
    """Build run_<marketplace>_<condition>_<make>_<yyyyMMdd>_<HHmmss>[_hex]."""
    if started_at.tzinfo is None:
        started_at = started_at.replace(tzinfo=timezone.utc)
    started_at = started_at.astimezone(timezone.utc)
    make_or_scope = slug_segment(make) if make else scope_digest((marketplace, condition))
    base = "_".join(
        [
            "run",
            slug_segment(marketplace),
            slug_segment(condition),
            make_or_scope,
            started_at.strftime("%Y%m%d"),
            started_at.strftime("%H%M%S"),
        ]
    )
    if disambiguator:
        return f"{base}_{slug_segment(disambiguator)[:8]}"
    return base


def collision_disambiguator(candidate: str, seed: str | int) -> str:
    """Return deterministic 8-char hex suffix for a colliding run name."""
    return hashlib.sha1(f"{candidate}:{seed}".encode("utf-8")).hexdigest()[:8]

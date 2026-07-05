"""Deterministic canonical key generation for operational categorical values."""

from __future__ import annotations

import re
from typing import Any

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

"""The one interface every marketplace adapter provides."""

from __future__ import annotations

from typing import Iterable, Protocol, runtime_checkable

from src.models import RawListing


@runtime_checkable
class MarketplaceAdapter(Protocol):
    """Anything that can stream raw listings for a (make, condition) scope."""

    def fetch(self, make: str, condition: str) -> Iterable[RawListing]: ...

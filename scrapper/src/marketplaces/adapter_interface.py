"""MarketplaceAdapter interface contract (FR-010..015).

A marketplace adapter is the only component permitted to perform network
I/O against an external marketplace. It yields RawListings (verbatim) and
page metadata as an iterable so the pipeline can stream without buffering
the full dataset in memory. Marketplace-specific parsing lives in the
adapter's extractor; the rest of the system never depends on marketplace
field names.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Optional, Protocol, runtime_checkable

from src.common.models import RawListing, Scope


@dataclass
class PageMetadata:
    """Per-page fetch metadata emitted alongside RawListings."""

    page: int
    hits_on_page: int
    nb_pages: Optional[int] = None
    nb_hits: Optional[int] = None
    retried: bool = False


@runtime_checkable
class MarketplaceAdapter(Protocol):
    """Stream RawListings for a single scope (marketplace, condition, make)."""

    scope: Scope

    def fetch(self, scope: Scope) -> Iterable[tuple[list[RawListing], PageMetadata]]:
        """Yield (page_listings, metadata) tuples, one per fetched page.

        Page 0 metadata MUST include nb_pages / nb_hits so the pipeline can
        apply the pagination cap. Each RawListing preserves the marketplace
        payload verbatim in ``raw_payload``.
        """
        ...

    @property
    def marketplace_name(self) -> str:
        """Stable marketplace identifier (e.g. "dubizzle")."""
        ...

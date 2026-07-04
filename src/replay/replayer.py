"""Offline deterministic replayer (FR-065..067, US5).

Rebuilds normalized Listings from previously stored RawListings WITHOUT
marketplace access, using an explicitly selected Normalization Version.
Replay rules (Constitution "Historical Data Preservation" + Replay US5):

- NEVER modifies RawListings (they are immutable ground truth).
- An EXPLICIT Normalization Version is required; replay is never implicit.
- Deterministic: the same RawListings + version yield identical Listings.

The replayer reuses the same Normalizer / Canonicalizer / Validator as
the live pipeline so replayed output matches an equivalent live run.
"""

from __future__ import annotations

from typing import Optional

from src.common.logger import get_logger
from src.common.models import Listing, Scope
from src.common.validation import Validator
from src.ingestion.canonicalizer import Canonicalizer
from src.ingestion.normalizer import Normalizer
from src.storage.interface import StorageAdapter


class Replayer:
    """Rebuild Listings offline from stored RawListings."""

    def __init__(
        self,
        storage: StorageAdapter,
        normalizer_version: str,
        scope: Scope,
        canonicalizer: Optional[Canonicalizer] = None,
        validator: Optional[Validator] = None,
    ):
        if not normalizer_version:
            raise ValueError("Replay requires an explicit normalization version")
        self._storage = storage
        self._scope = scope
        self._normalizer = Normalizer(normalizer_version)
        self._canonicalizer = canonicalizer or Canonicalizer()
        self._validator = validator or Validator()
        self._log = get_logger("replayer")

    def replay(self, dataset_version: Optional[str] = None) -> list[Listing]:
        """Rebuild accepted Listings from stored RawListings.

        No marketplace access occurs; only StorageAdapter.read_raw is used.
        Returns the canonicalized, validated, deduplicated Listings.
        """
        accepted: list[Listing] = []
        # read_raw is an iterable; we do NOT mutate the RawListing objects.
        for raw in self._storage.read_raw(dataset_version):
            try:
                listing = self._normalizer.normalize(raw, self._scope)
            except Exception as exc:
                self._log.warning(
                    "replay: record skipped during normalization",
                    extra={"uuid": raw.uuid, "error": str(exc)},
                )
                continue
            listing = self._canonicalizer.canonicalize(listing)
            result = self._validator.validate(listing)
            if result.accepted:
                accepted.append(listing)
            else:
                self._log.info(
                    "replay: listing skipped",
                    extra={"uuid": result.listing_uuid, "reason": result.reason},
                )

        if hasattr(self._validator, "dedup"):
            accepted, _dup = self._validator.dedup(accepted)
        return accepted

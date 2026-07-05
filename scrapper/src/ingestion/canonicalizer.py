"""Listing canonicalizer (FR-043..045)."""

from __future__ import annotations

from src.common.models import Listing
from src.normalization.canonicalization_engine import (
    DEFAULT_CANONICALIZATION_VERSION,
    CanonicalizationEngine,
)
from src.storage.interface import StorageAdapter

CANONICAL_MAPPING_VERSION = DEFAULT_CANONICALIZATION_VERSION


class Canonicalizer:
    """Compatibility wrapper around the shared canonicalization engine."""

    def __init__(
        self,
        mapping_version: str = CANONICAL_MAPPING_VERSION,
        storage: StorageAdapter | None = None,
        market: str = "global",
        operation: str = "ingestion",
    ):
        self.mapping_version = mapping_version
        self._engine = CanonicalizationEngine(storage, mapping_version, market, operation)

    def canonicalize(self, listing: Listing) -> Listing:
        return self._engine.canonicalize_listing(listing)

    def report(self):
        return self._engine.report()

    def reset_statistics(self) -> None:
        self._engine.reset_statistics()

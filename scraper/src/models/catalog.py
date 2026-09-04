"""Vehicle Reference Catalog and normalization statistics models."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass(frozen=True)
class VehicleReferenceCatalogRow:
    """Storage DTO for a Vehicle Reference Catalog row."""

    id: int | None
    market: str
    make_key: str
    make_display: str
    model_key: str
    model_display: str
    generation: str | None = None
    body_code: str | None = None
    start_year: int | None = None
    end_year: int | None = None
    facelift_start_year: int | None = None
    facelift_end_year: int | None = None
    aliases: dict[str, Any] = field(default_factory=dict)
    confidence: str = "manual"
    source_file: str | None = None
    source_row_hash: str | None = None
    last_synced_at: datetime | None = None


@dataclass(frozen=True)
class CatalogSyncReport:
    """Summary emitted by Vehicle Reference Catalog synchronization."""

    source_file: str
    inserted: int = 0
    updated: int = 0
    unchanged: int = 0
    rejected: int = 0
    conflicts: int = 0
    synced_at: datetime | None = None


@dataclass(frozen=True)
class NormalizationFieldStat:
    """Operational normalization counts for one field in one context."""

    market: str
    field_name: str
    raw_value: str | None
    canonical_key: str | None
    known: bool = False
    alias_matched: bool = False
    catalog_matched: bool = False
    count: int = 1


@dataclass
class NormalizationStatisticsReport:
    """Operational reporting envelope for normalization outcomes."""

    operation: str
    market: str
    canonicalization_version: str
    stats: list[NormalizationFieldStat] = field(default_factory=list)
    created_at: datetime | None = None

    @property
    def unknown_count(self) -> int:
        return sum(stat.count for stat in self.stats if not stat.known)

"""Normalization statistics collection for canonicalization operations."""

from __future__ import annotations

from collections import Counter
from datetime import datetime, timezone

from src.models import NormalizationFieldStat, NormalizationStatisticsReport


class NormalizationStatisticsCollector:
    """Aggregate known/unknown/alias/catalog outcomes without raw payloads."""

    def __init__(self, market: str, canonicalization_version: str, operation: str = "ingestion"):
        self.market = market
        self.canonicalization_version = canonicalization_version
        self.operation = operation
        self._counts: Counter[tuple[str, str | None, str | None, bool, bool, bool]] = Counter()

    def record(
        self,
        field_name: str,
        raw_value: str | None,
        canonical_key: str | None,
        *,
        known: bool,
        alias_matched: bool = False,
        catalog_matched: bool = False,
    ) -> None:
        self._counts[
            (field_name, raw_value, canonical_key, known, alias_matched, catalog_matched)
        ] += 1

    def report(self) -> NormalizationStatisticsReport:
        return NormalizationStatisticsReport(
            operation=self.operation,
            market=self.market,
            canonicalization_version=self.canonicalization_version,
            stats=[
                NormalizationFieldStat(
                    market=self.market,
                    field_name=field_name,
                    raw_value=raw_value,
                    canonical_key=key,
                    known=known,
                    alias_matched=alias_matched,
                    catalog_matched=catalog_matched,
                    count=count,
                )
                for (
                    field_name,
                    raw_value,
                    key,
                    known,
                    alias_matched,
                    catalog_matched,
                ), count in sorted(
                    self._counts.items(), key=lambda item: tuple(str(v) for v in item[0])
                )
            ],
            created_at=datetime.now(timezone.utc),
        )

    def reset(self) -> None:
        self._counts.clear()

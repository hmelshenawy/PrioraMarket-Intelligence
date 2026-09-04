"""CSV run artifacts (debug backend, FR-053..056).

Writes RawListings (verbatim JSON-lines), canonicalized Listings (CSV),
and the RunReport (JSON) under a run-scoped output directory. PostgreSQL
is the production backend; this backend exists for local inspection.
"""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Iterable

from src.models import (
    Listing,
    NormalizationStatisticsReport,
    RawListing,
    RunReport,
    VehicleReferenceCatalogRow,
)


class CsvStorageAdapter:
    """Filesystem CSV/JSON run artifacts implementing StorageAdapter."""

    def __init__(self, output_dir: Path, run_id: str):
        self._root = Path(output_dir)
        self._run_dir = self._root / run_id
        self._run_dir.mkdir(parents=True, exist_ok=True)

    @property
    def run_dir(self) -> Path:
        return self._run_dir

    def raw_path(self) -> Path:
        return self._run_dir / "raw_listings.jsonl"

    def listings_path(self) -> Path:
        return self._run_dir / "listings.csv"

    def report_path(self) -> Path:
        return self._run_dir / "run_report.json"

    def write_raw(self, raw_listings: Iterable[RawListing]) -> int:
        count = 0
        with open(self.raw_path(), "w", encoding="utf-8") as f:
            for raw in raw_listings:
                f.write(json.dumps(self._raw_to_dict(raw), default=str) + "\n")
                count += 1
        return count

    def write_listings(self, listings: Iterable[Listing]) -> int:
        records = [listing.to_record() for listing in listings]
        if not records:
            return 0
        # Stable column order: known fields then any lineage extras.
        fieldnames = list(records[0].keys())
        with open(self.listings_path(), "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(records)
        return len(records)

    def write_report(self, report: RunReport) -> None:
        with open(self.report_path(), "w", encoding="utf-8") as f:
            json.dump(report.to_dict(), f, indent=2, default=str)

    def find_vehicle_reference_catalog(
        self, market: str, make_key: str, model_key: str | None = None
    ) -> list[VehicleReferenceCatalogRow]:
        return []

    def write_normalization_statistics(self, report: NormalizationStatisticsReport) -> None:
        return None

    @staticmethod
    def _raw_to_dict(raw: RawListing) -> dict:
        return {
            "marketplace": raw.marketplace,
            "marketplace_listing_id": raw.marketplace_listing_id,
            "uuid": raw.uuid,
            "raw_payload": raw.raw_payload,
            "extracted_fields": raw.extracted_fields,
            "fetched_at": raw.fetched_at.isoformat(),
            "scrape_run_id": raw.scrape_run_id,
            "condition": raw.condition,
            "make_slug": raw.make_slug,
        }

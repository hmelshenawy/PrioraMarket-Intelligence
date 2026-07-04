"""CSV StorageAdapter implementation (FR-050..052, FR-053..056).

Persists RawListings (verbatim JSON-lines), canonicalized Listings (CSV),
and RunReport (JSON) under a run-scoped output directory. The ingestion
pipeline depends only on the StorageAdapter interface, so this CSV
implementation can be replaced by a database adapter without touching
ingestion logic (SC-008).
"""

from __future__ import annotations

import csv
import json
from datetime import datetime
from pathlib import Path
from typing import Iterable, Iterator, Optional

from src.common.models import (
    Listing,
    ListingRow,
    RawListing,
    RunContext,
    RunReport,
    RunRow,
    SnapshotRow,
)
from src.storage.interface import MarketplaceSourceNotFoundError


class CsvStorageAdapter:
    """Filesystem CSV/JSON storage implementing StorageAdapter."""

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
        path = self.raw_path()
        count = 0
        with open(path, "w", encoding="utf-8") as f:
            for raw in raw_listings:
                f.write(json.dumps(self._raw_to_dict(raw), default=str) + "\n")
                count += 1
        return count

    def write_listings(self, listings: Iterable[Listing]) -> int:
        listings = list(listings)
        if not listings:
            return 0
        path = self.listings_path()
        records = [listing.to_record() for listing in listings]
        # Stable column order: known fields then any lineage extras.
        known = list(records[0].keys())
        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=known)
            writer.writeheader()
            writer.writerows(records)
        return len(records)

    def write_report(self, report: RunReport) -> None:
        with open(self.report_path(), "w", encoding="utf-8") as f:
            json.dump(report.to_dict(), f, indent=2, default=str)

    def read_raw(self, dataset_version: Optional[str] = None) -> Iterator[RawListing]:
        """Read stored RawListings. If dataset_version given, read that run dir."""
        from datetime import datetime

        path = self.raw_path()
        if dataset_version is not None:
            # dataset_version currently maps to a run_id directory.
            alt = self._root / dataset_version / "raw_listings.jsonl"
            if alt.exists():
                path = alt
        if not path.exists():
            return
        with open(path, encoding="utf-8") as f:
            for line in f:
                if not line.strip():
                    continue
                d = json.loads(line)
                yield RawListing(
                    marketplace=d["marketplace"],
                    marketplace_listing_id=d.get("marketplace_listing_id"),
                    uuid=d.get("uuid"),
                    raw_payload=d.get("raw_payload") or {},
                    extracted_fields=d.get("extracted_fields") or {},
                    fetched_at=datetime.fromisoformat(d["fetched_at"]),
                    scrape_run_id=d["scrape_run_id"],
                    condition=d.get("condition", ""),
                    make_slug=d.get("make_slug"),
                )

    def resolve_marketplace_source_by_code(self, code: str):
        raise MarketplaceSourceNotFoundError(code)

    def find_listing_by_source_uuid(self, source: str, uuid: str) -> ListingRow | None:
        return None

    def insert_listing(self, row: ListingRow) -> int:
        return 0

    def insert_raw_listing(self, raw: RawListing, ctx: RunContext) -> int:
        return 0

    def update_listing(self, listing_id: int, row: ListingRow) -> None:
        return None

    def insert_snapshot(self, snap: SnapshotRow) -> int:
        return 0

    def resolve_run(self, run_name_or_id: str) -> RunRow | None:
        return None

    def read_raw_for_run(self, run_name_or_id: str) -> Iterator[RawListing]:
        yield from self.read_raw(run_name_or_id)

    def insert_ingestion_run(self, run: RunRow) -> int:
        return 0

    def finalize_ingestion_run(
        self, run_id: int, report: RunReport, status: str, completed_at: datetime
    ) -> None:
        return None

    def begin_listing_unit(self) -> None:
        return None

    def commit_listing_unit(self) -> None:
        return None

    def rollback_listing_unit(self) -> None:
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

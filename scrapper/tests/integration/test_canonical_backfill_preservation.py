from __future__ import annotations

from datetime import datetime, timezone

from src.common.models import BackfillListingCandidate, RawListing
from src.maintenance.canonical_backfill import CanonicalBackfillService
from src.storage.in_memory import InMemoryStorageAdapter


def test_canonical_backfill_preserves_raw_payload_and_raw_rows() -> None:
    storage = InMemoryStorageAdapter()
    raw = RawListing(
        marketplace="dubizzle",
        marketplace_listing_id="native-1",
        uuid="uuid-1",
        raw_payload={"make": "Mercedes Benz", "nested": {"keep": True}},
        extracted_fields={"make": "Mercedes Benz"},
        fetched_at=datetime.now(timezone.utc),
        scrape_run_id="run-1",
        condition="used",
        make_slug="mercedes-benz",
    )
    storage.raw.append(raw)
    storage.backfill_candidates.append(
        BackfillListingCandidate(
            id=1,
            source="dubizzle",
            uuid="uuid-1",
            canonical_payload={"make": "Mercedes Benz", "model": "C Class"},
            current_raw_listing_id=1,
        )
    )

    CanonicalBackfillService(storage).run(dry_run=False)

    assert storage.raw == [raw]
    assert storage.raw[0].raw_payload == {"make": "Mercedes Benz", "nested": {"keep": True}}
    assert storage.backfill_updates[0][1]["make"] == "mercedesbenz"

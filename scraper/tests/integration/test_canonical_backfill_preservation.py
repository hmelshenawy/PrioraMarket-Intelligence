from __future__ import annotations

from datetime import datetime, timezone

from src.backfill import CanonicalBackfillService
from src.models import RawListing
from tests.integration.backfill_store_stub import BackfillStoreStub


def test_canonical_backfill_preserves_raw_payload_and_raw_rows() -> None:
    storage = BackfillStoreStub()
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
    storage.rows.append(
        {
            "id": 1,
            "source": "dubizzle",
            "uuid": "uuid-1",
            "make": "Mercedes Benz",
            "model": "C Class",
            "current_raw_listing_id": 1,
        }
    )

    CanonicalBackfillService(storage).run(dry_run=False)

    # Backfill only rewrites listing canonical fields; raw rows are untouched.
    assert storage.raw == [raw]
    assert storage.raw[0].raw_payload == {"make": "Mercedes Benz", "nested": {"keep": True}}
    assert storage.updates[0]["make"] == "mercedesbenz"

from __future__ import annotations

from datetime import datetime, timezone

from src.common.models import RawListing, Scope
from src.replay.replayer import Replayer
from src.storage.in_memory import InMemoryStorageAdapter


def test_replay_uses_explicit_canonicalization_version() -> None:
    storage = InMemoryStorageAdapter()
    storage.write_raw(
        [
            RawListing(
                marketplace="dubizzle",
                marketplace_listing_id="1",
                uuid="uuid-1",
                raw_payload={"id": "1"},
                extracted_fields={
                    "uuid": "uuid-1",
                    "make": "BMW",
                    "model": "7 Series",
                    "trim": "M Sport",
                    "price_aed": 100000,
                },
                fetched_at=datetime.now(timezone.utc),
                scrape_run_id="run-1",
                condition="used",
                make_slug="bmw",
            )
        ]
    )

    replayer = Replayer(
        storage,
        normalizer_version="norm-1",
        canonicalization_version="canonical-key-test",
        scope=Scope("dubizzle", "used", "bmw"),
    )

    first = replayer.replay()
    second = replayer.replay()
    assert first[0].make == second[0].make == "bmw"
    assert first[0].model == second[0].model == "7series"
    assert first[0].canonicalization_version == "canonical-key-test"

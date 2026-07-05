from __future__ import annotations

from src.common.models import BackfillListingCandidate
from src.maintenance.canonical_backfill import CanonicalBackfillService
from src.storage.in_memory import InMemoryStorageAdapter


def test_canonical_backfill_is_idempotent_for_unchanged_inputs() -> None:
    storage = InMemoryStorageAdapter()
    storage.backfill_candidates.append(
        BackfillListingCandidate(
            id=1,
            source="dubizzle",
            uuid="uuid-1",
            canonical_payload={"make": "Mercedes Benz", "model": "C Class"},
            normalization_version="norm-1",
        )
    )

    first = CanonicalBackfillService(storage).run(dry_run=False, batch_size=10)
    second = CanonicalBackfillService(storage).run(dry_run=False, batch_size=10)

    assert first.updated == 1
    assert second.updated == 0
    assert second.unchanged == 1

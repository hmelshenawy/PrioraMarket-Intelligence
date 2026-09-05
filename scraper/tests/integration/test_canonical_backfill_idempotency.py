from __future__ import annotations

from src.backfill import CanonicalBackfillService
from src.models import BackfillListingCandidate
from tests.integration.backfill_store_stub import BackfillStoreStub


def _candidate(id_: int = 1, make: str = "Mercedes Benz") -> BackfillListingCandidate:
    return BackfillListingCandidate(
        id=id_,
        source="dubizzle",
        uuid=f"uuid-{id_}",
        canonical_payload={"make": make, "model": "C Class"},
        normalization_version="norm-1",
    )


def test_canonical_backfill_is_idempotent_for_unchanged_inputs() -> None:
    storage = BackfillStoreStub([_candidate()])

    first = CanonicalBackfillService(storage).run(dry_run=False, batch_size=10)
    second = CanonicalBackfillService(storage).run(dry_run=False, batch_size=10)

    assert first.updated == 1
    assert second.updated == 0
    assert second.unchanged == 1

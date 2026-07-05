from __future__ import annotations

from src.common.models import BackfillListingCandidate
from src.maintenance.canonical_backfill import CanonicalBackfillService
from src.storage.in_memory import InMemoryStorageAdapter


class FailingStorage(InMemoryStorageAdapter):
    def update_listing_backfill_payload(self, *args, **kwargs) -> None:
        if args[0] == 2:
            raise RuntimeError("boom")
        super().update_listing_backfill_payload(*args, **kwargs)


def _candidate(id_: int) -> BackfillListingCandidate:
    return BackfillListingCandidate(
        id=id_,
        source="dubizzle",
        uuid=f"uuid-{id_}",
        canonical_payload={"make": "Mercedes Benz", "model": f"C {id_}"},
    )


def test_canonical_backfill_reports_partial_failures_and_can_resume() -> None:
    storage = FailingStorage()
    storage.backfill_candidates.extend([_candidate(1), _candidate(2), _candidate(3)])

    first = CanonicalBackfillService(storage).run(dry_run=False, batch_size=2)
    second = CanonicalBackfillService(storage).run(
        dry_run=False, batch_size=2, resume_after_id=first.last_processed_id
    )

    assert first.failures == 1
    assert first.failed_ids == [2]
    assert first.updated == 2
    assert second.scanned == 0

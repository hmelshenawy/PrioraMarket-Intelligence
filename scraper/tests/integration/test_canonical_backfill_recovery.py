from __future__ import annotations

from src.backfill import CanonicalBackfillService
from tests.integration.backfill_store_stub import BackfillStoreStub


class FailingStore(BackfillStoreStub):
    def _apply_update(self, params) -> None:
        if params["listing_id"] == 2:
            raise RuntimeError("boom")
        super()._apply_update(params)


def _candidate(id_: int) -> dict:
    return {
        "id": id_,
        "source": "dubizzle",
        "uuid": f"uuid-{id_}",
        "make": "Mercedes Benz",
        "model": f"C {id_}",
    }


def test_canonical_backfill_reports_partial_failures_and_can_resume() -> None:
    storage = FailingStore([_candidate(1), _candidate(2), _candidate(3)])

    first = CanonicalBackfillService(storage).run(dry_run=False, batch_size=2)
    second = CanonicalBackfillService(storage).run(
        dry_run=False, batch_size=2, resume_after_id=first.last_processed_id
    )

    assert first.failures == 1
    assert first.failed_ids == [2]
    assert first.updated == 2
    assert second.scanned == 0

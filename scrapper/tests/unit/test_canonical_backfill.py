from __future__ import annotations

import pytest

from src.common.models import BackfillListingCandidate
from src.maintenance.canonical_backfill import CanonicalBackfillService
from src.storage.in_memory import InMemoryStorageAdapter
from src.storage.postgres_storage import PostgresStorageAdapter


class _CapturingPostgresStorage(PostgresStorageAdapter):
    def __init__(self):
        super().__init__(pool=None)
        self.sql = ""
        self.params = ()

    def _fetchall(self, sql: str, params: tuple = {}):
        self.sql = sql
        self.params = params
        return []


def _candidate(id_: int = 1, make: str = "Mercedes Benz") -> BackfillListingCandidate:
    return BackfillListingCandidate(
        id=id_,
        source="dubizzle",
        uuid=f"uuid-{id_}",
        canonical_payload={
            "make": make,
            "model": "C Class",
            "fuel_type": "Gasoline",
            "condition": "Used",
        },
        normalization_version="norm-1",
        current_raw_listing_id=99,
    )


def test_backfill_dry_run_reports_changes_without_updates() -> None:
    storage = InMemoryStorageAdapter()
    storage.backfill_candidates.append(_candidate())

    report = CanonicalBackfillService(storage).run(dry_run=True, batch_size=1)

    assert report.scanned == 1
    assert report.changed == 1
    assert report.updated == 0
    assert storage.backfill_updates == []
    assert storage.normalization_statistics[0].operation == "backfill"


def test_backfill_execute_updates_in_batches() -> None:
    storage = InMemoryStorageAdapter()
    storage.backfill_candidates.extend([_candidate(1), _candidate(2, make="BMW")])

    report = CanonicalBackfillService(storage).run(dry_run=False, batch_size=1)

    assert report.scanned == 2
    assert report.updated == 2
    assert report.last_processed_id == 2
    assert storage.backfill_updates[0][1]["make"] == "mercedesbenz"
    assert storage.backfill_updates[1][1]["make"] == "bmw"


def test_backfill_validates_batch_size() -> None:
    with pytest.raises(ValueError, match="batch_size"):
        CanonicalBackfillService(InMemoryStorageAdapter()).run(dry_run=True, batch_size=0)


def test_postgres_backfill_selection_without_resume_has_no_nullable_parameter() -> None:
    storage = _CapturingPostgresStorage()

    list(storage.read_listing_backfill_candidates(batch_size=100, after_id=None))

    assert "WHERE (%s IS NULL OR id > %s)" not in storage.sql
    assert "WHERE id > %s" not in storage.sql
    assert storage.params == (100,)


def test_postgres_backfill_selection_with_resume_filters_by_id() -> None:
    storage = _CapturingPostgresStorage()

    list(storage.read_listing_backfill_candidates(batch_size=100, after_id=25))

    assert "WHERE id > %s" in storage.sql
    assert storage.params == (25, 100)

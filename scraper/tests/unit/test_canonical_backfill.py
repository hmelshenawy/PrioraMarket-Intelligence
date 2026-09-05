from __future__ import annotations

import pytest

from src.backfill import CanonicalBackfillService


class _FakeCursor:
    def __init__(self, conn):
        self._conn = conn
        self._sql = ""
        self._params: tuple = ()

    def execute(self, sql, params=()):
        self._sql = sql
        self._params = params
        if "UPDATE listing" in sql:
            self._conn.updates.append(dict(params))

    def fetchone(self):
        rows = self._conn.matching_rows(self._sql, self._params)
        return rows[0] if rows else None

    def fetchall(self):
        return self._conn.matching_rows(self._sql, self._params)

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False


class _FakeBackfillConn:
    """Minimal fake connection: canned listing rows + recorded updates."""

    def __init__(self, rows):
        self._rows = [dict(row) for row in rows]
        self.updates = []  # recorded UPDATE param dicts

    def cursor(self):
        return _FakeCursor(self)

    def matching_rows(self, sql, params):
        if "FROM vehicle_reference_catalog" in sql:
            return []  # catalog lookups find nothing
        after_id, limit = (params[0], params[1]) if len(params) == 2 else (None, params[0])
        rows = [row for row in self._rows if after_id is None or row["id"] > after_id]
        return [dict(row) for row in rows[:limit]]


def _row(id_: int = 1, make: str = "Mercedes Benz") -> dict:
    return {
        "id": id_,
        "source": "dubizzle",
        "uuid": f"uuid-{id_}",
        "make": make,
        "model": "C Class",
        "trim": None,
        "condition": "Used",
        "fuel_type": "Gasoline",
        "transmission": None,
        "regional_spec": None,
        "body_type": None,
        "seller_type": None,
        "vehicle_condition": None,
        "specs": None,
        "color": None,
        "canonical_hash": "hash",
        "normalization_version": "norm-1",
        "canonicalization_version": None,
        "current_raw_listing_id": 99,
    }


def test_backfill_dry_run_reports_changes_without_updates() -> None:
    conn = _FakeBackfillConn([_row()])

    report = CanonicalBackfillService(conn).run(dry_run=True, batch_size=1)

    assert report.scanned == 1
    assert report.changed == 1
    assert report.updated == 0
    assert conn.updates == []


def test_backfill_execute_updates_in_batches() -> None:
    conn = _FakeBackfillConn([_row(1), _row(2, make="BMW")])

    report = CanonicalBackfillService(conn).run(dry_run=False, batch_size=1)

    assert report.scanned == 2
    assert report.updated == 2
    assert report.last_processed_id == 2
    assert conn.updates[0]["make"] == "mercedesbenz"
    assert conn.updates[1]["make"] == "bmw"


def test_backfill_unchanged_candidate_is_not_updated() -> None:
    row = _row()
    row.update(
        {
            "make": "mercedesbenz",
            "model": "cclass",
            "fuel_type": "petrol",
            "condition": "used",
            "vehicle_condition": "used",
            "canonicalization_version": "canonical-key-1",
        }
    )
    conn = _FakeBackfillConn([row])

    report = CanonicalBackfillService(conn).run(dry_run=False, batch_size=1)

    assert report.scanned == 1
    assert report.changed == 0
    assert report.unchanged == 1
    assert report.updated == 0
    assert conn.updates == []


def test_backfill_candidate_failure_is_recorded_not_raised() -> None:
    class _BadConn(_FakeBackfillConn):
        def cursor(self):
            cursor = super().cursor()
            original_execute = cursor.execute

            def execute(sql, params=()):
                if "UPDATE listing" in sql:
                    raise RuntimeError("database down")
                return original_execute(sql, params)

            cursor.execute = execute
            return cursor

    conn = _BadConn([_row()])

    report = CanonicalBackfillService(conn).run(dry_run=False, batch_size=1)

    assert report.scanned == 1
    assert report.failures == 1
    assert report.failed_ids == [1]
    assert report.updated == 0


def test_backfill_validates_batch_size() -> None:
    with pytest.raises(ValueError, match="batch_size"):
        CanonicalBackfillService(_FakeBackfillConn([])).run(dry_run=True, batch_size=0)


class _CapturingConn:
    """Records the SQL issued by the backfill candidate query."""

    def __init__(self):
        self.sql = ""
        self.params = ()

    def cursor(self):
        return self

    def execute(self, sql: str, params: tuple = ()):
        self.sql = sql
        self.params = params
        return self

    def fetchall(self):
        return []

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False


def test_postgres_backfill_selection_without_resume_has_no_nullable_parameter() -> None:
    from src.store import backfill_repo

    conn = _CapturingConn()

    list(backfill_repo.read_listing_backfill_candidates(conn, batch_size=100, after_id=None))

    assert "WHERE (%s IS NULL OR id > %s)" not in conn.sql
    assert "WHERE id > %s" not in conn.sql
    assert conn.params == (100,)


def test_postgres_backfill_selection_with_resume_filters_by_id() -> None:
    from src.store import backfill_repo

    conn = _CapturingConn()

    list(backfill_repo.read_listing_backfill_candidates(conn, batch_size=100, after_id=25))

    assert "WHERE id > %s" in conn.sql
    assert conn.params == (25, 100)

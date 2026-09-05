"""In-memory fake connection shared by canonical-backfill tests.

Mimics the psycopg connection API (``cursor()`` with
``execute``/``fetchone``/``fetchall``) that the backfill and catalog repo
functions use. UPDATE params are applied to the canned listing rows so
idempotency can be observed across runs, without touching PostgreSQL.
Raw listings are never touched by backfill.
"""

from __future__ import annotations

_CANONICAL_COLUMNS = (
    "make",
    "model",
    "trim",
    "condition",
    "fuel_type",
    "transmission",
    "regional_spec",
    "body_type",
    "seller_type",
    "vehicle_condition",
    "specs",
    "color",
    "canonical_hash",
    "normalization_version",
    "canonicalization_version",
)


class _Cursor:
    def __init__(self, conn):
        self._conn = conn
        self._sql = ""
        self._params: tuple = ()

    def execute(self, sql, params=()):
        self._sql = sql
        self._params = params
        if "UPDATE listing" in sql:
            self._conn._apply_update(params)

    def fetchone(self):
        rows = self._conn.matching_rows(self._sql, self._params)
        return rows[0] if rows else None

    def fetchall(self):
        return self._conn.matching_rows(self._sql, self._params)

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False


class BackfillStoreStub:
    def __init__(self, candidates=()):
        # Canned listing-table rows (dicts keyed by column name). Accepts
        # either plain row dicts or BackfillListingCandidate objects.
        self.rows = []
        for candidate in candidates:
            if isinstance(candidate, dict):
                row = dict(candidate)
            else:
                row = {
                    "id": candidate.id,
                    "source": candidate.source,
                    "uuid": candidate.uuid,
                    "current_raw_listing_id": candidate.current_raw_listing_id,
                    "normalization_version": candidate.normalization_version,
                }
                row.update(candidate.canonical_payload)
            self.rows.append(row)
        self.raw = []  # raw listings are never touched by backfill
        self.updates = []  # recorded UPDATE param dicts

    def cursor(self):
        return _Cursor(self)

    def _apply_update(self, params):
        self.updates.append(dict(params))
        row = next(row for row in self.rows if row["id"] == params["listing_id"])
        row.update({key: params[key] for key in _CANONICAL_COLUMNS})

    def matching_rows(self, sql, params):
        if "FROM vehicle_reference_catalog" in sql:
            return []  # catalog lookups find nothing
        after_id, limit = (params[0], params[1]) if len(params) == 2 else (None, params[0])
        rows = [dict(row) for row in self.rows if after_id is None or row["id"] > after_id]
        return rows[:limit]

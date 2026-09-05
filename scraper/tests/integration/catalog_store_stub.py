"""In-memory ``vehicle_reference_catalog`` fake connection for sync tests.

Mimics the psycopg connection API that the catalog repo uses, mirroring
the idempotent upsert semantics (insert / unchanged / conflict) without
touching PostgreSQL.
"""

from __future__ import annotations


class _Cursor:
    def __init__(self, stub):
        self._stub = stub
        self._pending = None

    def execute(self, sql, params=()):
        if sql.lstrip().upper().startswith("SELECT"):
            market, make_key, model_key, generation, body_code = params
            self._pending = next(
                (
                    row
                    for row in self._stub.vehicle_reference_catalog
                    if row["market"] == market
                    and row["make_key"] == make_key
                    and row["model_key"] == model_key
                    and row["generation"] == generation
                    and row["body_code"] == body_code
                ),
                None,
            )
        elif "INSERT INTO" in sql:
            row = dict(params)
            row["id"] = self._stub._next_id
            self._stub._next_id += 1
            self._stub.vehicle_reference_catalog.append(row)
            self._pending = None
        elif "UPDATE" in sql:
            params = dict(params)
            row = next(r for r in self._stub.vehicle_reference_catalog if r["id"] == params["id"])
            row.update(params)
            self._pending = None

    def fetchone(self):
        return self._pending

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False


class CatalogStoreStub:
    def __init__(self):
        self.vehicle_reference_catalog: list[dict] = []
        self._next_id = 1

    def cursor(self):
        return _Cursor(self)

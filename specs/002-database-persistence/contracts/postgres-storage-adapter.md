# Contract: PostgresStorageAdapter

**Feature**: 002 — Database Persistence Foundation
**Spec refs**: FR-002, FR-006, FR-060, FR-061, NFR-002, NFR-003, NFR-009, SC-007

`PostgresStorageAdapter` is the relational database persistence
implementation for PostgreSQL/Supabase. It conforms to the extended
`StorageAdapter` interface and owns **only** backend-specific implementation:
database calls and database transactions as requested by the
`PersistenceService` (FR-002).

## Implementation boundaries

- The database driver (`psycopg` 3 — R-1) is imported only in
  `src/db/connection.py` and `src/storage/postgres_storage.py`. No other
  module imports the driver, an ORM, a query builder, or a schema-generated
  module (SC-007).
- The ORM/query-builder/library choice is internal to this module and
  `src/db/connection.py`; it is **not** an ORM (R-1). SQL is hand-written and
  parameterized.
- The adapter contains **no** marketplace-specific logic, **no**
  ingestion/normalization/canonicalization logic, and **no** duplicated
  business rules (FR-002, FR-061, R-001). It executes exactly the operations
  the `PersistenceService` requests.

## Behavioral contract

- All Feature 001 four operations behave per the Feature 001 contract
  (`write_raw`, `write_listings`, `write_report`, `read_raw`), adapted to
  PostgreSQL rows.
- The additive Feature 002 operations implement the upsert/snapshot/run
  resolution/transaction-control surface (see
  `storage-adapter-extension.md`).
- `read_raw_for_run` selects `raw_listing` rows by `ingestion_run_id` in
  deterministic order (by `id`) — the basis for deterministic replay
  (FR-032, FR-033, R-004).
- `upsert_marketplace_source` upserts by `code` (R-9).
- `find_listing_by_source_uuid` selects by the `(source, uuid)` unique key.
- Transaction control maps to `psycopg` 3 transaction blocks; a per-listing
  unit is committed or rolled back exactly as the service requests (FR-054,
  FR-055, NFR-010).
- `insert_ingestion_run` enforces the unique `name` constraint; on a
  unique-violation it raises a named error the service maps to "retry with a
  disambiguator" (R-009, FR-011a).

## Failure modes (FR-053)

- `StorageConnectionError` — DB unreachable / `DATABASE_URL` invalid.
- `StorageSchemaError` — required tables/constraints missing (migrations not
  applied).
- `StorageConstraintError` — unique-constraint violation (e.g., run-name
  collision); surfaced to the service for disambiguator retry.

These are distinct, named failure modes; the pipeline fails fast with a clear
message and never produces partial silent output (R-005, NFR-004).

## Test contract (NFR-009)

The adapter MUST have unit/integration tests covering the backend persistence
operations, transaction control (commit/rollback), and
replay-from-ingestion-run. No business rule is tested through the adapter
alone — business rules are tested at the `PersistenceService` level.
# Implementation Plan: Database Persistence Foundation

**Branch**: `002-database-persistence` | **Date**: 2026-07-04 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/002-database-persistence/spec.md`

## Summary

Connect the frozen Feature 001 ingestion pipeline to PostgreSQL/Supabase by
introducing a `PersistenceService` business-rule layer between ingestion and
the existing `StorageAdapter` interface, and adding a conforming
`PostgresStorageAdapter` behind it. The flow becomes
Pipeline → `PersistenceService` → `StorageAdapter` → backend, with all
business persistence rules (deduplication by source + uuid, newest-wins,
meaningful-change detection via `canonicalHash`, `ListingSnapshot` creation
decision, per-listing transaction orchestration, replay run resolution) owned
**only** by the `PersistenceService`. The pipeline, extraction, normalization,
canonicalization, and validation code remain untouched and depend only on the
service, never on a database client, ORM, query builder, or schema.

The `IngestionRun` (renamed from Feature 001's `ScrapeRun` concept) becomes the
primary replay and lineage unit, correcting the ADR-012 gap: replay resolves a
named run via `replay --run <run-name-or-id> --normalization-version <version>`
and rebuilds listings from database-backed `RawListings` without marketplace
access. `DatasetVersion`, `DatasetVersionRun`, `datasetKey`, dataset grouping,
`ReplayRun`, disappearance inference, scheduling, search, analytics, AI, ML,
and authentication are explicitly out of scope. CSV and in-memory backends
remain available and passing; backend selection is configuration-only.

The plan delivers in nine incremental phases, each ending in a working,
testable system: Database Foundation → Schema → Persistence Layer → Listing
Persistence Logic → Ingestion Integration → Replay Integration → Backend
Selection → Testing → Documentation/ADRs.

## Technical Context

**Language/Version**: Python 3.11 (Feature 001 runtime; this feature extends
the existing pipeline, does not reimplement it).

**Primary Dependencies**: Feature 001 base (`requests`, `python-dotenv`,
structured logging, `pytest`, `pytest-mock`, `ruff`, `black`). New for this
feature: the approved database access approach (PostgreSQL driver + migration
tooling) documented in `research.md`. Database access is isolated behind
`PostgresStorageAdapter` and the `src/db/` connection modules; no database
access library, ORM, query builder, or schema-generated module leaks into
ingestion, normalization, canonicalization, validation, or the
`PersistenceService` (NFR-003, SC-007).

**Storage**: PostgreSQL/Supabase (production relational database) via a new
`PostgresStorageAdapter`; CSV and in-memory backends preserved unchanged
(Feature 001). The `StorageAdapter` interface is extended in a
backward-compatible way (ADR-documented) to expose the insert/update/read
operations and transaction control the `PersistenceService` needs.

**Testing**: `pytest` (unit, integration, contract, migration, replay,
transaction-rollback, regression). A live PostgreSQL instance is required for
integration/migration tests (local Docker Postgres or Supabase project; CI
service container). Feature 001 acceptance/contract tests must continue to
pass unchanged.

**Target Platform**: Cross-platform Python (Windows/Linux); single-process,
run-on-demand CLI execution. No scheduling, no orchestration, no
long-running services.

**Project Type**: Library + CLI (importable ingestion + persistence package
with run/replay entry points and a migration entry point).

**Performance Goals**: A real ingestion run persists raw listings, canonical
listings, snapshots, and run metadata to PostgreSQL with counts that reconcile
with the run report; per-listing atomic persistence; replay over a fixed run
+ normalization version is deterministic and completes without marketplace
access. No hard latency SLO is introduced in this feature (single-process,
run-on-demand).

**Constraints**: No direct database/ORM/query-builder/schema imports in
ingestion, extraction, normalization, canonicalization, validation, or the
`PersistenceService` (NFR-003, SC-007). No business rules inside any storage
adapter (FR-005, FR-061). No `DatasetVersion`/`datasetKey`/`ReplayRun`/
disappearance inference (FR-014, FR-036, NFR-011, NFR-012). Feature 001
artifacts frozen (FR-063). Per-listing atomic transactions with rollback
(FR-054/055, NFR-010). Secrets via configuration only (NFR-007). Migrations
only, idempotent and ordered (FR-040/042).

**Scale/Scope**: One marketplace (Dubizzle) exercised end-to-end, but all
persistence logic is marketplace-agnostic (Constitution Principle XII). The
schema supports multiple marketplaces, countries, and categories without
rework. Baseline volumes per the Feature 001 full sweep (≈25k used + ≈4k new)
govern index/constraint choices; no sharding or partitioning in this feature.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

Evaluated against the PrioraMarket Intelligence Constitution v1.1.0.

| Principle | Status | Evidence |
|-----------|--------|----------|
| I. Documentation First | ✅ Pass | Plan, data model, contracts, and ADRs produced/updated before implementation; spec is source of truth. |
| II. Design Before Implementation | ✅ Pass | Plan + research + data model + contracts precede tasks/implementation. |
| III. Domain-Driven Architecture | ✅ Pass | All work is within the Data Ingestion bounded context; no new bounded context introduced. |
| IV. Clean Layered Architecture | ✅ Pass | Pipeline (service) → `PersistenceService` (business rules) → `StorageAdapter` (repository, persistence only) → backend. No business logic in adapters; no database logic in the service. |
| V. API First | ⚠ N/A | No REST APIs in scope (internal pipeline + CLI); out of scope by spec NFR-012. Future feature exposes APIs. |
| VI. Database as Source of Truth | ✅ Pass | PostgreSQL becomes the authoritative source after ingestion; replay reads internal data only. |
| VII. Historical Data Preservation | ✅ Pass | `RawListings` immutable/verbatim; `ListingSnapshot` append-only; `IngestionRun` + run report retained; updates never destroy history. |
| VIII. AI Assists, Never Invents | ✅ N/A | No AI in this feature. |
| IX. Analytics Before AI | ✅ N/A | No analytics/AI in this feature. |
| X. Machine Learning as a Product Feature | ✅ N/A | No ML in this feature; `DatasetVersion`/dataset engineering deferred (spec FR-014). |
| XI. Data Quality Before Intelligence | ✅ Pass | Feature 001 validation/canonicalization/dedup gate runs before persistence (unchanged); invalid records counted as skipped, not persisted. |
| XII. Scalability by Design | ✅ Pass | Marketplace-agnostic persistence; schema supports multiple marketplaces/countries/categories; marketplace-specific logic stays in the Dubizzle adapter. |
| XIII. Backend-Centric Business Logic | ✅ Pass | All persistence business rules in `PersistenceService`; CLI is a thin wiring entry point only. |
| XIV. Modularity | ✅ Pass | Pipeline depends only on `PersistenceService`; service depends only on `StorageAdapter` interface; adapter internals private; interface extension is backward-compatible and ADR-documented. |
| XV. Security by Default | ✅ Pass | DB credentials via env config only; fail-fast on missing config; no secrets in logs/reports; external data treated as untrusted and validated before persistence. |
| XVI. Simplicity Over Complexity | ✅ Pass | YAGNI applied: no `DatasetVersion`, no `ReplayRun`, no disappearance inference, no scheduling; simplest backend-selection mechanism (config + CLI flag). |

**Gate result**: PASS. No unjustified violations. The single ⚠ (API First
N/A) is explicitly out of scope by approved spec NFR-012 and does not block.
Complexity Tracking left empty.

### Post-Design Re-check (after Phase 1)

Re-evaluated after `research.md`, `data-model.md`, and `contracts/` were
produced. The design introduces **no new constitution violations**:

- **IV (Clean Layered Architecture)**: confirmed — `PersistenceService`
  holds business rules; `PostgresStorageAdapter` is a repository
  (persistence only); the service imports no DB driver (NFR-003, SC-007
  enforced by a static gate test). The backward-compatible
  `StorageAdapter` extension (R-8) keeps the repository boundary intact.
- **VI (Database as Source of Truth)**: confirmed — PostgreSQL is the
  authoritative source after ingestion; replay reads internal data only.
- **VII (Historical Data Preservation)**: confirmed — `RawListing`
  immutable, `ListingSnapshot` append-only (no update/delete path),
  `IngestionRun` + run report retained; migrations are reversible and
  history-preserving (RESTRICT cascades).
- **XIV (Modularity)**: confirmed — pipeline depends only on
  `PersistenceService`; service depends only on the `StorageAdapter`
  interface; DB driver confined to `src/db/connection.py` +
  `src/storage/postgres_storage.py`; interface extension is additive and
  ADR-documented (ADR-014).
- **XV (Security by Default)**: confirmed — DB credentials via env only,
  fail-fast on missing config, no secrets in logs/reports.
- **XVI (Simplicity Over Complexity)**: confirmed — no ORM/query-builder
  layer (R-1), no `DatasetVersion`/`ReplayRun`/disappearance inference,
  simplest backend selection; lightweight reversible SQL migrations (R-2).

**Post-design gate result**: PASS. Complexity Tracking remains empty.

## Project Structure

### Documentation (this feature)

```text
specs/002-database-persistence/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output
│   ├── persistence-service.md
│   ├── storage-adapter-extension.md
│   ├── postgres-storage-adapter.md
│   ├── replay-cli.md
│   └── run-naming.md
└── tasks.md             # Phase 2 output (/speckit-tasks — not created here)
```

### Source Code (repository root)

```text
src/
├── config/
│   └── config.py            # Extended: DB/backend config (STORAGE_BACKEND, DATABASE_URL, ...)
├── common/
│   ├── models.py            # Extended: PersistenceService domain DTOs (no DB imports)
│   ├── canonical_hash.py    # NEW: deterministic canonical-hash generation (pure Python)
│   ├── run_naming.py        # NEW: run-name slug + disambiguator (pure Python)
│   └── logger.py            # Unchanged
├── marketplaces/
│   └── dubizzle/            # Unchanged (Feature 001 frozen)
├── ingestion/
│   ├── pipeline.py          # Unchanged behavior; persistence wired via PersistenceService at runner boundary
│   ├── runner.py            # Extended: backend selection, --run replay, postgres wiring
│   ├── normalizer.py        # Unchanged
│   └── canonicalizer.py     # Unchanged
├── persistence/
│   └── service.py           # NEW: PersistenceService — all business persistence rules
├── storage/
│   ├── interface.py         # Extended (backward-compatible): operations + transaction control
│   ├── csv_storage.py       # Unchanged (Feature 001 frozen)
│   ├── in_memory.py         # Unchanged (Feature 001 frozen)
│   └── postgres_storage.py  # NEW: PostgresStorageAdapter — DB calls + transactions only
├── db/
│   ├── connection.py        # NEW: connection/session factory (only module that imports the DB driver)
│   ├── migrations/          # NEW: ordered, idempotent SQL migrations
│   └── migrate.py           # NEW: migration CLI entry point (apply/rollback/status)
├── replay/
│   └── replayer.py          # Extended: resolve run via PersistenceService; DB-backed read_raw
└── reporting/
    └── run_report.py        # Unchanged

migrations/                  # (alt location if db/migrations not used; decided in research.md)

tests/
├── unit/
│   ├── test_canonical_hash.py
│   ├── test_run_naming.py
│   ├── test_persistence_service.py
│   └── test_replayer.py          # extended
├── integration/
│   ├── test_postgres_storage.py
│   ├── test_persistence_end_to_end.py
│   ├── test_migrations.py
│   ├── test_replay_db.py
│   ├── test_transaction_rollback.py
│   └── test_backend_selection.py
├── contract/
│   └── test_storage_adapter.py   # extended to include postgres adapter
└── regression/
    └── test_feature001_unchanged.py  # Feature 001 acceptance/contract re-run
```

**Structure Decision**: Single-project layout (Feature 001's `src/` package).
New subsystems are added as new modules/packages (`src/persistence/`,
`src/db/`, `src/common/canonical_hash.py`, `src/common/run_naming.py`,
`src/storage/postgres_storage.py`). No new top-level project. The DB driver is
isolated to `src/db/connection.py` + `src/storage/postgres_storage.py`; the
migration tool is isolated to `src/db/migrate.py` + `src/db/migrations/`.
Feature 001 modules are imported but not modified (frozen).

## Implementation Phases

> Each phase ends in a working, testable system. No phase leaves the project
> in a broken or partially usable state. Feature 001 behavior is green at
> every phase boundary. Phases are ordered by dependency; the implementation
> order is the phase number. Per-phase: **Depends on**, **Deliverable**,
> **Steps**, **Validation Checkpoint**, **Rollback Strategy**, **Risks**,
> **Complexity**, **Testing Strategy**.

---

### Phase 1 — Database Foundation

**Depends on**: Phase 0 (`research.md` resolves driver + migration tool).

**Deliverable**: Database connectivity verified from the runtime; a clean
PostgreSQL/Supabase instance is reachable, configurable, and a no-op migration
round-trip succeeds.

**Steps**:
1. Add the approved database access dependencies (PostgreSQL driver +
   migration tooling, per `research.md`) to `pyproject.toml` /
   `requirements.txt` under a new `db` optional-dependency group (and `dev`
   for migration tooling).
2. Extend `src/config/config.py` with database/backend configuration:
   `STORAGE_BACKEND` (`csv` | `in-memory` | `postgres`, default `csv`),
   `DATABASE_URL`, `DB_POOL_MIN`, `DB_POOL_MAX`, `DB_CONNECT_TIMEOUT`,
   migration schema search-path, and Supabase-compatible options. Required DB
   keys are validated **only when `postgres` is selected** (fail fast with a
   named `ConfigurationError` identifying the missing value — FR-053, US4-AC5).
3. Create `src/db/connection.py` — the **only** module that imports the DB
   driver. Exposes a connection/session factory bound to `DATABASE_URL` with
   pooling and timeout. No business logic, no SQL beyond connection setup.
4. Create `src/db/migrate.py` — migration CLI entry point invoked via the
   module entrypoint (`python -m src.db.migrate apply`,
   `python -m src.db.migrate status`, `python -m src.db.migrate rollback`).
   Create the `src/db/migrations/` directory with migration conventions
   (ordered, timestamped, idempotent, reversible up/down — Constitution
   "Migration Strategy").
5. Add a baseline no-op/initial migration (e.g., an `audit` or extension
   marker) to prove the round-trip: apply → status → rollback → apply.
6. Update `.env.example` with all new DB/backend variables, descriptions, and
   non-secret placeholders (Constitution "Environment Variables").
7. Local dev setup: document a one-command local Postgres (Docker) and a
   Supabase project option in `quickstart.md` (Phase 1 design output).

**Validation Checkpoint**:
- `migrate apply` succeeds against an empty database; `migrate status` reports
  applied; `migrate rollback` reverts; re-apply is idempotent.
- A connectivity smoke test (`tests/integration/test_db_connection.py`) opens
  and closes a connection from `src/db/connection.py` using `DATABASE_URL`.
- `STORAGE_BACKEND=postgres` with a missing `DATABASE_URL` raises a named
  `ConfigurationError` (fail fast).
- Feature 001 tests still pass (no regression — `STORAGE_BACKEND` defaults to
  `csv`).

**Rollback Strategy**: Revert dependency additions and config additions;
`migrate rollback` the baseline migration. Feature 001 path is untouched
because `STORAGE_BACKEND` defaults to `csv`.

**Risks**:
- R-1.1 Driver/version incompatibility with Supabase (TLS, pooling, pgbouncer).
  Mitigation: validate against both local Postgres and a Supabase project in
  integration tests; pin versions.
- R-1.2 Config-fail-fast gap leaking a missing value into a late-stage error.
  Mitigation: unit-test the config validator for every required DB key.

**Complexity**: Low–Medium. Mostly wiring + tooling selection.

**Testing Strategy**:
- Unit: config validation for all three backends and missing-DB-key cases.
- Integration: `test_db_connection.py` (connect/close), `test_migrations.py`
  (apply/rollback/idempotency on an empty DB).

---

### Phase 2 — Database Schema

**Depends on**: Phase 1 (connectivity + migration tooling).

**Deliverable**: A fresh database created completely from migrations with all
five entities, keys, foreign keys, indexes, unique constraints, cascade
rules, JSON columns, and timestamps.

**Steps**:
1. Author the schema migration(s) in `src/db/migrations/` (ordered, reversible)
   for the five entities per `data-model.md` (Phase 1):
   - `marketplace_source` — reference/seeded data (`code` unique, `name`,
     `country`, `base_url`, `created_at`, `updated_at`).
   - `ingestion_run` — unique readable `name` (unique constraint — FR-011a,
     R-009), `marketplace_source_id` FK, `marketplace`, `condition`, `make`,
     `status`, `started_at`/`completed_at`, page/record counts, `duration_ms`,
     `config_snapshot` (JSONB), `report_json` (JSONB), `created_at`.
   - `raw_listing` — `marketplace_source_id` FK, `ingestion_run_id` FK
     (cascade on run delete optional/RESTRICT — decided in `data-model.md`),
     `source`, `uuid`, `raw_payload` (JSONB, verbatim), `raw_hash`,
     `adapter_version`, `marketplace_schema_version`/`marketplace_payload_version`,
     `extracted_at`, `created_at`. Index on `ingestion_run_id`; index on
     `(source, uuid)`.
   - `listing` — `marketplace_source_id` FK, `source`, `uuid`, canonical
     fields, `status` (default `ACTIVE`), `first_seen_at`/`last_seen_at`,
     `first_seen_run_id`/`last_seen_run_id` FKs to `ingestion_run`,
     `current_raw_listing_id` FK, `canonical_hash`, `normalization_version`,
     `created_at`/`updated_at`. **Unique `(source, uuid)`** (dedup key —
     FR-041, SC-005). Index on `canonical_hash`, on `last_seen_run_id`.
   - `listing_snapshot` — `id`, `listing_id` FK, `ingestion_run_id` FK,
     `raw_listing_id` FK, `snapshot_hash`, **single `canonical_payload`
     (JSONB)** (no duplicated per-field columns — FR-022, SC-005),
     `changed_fields` (JSONB), `captured_at`, `created_at`. Append-only;
     index on `listing_id`/`captured_at`.
2. Define cascade rules: `raw_listing` → `ingestion_run` (RESTRICT or CASCADE
   per `data-model.md`; history-preserving default RESTRICT), `listing` →
   `marketplace_source` (RESTRICT), `listing_snapshot` → `listing` (CASCADE on
   listing delete is acceptable since snapshots are owned by the listing; but
   listing deletion is not performed in this feature — Constitution VII).
3. Define timestamps: all entities carry `created_at`; mutable entities
   (`marketplace_source`, `listing`) carry `updated_at`. JSON columns typed
   `JSONB` for indexability and native storage.
4. No `dataset_version`, `dataset_version_run`, or `replay_run` tables exist
   (SC-005, FR-014, FR-036).
5. **MarketplaceSource seed migration**: include a seed migration that inserts
   the initial marketplace reference data, idempotent on re-apply:
   - `code`: `dubizzle_uae`
   - `name`: `Dubizzle UAE`
   - `country`: `UAE`
   - `base_url`: `https://dubizzle.com`

   The seed MUST be repeatable/idempotent (e.g., `INSERT ... ON CONFLICT (code)
   DO NOTHING`, or an upsert that does not clobber `updated_at` when the row
   already exists). `IngestionRun` MUST reference an existing
   `MarketplaceSource`; the `PersistenceService` resolves `MarketplaceSource`
   by `code` rather than relying on every run to dynamically create it. The
   seed is part of the migration set so a fresh database is provisioned with
   the reference row alongside the schema (US5, SC-005).

**Validation Checkpoint**:
- `migrate apply` on an empty DB creates all five tables with required columns,
  PKs, FKs, the `(source, uuid)` unique constraint, and the
   `ingestion_run.name` unique constraint (SC-005).
- `migrate apply` again is idempotent (no error) (FR-042, US5-AC2).
- An additive follow-up migration applies without data loss on a populated DB
  (US5-AC3).
- A schema-introspection test asserts table/column/constraint existence.
- The `MarketplaceSource` seed row for `dubizzle_uae` exists after
  `migrate apply`, and re-applying migrations does not duplicate or clobber it
  (idempotent seed).

**Rollback Strategy**: `migrate rollback` reverts the schema migration in
reverse order; down-migrations drop tables cleanly. Re-apply restores.

**Risks**:
- R-2.1 JSONB-vs-JSON portability between local Postgres and Supabase.
  Mitigation: use `JSONB` consistently; test on both.
- R-2.2 Constraint naming collisions or FK ordering errors breaking
  create-from-scratch. Mitigation: ordered migrations; introspection test.
- R-2.3 Accidental duplicated per-field snapshot columns. Mitigation: schema
  test asserts `listing_snapshot` has exactly one `canonical_payload` and no
  per-field columns (SC-005).

**Complexity**: Medium. Schema design is the core data-modeling effort.

**Testing Strategy**:
- Migration tests: create-from-scratch, idempotency, reversibility, additive
  evolution (US5).
- Schema introspection tests: required tables, columns, PKs, FKs, unique
  constraints, no `dataset_version`/`replay_run` tables.

---

### Phase 3 — Persistence Layer

**Depends on**: Phase 2 (schema exists).

**Deliverable**: `PersistenceService`, the extended `StorageAdapter`
interface, and `PostgresStorageAdapter` compile and pass interface/contract
tests. No business logic inside the adapter.

**Steps**:
1. Extend `src/storage/interface.py` in a **backward-compatible** way
   (ADR-documented per FR-072/R-001a): add the operations the
   `PersistenceService` needs — e.g., `upsert_listing`, `insert_snapshot`,
   `find_listing_by_source_uuid`, `read_raw_for_run(run_name_or_id)`,
   `resolve_run(run_name_or_id)`, `begin_listing_unit()`/`commit()`/`rollback()`
   transaction control as requested by the service. CSV/in-memory adapters
   gain trivial conforming implementations (or a capability flag) so the
   existing Feature 001 contract test stays green. The interface MUST NOT
   encode business rules (FR-006).
2. Implement `src/persistence/service.py` — `PersistenceService` owns all
   business persistence rules (FR-005, FR-061): dedup by source + uuid,
   newest-wins, meaningful-change detection (compare new canonical hash to
   `Listing.canonicalHash`), snapshot creation decision, per-listing
   transaction orchestration, replay run resolution by name or id. It operates
   on marketplace-agnostic domain objects. It imports **no** DB driver/ORM/
   query-builder/schema module (NFR-003). It depends only on the
   `StorageAdapter` interface.
3. Implement `src/storage/postgres_storage.py` — `PostgresStorageAdapter`
   conforming to the (extended) interface. Owns **only** DB calls and
   transactions as requested by the service (FR-002). The database access
   approach is internal to this module and `src/db/connection.py` (per
   `research.md`). No marketplace logic, no
   ingestion/normalization/canonicalization logic, no duplicated business
   rules (FR-002, FR-061).
4. Keep `CsvStorageAdapter` and `InMemoryStorageAdapter` conforming to the
   extended interface (Feature 001 behavior unchanged — FR-003, FR-062).

**Validation Checkpoint**:
- `PersistenceService` unit tests pass with a fake/in-memory adapter
  (dedup, newest-wins, snapshot decision, run resolution) — no DB needed.
- `PostgresStorageAdapter` passes the extended contract test (protocol
  conformance + behavior parity for the operations the pipeline relies on).
- SC-007 grep: `src/storage/postgres_storage.py` and `src/db/connection.py`
  are the only modules importing a DB client/ORM/query-builder/schema module;
  `src/persistence/service.py` and ingestion modules import none.
- Feature 001 contract test (`tests/contract/test_storage_adapter.py`) still
  passes for CSV and in-memory.

**Rollback Strategy**: The extended interface is additive; removing the new
operations and the `persistence/` + `storage/postgres_storage.py` modules
restores the Feature 001 state. No Feature 001 file is modified in behavior.

**Risks**:
- R-001a (Adapter contract mismatch): the Feature 001 four-operation interface
  may not cleanly express upsert/snapshot/transaction/run-resolution.
  Mitigation: backward-compatible extension only; contract test green for all
  three adapters; ADR (FR-072).
- R-001 (Business rule leakage into adapters): rules could be duplicated in
  `PostgresStorageAdapter`. Mitigation: SC-007 grep + contract test;
  PersistenceService unit tests with a fake adapter prove the rules live in
  the service.
- R-002 (Coupling leakage): DB imports leaking into ingestion/service.
  Mitigation: SC-007 grep gate in tests.

**Complexity**: Medium–High. This is the architectural core of the feature.

**Testing Strategy**:
- Unit: `PersistenceService` against a fake adapter (no DB).
- Contract: extended `StorageAdapter` test parametrized over
  `csv`/`in-memory`/`postgres`.
- Static: SC-007 grep gate as an automated test.

---

### Phase 4 — Listing Persistence Logic

**Depends on**: Phase 3 (service + adapter compile and pass contract tests).

**Deliverable**: Listing persistence fully operational — deduplication,
newest-wins, `canonicalHash` comparison, snapshot creation, lineage updates,
and per-listing transaction boundaries all work against PostgreSQL.

**Steps**:
1. Implement `src/common/canonical_hash.py` — deterministic canonical-hash
   generation from the complete canonical listing state, order-independent
   where applicable (FR-023). The exact participating fields are an
   implementation detail documented in `data-model.md`/`research.md`, not in
   the spec. Pure Python; no DB imports.
2. Implement the per-listing persistence flow in `PersistenceService`
   (FR-054/055/056, NFR-010):
   - Resolve/seed `MarketplaceSource` (reference data).
   - Persist `RawListing` (verbatim, with content hash + ingestion metadata).
   - `find_listing_by_source_uuid`:
     - **No prior row**: insert `Listing` with `canonicalHash` = initial hash,
       `firstSeenAt`/`lastSeenAt` = now, `firstSeenRunId`/`lastSeenRunId` =
       current run, `status = ACTIVE`, `normalizationVersion`. No snapshot
       (FR-025).
     - **Prior row, new hash == `canonicalHash`**: refresh only
       `lastSeenAt`/`lastSeenRunId`; no snapshot; `canonicalHash` unchanged
       (FR-024).
     - **Prior row, new hash != `canonicalHash`** (meaningful change):
       create `ListingSnapshot` with prior `canonicalPayload` (single JSONB),
       `changedFields`, `snapshotHash`, `rawListingId`, `ingestionRunId`,
       `capturedAt`; update `Listing` to newest data; update `canonicalHash`
       to the new hash; refresh `lastSeenAt`/`lastSeenRunId`
       (FR-022, FR-026, US2-AC2).
   - All of the above in a **single atomic transaction per listing**; any
     failure rolls back the whole listing unit (FR-054/055).
3. Implement run-level reconciliation: `IngestionRun` status and run report
   reflect per-listing failures (a failure is recorded, the run continues with
   remaining listings where possible, status = `PARTIAL_FAILED` when failures
   occurred but data was produced — FR-056, SC-010).
4. Implement `MarketplaceSource` resolution in the `PersistenceService`
   (FR-010): the service resolves the `MarketplaceSource` by `code`
   (e.g., `dubizzle_uae`) from the seeded reference data (Phase 2 seed
   migration). The service MUST NOT rely on every run dynamically creating
   marketplace source data; if the required `MarketplaceSource` is missing,
   the run fails fast with a clear, named error. `IngestionRun` references the
   resolved, pre-existing `MarketplaceSource`.

**Validation Checkpoint**:
- US1 independent test: one run persists one `IngestionRun` (unique readable
  name), one `RawListing` per extracted listing, one `Listing` per validated
  listing with `firstSeenRunId`/`lastSeenRunId` set, and a run report on the
  run — counts reconcile (SC-001).
- US2 independent test: a second run with a changed field produces zero
  duplicate `Listing` rows, updates the current row, updates `canonicalHash`,
  creates exactly one `ListingSnapshot` with single `canonicalPayload`, and
  leaves unchanged listings with no new snapshot (SC-002).
- US2-AC3/AC4: unchanged re-observation refreshes only `lastSeenAt`/
  `lastSeenRunId`; first observation creates no snapshot.
- SC-010: forcing a failure mid-listing-unit leaves no partial state (rollback
  verified); run report reflects the failure.
- The `IngestionRun` references the seeded `MarketplaceSource` (`dubizzle_uae`);
  if the required `MarketplaceSource` is missing, the run fails fast with a
  clear, named error and does not create a partial run.

**Rollback Strategy**: Per-listing transactions roll back automatically on
failure; the run report records the failure. A failed run can be re-run
without duplicating listings (idempotent upsert by source + uuid).

**Risks**:
- R-003 (Snapshot noise or loss): wrong change-detection basis floods or drops
  snapshots. Mitigation: single deterministic `canonicalHash` basis (FR-023,
  FR-026); tests for changed and unchanged re-observation.
- R-005 (Partial silent output): mid-run failure leaves inconsistent state.
  Mitigation: per-listing atomic transactions (FR-054/055), run-status
  reconciliation (NFR-004), IngestionRun status/run report (FR-056).
- R-009 (Run-name collision): two runs same scope/second. Mitigation: unique
  constraint + disambiguator (Phase 6 run-naming; constraint exists from
  Phase 2).

**Complexity**: High. The correctness-critical business core.

**Testing Strategy**:
- Unit: `canonical_hash` determinism/order-independence; `PersistenceService`
  dedup/newest-wins/snapshot-decision/lineage against a fake adapter.
- Integration: end-to-end persistence to PostgreSQL (US1, US2).
- Transaction-rollback: force failure mid-unit; assert no partial state
  (SC-010).

---

### Phase 5 — Ingestion Integration

**Depends on**: Phase 4 (listing persistence operational).

**Deliverable**: Real ingestion persists data to PostgreSQL via the
`PersistenceService`, with extraction/normalization/canonicalization/
validation behavior unchanged.

**Steps**:
1. Wire the `PersistenceService` into the runner boundary
   (`src/ingestion/runner.py`) so that when `STORAGE_BACKEND=postgres` the
   pipeline persists through `PersistenceService` → `PostgresStorageAdapter`
   instead of writing CSVs. The pipeline's internal stages
   (fetch/normalize/canonicalize/validate/dedup) are **not modified**
   (FR-060, NFR-003, SC-006).
2. Preserve Feature 001 behavior for `csv` and `in-memory` backends: the
   default path is unchanged (FR-003, FR-062, NFR-008).
3. Ensure the run report is stored on the `IngestionRun` record when the
   PostgreSQL backend is used (FR-052, US1-AC1).
4. Preserve structured logging across all backends; no secrets in logs
   (FR-051, NFR-007). Distinct, named failure modes for storage error,
   missing config, missing schema (FR-053).
5. The CLI `run` command accepts backend selection (Phase 7 details the
   flag/config; here the wiring is in place).

**Validation Checkpoint**:
- A real ingestion run with `STORAGE_BACKEND=postgres` persists raw listings,
  canonical listings, snapshots (on change), and run metadata to PostgreSQL,
  and counts reconcile with the run report (US1, SC-001, NFR-001).
- A second run for the same scope updates existing listings by source + uuid
  with snapshots on meaningful change (US2, SC-002).
- Extraction/normalization/canonicalization/validation code is byte-for-byte
  unchanged (diff gate) — only the runner wiring and new modules differ
  (SC-006, US4-AC4).
- Feature 001 acceptance tests pass unchanged with `STORAGE_BACKEND=csv`
  (NFR-008).

**Rollback Strategy**: Set `STORAGE_BACKEND=csv` (default) to revert to
Feature 001 behavior at any time. No Feature 001 module is modified in
behavior.

**Risks**:
- R-007 (Feature 001 regression): wiring breaks CSV/in-memory. Mitigation:
  Feature 001 tests run unchanged (FR-062, NFR-008, SC-004); regression test
  suite.
- R-002 (Coupling leakage): wiring accidentally imports DB driver into the
  pipeline. Mitigation: SC-007 grep gate; pipeline depends only on
  `PersistenceService`.

**Complexity**: Medium. Mostly boundary wiring; correctness rests on Phases 3–4.

**Testing Strategy**:
- Integration: `test_persistence_end_to_end.py` (real run → PostgreSQL).
- Regression: Feature 001 acceptance + contract tests unchanged.
- Static: SC-007 grep gate.

---

### Phase 6 — Replay Integration

**Depends on**: Phase 5 (ingestion persists to PostgreSQL).

**Deliverable**: Replay works without marketplace access, resolving an
`IngestionRun` by name or id and rebuilding listings from database-backed
`RawListings` deterministically.

**Steps**:
1. Implement run-name generation in `src/common/run_naming.py`
   (FR-011, FR-011a): deterministic
   `run_<marketplace>_<condition>_<make-or-scope>_<yyyyMMdd>_<HHmmss>` UTC,
   with a short disambiguator (hash or sequence suffix) on collision. Pure
   Python; slug rules + disambiguator documented in `research.md` and an ADR
   (FR-071). The unique constraint on `ingestion_run.name` (Phase 2) enforces
   uniqueness; the service retries/appends a disambiguator on collision.
2. Implement replay run resolution in the `PersistenceService`
   (FR-030): `resolve_run(run_name_or_id)` → `IngestionRun`. Resolution logic
   lives in the service, not in any adapter (FR-005, FR-030).
3. Extend `read_raw_for_run(run_name_or_id)` on the `StorageAdapter` interface
   (backward-compatible) so replay loads only the `RawListings` linked to the
   selected `IngestionRun` via `ingestion_run_id` (FR-032). CSV/in-memory
   adapters gain conforming implementations (Feature 001 `read_raw` preserved).
4. Update `src/replay/replayer.py` and `src/ingestion/runner.py` replay path:
   `replay --run <run-name-or-id> --normalization-version <version>` resolves
   the run via the service, loads its `RawListings`, rebuilds `Listings` using
   the selected normalization version (the existing
   Normalizer/Canonicalizer/Validator), and writes transient output. No
   marketplace network access (FR-031). No `ReplayRun` row (FR-036).
5. Determinism: deterministic `RawListing` load order (e.g., by `id`/`uuid`)
   and deterministic rebuild so the same run + version yields identical output
   across executions (FR-033, NFR-005, R-004).
6. Unknown run: replay completes with zero listings and a clear message
   (FR-035, US3-AC5).
7. Replay under a newer normalization version MAY update a `Listing`'s
   `normalizationVersion` (FR-013, SC-011) — note in `data-model.md`/contracts.

**Validation Checkpoint**:
- US3 independent test: persist one run, then
  `replay --run <run-name-or-id> --normalization-version v1` rebuilds
  listings from only that run's `RawListings`, with zero marketplace access,
  and produces identical output when run twice (SC-003, NFR-005).
- Replay with an unknown run name/id completes with zero listings and a clear
  message, no error (FR-035).
- Replay never imports or calls a marketplace adapter (network-disabled test).
- Feature 001 replay tests are not modified; new behavior is covered by new
  tests (R-008).

**Rollback Strategy**: Replay is read-only and transient; rollback is a no-op.
The Feature 001 `--dataset` path is preserved (not deleted) per R-008; the new
`--run` path is additive.

**Risks**:
- R-004 (Non-deterministic replay): order-dependent rebuild. Mitigation:
  deterministic load order + deterministic rebuild (FR-032/033); test by
  running replay twice.
- R-008 (Replay contract change): Feature 001 used `--dataset` (ADR-012).
  Mitigation: new `--run` behavior is part of acceptance (US3) and ADR
  (FR-071); Feature 001 replay tests not modified.

**Complexity**: Medium. Run-naming + resolution + read-path; reuses existing
replay domain logic.

**Testing Strategy**:
- Unit: `run_naming` (format, UTC, disambiguator on collision);
  `PersistenceService.resolve_run` by name and by id.
- Integration: `test_replay_db.py` — replay over a DB-backed run, twice,
  assert identical output; network-disabled assertion; unknown-run message.

---

### Phase 7 — Backend Selection

**Depends on**: Phase 5 (postgres wiring) + Phase 6 (replay wiring).

**Deliverable**: All three storage backends (CSV, in-memory, PostgreSQL) are
interchangeable via configuration/CLI only — switching requires no code change
to ingestion logic.

**Steps**:
1. Implement the backend-selection factory at the runner boundary: read
   `STORAGE_BACKEND` (env) and/or a CLI `--storage-backend` flag; instantiate
   `CsvStorageAdapter`, `InMemoryStorageAdapter`, or
   `PersistenceService` + `PostgresStorageAdapter` accordingly.
2. When `postgres` is selected, validate required DB config (Phase 1) and
   fail fast with a named message on missing values or missing schema
   (FR-053, US4-AC5, edge case).
3. Add the CLI `--storage-backend` flag to `run` and `replay` subcommands
   (FR-004).
4. Ensure the in-memory and CSV paths still use the Feature 001 adapters
   directly (or via the service with a no-op transaction shim) — whichever
   keeps Feature 001 behavior byte-equivalent (SC-006).

**Validation Checkpoint**:
- US4 independent test: the same ingestion scope run three times with CSV,
  in-memory, and PostgreSQL produces equivalent persisted output for each
  backend; ingestion/extraction/normalization/canonicalization/validation
  code is unchanged across all three (SC-006).
- US4-AC5: missing required DB config with `postgres` selected fails fast
  with a named message.
- Feature 001 CSV and in-memory tests pass unchanged (US4-AC1/AC2, NFR-008).

**Rollback Strategy**: Default `STORAGE_BACKEND=csv` restores Feature 001
behavior. Backend selection is config/flag only.

**Risks**:
- R-1.3 Backend wiring asymmetry breaking substitutability. Mitigation:
  contract test parametrized over all three backends (SC-004).

**Complexity**: Low. Configuration + factory wiring.

**Testing Strategy**:
- Integration: `test_backend_selection.py` — three backends, equivalent
  output, code-unchanged assertion.
- Contract: `test_storage_adapter.py` parametrized over
  `csv`/`in-memory`/`postgres`.

---

### Phase 8 — Testing

**Depends on**: Phases 1–7 (functionality in place).

**Deliverable**: A complete test suite covering unit, integration, migration,
replay, transaction-rollback, contract, and regression tests, with Feature 001
compatibility maintained.

**Steps**:
1. **Unit tests**:
   - `test_canonical_hash.py` — determinism, order-independence,
     change-sensitivity (FR-023, R-003).
   - `test_run_naming.py` — format, UTC, disambiguator on collision
     (FR-011a, R-009).
   - `test_persistence_service.py` — dedup, newest-wins, snapshot decision,
     lineage, run resolution — against a fake adapter, no DB (NFR-009).
   - `test_replayer.py` — extended for `--run` resolution.
2. **Integration tests** (require a live PostgreSQL; local Docker + Supabase):
   - `test_postgres_storage.py` — backend persistence operations + transaction
     control (NFR-009).
   - `test_persistence_end_to_end.py` — real run → PostgreSQL (US1, US2,
     SC-001/002).
   - `test_migrations.py` — create-from-scratch, idempotency, reversibility,
     additive evolution (US5, SC-005).
   - `test_replay_db.py` — DB-backed replay, determinism, no-marketplace,
     unknown-run (US3, SC-003).
   - `test_transaction_rollback.py` — forced mid-unit failure leaves no
     partial state; run report reflects failure (SC-010, NFR-010).
   - `test_backend_selection.py` — three backends equivalent (US4, SC-006).
3. **Migration tests**: schema introspection (required tables/columns/PKs/
   FKs/unique constraints; no `dataset_version`/`replay_run` tables) (SC-005);
   the migration commands are exercised through the module entrypoint
   (`python -m src.db.migrate apply|status|rollback`).
4. **Replay tests**: determinism (run twice → identical), no marketplace
   access, unknown-run message (FR-031..035, NFR-005).
5. **Transaction rollback tests**: per-listing atomicity (FR-054/055, NFR-010,
   SC-010).
6. **Contract tests**: extend `tests/contract/test_storage_adapter.py` to
   parametrize over `csv`/`in-memory`/`postgres`; all conform to the extended
   `StorageAdapter` interface (SC-004, NFR-002).
7. **Regression tests**: `tests/regression/test_feature001_unchanged.py`
   re-runs Feature 001 acceptance + contract suites unchanged (FR-062, NFR-008,
   R-007); a diff/static gate that ingestion/extraction/normalization/
   canonicalization/validation modules are unchanged.
8. **Static gate test**: SC-007 grep — no DB/ORM/query-builder/schema imports
   in ingestion/extraction/normalization/canonicalization/validation or
   `PersistenceService`; no business rules inside any adapter.
9. **MarketplaceSource seed tests**:
   - The `dubizzle_uae` seed row exists after `python -m src.db.migrate apply`
     with `name`=`Dubizzle UAE`, `country`=`UAE`,
     `base_url`=`https://dubizzle.com`.
   - The seed operation is idempotent: re-applying migrations does not
     duplicate or clobber the row.
   - `IngestionRun` references the seeded `MarketplaceSource` (`dubizzle_uae`).
   - If the required `MarketplaceSource` is missing (e.g., seeded row deleted
     before a run), the `IngestionRun` fails fast with a clear, named error
     and no partial run is created.

**Validation Checkpoint**:
- Full suite green: unit + integration + migration + replay + rollback +
  contract + regression.
- SC-007 grep gate passes.
- Feature 001 acceptance + contract tests pass without modification
  (NFR-008, SC-004).

**Rollback Strategy**: Tests are additive; removing the new test files
restores the Feature 001 test set.

**Risks**:
- R-8.1 Integration tests flaky without a stable DB fixture. Mitigation:
  Docker Postgres service container + `pytest` fixtures with per-test schema
  isolation (apply/rollback per test).
- R-8.2 False-positive grep gate. Mitigation: precise patterns; allow-list
  for `src/db/` and `src/storage/postgres_storage.py` only.

**Complexity**: Medium. Test breadth, not depth of new logic.

**Testing Strategy**: This phase *is* the testing strategy; it is validated by
the Definition of Done (all suites green + constitution compliance).

---

### Phase 9 — Documentation & ADRs

**Depends on**: Phases 1–8 (behavior finalized).

**Deliverable**: Documentation for database setup, local development, Supabase
configuration, migration workflow, replay workflow, and storage backend
selection; required ADRs only.

**Steps**:
1. Author `quickstart.md` (Phase 1 design output, finalized here):
   - Local PostgreSQL (Docker) one-command setup.
   - Supabase project configuration.
   - Environment configuration (`.env` variables).
   - Migration workflow (`migrate apply/status/rollback`).
   - Running an ingestion with each backend.
   - Replay workflow (`replay --run <run-name-or-id> --normalization-version
     <version>`).
   - Backend selection via config/CLI (FR-070).
2. Add ADRs (only where an architectural decision is required — FR-071,
   FR-072):
   - **ADR-013 (IngestionRun as the Replay and Lineage Unit)** — records the
     decision, the deferral of `DatasetVersion`/Dataset grouping to a future
     Dataset Engineering feature, the run naming convention, and a reference
     to ADR-012 (FR-071, SC-009).
   - **ADR-014 (Database Persistence Strategy)** — records
     `PersistenceService`/`StorageAdapter` layering, transaction boundaries,
     upsert-by-source-+-uuid, snapshot trigger via `canonicalHash`, the
     backward-compatible `StorageAdapter` interface extension, and the
     database access approach documented in `research.md` (FR-072, SC-009).
3. Do **not** modify Feature 001 documentation, PRD, Constitution, SAD, spec,
   plan, or tasks (FR-063). ADRs only.

**Validation Checkpoint**:
- US6 independent test: following `quickstart.md` from a clean environment, an
  operator connects to PostgreSQL/Supabase and runs a persisted ingestion
  without reading source code (SC-008).
- ADR-013 and ADR-014 exist with the required content and ADR-012 reference
  (SC-009).
- Documentation explains backend selection and `--run` replay (US6-AC2).

**Rollback Strategy**: Documentation is additive; removing the new files
restores the prior doc set. ADRs are append-only (Constitution VII).

**Risks**:
- R-9.1 Doc drift from implementation. Mitigation: `/speckit-analyze`
  cross-artifact consistency check before Done (Constitution "Documentation
  Alignment").

**Complexity**: Low. Writing + ADR capture.

**Testing Strategy**: Doc-walkthrough test (US6 independent test); ADR
presence/content assertions in the regression suite.

---

## Phase Dependency Graph

```text
Phase 0 (research) ──▶ Phase 1 (DB foundation) ──▶ Phase 2 (schema)
                                                       │
                                                       ▼
                                                  Phase 3 (persistence layer)
                                                       │
                                                       ▼
                                                  Phase 4 (listing persistence logic)
                                                       │
                                                       ▼
                                                  Phase 5 (ingestion integration)
                                                       │
                                          ┌────────────┴───────────┐
                                          ▼                        ▼
                                   Phase 6 (replay)          Phase 7 (backend selection)
                                          └────────────┬───────────┘
                                                       ▼
                                                  Phase 8 (testing)
                                                       │
                                                       ▼
                                                  Phase 9 (docs + ADRs)
```

## Implementation Order & Incremental Delivery

- **Order**: 0 → 1 → 2 → 3 → 4 → 5 → (6 ∥ 7) → 8 → 9.
- Phases 6 and 7 may proceed in parallel after Phase 5; both depend only on
  Phase 5.
- **Incremental delivery**: every phase boundary leaves the project green:
  - After P1: DB reachable; Feature 001 still green (`csv` default).
  - After P2: full schema from migrations; Feature 001 still green.
  - After P3: persistence layer compiles + contract tests green; Feature 001
    still green.
  - After P4: listing persistence works against PostgreSQL; Feature 001 still
    green.
  - After P5: real ingestion persists to PostgreSQL; Feature 001 still green.
  - After P6: replay works from DB-backed runs; Feature 001 still green.
  - After P7: three backends interchangeable; Feature 001 still green.
  - After P8: full suite green.
  - After P9: documented + ADRs recorded.

## Complexity Tracking

> No Constitution Check violations require justification. Left empty.

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| — | — | — |
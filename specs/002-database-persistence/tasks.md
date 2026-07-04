# Tasks: Database Persistence Foundation

**Input**: Design documents from `/specs/002-database-persistence/`

**Prerequisites**: plan.md (required), spec.md (required), research.md, data-model.md, contracts/, quickstart.md

**Tests**: Included — the spec mandates testability (NFR-009, NFR-010) and the plan has a dedicated testing phase (Phase 8). Tests are written first (Red-Green) per the Constitution testing strategy.

**Organization**: Tasks are grouped by user story (US1–US6 from spec.md) to enable independent implementation and testing. Shared infrastructure that blocks all stories is in Phase 2 (Foundational).

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies on incomplete tasks)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Single project**: `src/`, `tests/` at repository root (per plan.md "Project Structure").
- New modules: `src/persistence/`, `src/db/`, `src/common/canonical_hash.py`, `src/common/run_naming.py`, `src/storage/postgres_storage.py`.
- Feature 001 modules are imported but NOT modified in behavior (frozen).

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization, dependencies, and configuration for the database backend.

- [X] T001 Create new project structure per implementation plan: `src/persistence/__init__.py`, `src/db/__init__.py`, `src/db/migrations/`, `src/common/canonical_hash.py`, `src/common/run_naming.py`, `src/storage/postgres_storage.py`, `tests/regression/`
- [X] T002 Add approved database access dependencies (PostgreSQL driver + migration tooling per `research.md`) to `pyproject.toml` and `requirements.txt` under a new `db` optional-dependency group (and `dev` for migration tooling)
- [X] T003 [P] Update `.env.example` with Feature 002 variables (`STORAGE_BACKEND`, `DATABASE_URL`, `DB_POOL_MIN`, `DB_POOL_MAX`, `DB_CONNECT_TIMEOUT`) with descriptions and non-secret placeholders
- [X] T004 [P] Extend `src/config/config.py` with backend selection (`STORAGE_BACKEND` `csv|in-memory|postgres`, default `csv`) and database config (`DATABASE_URL`, `DB_POOL_*`, `DB_CONNECT_TIMEOUT`); validate required DB keys only when `postgres` is selected, failing fast with a named `ConfigurationError`

**Checkpoint**: Project builds; config loads for all three backends; Feature 001 tests still pass (`csv` default).

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented: database connectivity, schema + seed, extended storage interface, and shared pure-Python helpers.

**⚠️ CRITICAL**: No user story work can begin until this phase is complete.

- [X] T005 [P] Implement `src/db/connection.py` — connection/session pool factory bound to `DATABASE_URL` with `DB_POOL_MIN`/`DB_POOL_MAX`/`DB_CONNECT_TIMEOUT`; this is the only module (with `src/storage/postgres_storage.py`) that imports the database driver
- [X] T006 [P] Implement `src/db/migrate.py` — migration CLI entrypoint invoked via `python -m src.db.migrate apply|status|rollback`; loads migrations from `src/db/migrations/`
- [X] T007 Create the schema migration in `src/db/migrations/` for all five entities (`marketplace_source`, `ingestion_run`, `raw_listing`, `listing`, `listing_snapshot`) with PKs, FKs, indexes, `UNIQUE (source, uuid)` on `listing`, `UNIQUE ingestion_run.name`, `JSONB` columns (`raw_payload`, `canonical_payload`, `changed_fields`, `config_snapshot`, `report_json`), `TIMESTAMPTZ` columns, and cascade rules per `data-model.md`; reversible up/down
- [X] T008 Create the MarketplaceSource seed migration in `src/db/migrations/` inserting `dubizzle_uae` (`name`=`Dubizzle UAE`, `country`=`UAE`, `base_url`=`https://dubizzle.com`) idempotently via `INSERT ... ON CONFLICT (code) DO NOTHING`
- [X] T009 [P] Extend `src/storage/interface.py` additively and backward-compatibly with: `resolve_marketplace_source_by_code` (lookup only — returns an existing `MarketplaceSource` by its unique `code`; MUST NOT insert or update; raises a named error when the code does not exist), `find_listing_by_source_uuid`, `insert_listing`, `update_listing`, `insert_snapshot`, `resolve_run`, `read_raw_for_run`, `insert_ingestion_run`, `finalize_ingestion_run`, `begin_listing_unit`, `commit_listing_unit`, `rollback_listing_unit` (default no-op implementations; no business rules). `MarketplaceSource` creation is exclusively the responsibility of migrations/seeding (T008), never the adapter.
- [X] T010 [P] Add conforming no-op/trivial implementations of the new `StorageAdapter` operations to `src/storage/csv_storage.py` and `src/storage/in_memory.py` without changing Feature 001 behavior
- [X] T011 [P] Implement `src/common/canonical_hash.py` — deterministic, order-independent canonical-hash generation over the complete canonical listing state (sorted keys, `sha256` hex); pure Python, no DB imports. The hash MUST represent ONLY the canonical business state of a `Listing`. Volatile/operational metadata MUST NEVER participate in hash generation; this includes, at minimum: `created_at`, `updated_at`, `first_seen_at`, `last_seen_at`, `first_seen_run_id`, `last_seen_run_id`, `ingestion_run_id`, any database-generated identifiers (surrogate PKs, `current_raw_listing_id`), all timestamps, and any other operational metadata that does not represent the canonical listing state. Excluded fields are listed in `data-model.md`.
- [X] T012 [P] Implement `src/common/run_naming.py` — `run_<marketplace>_<condition>_<make>_<yyyyMMdd>_<HHmmss>` UTC + 8-char hex disambiguator on collision; ASCII-slug rules per `contracts/run-naming.md`; pure Python, no DB imports

**Checkpoint**: Foundation ready — `python -m src.db.migrate apply` creates the full schema + seed; the extended `StorageAdapter` interface compiles; CSV/in-memory tests still pass; user story implementation can begin.

---

## Phase 3: User Story 1 — Persist a Full Ingestion Run to the Database (Priority: P1) 🎯 MVP

**Goal**: A real ingestion run persists raw listings, canonical listings, and run metadata into PostgreSQL/Supabase; the database becomes the source of truth after ingestion.

**Independent Test**: Run the Feature 001 ingestion pipeline against one make/condition with `STORAGE_BACKEND=postgres`; verify the database contains one `IngestionRun` (unique readable name), one `RawListing` per extracted listing (verbatim, linked by `ingestion_run_id`), one `Listing` per validated listing (`first_seen_run_id` and `last_seen_run_id` set), and a run report on the `IngestionRun` — counts reconciling with the run report (SC-001).

### Tests for User Story 1 (write first, ensure they FAIL)

- [X] T013 [P] [US1] Unit test for run-name generation (format, UTC, slug rules, disambiguator on collision) in `tests/unit/test_run_naming.py`
- [X] T014 [P] [US1] Unit test for canonical-hash determinism, order-independence, and volatile-metadata exclusion in `tests/unit/test_canonical_hash.py` (assert that changes to excluded fields — `created_at`, `updated_at`, `first_seen_at`/`last_seen_at`, `first_seen_run_id`/`last_seen_run_id`, `ingestion_run_id`, surrogate ids, timestamps — do NOT change the hash, while a meaningful business-state change does)
- [X] T015 [P] [US1] Integration test for full-run persistence to PostgreSQL (counts reconcile, raw verbatim, lineage set, run report stored) in `tests/integration/test_persistence_end_to_end.py`

### Implementation for User Story 1

- [X] T016 [US1] Implement `PostgresStorageAdapter` persistence operations in `src/storage/postgres_storage.py` (`resolve_marketplace_source_by_code` — returns the existing row by `code` and raises a named `MarketplaceSourceNotFoundError` when missing; MUST NOT insert or update `MarketplaceSource`; `insert_ingestion_run`, raw listing insert, `insert_listing`, `finalize_ingestion_run`, transaction control) — DB calls only, no business rules
- [X] T017 [US1] Implement `PersistenceService.begin_run` and the first-observation path of `persist_listing` in `src/persistence/service.py` (call `resolve_marketplace_source_by_code` to look up the seeded `MarketplaceSource` by `code`; handle `MarketplaceSourceNotFoundError` by failing the run fast with a clear, named error; MUST NEVER create or update `MarketplaceSource` — creation is migrations/seeding only; generate run name; persist `RawListing` + `Listing` with `canonical_hash` and `first_seen`/`last_seen` lineage; no snapshot on first observation)
- [X] T018 [US1] Wire `PersistenceService` + `PostgresStorageAdapter` into the `run` command for `STORAGE_BACKEND=postgres` at the runner boundary in `src/ingestion/runner.py` (Feature 001 pipeline stages unchanged)
- [X] T019 [US1] Store the run report on the `IngestionRun` record (`report_json`) when the PostgreSQL backend is used in `src/persistence/service.py`

**Checkpoint**: User Story 1 fully functional and independently testable — a real run persists to PostgreSQL and counts reconcile.

---

## Phase 4: User Story 2 — Idempotent Re-Ingestion with Change History (Priority: P1)

**Goal**: Re-running ingestion updates existing listings by source + uuid (newest wins) while preserving prior state in `ListingSnapshot` records on meaningful changes; per-listing atomic transactions.

**Independent Test**: Run ingestion twice against the same scope with a changed field on one listing; verify zero duplicate `Listing` rows per `(source, uuid)`, the changed listing's current row + `canonical_hash` updated, one `ListingSnapshot` with single `canonical_payload` for the change, and unchanged listings with no new snapshot (SC-002). Force a failure mid-listing-unit and verify no partial state (SC-010).

### Tests for User Story 2 (write first, ensure they FAIL)

- [ ] T020 [P] [US2] Unit test for `PersistenceService` dedup / newest-wins / snapshot decision / no-change refresh against a fake adapter in `tests/unit/test_persistence_service.py`
- [ ] T021 [P] [US2] Integration test for re-ingestion change history (snapshot on change, no snapshot on no-change, newest-wins, no duplicates) in `tests/integration/test_persistence_end_to_end.py` (extend)
- [ ] T022 [P] [US2] Transaction rollback test in `tests/integration/test_transaction_rollback.py` (force mid-unit failure → no partial state; run report reflects failure)

### Implementation for User Story 2

- [ ] T023 [US2] Implement meaningful-change detection and snapshot creation in `PersistenceService.persist_listing` in `src/persistence/service.py` (compare new canonical hash to `Listing.canonical_hash`; on change create `ListingSnapshot` with `canonical_payload`, `changed_fields`, `snapshot_hash`, `raw_listing_id`, `ingestion_run_id`, `captured_at`; update `Listing` to newest data and update `canonical_hash`; on no-change refresh only `last_seen_at`/`last_seen_run_id`)
- [ ] T024 [US2] Implement per-listing atomic transaction orchestration (`begin_listing_unit`/`commit`/`rollback`) and run-level reconciliation (`PARTIAL_FAILED` when failures occurred but data produced) in `src/persistence/service.py`

**Checkpoint**: User Stories 1 AND 2 both work independently — idempotent upsert with history and atomic per-listing persistence.

---

## Phase 5: User Story 3 — Replay from an Ingestion Run Using Database Raw Listings (Priority: P1)

**Goal**: Replay resolves an `IngestionRun` by name or id via `replay --run <run-name-or-id> --normalization-version <version>` and rebuilds listings from database-backed `RawListings` without marketplace access, deterministically.

**Independent Test**: Persist one run, then run `replay --run <run-name-or-id> --normalization-version v1`; verify replay resolves the run, loads only its `RawListings`, rebuilds listings with no marketplace access, and produces identical output when run twice (SC-003). An unknown run completes with zero listings and a clear message (FR-035).

### Tests for User Story 3 (write first, ensure they FAIL)

- [ ] T025 [P] [US3] Unit test for `PersistenceService.resolve_run` by name and by id in `tests/unit/test_persistence_service.py` (extend)
- [ ] T026 [P] [US3] Integration test for DB-backed replay (determinism on second run, no marketplace access, unknown-run zero-listings message) in `tests/integration/test_replay_db.py`

### Implementation for User Story 3

- [ ] T027 [US3] Implement `PersistenceService.resolve_run` (by name or id) and `load_raw_for_run` in `src/persistence/service.py` (resolution logic lives in the service, not in any adapter)
- [ ] T028 [US3] Implement `read_raw_for_run` in `src/storage/postgres_storage.py` selecting `raw_listing` rows by `ingestion_run_id` in deterministic order (by `id`)
- [ ] T029 [US3] Update replay to `replay --run <run-name-or-id> --normalization-version <version>` in `src/ingestion/runner.py` (`cmd_replay`) and `src/replay/replayer.py` (reuse Feature 001 Normalizer/Canonicalizer/Validator; no `ReplayRun` row; explicit normalization version required)

**Checkpoint**: All three P1 stories independently functional — persistence, idempotent history, and DB-backed replay.

---

## Phase 6: User Story 4 — Swappable Storage Backend Selected by Configuration (Priority: P2)

**Goal**: Selecting CSV, in-memory, or PostgreSQL via configuration/CLI yields equivalent persisted output with zero changes to ingestion/extraction/normalization/canonicalization/validation code.

**Independent Test**: Run the same scope three times with CSV, in-memory, and PostgreSQL; verify equivalent output per backend and that ingestion/extraction/normalization/canonicalization/validation code is unchanged (SC-006). Missing DB config with `postgres` selected fails fast with a named message (US4-AC5).

### Tests for User Story 4 (write first, ensure they FAIL)

- [ ] T030 [P] [US4] Integration test for backend-selection equivalence (three backends, equivalent output, code-unchanged assertion) in `tests/integration/test_backend_selection.py`
- [ ] T031 [P] [US4] Extend the storage contract test to parametrize over `csv`/`in-memory`/`postgres` in `tests/contract/test_storage_adapter.py`

### Implementation for User Story 4

- [ ] T032 [US4] Implement the backend-selection factory at the runner boundary in `src/ingestion/runner.py` (read `STORAGE_BACKEND` and/or `--storage-backend`; instantiate `CsvStorageAdapter`, `InMemoryStorageAdapter`, or `PersistenceService` + `PostgresStorageAdapter`)
- [ ] T033 [US4] Add the `--storage-backend` CLI flag to the `run` and `replay` subcommands in `src/ingestion/runner.py`
- [ ] T034 [US4] Add named fail-fast errors for missing DB config and missing schema in `src/storage/postgres_storage.py` and `src/config/config.py` (`StorageConnectionError`, `StorageSchemaError`)

**Checkpoint**: All three backends interchangeable via configuration/CLI only.

---

## Phase 7: User Story 5 — Schema Migrations from Scratch (Priority: P2)

**Goal**: Migrations create the full schema from an empty database deterministically; idempotent, reversible, and additive-evolution-safe; the `MarketplaceSource` seed is reproducible.

**Independent Test**: Start from an empty database, `python -m src.db.migrate apply`; verify all five tables, PKs, FKs, `UNIQUE (source, uuid)`, `UNIQUE ingestion_run.name`, single `canonical_payload` column (no duplicated per-field columns), and no `dataset_version`/`replay_run` tables (SC-005). Re-apply is idempotent; rollback reverses; an additive migration applies without data loss. The `dubizzle_uae` seed exists after apply and re-apply does not duplicate it.

> The schema and seed migrations are authored in Phase 2 (T007/T008) because all stories depend on them. This phase owns the migration-quality verification, command-entrypoint tests, and seed tests.

### Tests for User Story 5 (write first, ensure they FAIL)

- [ ] T035 [P] [US5] Migration create-from-scratch schema introspection test (tables, columns, PKs, FKs, unique constraints, single `canonical_payload`, no `dataset_version`/`replay_run` tables) in `tests/integration/test_migrations.py`
- [ ] T036 [P] [US5] Migration idempotency, reversibility, and additive-evolution tests in `tests/integration/test_migrations.py`
- [ ] T037 [P] [US5] MarketplaceSource seed tests (seed exists after apply, idempotent re-apply, `IngestionRun` references seeded source, missing-source fails fast) in `tests/integration/test_migrations.py`
- [ ] T038 [P] [US5] Migration command-entrypoint test exercising `python -m src.db.migrate apply|status|rollback` in `tests/integration/test_migrations.py`

### Implementation for User Story 5

- [ ] T039 [US5] Verify migration ordering/reproducibility and fix any ordering issues in `src/db/migrations/` (timestamped, ordered, reversible up/down)

**Checkpoint**: Migrations are production-quality — reproducible provisioning from scratch, idempotent, reversible, additive-safe; seed verified.

---

## Phase 8: User Story 6 — Documentation and ADRs for the Persistence Strategy (Priority: P3)

**Goal**: Documentation explains Supabase/PostgreSQL configuration, backend selection, and replay; ADRs record `IngestionRun` as the replay/lineage unit, `DatasetVersion` deferral, run naming, and the persistence strategy.

**Independent Test**: Follow `quickstart.md` from a clean environment to configure PostgreSQL/Supabase and run a persisted ingestion without reading source code (SC-008). ADR-013 and ADR-014 exist with the required content and ADR-012 reference (SC-009).

### Implementation for User Story 6

- [ ] T040 [P] [US6] Author ADR-013 (IngestionRun as the replay/lineage unit, deferral of `DatasetVersion`/Dataset grouping, run naming convention, reference to ADR-012) in `docs/adr/ADR-013.md`
- [ ] T041 [P] [US6] Author ADR-014 (database persistence strategy: `PersistenceService`/`StorageAdapter` layering, transaction boundaries, upsert-by-source-+-uuid, snapshot trigger via `canonicalHash`, backward-compatible interface extension, database access approach) in `docs/adr/ADR-014.md`
- [ ] T042 [US6] Finalize `specs/002-database-persistence/quickstart.md` (database setup, Supabase configuration, migration workflow, MarketplaceSource seeding, persisted ingestion, replay, backend selection)
- [ ] T043 [P] [US6] Documentation walkthrough test (operator can configure and run a persisted ingestion from `quickstart.md` alone) in `tests/regression/test_docs_walkthrough.py`

**Checkpoint**: Persistence foundation is operable and architecturally traceable.

---

## Phase 9: Polish & Cross-Cutting Concerns

**Purpose**: Cross-story quality gates — coupling-leak prevention, Feature 001 regression, lint/format, and end-to-end validation.

- [ ] T044 [P] SC-007 static gate test (no DB/ORM/query-builder/schema imports in ingestion/extraction/normalization/canonicalization/validation or `PersistenceService`; no business rules inside any adapter) in `tests/regression/test_no_db_leak.py`
- [ ] T045 [P] Feature 001 regression test (acceptance + contract suites unchanged; ingestion/extraction/normalization/canonicalization/validation modules unchanged) in `tests/regression/test_feature001_unchanged.py`
- [ ] T046 [P] Lint and format clean (`ruff` + `black`) across all new modules in `src/persistence/`, `src/db/`, `src/storage/postgres_storage.py`, `src/common/canonical_hash.py`, `src/common/run_naming.py`
- [ ] T047 Run `specs/002-database-persistence/quickstart.md` validation end-to-end against a clean local PostgreSQL and a Supabase project
- [ ] T048 [P] Verify count reconciliation invariants (NFR-004) in `tests/integration/test_persistence_end_to_end.py` (raw count, listing count, snapshot count, skipped/failures reconcile with run report)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — can start immediately.
- **Foundational (Phase 2)**: Depends on Setup completion — BLOCKS all user stories.
- **User Stories (Phases 3–8)**: All depend on Foundational completion.
  - P1 stories (US1 → US2 → US3) are ordered: US2 builds on US1's persistence; US3 builds on US1's run rows.
  - P2 stories (US4, US5) can proceed after the P1 stories (US4 needs postgres wiring from US1; US5 verifies migrations authored in Phase 2).
  - P3 (US6) can proceed after US1–US3 are functional.
- **Polish (Phase 9)**: Depends on all user stories being complete.

### User Story Dependencies

- **US1 (P1)**: Can start after Foundational — no dependencies on other stories. (MVP)
- **US2 (P1)**: Depends on US1 (re-observation builds on US1's first-observation persistence).
- **US3 (P1)**: Depends on US1 (replay resolves `IngestionRun` rows US1 produces). Independent of US2.
- **US4 (P2)**: Depends on US1 (postgres wiring) and US3 (replay wiring) to exercise all three backends.
- **US5 (P2)**: Depends on Foundational (migrations authored in T007/T008) — independent of US1–US4.
- **US6 (P3)**: Depends on US1–US3 being functional (docs/ADRs describe finalized behavior).

### Within Each User Story

- Tests written FIRST and FAIL before implementation (Red-Green).
- Adapter operations before service logic that uses them.
- Service logic before runner wiring.
- Story complete and independently tested before moving to the next priority.

### Parallel Opportunities

- All Setup tasks marked [P] (T003, T004) can run in parallel.
- All Foundational tasks marked [P] (T005, T006, T009, T010, T011, T012) can run in parallel; T007 → T008 (seed after schema) are sequential.
- Within each story, tests marked [P] can run in parallel.
- US5 and US6 can run in parallel with US4 (different files/concerns).
- Polish tasks T044, T045, T046, T048 are all [P] (different files).

---

## Parallel Example: User Story 1

```bash
# Launch all US1 tests together (write first, ensure they FAIL):
Task: "Unit test for run-name generation in tests/unit/test_run_naming.py"
Task: "Unit test for canonical-hash determinism + volatile-metadata exclusion in tests/unit/test_canonical_hash.py"
Task: "Integration test for full-run persistence in tests/integration/test_persistence_end_to_end.py"

# Then implement (sequential where dependencies exist):
Task: "PostgresStorageAdapter persistence ops in src/storage/postgres_storage.py"
Task: "PersistenceService.begin_run + first-observation persist_listing in src/persistence/service.py"
Task: "Wire PersistenceService into runner in src/ingestion/runner.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup.
2. Complete Phase 2: Foundational (CRITICAL — blocks all stories).
3. Complete Phase 3: User Story 1.
4. **STOP and VALIDATE**: Test US1 independently (real run → PostgreSQL, counts reconcile).
5. The database is now the source of truth for a single run.

### Incremental Delivery

1. Setup + Foundational → foundation ready (schema + seed + interface + helpers).
2. Add US1 → test independently → MVP (persist a full run).
3. Add US2 → test independently (idempotent upsert + history + atomicity).
4. Add US3 → test independently (DB-backed replay).
5. Add US4 → test independently (three backends interchangeable).
6. Add US5 → test independently (migration quality + seed).
7. Add US6 → test independently (docs + ADRs).
8. Polish → cross-cutting gates green.

### Parallel Team Strategy

With multiple developers after Foundational:
- Developer A: US1 → US2 → US3 (P1 chain).
- Developer B: US5 (migration-quality tests, independent of P1).
- Developer C: US6 (docs/ADRs, after US1–US3 behavior is clear).
- US4 after US1 + US3 are merged.

---

## Notes

- [P] tasks = different files, no dependencies on incomplete tasks.
- [Story] label maps a task to its user story for traceability.
- Each user story is independently completable and testable.
- Tests MUST fail before the implementation they guard is written (Red-Green).
- Commit after each task or logical group.
- Stop at any checkpoint to validate a story independently.
- Feature 001 modules are imported but NOT modified in behavior (frozen, FR-063).
- No `DatasetVersion`/`datasetKey`/`ReplayRun`/disappearance inference (FR-014, FR-036, NFR-011, NFR-012).
- No database access library leaks into ingestion, normalization, canonicalization, validation, or `PersistenceService` (NFR-003, SC-007).

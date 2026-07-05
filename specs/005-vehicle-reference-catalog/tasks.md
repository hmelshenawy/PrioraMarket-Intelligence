# Tasks: Canonical Data Model & Vehicle Reference Catalog

**Input**: Design documents from `/specs/005-vehicle-reference-catalog/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, quickstart.md, contracts/

**Tests**: Included because the approved implementation plan explicitly requires Python unit/normalization/catalog sync/migration/replay/backfill tests and backend compatibility verification.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel because it touches different files and does not depend on incomplete tasks.
- **[Story]**: Maps to the user story phase, e.g. `[US1]`.
- Every task includes an exact repository path.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Prepare files, fixtures, and shared documentation references before feature work begins.

- [X] T001 Create canonical vehicle catalog CSV fixture directory in `scrapper/tests/fixtures/vehicle_reference_catalog/`
- [X] T002 [P] Create initial catalog fixture CSV for Mercedes/BMW/VW/Chevy aliases in `scrapper/tests/fixtures/vehicle_reference_catalog/vehicle_reference_catalog.csv`
- [X] T003 [P] Create invalid catalog fixture CSV for synchronization validation failures in `scrapper/tests/fixtures/vehicle_reference_catalog/vehicle_reference_catalog_invalid.csv`
- [X] T004 [P] Create backfill fixture data for existing non-canonical listing rows in `scrapper/tests/fixtures/backfill/listings_before_canonicalization.json`
- [X] T005 [P] Create replay fixture data for canonicalization version checks in `scrapper/tests/fixtures/replay/raw_listings_canonicalization.json`
- [X] T006 Document feature-specific command expectations in `specs/005-vehicle-reference-catalog/quickstart.md`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Define shared domain models, storage boundaries, and migration scaffolding required by all user stories.

**CRITICAL**: No user story work can begin until this phase is complete.

- [X] T007 Extend canonical listing/domain fields for trim, fuel type, transmission, body type, seller type, condition, specs, color, and canonicalization version in `scrapper/src/common/models.py`
- [X] T008 [P] Add normalization statistics domain models for known/unknown/alias/catalog counts in `scrapper/src/common/models.py`
- [X] T009 [P] Add vehicle reference catalog row domain model with market, display values, aliases, confidence, and sync provenance in `scrapper/src/common/models.py`
- [X] T010 Extend storage protocol with catalog lookup, catalog synchronization, normalization statistics, and batched listing-read operations in `scrapper/src/storage/interface.py`
- [X] T011 Add PostgreSQL storage method stubs for catalog lookup, sync, stats persistence, and backfill batches in `scrapper/src/storage/postgres_storage.py`
- [X] T012 Add in-memory storage support for catalog lookup and normalization statistics test doubles in `scrapper/src/storage/in_memory.py`
- [X] T013 Add CSV storage no-op or read-only compatibility behavior for catalog/statistics interface additions in `scrapper/src/storage/csv_storage.py`
- [X] T014 Create forward SQL migration for `vehicle_reference_catalog`, catalog provenance fields, listing categorical fields, and canonicalization version handling in `scrapper/src/db/migrations/202607050001_vehicle_reference_catalog.sql`
- [X] T015 Create rollback SQL migration for vehicle reference catalog schema changes in `scrapper/src/db/migrations/202607050001_vehicle_reference_catalog.rollback.sql`
- [X] T016 [P] Add migration tests for forward/rollback catalog schema evolution in `scrapper/tests/integration/test_vehicle_reference_catalog_migration.py`
- [X] T017 [P] Add storage contract tests for new catalog/statistics/backfill storage protocol methods in `scrapper/tests/contract/test_storage_vehicle_reference_catalog.py`

**Checkpoint**: Shared models, storage boundaries, and migration scaffolding are ready for user stories.

---

## Phase 3: User Story 1 - Persist Canonical Operational Data (Priority: P1) MVP

**Goal**: Newly processed listings store deterministic canonical keys for supported categorical operational fields while raw payloads remain unchanged.

**Independent Test**: Process representative marketplace categorical values and verify listing categorical values are canonical keys, semantic letters/numbers are preserved, unknown values continue through deterministic canonicalization, statistics are emitted, and raw payloads are unchanged.

### Tests for User Story 1

- [X] T018 [P] [US1] Add canonical key generation unit tests for separators, punctuation, semantic preservation, and immutable key examples in `scrapper/tests/unit/test_canonical_key_engine.py`
- [X] T019 [P] [US1] Add canonicalization alias and unknown-value statistics tests in `scrapper/tests/unit/test_canonicalization_statistics.py`
- [X] T020 [P] [US1] Add supported categorical field normalization tests for make, model, trim, fuel type, transmission, body type, seller type, condition, specs, and color in `scrapper/tests/unit/test_supported_categorical_fields.py`
- [X] T021 [P] [US1] Add ingestion integration test proving raw payload preservation and canonical listing persistence in `scrapper/tests/integration/test_ingestion_canonical_persistence.py`
- [X] T022 [P] [US1] Add replay equivalence test for fixed raw inputs and canonicalization version in `scrapper/tests/integration/test_replay_canonicalization_version.py`

### Implementation for User Story 1

- [X] T023 [US1] Implement deterministic canonical key generation helper preserving letters and numbers in `scrapper/src/normalization/canonical_key.py`
- [X] T024 [US1] Implement normalization statistics collector for known, unknown, alias, and catalog matches in `scrapper/src/reporting/normalization_statistics.py`
- [X] T025 [US1] Implement catalog-aware canonicalization engine with alias resolution and version propagation in `scrapper/src/normalization/canonicalization_engine.py`
- [X] T026 [US1] Replace existing make/model canonicalization call sites with the canonicalization engine in `scrapper/src/ingestion/canonicalizer.py`
- [X] T027 [US1] Extend listing copy/update behavior for all supported categorical fields in `scrapper/src/common/models.py`
- [X] T028 [US1] Wire normalization statistics into live ingestion reporting in `scrapper/src/ingestion/pipeline.py`
- [X] T029 [US1] Persist canonicalization version and canonical categorical values through persistence service payload generation in `scrapper/src/persistence/service.py`
- [X] T030 [US1] Include canonicalization version and supported categorical fields in canonical payload hashing decisions in `scrapper/src/common/canonical_hash.py`
- [X] T031 [US1] Update replay to use the same canonicalization engine and explicit version handling in `scrapper/src/replay/replayer.py`
- [X] T032 [US1] Add CLI/config wiring for canonicalization version selection in `scrapper/src/ingestion/runner.py`

**Checkpoint**: User Story 1 is independently functional and testable as the MVP.

---

## Phase 4: User Story 2 - Maintain Reference Catalog as Source of Truth (Priority: P1)

**Goal**: Vehicle Reference Catalog records define canonical keys, display values, generation metadata, aliases, market context, confidence, and provenance as the source consumed by operational and presentation systems.

**Independent Test**: Review synchronized catalog entries and confirm required fields exist, aliases belong to catalog records, display values are available for presentation consumers, and operational logic uses canonical keys.

### Tests for User Story 2

- [X] T033 [P] [US2] Add catalog row validation tests for required fields and immutable canonical keys in `scrapper/tests/unit/test_vehicle_reference_catalog_model.py`
- [X] T034 [P] [US2] Add catalog lookup tests for canonical identity, display values, aliases, and market scoping in `scrapper/tests/unit/test_vehicle_reference_catalog_lookup.py`
- [X] T035 [P] [US2] Add backend Prisma schema compatibility test expectations for `vehicle_reference_catalog` in `backend/test/integration/vehicle-reference-catalog.prisma-spec.ts`
- [X] T036 [P] [US2] Add backend no-normalization compatibility test for repository/search behavior in `backend/test/integration/listing-canonical-read.compat.spec.ts`

### Implementation for User Story 2

- [X] T037 [US2] Implement vehicle reference catalog domain validation in `scrapper/src/normalization/vehicle_reference_catalog.py`
- [X] T038 [US2] Implement catalog lookup provider backed by storage protocol in `scrapper/src/normalization/catalog_lookup.py`
- [X] T039 [US2] Replace legacy `vehicle_generation_catalog` references in catalog seeding logic with Vehicle Reference Catalog naming in `scrapper/src/db/seed_vehicle_catalog.py`
- [X] T040 [US2] Implement PostgreSQL catalog lookup queries by market, make key, model key, and aliases in `scrapper/src/storage/postgres_storage.py`
- [X] T041 [US2] Update backend Prisma model from `vehicle_generation_catalog` to `vehicle_reference_catalog` with display, alias, confidence, and provenance fields in `backend/prisma/schema.prisma`
- [X] T042 [US2] Update backend repository read models to consume canonical keys and catalog display values without normalization in `backend/src/listings/listings.repository.ts`
- [X] T043 [US2] Update backend search/filter compatibility paths to use persisted canonical fields in `backend/src/listings/listings.service.ts`
- [X] T044 [US2] Verify presentation contract exposes catalog display values without client reconstruction in `frontend/src/lib/api.ts`

**Checkpoint**: User Story 2 is independently functional and catalog data is the source of truth for identity and display values.

---

## Phase 5: User Story 3 - Synchronize Catalog from Reference Files (Priority: P2)

**Goal**: CSV reference files safely and idempotently synchronize the Vehicle Reference Catalog as the authoritative source.

**Independent Test**: Apply the same CSV file set repeatedly and confirm inserted/updated/unchanged/rejected counts, catalog state, and provenance remain correct and stable.

### Tests for User Story 3

- [X] T045 [P] [US3] Add CSV parser validation tests for valid, invalid, and missing catalog columns in `scrapper/tests/unit/test_vehicle_reference_catalog_csv.py`
- [X] T046 [P] [US3] Add idempotent synchronization integration tests for repeated CSV application in `scrapper/tests/integration/test_vehicle_reference_catalog_sync.py`
- [X] T047 [P] [US3] Add sync provenance and conflict-reporting tests in `scrapper/tests/integration/test_vehicle_reference_catalog_sync_reporting.py`

### Implementation for User Story 3

- [X] T048 [US3] Implement CSV reference file reader and validator in `scrapper/src/db/vehicle_reference_catalog_csv.py`
- [X] T049 [US3] Implement idempotent catalog synchronization service with inserted/updated/unchanged/rejected reporting in `scrapper/src/db/vehicle_reference_catalog_sync.py`
- [X] T050 [US3] Implement sync provenance updates and manual-conflict reporting in `scrapper/src/storage/postgres_storage.py`
- [X] T051 [US3] Add catalog synchronization CLI entry point to migration/database tooling in `scrapper/src/db/migrate.py`
- [X] T052 [US3] Add initial curated CSV catalog source file for supported examples in `scrapper/data/reference/vehicle_reference_catalog.csv`
- [X] T053 [US3] Document CSV ownership and sync execution in `specs/005-vehicle-reference-catalog/quickstart.md`

**Checkpoint**: User Story 3 is independently functional and catalog synchronization is repeatable and traceable.

---

## Phase 6: User Story 4 - Backfill Existing Listings Safely (Priority: P2)

**Goal**: Existing listings can be backfilled to canonical values without modifying raw payloads, identifiers, or historical records, and reruns remain safe.

**Independent Test**: Run backfill on representative existing listings multiple times and verify canonical values are stable, raw payloads are byte-for-byte unchanged, identifiers/history are preserved, and operational reports reconcile.

### Tests for User Story 4

- [X] T054 [P] [US4] Add backfill dry-run and batching unit tests in `scrapper/tests/unit/test_canonical_backfill.py`
- [X] T055 [P] [US4] Add backfill idempotency integration test for reruns with unchanged inputs in `scrapper/tests/integration/test_canonical_backfill_idempotency.py`
- [X] T056 [P] [US4] Add backfill raw payload and listing history preservation test in `scrapper/tests/integration/test_canonical_backfill_preservation.py`
- [X] T057 [P] [US4] Add partial-failure recovery test for batched backfill in `scrapper/tests/integration/test_canonical_backfill_recovery.py`

### Implementation for User Story 4

- [X] T058 [US4] Implement existing listing selection and batching storage methods in `scrapper/src/storage/postgres_storage.py`
- [X] T059 [US4] Implement canonical backfill service using the shared canonicalization engine in `scrapper/src/maintenance/canonical_backfill.py`
- [X] T060 [US4] Implement dry-run, batch-size, version, and resume options for backfill entry point in `scrapper/src/maintenance/canonical_backfill.py`
- [X] T061 [US4] Implement backfill operational reporting for counts, unknown values, skipped rows, and failures in `scrapper/src/reporting/normalization_statistics.py`
- [X] T062 [US4] Add backfill CLI wiring without marketplace access in `scrapper/src/ingestion/runner.py`
- [X] T063 [US4] Document backfill dry-run, execution, rerun, and rollback validation in `specs/005-vehicle-reference-catalog/quickstart.md`

**Checkpoint**: User Story 4 is independently functional and existing listings can be safely backfilled.

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Cross-story validation, compatibility checks, documentation cleanup, and final verification.

- [X] T064 [P] Run Python unit and integration test validation and document commands in `specs/005-vehicle-reference-catalog/quickstart.md`
- [X] T065 [P] Run backend Prisma generation and build verification and document results in `specs/005-vehicle-reference-catalog/quickstart.md`
- [X] T066 [P] Add regression test confirming scoped-out generation classification is absent in `scrapper/tests/regression/test_no_generation_classification.py`
- [X] T067 [P] Add regression test confirming backend has no marketplace normalization dictionaries in `backend/test/unit/no-marketplace-normalization.spec.ts`
- [X] T068 Review all new logging/statistics paths for raw payload leakage in `scrapper/src/reporting/normalization_statistics.py`
- [X] T069 Update final validation evidence and completion criteria in `specs/005-vehicle-reference-catalog/quickstart.md`
- [X] T070 Run Spec Kit cross-artifact consistency review and capture findings in `specs/005-vehicle-reference-catalog/checklists/requirements.md`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies; can start immediately.
- **Foundational (Phase 2)**: Depends on Setup completion; blocks all user stories.
- **User Story 1 (Phase 3)**: Depends on Foundational; MVP scope.
- **User Story 2 (Phase 4)**: Depends on Foundational; can proceed in parallel with US1 after shared models/storage contracts exist, but backend compatibility tasks depend on schema decisions from US2 tasks.
- **User Story 3 (Phase 5)**: Depends on Foundational and benefits from US2 catalog model/lookup completion.
- **User Story 4 (Phase 6)**: Depends on US1 canonicalization engine and US2/US3 catalog availability.
- **Polish (Phase 7)**: Depends on selected user stories being complete.

### User Story Dependencies

- **US1 Persist Canonical Operational Data (P1)**: Can start after Foundational; MVP.
- **US2 Maintain Reference Catalog as Source of Truth (P1)**: Can start after Foundational; required for production catalog-backed aliases and display values.
- **US3 Synchronize Catalog from Reference Files (P2)**: Depends on US2 catalog model and storage shape.
- **US4 Backfill Existing Listings Safely (P2)**: Depends on US1 canonicalization and US3 synchronized catalog data.

### Within Each User Story

- Tests should be written first and fail before implementation.
- Domain models/storage boundaries before services.
- Services before CLI/backend integration.
- Core implementation before compatibility checks.
- Story checkpoint must pass before moving to the next dependent story.

---

## Parallel Opportunities

- Setup fixture tasks T002-T005 can run in parallel.
- Foundational tests T016-T017 can run in parallel after migration/storage scaffolding decisions are clear.
- US1 tests T018-T022 can run in parallel before implementation.
- US2 tests T033-T036 can run in parallel before implementation.
- US3 tests T045-T047 can run in parallel before implementation.
- US4 tests T054-T057 can run in parallel before implementation.
- Polish verification tasks T064-T067 can run in parallel after implementation.

## Parallel Example: User Story 1

```bash
Task: "T018 [P] [US1] Add canonical key generation unit tests for separators, punctuation, semantic preservation, and immutable key examples in scrapper/tests/unit/test_canonical_key_engine.py"
Task: "T019 [P] [US1] Add canonicalization alias and unknown-value statistics tests in scrapper/tests/unit/test_canonicalization_statistics.py"
Task: "T020 [P] [US1] Add supported categorical field normalization tests for make, model, trim, fuel type, transmission, body type, seller type, condition, specs, and color in scrapper/tests/unit/test_supported_categorical_fields.py"
Task: "T021 [P] [US1] Add ingestion integration test proving raw payload preservation and canonical listing persistence in scrapper/tests/integration/test_ingestion_canonical_persistence.py"
Task: "T022 [P] [US1] Add replay equivalence test for fixed raw inputs and canonicalization version in scrapper/tests/integration/test_replay_canonicalization_version.py"
```

## Parallel Example: User Story 2

```bash
Task: "T033 [P] [US2] Add catalog row validation tests for required fields and immutable canonical keys in scrapper/tests/unit/test_vehicle_reference_catalog_model.py"
Task: "T034 [P] [US2] Add catalog lookup tests for canonical identity, display values, aliases, and market scoping in scrapper/tests/unit/test_vehicle_reference_catalog_lookup.py"
Task: "T035 [P] [US2] Add backend Prisma schema compatibility test expectations for vehicle_reference_catalog in backend/test/integration/vehicle-reference-catalog.prisma-spec.ts"
Task: "T036 [P] [US2] Add backend no-normalization compatibility test for repository/search behavior in backend/test/integration/listing-canonical-read.compat.spec.ts"
```

## Parallel Example: User Story 3

```bash
Task: "T045 [P] [US3] Add CSV parser validation tests for valid, invalid, and missing catalog columns in scrapper/tests/unit/test_vehicle_reference_catalog_csv.py"
Task: "T046 [P] [US3] Add idempotent synchronization integration tests for repeated CSV application in scrapper/tests/integration/test_vehicle_reference_catalog_sync.py"
Task: "T047 [P] [US3] Add sync provenance and conflict-reporting tests in scrapper/tests/integration/test_vehicle_reference_catalog_sync_reporting.py"
```

## Parallel Example: User Story 4

```bash
Task: "T054 [P] [US4] Add backfill dry-run and batching unit tests in scrapper/tests/unit/test_canonical_backfill.py"
Task: "T055 [P] [US4] Add backfill idempotency integration test for reruns with unchanged inputs in scrapper/tests/integration/test_canonical_backfill_idempotency.py"
Task: "T056 [P] [US4] Add backfill raw payload and listing history preservation test in scrapper/tests/integration/test_canonical_backfill_preservation.py"
Task: "T057 [P] [US4] Add partial-failure recovery test for batched backfill in scrapper/tests/integration/test_canonical_backfill_recovery.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup.
2. Complete Phase 2: Foundational prerequisites.
3. Complete Phase 3: US1 Persist Canonical Operational Data.
4. Stop and validate US1 independently with canonicalization, raw preservation, unknown statistics, and replay-version checks.

### Incremental Delivery

1. Setup + Foundational establishes shared schema/model/storage boundaries.
2. US1 delivers canonical operational listing persistence for new ingestion.
3. US2 makes the Vehicle Reference Catalog the source of truth for identity/display/aliases.
4. US3 adds authoritative CSV synchronization and provenance.
5. US4 safely backfills existing listings.
6. Polish validates backend/presentation compatibility and scoped-out capability exclusions.

### Parallel Team Strategy

1. Complete Setup and Foundational work together.
2. Start US1 and US2 in parallel after Foundational if separate engineers own scraper canonicalization and catalog/backend compatibility.
3. Start US3 after US2 catalog shape is stable.
4. Start US4 after US1 canonicalization and US3 catalog synchronization are available.

---

## Notes

- `[P]` tasks touch different files and can run in parallel when prerequisites are satisfied.
- `[US1]`, `[US2]`, `[US3]`, and `[US4]` labels map directly to the final feature specification user stories.
- Tests are included because the implementation plan explicitly requires Python and backend verification coverage.
- Avoid introducing fuzzy matching, AI, VIN decoding, valuation, generation classification, market analytics, price intelligence, additional services, or frontend canonicalization logic.

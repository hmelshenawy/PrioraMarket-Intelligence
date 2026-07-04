# Tasks: Data Ingestion Foundation

**Input**: Design documents from `/specs/001-data-ingestion-foundation/`

**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/, quickstart.md

**Tests**: Included. The approved plan's Definition of Done and Testing Strategy require unit, integration, contract, and acceptance suites (including parity regression and replay determinism). Test tasks are therefore generated alongside implementation tasks. Write tests first (Red-Green) where a contract/unit test precedes the module it guards.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story. Story order follows spec.md priorities: US1 (P1) → US2 (P2) → US3 (P2) → US4 (P3) → US5 (P4).

## Format: `[ID] [P?] [Story?] Description`

- **[P]**: Can run in parallel (different files, no dependencies on incomplete tasks)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Project type**: Single Python project — `src/` and `tests/` at repository root.
- Source modules live under `src/<package>/`; tests under `tests/<unit|integration|contract>/`; fixtures under `tests/fixtures/`.
- Paths below are repository-relative.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure.

- [X] T001 Create project structure per implementation plan (src/ package skeleton: config/, common/, marketplaces/dubizzle/, ingestion/, storage/, replay/, reporting/) in src/
- [X] T002 [P] Configure linting and formatting tools (ruff/black) and pytest in pyproject.toml
- [X] T003 [P] Add .gitignore for outputs/secrets and .env.example stub in .gitignore and .env.example

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented.

**⚠️ CRITICAL**: No user story work can begin until this phase is complete.

- [X] T004 [P] Implement RawListing domain model (immutable, verbatim payload + extracted fields) in src/common/models.py
- [X] T005 Implement Listing and ValidationResult domain models in src/common/models.py (depends T004)
- [X] T006 Implement IngestionRun, DatasetVersion, NormalizationVersion, and RunReport metric structures in src/common/models.py (depends T005)
- [X] T007 [P] Implement centralized configuration module (env loading, fail-fast on missing required values, typed config, feature flags) in src/config/config.py
- [X] T008 [P] Implement structured (JSON) logging with run correlation id and secret scrubbing in src/common/logger.py
- [X] T009 [P] Define StorageAdapter interface (write_raw, write_listings, write_report, read_raw) in src/storage/interface.py

**Checkpoint**: Foundation ready — domain models, config, logging, and the storage interface exist. User story implementation can now begin.

---

## Phase 3: User Story 1 - Execute a Modular Ingestion Run (Priority: P1) 🎯 MVP

**Goal**: A single scoped ingestion run produces parity listings, preserved raw payloads, and a structured run report (basic metrics + dataset version + lineage).

**Independent Test**: Run the pipeline against one make and one condition and verify (a) normalized listing count matches the current prototype scraper for the same scope, (b) a raw payload artifact is produced for each listing, and (c) a run report with basic metrics is emitted.

### Tests for User Story 1

> Write these first; ensure they FAIL before implementation where they guard a contract.

- [X] T010 [P] [US1] Contract test for MarketplaceAdapter interface (pagination, retry, rate-limit, verbatim RawListing) in tests/contract/test_marketplace_adapter.py
- [X] T011 [P] [US1] Define MarketplaceAdapter interface contract (streaming/iterable RawListing output + page metadata) in src/marketplaces/adapter_interface.py

### Implementation for User Story 1

- [X] T012 [P] [US1] Implement Dubizzle request construction and pagination (preserve prototype nbPages handling, cap 500) in src/marketplaces/dubizzle/adapter.py
- [X] T013 [US1] Implement retry/backoff, rate limiting, and configurable timeout in src/marketplaces/dubizzle/adapter.py (depends T012)
- [X] T014 [P] [US1] Implement extractor: marketplace payload → RawListing (raw payload preserved verbatim) in src/marketplaces/dubizzle/extractor.py
- [X] T015 [P] [US1] Define Normalization Version scheme and implement normalizer (RawListing → Listing, deterministic, marketplace-independent) in src/ingestion/normalizer.py
- [X] T016 [US1] Implement canonicalizer with versioned canonical-value mappings (make, model, fuel, transmission, regional spec, body type) in src/ingestion/canonicalizer.py (depends T015)
- [X] T017 [P] [US1] Implement minimal validator (happy-path passthrough; full rules delivered in US3) in src/common/validation.py
- [X] T018 [P] [US1] Implement CSV StorageAdapter (write_raw, write_listings, write_report, read_raw) in src/storage/csv_storage.py
- [X] T019 [US1] Implement pipeline orchestration (happy-path state machine: FETCHING→NORMALIZING→CANONICALIZING→VALIDATING→STORING→COMPLETED) in src/ingestion/pipeline.py (depends T011–T018)
- [X] T020 [US1] Implement run report assembly with basic metrics (FR-061), dataset version assignment, and per-listing lineage (FR-023) in src/reporting/run_report.py (depends T019)
- [X] T021 [US1] Implement CLI runner entry point for ingestion (`run --marketplace --condition --make`) in src/ingestion/runner.py (depends T019, T020)
- [X] T022 [US1] Integration test: scoped run produces parity listings + raw payloads + basic run report in tests/integration/test_ingestion_run.py (depends T021)

**Checkpoint**: User Story 1 is fully functional and testable independently — the MVP ingestion run works end-to-end.

---

## Phase 4: User Story 2 - Resilient Ingestion with Partial-Failure Tolerance (Priority: P2)

**Goal**: A failed page or record does not discard the rest of the run; failures are retried, isolated, and recorded.

**Independent Test**: Force a failure on one page mid-run and verify the run completes, the failed page is recorded in the run report's failures, and listings from all other pages are still produced.

### Tests for User Story 2

- [X] T023 [P] [US2] Unit test for retry/backoff and timeout handling under transient failures in tests/unit/test_adapter_retry.py

### Implementation for User Story 2

- [X] T024 [US2] Harden adapter retry/backoff/timeout for transient network and rate-limit responses in src/marketplaces/dubizzle/adapter.py (depends T023)
- [X] T025 [US2] Implement pipeline failure isolation (page/record failures logged and skipped, not fatal) in src/ingestion/pipeline.py (depends T019)
- [X] T026 [US2] Implement PARTIAL_FAILED terminal state and failure recording in run report in src/ingestion/pipeline.py and src/reporting/run_report.py (depends T025)
- [X] T027 [US2] Integration test: forced page failure leaves run completing with failures recorded in tests/integration/test_resilience.py (depends T026)

**Checkpoint**: User Stories 1 AND 2 work independently — the run is resilient to partial failures.

---

## Phase 5: User Story 3 - Validation Gate Before Persistence (Priority: P2)

**Goal**: Every listing is validated before persistence; invalid records are isolated, logged, and counted as skipped — never fatal.

**Independent Test**: Feed the pipeline a fixture with one valid and several invalid listings (missing uuid, non-numeric price, missing required fields) and verify the valid listing is persisted while each invalid listing is logged with a reason and counted as skipped.

### Tests for User Story 3

- [X] T028 [P] [US3] Unit test for validation rules (uuid, required fields, numeric values, consistency) in tests/unit/test_validation.py

### Implementation for User Story 3

- [X] T029 [US3] Implement full validation rules producing ValidationResult (replaces T017 minimal validator) in src/common/validation.py (depends T028)
- [X] T030 [US3] Implement run-level UUID deduplication (newest occurrence wins, duplicate counter incremented) in src/common/validation.py (depends T029)
- [X] T031 [US3] Ensure invalid/duplicate records are logged and counted as skipped without aborting the run in src/common/validation.py and src/ingestion/pipeline.py (depends T030)
- [X] T032 [US3] Integration test: invalid records skipped/logged and not persisted; valid records persist in tests/integration/test_validation_gate.py (depends T031)

**Checkpoint**: User Stories 1, 2, AND 3 work independently — the validation gate is robust.

---

## Phase 6: User Story 4 - Configurable, Secret-Free, Pluggable Pipeline (Priority: P3)

**Goal**: All runtime behavior is env-driven with no hardcoded secrets/paths, and storage is substitutable behind the interface without ingestion-code changes.

**Independent Test**: Run the pipeline with configuration supplied entirely through environment variables (no code edits), then substitute an alternative storage adapter behind the storage interface and confirm ingestion logic is unchanged.

### Tests for User Story 4

- [X] T033 [P] [US4] Contract test for StorageAdapter interface (CSV adapter + substitute adapter satisfy the same contract) in tests/contract/test_storage_adapter.py

### Implementation for User Story 4

- [X] T034 [US4] Complete configuration: feature flags (EnableValidation, EnableCanonicalization, EnableReplay, EnableStructuredLogging, EnableCsvStorage), fail-fast for all required values in src/config/config.py (depends T007)
- [X] T035 [US4] Remove all hardcoded secrets and filesystem paths from source; route through config (scan + fix) across src/
- [X] T036 [US4] Implement substitute (in-memory/test) StorageAdapter and prove ingestion unaffected in tests/contract/test_storage_substitutability.py (depends T033, T009)
- [X] T037 [US4] Integration test: env-driven configuration + storage substitutability (SC-007, SC-008) in tests/integration/test_config_and_storage.py (depends T034, T036)

**Checkpoint**: User Stories 1–4 work independently — the pipeline is configuration-driven and storage-pluggable.

---

## Phase 7: User Story 5 - Replay Existing Raw Data (Priority: P4)

**Goal**: Rebuild normalized Listings from previously stored RawListings without marketplace access, using an explicitly selected Normalization Version, deterministically.

**Independent Test**: Take stored Raw Listings, run replay with the newest normalization and validation rules, and verify normalized Listings are produced with no marketplace access and identical results on a second run.

### Tests for User Story 5

- [X] T038 [P] [US5] Unit test for replayer determinism and RawListing immutability in tests/unit/test_replayer.py

### Implementation for User Story 5

- [X] T039 [US5] Implement replayer reading stored RawListings via StorageAdapter.read_raw (no marketplace access) in src/replay/replayer.py (depends T038)
- [X] T040 [US5] Enforce Replay Rules: never modify RawListings, explicit Normalization Version selection, deterministic regeneration in src/replay/replayer.py (depends T039)
- [X] T041 [US5] Implement replay CLI command (`replay --dataset --normalization-version`) in src/ingestion/runner.py (depends T040)
- [X] T042 [US5] Integration test: replay rebuilds Listings offline, deterministically, with explicit version in tests/integration/test_replay.py (depends T041)

**Checkpoint**: All user stories (1–5) are independently functional, including offline deterministic replay.

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Cross-story metrics, parity regression, end-to-end acceptance, and records.

- [X] T043 [P] Build fixture corpus from recorded prototype output in tests/fixtures/
- [X] T044 Parity regression: refactored pipeline vs. prototype for identical scope (SC-001) in tests/integration/test_parity.py (depends T022, T043)
- [X] T045 [P] Wire extended run-report metrics (retry_count, duplicate_count, validation_failures, pages_per_second, listings_per_second, fetch_duration, processing_duration, storage_duration — FR-063) in src/reporting/run_report.py
- [X] T046 [P] Wire optional operational metrics (start_time, end_time, total_duration, peak_memory, peak_cpu — FR-064) in src/reporting/run_report.py
- [X] T047 [P] Implement run-report stop-position identification (last successful page, failing page, stage at failure) for failure recovery in src/reporting/run_report.py
- [X] T048 End-to-end acceptance covering SC-001–SC-009 in tests/integration/test_acceptance.py (depends T044, T045, T046, T047)
- [X] T049 [P] Create Architecture Decision Log (ADR-008 Canonicalization strategy, ADR-009 Storage abstraction design, ADR-010 Marketplace adapter behavior) in docs/adr/
- [X] T050 [P] Documentation consistency check vs. Constitution and spec across plan.md, data-model.md, contracts/, quickstart.md

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — can start immediately.
- **Foundational (Phase 2)**: Depends on Setup completion — BLOCKS all user stories.
- **User Stories (Phases 3–7)**: All depend on Foundational phase completion.
  - US1 (P1) is the MVP and builds the end-to-end happy-path pipeline.
  - US2 (P2) depends on US1 (hardens adapter resilience + pipeline failure isolation).
  - US3 (P2) depends on US1 (replaces the minimal validator with the full validation gate).
  - US4 (P3) depends on US1 (completes config + proves storage substitutability).
  - US5 (P4) depends on US1 (reuses normalizer/canonicalizer/validator over stored RawListings).
- **Polish (Phase 8)**: Depends on all user stories being complete.

### User Story Dependencies

- **US1 (P1)**: Starts after Foundational — no dependencies on other stories. (MVP)
- **US2 (P2)**: Starts after US1 — hardens resilience on the US1 pipeline.
- **US3 (P2)**: Starts after US1 — hardens validation on the US1 pipeline.
- **US4 (P3)**: Starts after US1 — completes config and storage substitutability.
- **US5 (P4)**: Starts after US1 — reuses US1 stages over stored RawListings.

### Within Each User Story

- Contract/unit tests (where present) MUST be written and FAIL before the module they guard.
- Models before services; services before orchestration; orchestration before CLI; CLI before integration tests.
- Core implementation before integration.
- Story complete before moving to the next priority.

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel (T002, T003).
- Foundational tasks on different files can run in parallel (T004, T007, T008, T009); same-file model tasks (T004→T005→T006) are sequential.
- Within US1: T010, T011, T012, T014, T015, T017, T018 are parallelizable (different files); T013 depends on T012; T016 on T015; T019 wires all; T020–T022 sequential.
- Within US2/US3/US4/US5: each has one [P] test task that can start immediately.
- Polish [P] tasks (T043, T045, T046, T047, T049, T050) can run in parallel; T044 and T048 are sequential gates.

---

## Parallel Example: User Story 1

```bash
# Launch independent US1 tasks together (different files, no dependencies):
Task: "T010 [P] [US1] Contract test for MarketplaceAdapter interface in tests/contract/test_marketplace_adapter.py"
Task: "T011 [P] [US1] Define MarketplaceAdapter interface contract in src/marketplaces/adapter_interface.py"
Task: "T014 [P] [US1] Implement extractor in src/marketplaces/dubizzle/extractor.py"
Task: "T015 [P] [US1] Implement normalizer in src/ingestion/normalizer.py"
Task: "T017 [P] [US1] Implement minimal validator in src/common/validation.py"
Task: "T018 [P] [US1] Implement CSV StorageAdapter in src/storage/csv_storage.py"

# Then sequential wiring:
Task: "T019 [US1] Implement pipeline orchestration in src/ingestion/pipeline.py"
Task: "T020 [US1] Implement run report in src/reporting/run_report.py"
Task: "T021 [US1] Implement CLI runner in src/ingestion/runner.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup.
2. Complete Phase 2: Foundational (CRITICAL — blocks all stories).
3. Complete Phase 3: User Story 1 (end-to-end happy-path pipeline + basic run report).
4. **STOP and VALIDATE**: parity vs. prototype, raw payloads, basic run report.
5. Demo the MVP ingestion run.

### Incremental Delivery

1. Setup + Foundational → foundation ready.
2. Add US1 → test independently → MVP delivered.
3. Add US2 → test resilience independently.
4. Add US3 → test validation gate independently.
5. Add US4 → test config + storage substitutability independently.
6. Add US5 → test replay independently.
7. Polish → parity regression, full metrics, end-to-end acceptance (SC-001–SC-009), ADRs, doc consistency.

### Parallel Team Strategy

With multiple developers:
1. Team completes Setup + Foundational together.
2. Once Foundational is done: US1 first (it unblocks US2–US5).
3. After US1: US2, US3, US4, US5 can proceed in parallel (different hardening surfaces) if team capacity allows.
4. Polish is a final shared gate.

---

## Notes

- [P] tasks = different files, no dependencies on incomplete tasks.
- [Story] label maps a task to its user story for traceability.
- Each user story is independently completable and testable.
- Write contract/unit tests first and confirm they FAIL before implementing the guarded module.
- Commit after each task or logical group.
- Stop at any checkpoint to validate a story independently.
- Avoid: vague tasks, same-file conflicts, cross-story dependencies that break independence.
- US1 ships a minimal validator (T017); US3 (T029) replaces it with the full validation gate — this keeps US1 lean and US3 independently testable.
- Extended (FR-063) and optional operational (FR-064) run-report metrics are wired in Polish (T045, T046) before final acceptance; US1's run report ships basic metrics (FR-061) only.
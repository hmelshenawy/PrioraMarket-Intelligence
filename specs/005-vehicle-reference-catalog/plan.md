# Implementation Plan: Canonical Data Model & Vehicle Reference Catalog

**Branch**: `003-backend-search-api` | **Date**: 2026-07-04 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/005-vehicle-reference-catalog/spec.md`

## Summary

Establish the canonical operational data foundation inside the Python scraper/data-ingestion bounded context. The scraper remains the owner of schema, migrations, ingestion, normalization, replay, persistence, catalog synchronization, operational statistics, and backfill. The backend remains read-only and consumes PostgreSQL through Prisma without adding marketplace-specific normalization. Presentation consumers receive catalog display values and never reconstruct labels from canonical keys.

The implementation preserves the approved flow:

```text
Raw Marketplace
↓
Extraction
↓
Normalization
↓
Canonicalization
↓
Vehicle Reference Catalog Lookup
↓
Listing Persistence
↓
Backend
↓
Frontend
```

The plan is intentionally lightweight: deterministic canonicalization, catalog-owned aliases, CSV-owned catalog synchronization, provenance, normalization statistics, canonicalization version persistence, replay compatibility, safe backfill, backend compatibility, and presentation-ready display values. It does not introduce fuzzy matching, AI, VIN decoding, market analytics, price intelligence, generation classification, new services, or additional infrastructure.

## Technical Context

**Language/Version**: Python 3.11 for scraper-owned ingestion, migrations, replay, synchronization, and backfill; TypeScript/NestJS for read-only backend compatibility; TypeScript/Next.js presentation compatibility only.

**Primary Dependencies**: Existing scraper dependencies (`requests`, `python-dotenv`, `psycopg`, `yoyo-migrations`, `pytest`, `ruff`, `black`); existing backend dependencies (`NestJS`, `Prisma`, `Jest`). No new external service dependency is introduced by this feature.

**Storage**: PostgreSQL/Supabase via scraper-owned SQL migrations and backend Prisma schema synchronization. CSV reference files are authoritative for the Vehicle Reference Catalog; PostgreSQL is the synchronized operational copy.

**Testing**: Python `pytest` for unit, normalization, catalog sync, migration, replay, and backfill tests; backend `npm run build`, `npm run prisma:generate`, Jest repository/integration compatibility checks. Frontend testing is limited to compatibility considerations and is not a primary test surface for this feature.

**Target Platform**: Cross-platform local/CI execution on Windows and Linux; single-process scraper CLI/pipeline execution; PostgreSQL-backed environments already used by the project.

**Project Type**: Data ingestion library + CLI with read-only web-service compatibility. The feature belongs to the Data Ingestion bounded context and updates backend schema awareness only.

**Performance Goals**: Catalog lookup should be efficient enough for existing ingestion/replay volumes without introducing caching complexity; repeated CSV synchronization and backfill should be safe to rerun and complete in bounded batches; backend search/filter behavior should remain compatible after Prisma synchronization.

**Constraints**: Backend must not contain marketplace-specific normalization or canonicalization logic. Presentation consumers must not reconstruct display names. Raw listing payloads remain immutable. Canonical keys are immutable once introduced. Unknown values must not block ingestion. Migrations must be ordered, reversible, idempotent, and history-preserving. No generation classification logic is implemented.

**Scale/Scope**: Current scope supports existing marketplace ingestion and is designed for multiple marketplaces through market-scoped catalog records. Supported categorical fields include make, model, trim, fuel type, transmission, body type, seller type, vehicle condition, specs, and color. Numeric and free-text fields remain outside categorical canonicalization.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

Evaluated against PrioraMarket Intelligence Constitution v1.1.0.

| Principle | Status | Evidence |
|-----------|--------|----------|
| I. Documentation First | Pass | Final spec is approved; this plan, research, data model, contracts, and quickstart precede tasks and implementation. |
| II. Design Before Implementation | Pass | No code or task list is produced; design artifacts are generated first. |
| III. Domain-Driven Architecture | Pass | Work stays in Data Ingestion; backend/presentation changes are compatibility-only consumers of the canonical data foundation. |
| IV. Clean Layered Architecture | Pass | Scraper pipeline owns normalization/canonicalization orchestration; persistence remains behind storage/persistence boundaries; backend repositories remain read-only. |
| V. API First | N/A | No new public API is required; existing backend APIs remain compatible. Any future display-name API expansion is additive and outside implementation code in this plan. |
| VI. Database as Source of Truth | Pass | After ingestion/synchronization, PostgreSQL remains the internal operational source. CSV is authoritative only for catalog synchronization input. |
| VII. Historical Data Preservation | Pass | Raw listings remain immutable; backfill is non-destructive; listing identifiers and history are preserved. |
| VIII. AI Assists, Never Invents | N/A | AI is explicitly out of scope. |
| IX. Analytics Before AI | Pass | Canonical keys prepare deterministic analytics without adding analytics features. |
| X. Machine Learning as Product Feature | N/A | ML is out of scope. |
| XI. Data Quality Before Intelligence | Pass | Unknown-value statistics, canonicalization versioning, and deterministic normalization improve data quality and traceability. |
| XII. Scalability by Design | Pass | Catalog records are market-scoped; backend has no marketplace-specific normalization; CSV sync supports adding brands/markets. |
| XIII. Backend-Centric Business Logic | Pass | Backend remains read-only; business normalization stays in scraper ingestion, not frontend/presentation. |
| XIV. Modularity | Pass | Canonicalization engine, catalog synchronization, persistence updates, backfill, and backend compatibility have separate boundaries. |
| XV. Security by Default | Pass | No secrets added; external marketplace data remains untrusted and normalized before persistence; logs/statistics avoid raw sensitive payloads. |
| XVI. Simplicity Over Complexity | Pass | No additional services, no fuzzy matching, no history/versioning subsystem for catalog beyond lightweight provenance. |

**Gate result**: PASS. No constitution violations require complexity tracking.

### Post-Design Re-check

Phase 0 and Phase 1 artifacts preserve the same boundaries. The data model keeps aliases inside Vehicle Reference Catalog records, uses lightweight provenance instead of catalog history, and treats canonicalization versioning as traceability metadata rather than a separate rules service. Contracts are internal compatibility contracts and do not introduce public API scope. **Post-design gate result: PASS.**

## Project Structure

### Documentation (this feature)

```text
specs/005-vehicle-reference-catalog/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   ├── scraper-canonicalization-contract.md
│   ├── catalog-synchronization-contract.md
│   ├── backend-compatibility-contract.md
│   └── presentation-compatibility-contract.md
└── tasks.md             # Phase 2 output from /speckit-tasks, not created by this plan
```

### Source Code (repository root)

```text
scrapper/
├── src/
│   ├── ingestion/          # Existing extraction/normalization/canonicalization pipeline boundary
│   ├── normalization/      # Canonical key and catalog lookup logic boundary
│   ├── persistence/        # Listing persistence orchestration boundary
│   ├── db/                 # SQL migrations and catalog synchronization entry points
│   ├── replay/             # Existing replay pipeline integration point
│   ├── reporting/          # Operational normalization statistics reporting boundary
│   └── maintenance/        # Existing-listing backfill boundary
└── tests/                  # Python unit, integration, migration, replay, and backfill tests

backend/
├── prisma/                 # Prisma schema synchronized to PostgreSQL migrations
├── src/                    # Read-only repositories/services/controllers remain marketplace-agnostic
└── test/                   # Build, repository, and integration compatibility checks

frontend/                   # Presentation compatibility only; no canonicalization logic
```

**Structure Decision**: The scraper remains the implementation owner. Backend and frontend receive only compatibility-level updates needed to consume canonical fields and catalog display data; no business normalization moves downstream.

## Architecture Overview

### Module Boundaries

The canonicalization engine belongs in the scraper pipeline after extraction and generic normalization, before listing persistence. It is responsible for deterministic key creation, catalog-owned alias resolution, rule-version tagging, and unknown-value statistics. It should not own SQL persistence details.

The Vehicle Reference Catalog synchronization boundary belongs in scraper-owned database tooling. It reads curated CSV reference files, validates source rows, applies idempotent changes to `vehicle_reference_catalog`, records last synchronization provenance, and reports synchronization outcomes.

Listing persistence remains responsible for storing normalized canonical fields, canonical hashes, normalization/canonicalization version metadata, raw-listing links, and existing history semantics. It should not infer display names or perform marketplace-specific extraction.

Backfill belongs in scraper maintenance tooling. It reuses the same canonicalization engine and catalog lookup behavior as live ingestion, runs in batches, is safe to rerun, and does not mutate raw payloads or listing identifiers.

Backend compatibility is limited to Prisma synchronization, repository compatibility, existing search/filter behavior, and optional read exposure of catalog-backed display values when already supported by API design. Backend must not canonicalize marketplace values.

Presentation compatibility is limited to consuming display values supplied through backend/catalog data. Presentation consumers do not reconstruct names from canonical keys.

## Implementation Phases

### Phase 1: Canonicalization Engine

Introduce a scraper-owned canonicalization engine that operates on supported categorical fields: make, model, trim, fuel type, transmission, body type, seller type, vehicle condition, specs, and color. The engine applies a deterministic pipeline: trim, lowercase, remove spaces/hyphens/underscores/punctuation, preserve semantic letters and numbers, resolve aliases from catalog-owned alias data, record unknown values, and attach the canonicalization version used for processing.

The engine must preserve business meaning: `C200` becomes `c200`, `E53 AMG` becomes `e53amg`, `GLC300 Coupe` becomes `glc300coupe`, and `7 Series` becomes `7series`. Unknown values continue through deterministic canonicalization and never block ingestion.

Validation focuses on pure deterministic behavior, version tagging, alias resolution precedence, unknown-value reporting, and replay equivalence. Existing mapping logic should be consolidated or wrapped so future rule changes have one versioned boundary.

### Phase 2: Vehicle Reference Catalog

Evolve the existing generation catalog into the Vehicle Reference Catalog, represented by `vehicle_reference_catalog`. CSV files are the authoritative source; PostgreSQL is a synchronized copy. Catalog records include market, make/model canonical keys, display values, generation/body/year/facelift metadata, aliases, confidence, and lightweight synchronization provenance.

Synchronization validates CSV input, applies idempotent upserts keyed by market and canonical identity, records last-synchronized metadata, and reports inserted/updated/unchanged/rejected rows. Manual database edits are non-authoritative and should be overwritten or reported when they conflict with CSV source data.

The migration strategy should rename or replace the existing `vehicle_generation_catalog` safely, preserving existing catalog data where possible and keeping rollback available. Catalog evolution remains intentionally simple: aliases stay on catalog records and no separate catalog-history/versioning subsystem is introduced.

### Phase 3: Listing Canonical Persistence

Update live ingestion persistence so supported categorical fields in `listing` store canonical keys, not marketplace display values. Persist the canonicalization/normalization rule version used for each normalized listing. Preserve raw listings unchanged and preserve canonical hash semantics by deciding whether canonical hashes include the version metadata consistently.

Replay compatibility is mandatory: replay should use explicit canonicalization/normalization versions and produce deterministic listing output from immutable raw listings. Existing replay should interact with the same canonicalization engine as live ingestion.

Persistence changes should be additive or safely transitional where possible so backend read behavior continues during rollout. Numeric and free-text fields remain unchanged.

### Phase 4: Existing Listing Backfill

Backfill existing listings through the same canonicalization engine and catalog lookup path used by live ingestion. Backfill runs in bounded batches, records operational outcomes, and is repeatable, idempotent, safe to rerun, and non-destructive.

Backfill must preserve listing identifiers, raw payloads, first/last seen metadata, run links, and historical records. Rollback considerations should rely on reversible schema migrations and pre-backfill validation/snapshots of affected normalized columns rather than modifying raw payloads. Rerunning backfill with unchanged inputs and rule versions must produce the same normalized values without duplicate or conflicting state.

### Phase 5: Backend Compatibility

Synchronize Prisma with the evolved PostgreSQL schema after scraper migrations are defined. Confirm generated Prisma types and repositories continue to read listings, filters, and search data without introducing normalization logic. Existing API contracts should remain backward compatible where possible; additive fields for catalog display values or canonical metadata must not break existing clients.

Backend search and filtering should operate on canonical keys already persisted by the scraper. Any display-name needs must be satisfied by reading catalog-backed display data, not by reconstructing strings or applying marketplace-specific mappings.

### Phase 6: Frontend Compatibility

Presentation consumers use display values supplied by backend/catalog data. They should receive or request display values associated with canonical keys and must not infer `Mercedes-Benz` from `mercedesbenz` or `C-Class` from `cclass`.

Future caching opportunities may include backend-side or client-side caching of catalog display mappings, but caching is not required for this foundation. Any cache must preserve canonical-key immutability and catalog display-value evolution.

## Database Planning

Migration order should be schema-first and compatibility-aware: introduce or rename `vehicle_reference_catalog`; add required display fields, aliases, confidence, market identity, and synchronization provenance; add or confirm listing canonical fields and canonicalization version metadata; add indexes needed for catalog lookup by market/make/model and listing search/filter fields; synchronize Prisma schema after SQL migrations are finalized; run backfill only after catalog synchronization and live canonicalization are validated.

Schema evolution must preserve `raw_listing` unchanged. Existing listing records should remain readable throughout rollout. If renaming `vehicle_generation_catalog` is more disruptive than creating `vehicle_reference_catalog` and migrating data, prefer the safer path documented in migration notes. Rollbacks must restore pre-change schema shape without deleting raw listings or history.

Replay compatibility requires retained raw payloads, explicit normalization/canonicalization versions, and deterministic reprocessing. Backfill execution order is: apply migrations, synchronize catalog from CSV, validate catalog, enable canonicalization for new ingestion, run dry-run/reporting pass for existing listings, run batched backfill, validate counts and samples, then synchronize backend Prisma.

## Operational Planning

Monitoring should focus on ingestion normalization statistics, unknown categorical values by field and market, catalog synchronization counts, rejected CSV rows, backfill progress, replay/version usage, and error categories. Logging should be structured and avoid full raw payloads at normal log levels.

Unknown values are operational signals, not ingestion failures. They should be reported so data stewards can improve CSV catalog entries and aliases. Synchronization reporting should make it clear which CSV source was applied, when it was applied, and how many catalog rows changed.

Error handling should fail fast for invalid catalog CSV structure, invalid migration state, or unsafe backfill preconditions. Per-listing normalization issues should be counted and reported without blocking unrelated listings unless they indicate a systemic pipeline failure.

Replay behavior should require explicit version selection or a clearly recorded default version, read immutable raw listings, and produce repeatable outputs for the same input/version combination.

## Testing Strategy

### Python

Unit tests cover canonical key generation, semantic preservation, immutable key examples, alias resolution, unknown-value statistics, and canonicalization version propagation.

Normalization tests cover all supported categorical fields and verify numeric/free-text fields are unaffected.

Catalog synchronization tests cover CSV validation, idempotent repeated sync, market-scoped identity, provenance metadata, aliases stored on catalog records, conflict handling, and rejected-row reporting.

Migration tests cover forward/rollback execution, catalog rename/evolution, indexes/constraints, raw-listing preservation, and Prisma-compatible schema shape.

Replay tests cover deterministic output for a fixed raw listing set and canonicalization version, unknown-value reporting during replay, and no marketplace access.

Backfill tests cover dry-run/reporting behavior, batching, idempotent reruns, non-destructive updates, preserved identifiers/history, and partial-failure recovery.

### Backend

Build verification confirms TypeScript/NestJS compiles after Prisma synchronization.

Prisma synchronization verification confirms the schema maps the evolved `listing` and `vehicle_reference_catalog` tables correctly.

Repository compatibility verification confirms existing read paths, search, and filters continue to function with canonical values.

Integration verification confirms backend does not perform normalization or display-name reconstruction and can read catalog display values where required by existing API behavior.

### Frontend Compatibility

No frontend implementation testing is required in this plan. Compatibility review should confirm presentation consumers can receive display values from backend/catalog data and are not required to reconstruct labels from canonical keys.

## Risks and Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Catalog rename/evolution breaks backend Prisma reads | Backend build or runtime failures | Sequence SQL migrations before Prisma sync; run Prisma generation/build; prefer additive transitional changes where safer. |
| Backfill changes historical semantics | Loss of auditability or inconsistent listings | Preserve raw payloads, identifiers, first/last seen metadata, and history; dry-run first; batch and validate. |
| Canonical key changes after release | Broken analytics/search/filters/URLs/caches/integrations | Treat keys as immutable; add aliases/display changes instead of renaming keys; review CSV changes for key stability. |
| Unknown marketplace values hide data quality issues | Catalog quality degrades silently | Emit normalization statistics by field/market/run; review unknown reports as catalog improvement input. |
| Replay outputs differ from live ingestion | Non-reproducible data lineage | Reuse same canonicalization engine; persist rule versions; require explicit replay versions. |
| CSV synchronization overwrites manual DB edits unexpectedly | Operator confusion | Document CSV ownership; report conflicts; treat DB as synchronized copy only. |
| Over-engineering catalog versioning | Delays foundation feature | Keep only last-synchronized provenance; defer catalog history/versioning. |
| Backend accidentally duplicates normalization logic | Divergent behavior | Contract tests/review gate: backend reads canonical values only and never maps marketplace names. |

## Performance Considerations

Catalog lookup performance should rely on straightforward indexes by market, make key, model key, and aliases where practical. In-memory lookup during a single ingestion or backfill run is acceptable if it is loaded from the authoritative synchronized catalog and does not become a separate source of truth.

Synchronization performance should prioritize correctness and idempotency over bulk optimization. CSV files are expected to be small enough for simple validation and upsert workflows at this stage.

Replay performance should remain comparable to existing replay plus catalog lookup overhead. Avoid network calls and marketplace access during replay.

Backfill scalability should use bounded batches, resumable progress reporting, and transaction scopes that avoid locking the entire listing table. Avoid premature partitioning, background services, or distributed processing.

## Validation and Completion Criteria

Implementation is complete when migrations apply and roll back cleanly; `vehicle_reference_catalog` contains synchronized catalog data from CSV with provenance; repeated catalog synchronization is idempotent; newly ingested supported categorical values persist as canonical keys with rule version metadata; unknown values are reported without blocking ingestion; replay is deterministic for fixed raw inputs and versions; backfill preserves raw payloads, identifiers, and history and is safe to rerun; backend Prisma generation/build succeeds; backend repository/search/filter compatibility is verified; presentation consumers have catalog display values available without reconstructing names.

Operational verification must include sample normalization statistics, synchronization reporting, backfill reporting, replay-version traceability, and confirmation that scoped-out capabilities remain absent: fuzzy matching, AI, VIN decoding, valuation, generation classification, market analytics, price intelligence, and additional services.

## Complexity Tracking

No constitution violations or complexity exceptions are introduced.

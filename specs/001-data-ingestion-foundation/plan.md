# Implementation Plan: Data Ingestion Foundation

**Branch**: `001-data-ingestion-foundation` | **Date**: 2026-07-04 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/001-data-ingestion-foundation/spec.md`

## Summary

Refactor the existing monolithic Dubizzle prototype scraper
(`dubizzle_full_scrape_v2.py`) into a modular, production-ready ingestion
pipeline organized around bounded responsibilities: configuration,
marketplace adapter, extraction, normalization, canonicalization,
validation, storage, logging, pipeline orchestration, run reporting, and
replay. The pipeline MUST produce the same listings as the current
scraper (parity), preserve raw marketplace payloads as immutable
RawListings, normalize + canonicalize listings into platform models,
validate and deduplicate them, persist via a replaceable storage
interface (CSV now, database later), and emit a structured run report
with basic, extended, and optional operational metrics. No database, API,
AI, ML, analytics, or UI is introduced.

## Technical Context

**Language/Version**: Python 3.11 (the existing prototype scraper is
Python; this feature refactors it rather than reimplementing in a new
language).

**Primary Dependencies**: `requests` (HTTP), `python-dotenv`
(environment configuration), `structlog` (structured logging), `pytest` +
`pytest-mock` (testing). No web framework, no ORM, no database driver.

**Storage**: CSV files via a storage abstraction interface (interim only;
replaceable by PostgreSQL/Supabase in a future feature without touching
ingestion logic).

**Testing**: `pytest` (unit, integration, contract), with fixture
RawListings and recorded marketplace payloads for parity/replay tests.

**Target Platform**: Cross-platform Python (Windows/Linux); single-process
CLI execution.

**Project Type**: Library + CLI (an importable ingestion package with a
run/replay command-line entry point).

**Performance Goals**: Listing parity with the current scraper for an
identical scope; complete a full Dubizzle sweep (≈25k used + ≈4k new
listings baseline) within the same order of magnitude as the prototype,
governed by configurable rate limiting.

**Constraints**: No database, no REST APIs, no auth, no AI/ML/analytics,
no UI; configurable rate limit and retry/backoff; single-process;
marketplace-specific logic isolated to the Dubizzle adapter; secrets and
hardcoded filesystem paths forbidden in source.

**Scale/Scope**: One marketplace (Dubizzle) in this feature, but
architecture MUST be marketplace-agnostic (Constitution Principle XI);
≈25k+4k listing baseline per full run; per-make/per-condition traversal
preserved from the prototype.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

Evaluated against the PrioraMarket Intelligence Constitution v1.1.0.

| Principle | Status | Evidence |
|-----------|--------|----------|
| I. Documentation First | ✅ Pass | Plan derives strictly from approved spec; no requirement added/removed. |
| II. Design Before Implementation | ✅ Pass | Plan + data model + contracts produced before tasks/implementation. |
| III. Domain-Driven Architecture | ✅ Pass | All work is within the Data Ingestion bounded context. |
| IV. Clean Layered Architecture | ✅ Pass | Adapter/Normalizer/Canonicalizer/Validator/Storage each own one responsibility; no business logic in transport or storage. |
| V. API First | ⚠ N/A | No REST APIs in scope (internal pipeline); future feature will expose APIs. Justified by spec NFR-009. |
| VI. Database as Source of Truth | ✅ Pass | Pipeline ingests external data into internal storage; downstream uses internal data only. |
| VII. Historical Data Preservation | ✅ Pass | RawListings preserved verbatim and immutably; run reports and dataset versions retained. |
| VIII. AI Assists, Never Invents | ✅ N/A | No AI in this feature. |
| IX. Analytics Before AI | ✅ N/A | No analytics/AI in this feature. |
| X. Data Quality Before Intelligence | ✅ Pass | Validation + canonicalization + dedup gate every listing before persistence. |
| XI. Scalability by Design | ✅ Pass | Marketplace-agnostic adapter pattern; second marketplace requires only a new adapter. |
| XII. Backend-Centric Business Logic | ✅ Pass | All logic in pipeline modules; CLI is a thin entry point only. |
| XIII. Modularity | ✅ Pass | Modules communicate via defined interfaces; internals private. |
| XIV. Security by Default | ✅ Pass | Env-based config, no hardcoded secrets, external data treated as untrusted and validated. |
| XV. Security by Default (rate limiting) | ✅ Pass | Configurable rate limit + retry/backoff. |
| XVI. Simplicity Over Complexity | ✅ Pass | CSV interim; no DB/API/UI; YAGNI applied. |

**Gate result**: PASS. No unjustified violations. The single ⚠ (API First
N/A) is explicitly out of scope by approved spec NFR-009 and does not
block. Complexity Tracking left empty.

## Project Structure

### Documentation (this feature)

```text
specs/001-data-ingestion-foundation/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output (internal module + data contracts)
│   ├── module-interfaces.md
│   └── run-report-schema.md
└── tasks.md             # Phase 2 output (/speckit-tasks — not created here)
```

### Source Code (repository root)

```text
src/
├── config/
│   └── config.py            # Centralized env-driven configuration
├── common/
│   ├── logger.py            # Structured logging setup
│   ├── validation.py        # Validation rules (marketplace-independent)
│   └── models.py            # Domain models: RawListing, Listing, IngestionRun, etc.
├── marketplaces/
│   └── dubizzle/
│       ├── adapter.py       # HTTP, pagination, retry, rate limit, response parsing
│       └── extractor.py     # Payload → RawListing (preserves raw verbatim)
├── ingestion/
│   ├── normalizer.py        # RawListing → platform Listing object
│   ├── canonicalizer.py     # Business value standardization (make/model/fuel/...)
│   ├── pipeline.py          # Stage orchestration + state machine
│   └── runner.py            # CLI entry: configure, run, emit report
├── storage/
│   ├── interface.py         # StorageAdapter interface (Protocol/ABC)
│   └── csv_storage.py       # CSV implementation of StorageAdapter
├── replay/
│   └── replayer.py          # Rebuild Listings from stored RawListings (no marketplace access)
└── reporting/
    └── run_report.py        # Run report + dataset version + metrics assembly

tests/
├── unit/                    # Per-module unit tests
├── integration/             # Cross-module / pipeline integration tests
├── contract/                # Interface contract tests (storage adapter, etc.)
└── fixtures/                # Recorded RawListings / marketplace payloads
```

**Structure Decision**: Single-project layout (Option 1) — a Python
package under `src/` with `tests/` at the repository root. No backend/
frontend split (no UI in scope). Modules are organized by responsibility
per the spec's Domain Pipeline Model; marketplace-specific code is
isolated under `src/marketplaces/dubizzle/` so a second marketplace is an
additive `src/marketplaces/<name>/` package.

## Complexity Tracking

> No Constitution Check violations require justification. Table left empty.

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| — | — | — |

## Implementation Strategy

**Implementation order** follows the data-flow dependency chain of the
Domain Pipeline Model, bottom-up, so each stage can be unit-tested in
isolation before the next stage consumes its output:

1. **Foundation** → domain models + configuration + logging (everything
   depends on these).
2. **Ingestion primitives** → extraction (RawListing), normalization
   (Listing), canonicalization (canonical values), validation +
   dedup (Validation Result). Each is pure and independently testable.
3. **I/O boundaries** → marketplace adapter (produces RawListings) and
   storage adapter (consumes RawListings + Listings). Both are behind
   interfaces.
4. **Orchestration** → pipeline (state machine wiring the stages) + run
   report (metrics + dataset version).
5. **Replay** → reuses normalizer/canonicalizer/validator over stored
   RawListings; no adapter access.
6. **Testing & hardening** → parity regression vs. the prototype,
  resilience tests, end-to-end acceptance.

**Dependency flow** (matches the pipeline diagram):

```text
config ─┐
models ─┼─→ adapter ─→ extractor ─→ RawListing
logger ─┘                            │
                                     ↓
                          normalizer ─→ Listing
                                     │
                                     ↓
                          canonicalizer ─→ canonical Listing
                                     │
                                     ↓
                          validator/dedup ─→ Validation Result
                                     │
                                     ↓
                          storage (via interface) + run_report
```

Replay branches at `RawListing` → `normalizer` (skipping the adapter),
using an explicitly selected Normalization Version.

**Module interaction**: modules communicate only through the interfaces
in `contracts/module-interfaces.md`. No module imports another module's
internals. The pipeline orchestrator is the only component that wires
stages together; stages do not call each other directly.

**Risk reduction strategy**:

- Build pure stages first (normalizer, canonicalizer, validator) so
  logic is testable without network or storage.
- Pin listing parity early (Phase 12) against recorded prototype output
  to catch refactor drift before downstream stages harden around it.
- Keep storage and marketplace behind interfaces from day one so
  substitution is structural, not retrofitted.
- Treat all marketplace data as untrusted; validation is mandatory before
  persistence, and invalid records are isolated, not fatal.

## Architecture Mapping

Each module maps to spec Functional Requirements. Per module:
**Responsibilities / Inputs / Outputs / Dependencies**.

### Configuration (`src/config/config.py`)
- **Responsibilities**: Centralized, env-driven configuration loading;
  fail-fast on missing required values; expose typed config object.
  (FR-001, FR-002, FR-003)
- **Inputs**: Environment variables / `.env`.
- **Outputs**: A validated configuration object (marketplace endpoint,
  credentials, output paths, retry/rate-limit/timeout parameters).
- **Feature Flags**: Configuration-driven operational flags for debugging:
  `EnableValidation`, `EnableCanonicalization`, `EnableReplay`,
  `EnableStructuredLogging`, `EnableCsvStorage`. Flags exist only for
  operational control and debugging; business logic MUST NEVER depend on
  feature flags.
- **Dependencies**: `python-dotenv`; domain models (for config shape).

### Domain Models (`src/common/models.py`)
- **Responsibilities**: Define `RawListing`, `Listing` (normalized),
  `IngestionRun`, `ValidationResult`, `DatasetVersion`,
  `NormalizationVersion`, run-report metric structures. Immutable value
  objects where applicable. (FR-020–022, FR-023, Key Entities)
- **Inputs**: None (declarative).
- **Outputs**: Domain types consumed by all other modules.
- **Dependencies**: Standard library only.

### Marketplace Adapter (`src/marketplaces/dubizzle/adapter.py`)
- **Responsibilities**: HTTP communication, request construction,
  pagination, retry/backoff, rate limiting, response parsing,
  marketplace-specific field mapping. Produces RawListings via the
  extractor. No business logic. (FR-010–015)
- **Inputs**: Configuration; scope (marketplace, condition, make).
- **Outputs**: A streaming/iterable sequence of RawListings, yielded
  progressively as pages are processed, plus page-level fetch metadata
  (for metrics).
- **Streaming direction**: adapters SHOULD expose iterable/streaming
  interfaces whenever practical, progressively yielding RawListings per
  page. Purpose: reduced memory usage, scalable ingestion, and future
  compatibility with queues, workers, and distributed execution. This
  does NOT require asynchronous execution; it only establishes the
  preferred architectural direction.
- **Dependencies**: `requests`, config, logger, extractor, models.

### Extraction (`src/marketplaces/dubizzle/extractor.py`)
- **Responsibilities**: Parse marketplace payload into a RawListing;
  preserve raw payload verbatim; extract normalized listing fields
  without leaking marketplace field names upward. (FR-020–022)
- **Inputs**: A raw marketplace hit/payload.
- **Outputs**: A `RawListing` (immutable, verbatim payload + extracted
  fields).
- **Dependencies**: models.
- **Note**: Extraction is the adapter's parsing step; it lives in the
  marketplace package so marketplace-specific shape handling stays
  isolated, while the adapter handles transport.

### Normalization (`src/ingestion/normalizer.py`)
- **Responsibilities**: Map a RawListing into the platform's
  marketplace-independent Listing object shape. Deterministic. Does NOT
  standardize business values (that is canonicalization). Tagged with the
  active Normalization Version. (FR-040–042)
- **Inputs**: `RawListing`, `NormalizationVersion`.
- **Outputs**: `Listing` (normalized, not yet canonicalized).
- **Dependencies**: models.

### Canonicalization (`src/ingestion/canonicalizer.py`)
- **Responsibilities**: Standardize business values (make, model, fuel
  type, transmission, regional spec, body type) into platform-wide
  canonical values. Deterministic and marketplace-independent. (FR-043,
  FR-044, FR-045)
- **Inputs**: `Listing` (normalized).
- **Outputs**: `Listing` with canonical business values.
- **Dependencies**: models; a canonical-value mapping (versioned with the
  Normalization Version).

### Validation (`src/common/validation.py`)
- **Responsibilities**: Validate canonicalized Listings (uuid, required
  fields, numeric values, basic consistency); deduplicate by marketplace
  UUID within the run (newest wins, duplicate counter incremented);
  produce Validation Results; invalid records logged, not fatal.
  (FR-030–033)
- **Inputs**: Canonicalized `Listing`; run-level dedup index.
- **Outputs**: `ValidationResult` (accepted/rejected + reason);
  dedup计数.
- **Dependencies**: models, logger.

### Storage (`src/storage/interface.py` + `csv_storage.py`)
- **Responsibilities**: Persist RawListings and canonicalized Listings
  through a `StorageAdapter` interface; CSV is the initial
  implementation. Ingestion logic is independent of the storage
  implementation. (FR-050–052)
- **Inputs**: RawListings + Listings + run metadata.
- **Outputs**: Written artifacts (CSV files); write confirmation for
  run-report reconciliation.
- **Dependencies**: models, config (output paths).

### Logging (`src/common/logger.py`)
- **Responsibilities**: Structured logging setup (JSON); correlation/run
  identifier on every log; no secrets logged. (FR-060, FR-062)
- **Inputs**: Configuration.
- **Outputs**: A configured structured logger.
- **Dependencies**: `structlog`.

### Pipeline (`src/ingestion/pipeline.py`)
- **Responsibilities**: Orchestrate the stage chain
  (fetch → extract → normalize → canonicalize → validate/dedup → store)
  per page; implement the Pipeline State Machine; isolate page/record
  failures; advance run state. (FR-070–072, Pipeline State Machine)
- **Inputs**: Configuration; scope; adapter; stage handlers; storage;
  run report.
- **Outputs**: Completed run in a terminal state (COMPLETED /
  PARTIAL_FAILED / FAILED).
- **Dependencies**: all stage modules, models, logger.

### Run Report (`src/reporting/run_report.py`)
- **Responsibilities**: Assemble run report with basic metrics (FR-061),
  extended metrics (FR-063), optional operational metrics (FR-064);
  assign Dataset Version; bind Normalization Version. (Dataset Versioning,
  FR-023 lineage)
- **Inputs**: Per-stage counters/timers from the pipeline.
- **Outputs**: A `RunReport` artifact (structured, persistable).
- **Dependencies**: models.

### Replay (`src/replay/replayer.py`)
- **Responsibilities**: Rebuild normalized + canonicalized Listings from
  stored RawListings using an explicitly selected Normalization Version;
  never modify RawListings; deterministic; no marketplace access.
  (User Story 5, Replay Rules)
- **Inputs**: Stored RawListings; selected `NormalizationVersion`;
  normalizer/canonicalizer/validator.
- **Outputs**: Regenerated Listings / Validation Results / Dataset
  Version.
- **Dependencies**: storage (read RawListings), normalizer,
  canonicalizer, validator, run report.

## Implementation Phases

### Phase 1 — Project Foundation
- **Purpose**: Establish package layout, tooling, and domain models.
- **Deliverables**: `src/` package skeleton, `src/common/models.py`,
  lint/format config, test harness.
- **Dependencies**: Approved spec + plan.
- **Completion criteria**: Package imports cleanly; domain model types
  defined and unit-tested for immutability/shape.

### Phase 2 — Configuration
- **Purpose**: Centralized env-driven configuration; remove hardcoded
  secrets/paths.
- **Deliverables**: `src/config/config.py`, `.env.example`, fail-fast
  validation.
- **Dependencies**: Phase 1.
- **Completion criteria**: All runtime values sourced from env; missing
  required value fails fast with a named message; zero hardcoded
  secrets/paths in source (verifiable by scan).

### Phase 3 — Logging
- **Purpose**: Structured logging foundation used by all modules.
- **Deliverables**: `src/common/logger.py` (structured/JSON), run
  correlation id, secret scrubbing.
- **Dependencies**: Phase 2.
- **Completion criteria**: Logs are structured, include run id, and
  scrub secrets; verified by a logging unit test.

### Phase 4 — Domain Models
- **Purpose**: Finalize all domain entities and value objects.
- **Deliverables**: `RawListing`, `Listing`, `IngestionRun`,
  `ValidationResult`, `DatasetVersion`, `NormalizationVersion`,
  `RunReport` metric structures.
- **Dependencies**: Phase 1.
- **Completion criteria**: Models cover all Key Entities; serialization
  round-trips; immutability enforced for RawListing.

### Phase 5 — Marketplace Adapter (Dubizzle)
- **Purpose**: HTTP/pagination/retry/rate-limit/response parsing behind
  the adapter interface, producing RawListings via the extractor.
- **Deliverables**: `src/marketplaces/dubizzle/adapter.py`,
  `extractor.py`; adapter interface contract.
- **Dependencies**: Phases 2, 3, 4.
- **Completion criteria**: Adapter fetches a make+condition scope,
  paginates, retries on transient failures, rate-limits, and yields
  RawListings with verbatim payloads; no business logic in adapter.

### Phase 6 — Normalization
- **Purpose**: RawListing → platform Listing object mapping,
  marketplace-independent, tagged with Normalization Version.
- **Deliverables**: `src/ingestion/normalizer.py`; normalization version
  scheme.
- **Dependencies**: Phase 4.
- **Completion criteria**: Normalizer is deterministic, pure, and
  marketplace-independent; unit-tested against fixture RawListings.

### Phase 7 — Canonicalization
- **Purpose**: Standardize business values into canonical values.
- **Deliverables**: `src/ingestion/canonicalizer.py`; versioned
  canonical-value mappings (make/model/fuel/transmission/regional/body).
- **Dependencies**: Phase 6.
- **Completion criteria**: Equivalent values collapse to one canonical
  value deterministically and marketplace-independently (FR-044);

### Phase 8 — Validation & Deduplication
- **Purpose**: Validate canonicalized listings; dedup by UUID within run.
- **Deliverables**: `src/common/validation.py`; run-level dedup index.
- **Dependencies**: Phase 7.
- **Completion criteria**: Invalid records logged + skipped (not fatal);
  duplicates collapsed (newest wins, counter incremented); FR-030–033
  satisfied.

### Phase 9 — Storage Abstraction (CSV)
- **Purpose**: `StorageAdapter` interface + CSV implementation.
- **Deliverables**: `src/storage/interface.py`, `csv_storage.py`.
- **Dependencies**: Phase 4.
- **Completion criteria**: Storage accessed only via interface; a
  substitute adapter passes the same contract tests; ingestion code
  unchanged by the swap (FR-050–052).

### Phase 10 — Pipeline Orchestration & State Machine
- **Purpose**: Wire stages into the pipeline; implement the state
  machine; isolate page/record failures.
- **Deliverables**: `src/ingestion/pipeline.py`, `runner.py` (CLI entry).
- **Dependencies**: Phases 5, 6, 7, 8, 9.
- **Completion criteria**: A full run reaches a terminal state
  (COMPLETED / PARTIAL_FAILED / FAILED); a forced page failure does not
  terminate the run; state transitions match the spec.

### Phase 11 — Run Report & Dataset Versioning
- **Purpose**: Assemble run report with basic + extended + optional
  metrics; assign Dataset Version; bind Normalization Version.
- **Deliverables**: `src/reporting/run_report.py`.
- **Dependencies**: Phase 10.
- **Completion criteria**: Every run emits a report with all required
  metrics and a dataset version; lineage (FR-023) recorded per listing.

### Phase 12 — Replay
- **Purpose**: Rebuild Listings from stored RawListings without
  marketplace access.
- **Deliverables**: `src/replay/replayer.py`.
- **Dependencies**: Phases 6, 7, 8, 9, 11.
- **Completion criteria**: Replay produces deterministic Listings from
  fixtures using an explicit Normalization Version; never modifies
  RawListings; works with marketplace access disabled.

### Phase 13 — Testing, Parity & Hardening
- **Purpose**: Parity regression vs. prototype, resilience, end-to-end
  acceptance.
- **Deliverables**: Full unit/integration/contract/acceptance suites;
  fixture corpus.
- **Dependencies**: All prior phases.
- **Completion criteria**: All Success Criteria SC-001–SC-009 verified;
  parity with prototype confirmed; resilience under forced failures
  confirmed.

## Work Breakdown

> Complexity: Small / Medium / Large. IDs are phase-prefixed (P<phase>.T<nn>).

### Phase 1 — Project Foundation
- **P1.T01** — Create `src/` package skeleton and module placeholders per
  Project Structure. **Outcome**: importable package tree. **Deps**: —.
  **Complexity**: Small.
- **P1.T02** — Configure lint/format (ruff/black or equivalent) and
  pytest. **Outcome**: `make`/CLI lint+test commands work. **Deps**: P1.T01.
  **Complexity**: Small.
- **P1.T03** — Add `.gitignore` for outputs/secrets and `.env.example`
  stub. **Outcome**: secrets/outputs not committable. **Deps**: P1.T01.
  **Complexity**: Small.

### Phase 2 — Configuration
- **P2.T01** — Define typed configuration object covering endpoint,
  credentials, output paths, retry, rate limit, timeout. **Outcome**:
  config schema. **Deps**: P1.T01. **Complexity**: Small.
- **P2.T02** — Implement env loader with fail-fast on missing required
  values. **Outcome**: missing-value raises named error. **Deps**: P2.T01.
  **Complexity**: Small.
- **P2.T03** — Remove all hardcoded secrets/paths from prototype-derived
  code; route through config. **Outcome**: source scan clean. **Deps**:
  P2.T01. **Complexity**: Medium.

### Phase 3 — Logging
- **P3.T01** — Configure structured (JSON) logging with run correlation
  id. **Outcome**: structured logs with run id. **Deps**: P2.T01.
  **Complexity**: Small.
- **P3.T02** — Add secret scrubbing in log formatter. **Outcome**: no
  secret strings in logs. **Deps**: P3.T01. **Complexity**: Small.

### Phase 4 — Domain Models
- **P4.T01** — Define `RawListing` (immutable, verbatim payload +
  extracted fields). **Outcome**: RawListing type + immutability test.
  **Deps**: P1.T01. **Complexity**: Small.
- **P4.T02** — Define `Listing` (normalized/canonicalizable) and
  `ValidationResult`. **Outcome**: types + shape tests. **Deps**: P4.T01.
  **Complexity**: Small.
- **P4.T03** — Define `IngestionRun`, `DatasetVersion`,
  `NormalizationVersion`, and run-report metric structures. **Outcome**:
  types + serialization round-trip tests. **Deps**: P4.T01.
  **Complexity**: Medium.

### Phase 5 — Marketplace Adapter (Dubizzle)
- **P5.T01** — Define `MarketplaceAdapter` interface contract. **Outcome**:
  interface + contract test stub. **Deps**: P4.T01. **Complexity**: Small.
- **P5.T02** — Implement request construction + pagination (preserve
  prototype's nbPages handling, cap at 500). **Outcome**: paginates a
  scope correctly. **Deps**: P5.T01, P2.T01. **Complexity**: Medium.
- **P5.T03** — Implement retry/backoff + rate limiting + timeout.
  **Outcome**: transient failures retried; rate limit enforced. **Deps**:
  P5.T02. **Complexity**: Medium.
- **P5.T04** — Implement extractor: payload → `RawListing` (verbatim
  payload preserved). **Outcome**: RawListings with verbatim payloads.
  **Deps**: P5.T01, P4.T01. **Complexity**: Medium.
- **P5.T05** — Port prototype's per-make/per-condition traversal into the
  adapter. **Outcome**: adapter drives the same scope as prototype.
  **Deps**: P5.T02, P5.T04. **Complexity**: Medium.

### Phase 6 — Normalization
- **P6.T01** — Define Normalization Version scheme. **Outcome**: version
  identifier + ruleset binding. **Deps**: P4.T03. **Complexity**: Small.
- **P6.T02** — Implement normalizer: RawListing → Listing, deterministic,
  marketplace-independent. **Outcome**: normalized Listings from
  fixtures. **Deps**: P4.T02, P6.T01. **Complexity**: Medium.

### Phase 7 — Canonicalization
- **P7.T01** — Define canonical-value mappings for make, model, fuel,
  transmission, regional spec, body type. **Outcome**: versioned mapping
  tables. **Deps**: P6.T01. **Complexity**: Medium.
- **P7.T02** — Implement canonicalizer (deterministic,
  marketplace-independent). **Outcome**: equivalent values collapse.
  **Deps**: P7.T01, P6.T02. **Complexity**: Medium.

### Phase 8 — Validation & Deduplication
- **P8.T01** — Implement validation rules (uuid, required, numeric,
  consistency) producing `ValidationResult`. **Outcome**: invalid records
  rejected + logged. **Deps**: P4.T02, P3.T01. **Complexity**: Medium.
- **P8.T02** — Implement run-level UUID dedup (newest wins, counter
  incremented). **Outcome**: duplicates collapsed + counted. **Deps**:
  P8.T01. **Complexity**: Small.

### Phase 9 — Storage Abstraction (CSV)
- **P9.T01** — Define `StorageAdapter` interface (write RawListings +
  Listings + run metadata; read RawListings for replay). **Outcome**:
  interface + contract tests. **Deps**: P4.T01. **Complexity**: Small.
- **P9.T02** — Implement CSV `StorageAdapter`. **Outcome**: CSV artifacts
  written + readable back. **Deps**: P9.T01, P2.T01. **Complexity**:
  Medium.
- **P9.T03** — Prove substitutability with a second in-memory/test
  adapter via the same contract tests. **Outcome**: ingestion unaffected
  by adapter swap. **Deps**: P9.T01. **Complexity**: Small.

### Phase 10 — Pipeline Orchestration & State Machine
- **P10.T01** — Implement state machine (states + transitions per spec).
  **Outcome**: legal transitions only; terminal states absorbing.
  **Deps**: P4.T03. **Complexity**: Medium.
- **P10.T02** — Wire stage chain per page with failure isolation (page/
  record failures recorded, not fatal). **Outcome**: partial failures do
  not abort run. **Deps**: P10.T01, P5, P6, P7, P8, P9. **Complexity**:
  Large.
- **P10.T03** — Implement CLI runner (`runner.py`) entry point. **Outcome**:
  `run` command executes a scoped ingestion. **Deps**: P10.T02.
  **Complexity**: Small.

### Phase 11 — Run Report & Dataset Versioning
- **P11.T01** — Collect per-stage counters/timers (basic + extended +
  optional metrics). **Outcome**: metrics available to report. **Deps**:
  P10.T02. **Complexity**: Medium.
- **P11.T02** — Assign Dataset Version and bind Normalization Version;
  record per-listing lineage (FR-023). **Outcome**: dataset version +
  lineage on every listing. **Deps**: P11.T01, P6.T01. **Complexity**:
  Medium.
- **P11.T03** — Emit structured, persistable `RunReport`. **Outcome**:
  report artifact per run. **Deps**: P11.T01. **Complexity**: Small.

### Phase 12 — Replay
- **P12.T01** — Implement replayer reading stored RawListings via
  storage interface (no adapter access). **Outcome**: replay runs offline.
  **Deps**: P9.T01, P6, P7, P8. **Complexity**: Medium.
- **P12.T02** — Enforce Replay Rules: never modify RawListings; explicit
  Normalization Version; deterministic regeneration. **Outcome**: replay
  rules satisfied + tested. **Deps**: P12.T01. **Complexity**: Medium.

### Phase 13 — Testing, Parity & Hardening
- **P13.T01** — Build fixture corpus from recorded prototype output.
  **Outcome**: fixtures for parity + replay tests. **Deps**: P5, P9.
  **Complexity**: Medium.
- **P13.T02** — Parity regression: refactored pipeline vs. prototype for
  identical scope (SC-001). **Outcome**: 100% listing parity proven.
  **Deps**: P13.T01, P10. **Complexity**: Large.
- **P13.T03** — Resilience tests: forced page/record failures (SC-004,
  SC-005). **Outcome**: run completes with failures recorded. **Deps**:
  P10. **Complexity**: Medium.
- **P13.T04** — End-to-end acceptance covering SC-001–SC-009. **Outcome**:
  all Success Criteria verified. **Deps**: all phases. **Complexity**:
  Large.

## Testing Strategy

> No test code is generated here. This describes what each phase must
> test and how. Tests are OPTIONAL unless the feature/spec requests them;
> this feature's spec implies validation, parity, and replay
> verification, so the suites below are required for Definition of Done.

### Unit tests (per module)
- **Configuration**: missing-value fail-fast; typed access.
- **Models**: immutability of `RawListing`; serialization round-trips.
- **Extractor**: payload → RawListing with verbatim preservation.
- **Normalizer**: deterministic mapping; marketplace-independence.
- **Canonicalizer**: equivalent values → one canonical value; determinism.
- **Validator**: each rejection reason; dedup newest-wins + counter.
- **Storage**: CSV write/read round-trip; interface conformance.
- **Run report**: all metrics present; dataset version format.
- **Replayer**: deterministic output; RawListing immutability preserved.

### Integration tests (cross-module)
- Adapter → extractor → normalizer → canonicalizer → validator → storage
  over a recorded fixture scope.
- Pipeline state transitions on success, partial failure, and fatal
  failure.
- Run report reconciliation against written records.

### Contract tests
- `StorageAdapter` interface: CSV adapter and a substitute adapter both
  satisfy the same contract (FR-051).
- `MarketplaceAdapter` interface: contract for fetch/paginate/retry
  behavior (using recorded responses, no live network in CI).

### Acceptance tests
- US1: a scoped run produces parity listings + raw payloads + run report.
- US2: a forced page failure leaves the run completing with failures
  recorded.
- US3: invalid records are skipped/logged and not persisted.
- US4: env-driven config + storage substitutability.
- US5: replay rebuilds Listings offline, deterministically, with an
  explicit Normalization Version.

### Regression considerations
- **Parity regression** (SC-001) is the primary regression gate: any
  change to extraction/normalization/canonicalization must preserve
  listing parity vs. the prototype fixture corpus.
- Canonicalization changes are versioned (Normalization Version); replay
  under an older version must reproduce older outputs.
- Storage adapter changes must not affect ingestion results (contract
  tests guard this).

## Validation Gates

No phase proceeds until the previous gate passes.

1. **Architecture Review** (after Phase 1–4): module boundaries,
   interfaces, and domain models conform to the spec's Domain Pipeline
   Model and Separation of Responsibilities.
2. **Configuration & Logging Review** (after Phase 2–3): no hardcoded
   secrets/paths; structured logging with scrubbing verified.
3. **Adapter Review** (after Phase 5): adapter contains no business
   logic; produces verbatim RawListings; retry/rate-limit verified.
4. **Normalization & Canonicalization Review** (after Phase 6–7):
   normalization ≠ canonicalization; determinism + marketplace
   independence verified.
5. **Validation Review** (after Phase 8): invalid records isolated, not
   fatal; dedup deterministic with counter.
6. **Storage Review** (after Phase 9): storage interface substitutability
   proven; ingestion unaffected by adapter swap.
7. **Pipeline Review** (after Phase 10): state machine correct; partial
   failures isolated; terminal states absorbing.
8. **Reporting Review** (after Phase 11): all required metrics present;
   dataset version + lineage recorded.
9. **Replay Review** (after Phase 12): replay offline, deterministic,
   RawListing-immutability preserved, explicit Normalization Version.
10. **Final Review** (after Phase 13): all Success Criteria SC-001–SC-009
    pass; Constitution re-check passes; Definition of Done met.

## Risks

| Risk | Cause | Impact | Mitigation |
|------|-------|--------|------------|
| Parity drift vs. prototype | Refactor unintentionally changes extraction/normalization | SC-001 fails; trust in refactor undermined | Pin parity early (Phase 13) against recorded fixture corpus; gate every stage change on parity regression. |
| Marketplace payload/endpoint change | Dubizzle alters Algolia shape or adds anti-bot | Adapter yields fewer/no RawListings | Isolate shape handling in extractor; preserve verbatim RawListings so re-processing is possible without re-fetch; log + skip malformed pages. |
| Rate limiting / IP blocking | Aggressive fetching | Reduced yield or blocked run | Conservative default rate limit + backoff (FR-013, FR-012); configurable. |
| Marketplace logic leakage | Field names leak into common modules | Breaks future multi-marketplace support (Principle XI) | Normalizer/Canonicalizer/Validator are marketplace-independent; marketplace code confined to `marketplaces/dubizzle/`; enforced by review gate. |
| Secret leakage | Credentials committed or logged | Security violation (Principle XIV) | Env-only config; secret scrubbing in logs; `.gitignore` for `.env`/outputs; source scan gate. |
| Silent partial output | Storage write failure mid-run | Appears complete but is incomplete | Fail run gracefully on storage errors; reconcile run-report counts with written records. |
| Canonicalization ambiguity | Equivalent values map incorrectly | Bad canonical values pollute downstream | Versioned canonical mappings; deterministic rules; unit tests per category; replay can correct later via new Normalization Version. |
| Replay non-determinism | Implicit "current" rules used | Historical reproducibility broken | Replay MUST use an explicit Normalization Version (Replay Rules); tested. |

### Failure Recovery

- Every pipeline stage SHOULD fail independently whenever possible.
- Failures MUST be isolated to the affected page or record.
- A failed page MUST NEVER invalidate previously processed pages.
- The RunReport MUST always identify exactly where execution stopped
  (last successful page, failing page, and the stage at failure), so a
  run can be diagnosed and — in a future feature — resumed from a
  checkpoint.

## Deliverables

- Centralized configuration module (`src/config/`)
- Domain models (`src/common/models.py`)
- Structured logging (`src/common/logger.py`)
- Dubizzle Marketplace Adapter + extractor (`src/marketplaces/dubizzle/`)
- Normalizer (`src/ingestion/normalizer.py`)
- Canonicalizer (`src/ingestion/canonicalizer.py`)
- Validation + dedup module (`src/common/validation.py`)
- Storage abstraction + CSV implementation (`src/storage/`)
- Pipeline orchestration + state machine (`src/ingestion/pipeline.py`)
- CLI runner (`src/ingestion/runner.py`)
- Run reporting + dataset versioning (`src/reporting/run_report.py`)
- Replay capability (`src/replay/replayer.py`)
- Test suites: unit, integration, contract, acceptance + fixture corpus
- Architecture Decision Log (ADR): records important implementation
  decisions discovered during Feature 001 implementation (e.g., ADR-008
  Canonicalization strategy, ADR-009 Storage abstraction design, ADR-010
  Marketplace adapter behavior). ADRs are implementation records; they do
  NOT replace the Constitution or SAD.
- Phase 0/1 artifacts: `research.md`, `data-model.md`, `contracts/`,
  `quickstart.md`

## Definition of Done

The feature is complete only when:

- All Feature Requirements (FR-001 … FR-064) are implemented.
- All Acceptance Criteria (US1–US5) pass.
- All Validation Gates (1–10) pass.
- Unit, integration, contract, and acceptance tests pass.
- No hardcoded configuration (secrets or filesystem paths) exists in
  source (verifiable by scan).
- Marketplace-specific logic is isolated to the Dubizzle adapter package.
- Storage remains replaceable (substitute adapter passes contract tests
  with no ingestion-code change).
- Replay works deterministically with an explicit Normalization Version
  and never modifies RawListings.
- Listing parity with the current prototype scraper is proven (SC-001).
- Documentation (`plan.md`, `data-model.md`, `contracts/`,
  `quickstart.md`) remains consistent with the Constitution and spec.

## Deferred Capabilities

Capabilities recorded as architectural considerations for future features.
They are NOT implemented in Feature 001.

### Checkpoint & Resume

The ingestion pipeline should eventually support checkpointing
long-running ingestion jobs. Checkpoint metadata may include:

- `scrape_run_id`
- `marketplace`
- `condition`
- `make`
- `current_page`
- `total_pages`
- `timestamp`

Purpose: if execution is interrupted unexpectedly, a future
implementation should be able to resume from the latest completed
checkpoint instead of restarting from the beginning.

Checkpointing is NOT implemented in Feature 001. It is an architectural
consideration only — the Failure Recovery requirement that the RunReport
identify exactly where execution stopped (see Risks → Failure Recovery)
is the Feature 001 foundation that makes future resume possible.

## Constraints

Do NOT (enforced by spec NFR-009 and this plan):

- Generate implementation code (this plan is a roadmap only).
- Change or add requirements.
- Introduce new features outside Feature 001.
- Introduce database persistence (PostgreSQL/Supabase/Prisma).
- Introduce REST APIs.
- Introduce authentication.
- Introduce AI, machine learning, or analytics.
- Introduce parallel execution.
- Introduce distributed workers.
- Introduce message queues.
- Introduce a dashboard or any web UI.

Stay strictly within Feature 001: Data Ingestion Foundation.
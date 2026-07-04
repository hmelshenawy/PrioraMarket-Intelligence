# Feature Specification: Data Ingestion Foundation

**Feature Branch**: `001-data-ingestion-foundation`

**Created**: 2026-07-04

**Status**: Draft

**Input**: User description: "Create Feature 001: Data Ingestion Foundation — refactor the current prototype Dubizzle scraper into a modular, production-ready ingestion pipeline that can later persist to PostgreSQL/Supabase without major architectural changes."

## User Scenarios & Testing *(mandatory)*

> **Context**: This feature is an internal platform capability with no end-user
> UI. The primary actor is the **Platform Operator / Data Engineer** who runs
> and maintains ingestion. A secondary actor is the **Platform itself**
> (downstream contexts that will later consume ingested data). User stories
> are framed from the operator's perspective and each is independently
> testable as a delivery increment.

### User Story 1 - Execute a Modular Ingestion Run (Priority: P1)

As a Platform Operator, I want to run a single ingestion command scoped by
marketplace, vehicle condition, and make, so that I obtain normalized
listings and their original marketplace payloads stored locally, with a
structured run report summarizing what happened.

**Why this priority**: This is the MVP. It delivers the core refactor
outcome — replacing the monolithic prototype script with a modular pipeline
that produces the same listings as today, preserves raw payloads, and
emits a run report. Without this, none of the other stories have a
pipeline to attach to.

**Independent Test**: Run the pipeline against one make and one condition
and verify that (a) the normalized listing count matches the current
prototype scraper for the same scope, (b) a raw payload artifact is
produced for each listing, and (c) a run report containing marketplace,
condition, make, pages processed, listings extracted, listings skipped,
execution duration, and failures is emitted.

**Acceptance Scenarios**:

1. **Given** the pipeline is configured for a target marketplace, **When**
   the operator starts a run scoped to a specific condition and make,
   **Then** the run completes and produces a normalized listings artifact
   whose record count matches the current prototype scraper for the same
   scope (listing parity).
2. **Given** a run is in progress, **When** the marketplace returns listing
   hits across multiple pages, **Then** every page is fetched in order and
   all hits are extracted into normalized domain objects.
3. **Given** a run completes, **When** the operator inspects the output,
   **Then** each normalized listing is accompanied by its original
   marketplace payload preserved verbatim.
4. **Given** a run completes, **When** the operator inspects the run
   report, **Then** it contains marketplace, condition, make, pages
   processed, listings extracted, listings skipped, execution duration,
   and failure count.

---

### User Story 2 - Resilient Ingestion with Partial-Failure Tolerance (Priority: P2)

As a Platform Operator, I want the pipeline to continue running when an
individual page or record fails, so that a single transient error does not
discard the rest of the ingestion run.

**Why this priority**: Resilience is what separates a prototype from a
production ingestion service. It does not need the pluggable storage or
configuration work to be valuable, and it is independently testable on top
of US1.

**Independent Test**: Force a failure on one page (e.g., simulated timeout
or malformed response) mid-run and verify the run completes, the failed
page is recorded in the run report's failures, and listings from all other
pages are still produced.

**Acceptance Scenarios**:

1. **Given** a page request fails after exhausting retries, **When** the
   pipeline processes the run, **Then** the failed page is logged and
   recorded as a failure and the run proceeds to the next page.
2. **Given** a request times out, **When** the timeout occurs, **Then**
   the pipeline retries the request according to its retry policy before
   recording a failure.
3. **Given** one or more pages fail during a run, **When** the run
   finishes, **Then** the pipeline completes gracefully and the run report
   reflects the count of failures and the pages they occurred on.
4. **Given** a single listing record cannot be extracted or normalized,
   **When** the pipeline encounters it, **Then** that record is skipped
   and logged without aborting the page or the run.

---

### User Story 3 - Validation Gate Before Persistence (Priority: P2)

As a Platform Operator, I want every extracted listing to be validated
before it is persisted, so that invalid records are isolated and logged
rather than corrupting the output dataset.

**Why this priority**: Data quality is the platform's primary asset
(Constitution Principle X). Validation must exist before any downstream
analytics or ML can be built. It is independently testable on top of US1.

**Independent Test**: Feed the pipeline a fixture containing one valid and
several invalid listings (missing uuid, non-numeric price, missing required
fields) and verify the valid listing is persisted while each invalid
listing is logged with a reason and counted as skipped.

**Acceptance Scenarios**:

1. **Given** a listing lacks a uuid, **When** validation runs, **Then**
   the listing is rejected, logged with the reason "missing uuid", and
   counted as skipped.
2. **Given** a listing has a non-numeric or missing price, **When**
   validation runs, **Then** the listing is rejected and logged.
3. **Given** a listing is missing one or more required fields, **When**
   validation runs, **Then** the listing is rejected and logged with the
   specific missing field(s).
4. **Given** a listing fails basic data consistency checks (e.g.,
   contradictory fields), **When** validation runs, **Then** the listing
   is rejected and logged.
5. **Given** one or more listings are invalid, **When** the run finishes,
   **Then** the run is not terminated and the run report's listings
   skipped count reflects the rejected records.

---

### User Story 4 - Configurable, Secret-Free, Pluggable Pipeline (Priority: P3)

As a Platform Operator, I want all runtime behavior driven by environment
configuration and storage hidden behind an interface, so that I can run the
pipeline in different environments without code changes and replace CSV
storage with a database later without touching ingestion logic.

**Why this priority**: This makes the pipeline production-grade and
future-proof. It builds on US1–US3 and is independently testable by
verifying configuration sourcing and storage-interface substitution.

**Independent Test**: Run the pipeline with configuration supplied entirely
through environment variables (no code edits), then run a test that
substitutes an alternative storage adapter behind the storage interface
and confirms the ingestion logic is unchanged.

**Acceptance Scenarios**:

1. **Given** the operator sets configuration via environment variables,
   **When** the pipeline starts, **Then** it reads all required values
   (marketplace endpoint, credentials, output paths, retry/rate-limit
   parameters) from configuration without any hardcoded values in code.
2. **Given** the codebase is inspected, **When** checked for secrets and
   hardcoded filesystem paths, **Then** none are found in source.
3. **Given** a required configuration value is missing, **When** the
   pipeline starts, **Then** it fails fast with a clear message naming the
   missing value.
4. **Given** the storage layer is accessed only through a defined
   interface, **When** an alternative storage adapter is provided, **Then**
   the ingestion pipeline produces identical results without changes to
   ingestion, extraction, normalization, or validation logic.

---

### User Story 5 - Replay Existing Raw Data (Priority: P4)

As a Platform Operator, I want to rebuild normalized listings from
previously stored Raw Listings, so that improvements to normalization or
validation can be applied without re-scraping the marketplace.

**Why this priority**: Replay is foundational for future ML and data
quality improvements, but it is not required for the initial ingestion MVP.
It depends on RawListing preservation (US1) and a marketplace-independent
normalizer and validator being in place.

**Independent Test**: Take a set of previously stored Raw Listings, run
replay against them with the newest normalization and validation rules,
and verify normalized Listings are produced with no marketplace access.

**Acceptance Scenarios**:

1. **Given** a set of stored Raw Listings exists, **When** the operator
   runs replay, **Then** normalized Listings are rebuilt from those Raw
   Listings.
2. **Given** replay is running, **When** the marketplace is unreachable or
   access is disabled, **Then** replay still completes because it requires
   no marketplace access.
3. **Given** normalization or validation rules have changed since the Raw
   Listings were originally captured, **When** replay runs, **Then** the
   newest rules are applied to produce the rebuilt Listings.
4. **Given** the same Raw Listings and the same rules, **When** replay is
   run twice, **Then** the resulting normalized Listings are identical
   (deterministic results).

**Replay Rules**:

- Replay MUST NEVER modify a RawListing.
- Replay MAY regenerate: the Listing, the Validation Result, and the
  Dataset Version.
- Replay MUST preserve historical reproducibility — a replay of the same
  Raw Listings under the same Normalization Version MUST reproduce the
  same derived artifacts.
- Replay MUST always use an explicitly selected Normalization Version; it
  MUST NOT implicitly use "whatever is current" without an explicit choice.

---

### Edge Cases

- A marketplace response page returns zero hits (empty result) — pipeline
  must treat this as a normal end-of-data or no-data condition, not an
  error.
- Pagination signals end of data partway through a make — pipeline must
  stop fetching further pages for that make and move on.
- A marketplace response is malformed or unexpectedly shaped (missing
  expected keys, unexpected types) — the page/record is logged and
  skipped, run continues.
- The same listing uuid appears more than once within a single run — the
  pipeline must deduplicate so it is persisted once, with deterministic
  resolution (e.g., newest occurrence wins), and the duplicate is counted.
- The marketplace returns a rate-limiting or temporary-error response —
  the pipeline applies retry/backoff and, if still failing, records the
  page as a failure and continues.
- A numeric field (e.g., price, year, kilometers) is provided as a string
  or is empty — validation rejects or coerces deterministically and logs
  the record.
- A make or condition slug yields no matching category path — the
  pipeline logs the situation and produces zero listings for that scope
  without crashing.
- The output destination is unwritable (disk full, permissions) — the
  pipeline reports a clear storage error and fails the run gracefully
  rather than producing a partial silent output.
- An individual listing's raw payload is very large or contains unusual
  encoding — it is still preserved verbatim without truncation.
- The run is interrupted and re-executed with the same parameters —
  behavior is documented and deterministic (idempotent intent preserved;
  no duplicate output records for the same scope).

## Requirements *(mandatory)*

### Functional Requirements

**Configuration**

- **FR-001**: The pipeline MUST source all runtime configuration from a
  centralized configuration module driven by environment variables.
- **FR-002**: The pipeline MUST NOT contain hardcoded secrets or hardcoded
  filesystem paths in source code.
- **FR-003**: The pipeline MUST fail fast with a clear, named message when
  a required configuration value is missing.

**Marketplace Adapter**

- **FR-010**: The pipeline MUST provide a dedicated marketplace adapter
  responsible only for HTTP communication, request construction,
  pagination, retry handling, rate limiting, and response parsing.
- **FR-011**: The marketplace adapter MUST contain no business logic
  (no normalization or validation); its only data responsibility is
  marketplace-specific field mapping.
- **FR-012**: The marketplace adapter MUST apply a configurable retry
  policy with backoff for failed or timed-out requests.
- **FR-013**: The marketplace adapter MUST enforce a configurable rate
  limit between requests.
- **FR-014**: The marketplace adapter MUST support configurable request
  timeouts.
- **FR-015**: Every marketplace MUST provide its own adapter (e.g.,
  `DubizzleAdapter`, a future `FutureMarketplaceAdapter`). The ingestion
  pipeline MUST remain marketplace-independent. The adapter owns HTTP
  communication, request construction, pagination, response parsing, and
  marketplace-specific field mapping. No business logic belongs inside
  adapters.

**Data Extraction**

- **FR-020**: The pipeline MUST separate listing extraction into a
  dedicated component that parses the marketplace payload and returns
  domain objects.
- **FR-021**: The extraction component MUST preserve the raw marketplace
  payload verbatim alongside each extracted listing.
- **FR-022**: The extraction component MUST extract normalized listing
  fields from the marketplace payload without applying marketplace-specific
  naming to the rest of the system.
- **FR-023**: Every normalized listing MUST be traceable to its
  marketplace, its raw listing, the ingestion run that produced it, and the
  dataset version it belongs to. The platform MUST be capable of
  reconstructing how a normalized listing was produced (data lineage).

**Validation**

- **FR-030**: The pipeline MUST validate every listing before persistence,
  checking at minimum: uuid presence, required fields, numeric value
  validity, and basic data consistency.
- **FR-031**: Invalid records MUST be logged with a reason and counted as
  skipped; they MUST NOT terminate the ingestion run.
- **FR-032**: Validation rules MUST be defined in a dedicated, reusable
  component independent of marketplace-specific logic.
- **FR-033**: Listings duplicated within the same ingestion run MUST be
  deduplicated using the marketplace UUID before persistence. Deduplication
  MUST be deterministic: the newest occurrence wins, and a duplicate
  counter MUST be incremented for each suppressed duplicate.

**Normalization**

- **FR-040**: The pipeline MUST normalize marketplace-specific data into
  the platform's internal listing format via a dedicated normalizer.
- **FR-041**: Marketplace-specific logic MUST be isolated so that no
  component outside the marketplace adapter depends on marketplace field
  names.
- **FR-042**: The normalized listing format MUST be stable and independent
  of any single marketplace's payload shape.

**Canonicalization**

- **FR-043**: The platform MUST canonicalize normalized business values
  before validation. Equivalent marketplace values (e.g., `Mercedes Benz`,
  `Mercedes-Benz`, `Mercedes`) MUST be converted into a single
  platform-wide canonical value (e.g., `Mercedes-Benz`). This applies to
  at least make, model, fuel type, transmission, regional spec, and body
  type.
- **FR-044**: Canonicalization MUST be deterministic and
  marketplace-independent. The same input value MUST always produce the
  same canonical value regardless of which marketplace supplied it.
- **FR-045**: Canonical values MUST become the platform's internal
  representation of business values. Downstream components (validation,
  storage, and future analytics/ML) MUST consume canonical values, not raw
  marketplace values.

**Storage**

- **FR-050**: The pipeline MUST persist output via a storage interface,
  with CSV as the initial implementation.
- **FR-051**: The storage interface MUST allow CSV to be replaced by a
  database (e.g., PostgreSQL/Supabase) in a future feature without
  changes to ingestion, extraction, normalization, or validation logic.
- **FR-052**: The pipeline MUST continue to use CSV as the interim storage
  format for this feature; no database is implemented here.

**Logging & Run Reporting**

- **FR-060**: The pipeline MUST use structured logging throughout.
- **FR-061**: Every ingestion run MUST produce a run report containing at
  minimum the basic metrics: marketplace, condition, make, pages processed,
  listings extracted, listings skipped, execution duration, and failures.
- **FR-062**: Logs MUST NOT contain secrets.
- **FR-063**: The run report MUST also include extended metrics:
  `retry_count`, `duplicate_count`, `validation_failures`,
  `pages_per_second`, `listings_per_second`, `fetch_duration`,
  `processing_duration`, and `storage_duration`. These metrics support
  monitoring and future optimization of the ingestion pipeline.
- **FR-064**: The run report MAY include optional operational metrics:
  `start_time`, `end_time`, `total_duration`, `peak_memory`, and
  `peak_cpu`. These metrics are intended for operational monitoring and
  future optimization and are not required for run correctness.

**Error Handling**

- **FR-070**: The pipeline MUST support request retry, timeout handling,
  partial failures, and graceful completion.
- **FR-071**: A failed page MUST NOT terminate the entire ingestion
  process whenever recovery is possible; the run continues with remaining
  pages.
- **FR-072**: The pipeline MUST distinguish retryable failures (transient
  network/rate-limit) from non-retryable failures (malformed data) in
  logging and run reporting.

**Architecture & Modularity**

- **FR-080**: The prototype scraper MUST be refactored into small modules
  with single responsibilities (configuration, ingestion orchestration,
  marketplace adapter, extraction, normalization, storage, logging,
  validation, domain models).
- **FR-081**: Modules MUST communicate through clear interfaces; internal
  implementation details of one module MUST NOT be relied upon by another.
- **FR-082**: The ingestion orchestration MUST be separable from any
  specific marketplace so that adding a second marketplace does not
  require rewriting ingestion logic.

### Non-Functional Requirements

- **NFR-001 (Parity)**: The refactored pipeline MUST produce the same
  normalized listings as the current prototype scraper for an identical
  scope (marketplace, condition, make).
- **NFR-002 (Maintainability)**: Each module MUST have a single
  responsibility and be independently readable and testable.
- **NFR-003 (Configurability)**: All environment-specific values MUST be
  externalized; no code change is required to run in a new environment.
- **NFR-004 (Resilience)**: The pipeline MUST complete a run whenever at
  least one page succeeds, isolating failures to the affected page/record.
- **NFR-005 (Observability)**: A run's outcome MUST be reconstructable
  from its structured logs and run report alone, without re-running
  ingestion.
- **NFR-006 (Future-Proofing)**: Replacing CSV storage with a database
  MUST require changes only within the storage layer, not ingestion logic.
- **NFR-007 (Secret Hygiene)**: No secret material MAY appear in source
  code, logs, or run reports.
- **NFR-008 (Portability)**: Marketplace-specific logic MUST be confined
  to the marketplace adapter; the rest of the pipeline MUST be
  marketplace-agnostic.
- **NFR-009 (No Scope Creep)**: This feature MUST NOT introduce
  PostgreSQL, Supabase, Prisma, REST APIs, NestJS, authentication,
  analytics, AI, machine learning, price prediction, a dashboard, or any
  web UI.

### Key Entities *(include if feature involves data)*

- **RawListing**: The original marketplace listing exactly as received from
  the marketplace. Responsibilities:
  - Immutable.
  - Preserved verbatim (no transformation, truncation, or enrichment).
  - The source for re-processing.
  - The source for debugging.
  - The source for future normalization improvements.
  - The source for ML dataset rebuilding.
  RawListing is NOT the same as the normalized Listing. It is the ground
  truth from which a normalized Listing is derived; the normalized Listing
  is a derived, marketplace-independent projection. Every normalized
  Listing MUST be traceable back to its marketplace, its RawListing, the
  ingestion run that produced it, and the dataset version it belongs to
  (data lineage).
- **Listing (Normalized)**: The platform's internal, marketplace-independent
  representation of a marketplace vehicle listing. Stable fields
  (e.g., uuid, make, condition, price, year, source url). The authoritative
  shape consumed by future contexts. Derived from a RawListing via the
  normalizer; never received directly from a marketplace.
- **Ingestion Run**: A single execution of the pipeline scoped by
  marketplace, condition, and make. Carries the run report metadata (basic
  and extended metrics) and identifies the produced artifacts and dataset
  version.
- **Marketplace Source**: An external data provider (Dubizzle in this
  feature) accessed through a marketplace adapter. Identified independently
  of any specific marketplace's internal field names.
- **Validation Result**: The outcome of validating a listing — accepted or
  rejected with a reason — recorded for skipped-record accounting.
- **Dataset Version**: An identifier assigned to a successful ingestion run
  that ties produced listings to a specific scrape run, marketplace,
  execution timestamp, and ingestion configuration (see Dataset Versioning).
- **Normalization Version**: An identifier for the set of normalization and
  canonicalization rules used to produce a normalized Listing. Tracks
  which rules generated a derived Listing. Replay MAY produce different
  normalized Listings if the Normalization Version changes; a RawListing
  never changes — only derived artifacts change (see Replay, User Story 5).

## Domain Pipeline Model

> Conceptual model only. This describes responsibilities and data flow,
> not implementation details (no frameworks, libraries, or file layouts).

```text
Marketplace
    ↓
Marketplace Adapter
    ↓
RawListing
    ↓
Listing Normalizer
    ↓
Canonicalizer
    ↓
Listing Validator
    ↓
Storage Adapter
    ↓
Run Report
```

Stage responsibilities:

- **Marketplace**: an external data provider (e.g., Dubizzle). The source of
  original listing data. Treated as untrusted and outside the platform's
  control.
- **Marketplace Adapter**: owned per marketplace. Responsible for HTTP
  communication, request construction, pagination, response parsing, and
  marketplace-specific field mapping. Produces RawListings. Contains no
  business logic.
- **RawListing**: the immutable, verbatim original listing as received from
  the marketplace. Preserved unchanged. The ground truth for all downstream
  derivation, debugging, re-processing, and ML dataset rebuilding.
- **Listing Normalizer**: maps a RawListing into the platform's
  marketplace-independent object shape. Confines marketplace-specific
  transformation logic (with the adapter). Deterministic. Does NOT
  standardize business values.
- **Canonicalizer**: standardizes business values into platform-wide
  canonical values (e.g., `Mercedes Benz`, `Mercedes-Benz`, `Mercedes` →
  `Mercedes-Benz`; likewise model names, fuel types, transmission names,
  regional specs, body types). Runs after normalization and before
  validation. Normalization maps marketplace payloads into platform
  objects; canonicalization standardizes business values — these are
  separate responsibilities.
- **Listing Validator**: validates the canonicalized Listing (uuid, required
  fields, numeric values, basic consistency) and deduplicates by
  marketplace UUID. Rejects and logs invalid records without aborting the
  run.
- **Storage Adapter**: persists RawListings and canonicalized Listings
  through a storage interface (CSV in this feature; replaceable by a
  database in a future feature). Ingestion logic is independent of the
  storage implementation.
- **Run Report**: the structured outcome of the run, carrying basic and
  extended metrics and the dataset version.

### Separation of Responsibilities

Each component owns exactly one responsibility. No component MAY own
another component's responsibility.

- **Marketplace Adapter** — marketplace communication, pagination, request
  construction, response parsing.
- **Normalizer** — platform object mapping.
- **Canonicalizer** — business value standardization.
- **Validator** — data quality checks.
- **Storage Adapter** — persistence.

## Pipeline State Machine

> Describes ingestion execution flow only. States are conceptual and do not
> imply a specific implementation.

States:

- **CREATED**: the run has been initialized with its configuration and scope
  but has not started fetching.
- **RUNNING**: the run is active and progressing through its stages.
- **FETCHING**: the marketplace adapter is requesting and receiving pages.
- **NORMALIZING**: RawListings are being transformed into normalized
  Listings.
- **CANONICALIZING**: normalized Listings are having their business values
  standardized into platform-wide canonical values.
- **VALIDATING**: canonicalized Listings are being validated and
  deduplicated.
- **STORING**: validated Listings and RawListings are being persisted via
  the storage adapter.
- **COMPLETED**: the run finished successfully with no unrecoverable
  failures.
- **FAILED**: the run could not complete due to an unrecoverable failure
  (e.g., missing configuration, storage unavailable at start).
- **PARTIAL_FAILED**: the run completed with one or more page or record
  failures recorded; usable output was still produced.

Transition rules (brief):

- CREATED → RUNNING when execution starts.
- RUNNING ↔ FETCHING / NORMALIZING / CANONICALIZING / VALIDATING / STORING
  as the pipeline progresses through stages (stages may interleave per
  page).
- FETCHING / NORMALIZING / CANONICALIZING / VALIDATING / STORING →
  COMPLETED when all pages are processed and output is persisted with no
  unrecoverable failure.
- FETCHING / NORMALIZING / CANONICALIZING / VALIDATING / STORING →
  PARTIAL_FAILED when the run completes but some pages or records failed
  and were recorded.
- Any state → FAILED on an unrecoverable error that prevents usable output.
- A run MUST NOT transition back to CREATED. Terminal states (COMPLETED,
  FAILED, PARTIAL_FAILED) are absorbing.

## Dataset Versioning

Every successful ingestion run produces a dataset version. The dataset
version identifies:

- the scrape run,
- the marketplace,
- the execution timestamp,
- the ingestion configuration.

Purpose: future analytics and ML models MUST always reference a specific
dataset version, so that results are reproducible and traceable to the
exact data that produced them. Each dataset version is produced under a
specific Normalization Version (see Key Entities), so a derived Listing is
fully identified by its RawListing together with its Normalization Version
and Dataset Version.

Example identifier: `dataset_2026_07_04_001`.

This feature establishes the **concept** of dataset versioning only. Actual
dataset persistence and management (storage, indexing, retention, lineage
registries) will be implemented in a future feature.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: For an identical scope (marketplace, condition, make), the
  refactored pipeline produces a normalized listing set equal to the
  current prototype scraper's output (100% listing parity).
- **SC-002**: 100% of persisted listings have an accompanying raw
  marketplace payload preserved verbatim.
- **SC-003**: 100% of persisted listings have passed the validation gate
  (uuid, required fields, numeric values, basic consistency).
- **SC-004**: A run in which one or more pages are forced to fail still
  completes and produces listings from all non-failed pages, with every
  failure recorded in the run report.
- **SC-005**: A run in which one or more records are invalid still
  completes, with each invalid record logged with a reason and reflected
  in the listings-skipped count, and zero invalid records persisted.
- **SC-006**: Every completed run emits a run report containing
  marketplace, condition, make, pages processed, listings extracted,
  listings skipped, execution duration, and failures — verifiable from the
  report alone.
- **SC-007**: All runtime configuration is supplied via environment; a
  grep of the source tree finds zero hardcoded secrets and zero hardcoded
  filesystem paths.
- **SC-008**: Substituting an alternative storage adapter behind the
  storage interface yields identical ingestion results with zero changes
  to ingestion, extraction, normalization, or validation code.
- **SC-009**: Adding a second marketplace requires changes only within a
  new marketplace adapter — no ingestion-orchestration logic is rewritten.

## Assumptions

- The implementation language and runtime are those of the existing
  prototype scraper (a Python script, `dubizzle_full_scrape_v2.py`); this
  feature refactors that script rather than reimplementing in a new
  language.
- The existing scraper's data source (a marketplace search endpoint) and
  its per-make/per-condition traversal strategy remain valid; this feature
  preserves behavior, it does not redesign the source.
- Dubizzle is the only marketplace in scope for this feature, but the
  architecture MUST be marketplace-agnostic per Constitution Principle XI
  (Scalability by Design).
- CSV remains an acceptable interim storage format; persistence to
  PostgreSQL/Supabase is explicitly deferred to a later feature.
- Execution is single-process and run-on-demand; scheduling, orchestration,
  and continuous ingestion are out of scope for this feature.
- The operator running the pipeline has network access to the marketplace
  and a writable local output location.
- The suggested module layout
  (`config/`, `ingestion/`, `marketplaces/<marketplace>/`, `storage/`,
  `common/`) is a planning reference; exact module names may differ as long
  as the responsibilities defined in the Functional Requirements are
  preserved.
- Listing parity (SC-001) is defined over normalized listing identity and
  field values, not over incidental differences such as output file format
  or row ordering.

## Risks

- **R-001 (Source instability)**: The marketplace may change its payload
  shape, endpoint, or introduce anti-bot/rate-limiting that breaks
  extraction or reduces yield. Mitigation: isolate marketplace-specific
  logic in the adapter; preserve raw payloads so re-processing is possible
  without re-fetching; log and skip malformed pages rather than crash.
- **R-002 (Parity drift)**: The refactor may unintentionally change which
  listings are produced versus the prototype. Mitigation: define parity
  explicitly (Assumptions) and verify SC-001 against the prototype for the
  same scope before declaring done.
- **R-003 (Rate limiting / IP blocking)**: Aggressive fetching may trigger
  blocking. Mitigation: configurable rate limit and backoff (FR-013,
  FR-012) defaulting to conservative values.
- **R-004 (Secret leakage)**: Credentials may be accidentally committed or
  logged. Mitigation: centralized config (FR-001), secret-free source
  (NFR-007), log scrubbing (FR-062).
- **R-005 (Marketplace logic leakage)**: Marketplace field names may leak
  into common code, breaking future multi-marketplace support. Mitigation:
  normalization isolation (FR-040, FR-041, FR-042) and marketplace-agnostic
  pipeline (FR-082, NFR-008).
- **R-006 (Raw payload storage growth)**: Preserving raw payloads
  verbatim increases storage volume. Mitigation: accepted for this feature
  (CSV interim); future storage feature will address retention.
- **R-007 (Silent partial output)**: A storage write failure could produce
  a partial file that looks complete. Mitigation: fail the run gracefully
  on storage errors (Edge Cases) and require the run report to reconcile
  counts with written records.

## Dependencies

- The existing prototype scraper (`dubizzle_full_scrape_v2.py`) as the
  behavior reference and refactoring starting point.
- Approved PRD, SAD, and Constitution (this feature conforms to
  Constitution Principles III, IV, VI, VII, X, XI, XIII, XIV and the Data
  Engineering Principles: incremental ingestion, idempotent scraping
  intent, UUID-based deduplication, historical/raw-payload preservation,
  and reproducible ETL).
- Network access to the target marketplace's search endpoint.
- A Python runtime environment with the packages already used by the
  prototype (HTTP, JSON, CSV, environment loading).
- A writable local filesystem path for CSV and raw-payload output,
  supplied via configuration.
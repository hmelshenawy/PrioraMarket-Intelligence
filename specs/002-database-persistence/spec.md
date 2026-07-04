# Feature Specification: Database Persistence Foundation

**Feature Branch**: `002-database-persistence`

**Created**: 2026-07-04

**Status**: Draft

**Input**: User description: "Build the database persistence foundation for PrioraMarket Intelligence. Connect the Feature 001 ingestion pipeline to PostgreSQL/Supabase while preserving the StorageAdapter architecture and keeping CSV storage available for development and testing."

## User Scenarios & Testing *(mandatory)*

> **Context**: This feature is an internal platform capability with no end-user
> UI. The primary actor is the **Platform Operator / Data Engineer** who runs
> ingestion and replays runs. A secondary actor is the **Platform itself**
> (downstream analytics, ML, and reporting contexts that will consume persisted
> data). User stories are framed from the operator's perspective and each is
> independently testable as a delivery increment. Feature 001 (Data Ingestion
> Foundation) is **frozen**: this feature MUST NOT modify Feature 001
> documentation, spec, plan, or tasks, and MUST NOT break existing Feature 001
> behavior. Architectural decisions arising during this feature are recorded
> as ADRs rather than by editing Feature 001 artifacts.

### User Story 1 - Persist a Full Ingestion Run to the Database (Priority: P1)

As a Platform Operator, I want a real ingestion run to persist raw listings,
canonical listings, snapshots, and ingestion-run metadata into
PostgreSQL/Supabase, so that the database becomes the source of truth after
ingestion instead of CSV files on disk.

**Why this priority**: This is the MVP of the persistence foundation. It
delivers the core outcome — connecting the existing ingestion pipeline to a
durable database while preserving raw payloads, derived listings, and run
metadata. None of the other stories have a persistent store to attach to
until this works.

**Independent Test**: Run the Feature 001 ingestion pipeline against one make
and one condition with the database storage backend selected, then verify that
the database contains: one IngestionRun row with a unique readable run name,
one RawListing row per extracted listing (with the raw payload preserved
verbatim and linked to the IngestionRun), one Listing row per canonical
listing (with `firstSeenRunId` and `lastSeenRunId` set to that run), and a run
report stored on the IngestionRun — all matching the counts in the run report.

**Acceptance Scenarios**:

1. **Given** the database storage backend is configured and the schema is
   applied, **When** the operator runs an ingestion scoped to a marketplace,
   condition, and make, **Then** an IngestionRun record is created with a
   unique readable run name, status, timing, page/record counts, duration,
   configuration snapshot, and the run report.
2. **Given** an ingestion run completes, **When** the operator queries the
   database, **Then** one RawListing exists per extracted listing, linked to
   the IngestionRun via `ingestionRunId`, with the original marketplace
   payload preserved verbatim and a content hash stored alongside it.
3. **Given** an ingestion run completes, **When** the operator queries the
   database, **Then** one canonical Listing exists per validated listing, with
   source, uuid, title, make, model, trim, year, price, mileage, condition,
   location, seller type, url, status, first-seen and last-seen timestamps,
   `firstSeenRunId` and `lastSeenRunId`, the current raw listing, and
   `normalizationVersion`.
4. **Given** an ingestion run completes, **When** the operator inspects the
   IngestionRun record, **Then** it carries a unique readable run name of the
   form `run_<marketplace>_<condition>_<make>_<yyyyMMdd>_<HHmmss>` (UTC) that
   can be used to resolve the run for replay.
5. **Given** an ingestion run is persisted to the database, **When** the
   operator compares database row counts to the run report, **Then** raw
   listing count, canonical listing count, and skipped/failure counts all
   reconcile with the run report.

---

### User Story 2 - Idempotent Re-Ingestion with Change History (Priority: P1)

As a Platform Operator, I want re-running ingestion for the same marketplace
scope to update existing listings by source + uuid while preserving previous
state in snapshots when meaningful fields change, so that the current Listing
table always reflects the newest data and historical changes are never lost.

**Why this priority**: Idempotent upsert with history is what makes the
database a trustworthy source of truth. Without deduplication by source +
uuid, repeated runs would duplicate listings; without snapshots, history
would be silently overwritten. It is independently testable on top of US1.

**Independent Test**: Run ingestion twice against the same scope with a
changed price and mileage on one listing between runs, then verify: the
Listing table still contains exactly one row per source + uuid (no
duplicates), the changed listing's current row reflects the newest price and
mileage and its `canonicalHash` has been updated, a ListingSnapshot row
exists capturing the prior canonical listing state in a single
`canonicalPayload` plus the changed-field list and a snapshot hash, and
unchanged listings have no new snapshot (their `canonicalHash` is
unchanged and only `lastSeenAt`/`lastSeenRunId` are refreshed).

**Acceptance Scenarios**:

1. **Given** a listing already exists in the database for a given source +
   uuid, **When** a new ingestion run delivers an updated version of that
   listing, **Then** the existing Listing row is updated in place (newest data
   wins) and no duplicate Listing row is created.
2. **Given** a meaningful change to the canonical listing state occurs
   between runs (the new canonical hash differs from `Listing.canonicalHash`),
   **When** the new run persists the updated listing, **Then** a
   ListingSnapshot row is created capturing the prior canonical listing state
   in a single `canonicalPayload` (not duplicated field columns), the
   changed-field list, a snapshot hash, the producing run, and the prior raw
   listing reference; the Listing row is updated to the newest data and its
   `canonicalHash` is updated to the new canonical hash.
3. **Given** a listing is re-observed with no meaningful field changes
   (the new canonical hash equals `Listing.canonicalHash`),
   **When** the new run persists it, **Then** only the Listing's `lastSeenAt`
   and `lastSeenRunId` are refreshed; no new ListingSnapshot is created and
   `canonicalHash` is unchanged.
4. **Given** a new run observes a listing not seen in any prior run, **When**
   it is persisted, **Then** a new Listing row is created with `firstSeenAt`
   and `lastSeenAt` set to the current run, `firstSeenRunId` and
   `lastSeenRunId` set to the current run, `canonicalHash` set to the
   initial canonical hash, and status `ACTIVE`; no snapshot is
   created for the initial state (the first observation is the current
   state).
5. **Given** multiple ingestion runs occur for the same scope, **When** the
   operator counts Listing rows by source + uuid, **Then** the count is
   stable (one row per distinct source + uuid) regardless of how many runs
   occurred.

---

### User Story 3 - Replay from an Ingestion Run Using Database Raw Listings (Priority: P1)

As a Platform Operator, I want replay to rebuild normalized listings from an
IngestionRun backed by database-stored raw listings, so that I can re-apply
normalization and validation improvements without re-scraping the marketplace.

**Why this priority**: This makes the IngestionRun the primary replay and
lineage unit for Feature 002, replacing the Feature 001 `--dataset` argument
that actually resolved by run id (ADR-012). Replay now explicitly resolves a
named run via `--run <run-name-or-id>`. It is independently testable on top
of US1.

**Independent Test**: Persist one ingestion run, then run
`replay --run <run-name-or-id> --normalization-version v1` and verify: replay
resolves the selected IngestionRun, loads only the RawListings linked to that
run via `ingestionRunId`, rebuilds normalized Listings using the selected
normalization version, performs no marketplace network access, and produces
deterministic output when run twice.

**Acceptance Scenarios**:

1. **Given** an IngestionRun exists with linked RawListings, **When** the
   operator runs `replay --run <run-name-or-id> --normalization-version v1`,
   **Then** replay resolves the IngestionRun (by run name or run id) and
   loads only the RawListings linked to that run from the database.
2. **Given** replay is running from a database-backed IngestionRun, **When**
   the marketplace is unreachable or network access is disabled, **Then**
   replay still completes because it reads only stored RawListings.
3. **Given** the same IngestionRun and the same selected normalization
   version, **When** replay is run twice, **Then** the rebuilt Listings are
   identical (deterministic results).
4. **Given** replay rebuilds listings, **When** the operator inspects output,
   **Then** rebuilt Listings are traceable to their RawListings and their
   IngestionRun (data lineage preserved), and rebuilt Listings record the
   selected `normalizationVersion`.
5. **Given** replay is invoked with a run name or id that does not match any
   IngestionRun, **When** replay runs, **Then** it completes with zero
   listings and a clear message rather than erroring.

**Replay Rules (carried from Feature 001)**:

- Replay MUST NEVER modify a RawListing.
- Replay MUST always use an explicitly selected Normalization Version; it
  MUST NOT implicitly use "whatever is current."
- Replay MUST preserve historical reproducibility — replaying the same
  RawListings under the same Normalization Version MUST reproduce the same
  derived artifacts.
- Replay output is transient in Feature 002; no `ReplayRun` row is created.

---

### User Story 4 - Swappable Storage Backend Selected by Configuration (Priority: P2)

As a Platform Operator, I want to select the storage backend (CSV, in-memory,
or PostgreSQL) through configuration and the CLI, so that I can use CSV and
in-memory for development/testing and PostgreSQL for production without code
changes to ingestion logic.

**Why this priority**: This delivers the configurability and swappability
promise of the StorageAdapter architecture. It builds on US1–US3 and is
independently testable by verifying backend selection and substitutability.

**Independent Test**: Run the same ingestion scope three times selecting CSV,
in-memory, and PostgreSQL backends respectively, then verify each run
produces equivalent persisted output for its backend and that the ingestion,
extraction, normalization, canonicalization, and validation code is unchanged
across all three.

**Acceptance Scenarios**:

1. **Given** the operator selects the CSV backend via configuration, **When**
   ingestion runs, **Then** output is written to CSV exactly as in Feature 001
   and all Feature 001 CSV tests still pass.
2. **Given** the operator selects the in-memory backend via configuration,
   **When** ingestion runs, **Then** output is held in memory and the
   Feature 001 in-memory tests still pass.
3. **Given** the operator selects the PostgreSQL backend via configuration,
   **When** ingestion runs, **Then** output is persisted to PostgreSQL/Supabase
   per US1 and US2.
4. **Given** the storage backend is swapped, **When** the ingestion code is
   inspected, **Then** no ingestion, extraction, normalization,
   canonicalization, or validation logic has changed — only the storage
   adapter and its wiring differ.
5. **Given** a required database configuration value is missing, **When** the
   PostgreSQL backend is selected, **Then** the pipeline fails fast with a
   clear, named message identifying the missing value.

---

### User Story 5 - Schema Migrations from Scratch (Priority: P2)

As a Platform Operator, I want database migrations that can create the full
schema from nothing, so that a fresh database can be provisioned
deterministically and schema changes are version-controlled.

**Why this priority**: Reproducible provisioning is required for testability
and for any future environment. It is independently testable by applying
migrations to an empty database and verifying the schema.

**Independent Test**: Start from an empty database, apply migrations, then
verify all required tables and relationships exist (MarketplaceSource,
IngestionRun, RawListing, Listing, ListingSnapshot) with the required
columns and constraints, including the source + uuid uniqueness constraint
and the unique run-name constraint on IngestionRun.

**Acceptance Scenarios**:

1. **Given** an empty database, **When** migrations are applied, **Then** the
   full schema is created with all required tables, columns, primary keys,
   foreign keys, and uniqueness constraints (including the source + uuid
   uniqueness used for deduplication and a unique constraint on
   IngestionRun.name).
2. **Given** migrations have already been applied, **When** migrations are
   applied again, **Then** they are idempotent and do not error.
3. **Given** an existing schema from a prior migration version, **When** a
   new migration is applied, **Then** the schema is updated without data loss
   where the change is additive.
4. **Given** the migration set is inspected, **When** checked for ordering,
   **Then** migrations are ordered and reproducible across environments.

---

### User Story 6 - Documentation and ADRs for the Persistence Strategy (Priority: P3)

As a Platform Operator, I want documentation explaining how to configure
Supabase/PostgreSQL and ADRs capturing the use of IngestionRun as the replay
and lineage unit, the deferral of DatasetVersion, the run naming convention,
and the persistence strategy, so that the persistence foundation is operable
and its architectural decisions are traceable.

**Why this priority**: Operability and traceability are required for a
production foundation but are not blocking for the persistence behavior
itself. It is independently testable by verifying documentation and ADRs
exist and are accurate.

**Independent Test**: Follow the documentation from a clean environment to
configure a Supabase/PostgreSQL connection, run one ingestion, and verify it
persists; then verify ADRs exist recording: IngestionRun as the Feature 002
replay/lineage unit, deferral of DatasetVersion/Dataset grouping to a future
Dataset Engineering feature, the run naming convention, and the persistence
strategy and transaction boundaries.

**Acceptance Scenarios**:

1. **Given** a clean environment, **When** the operator follows the
   configuration documentation, **Then** they can connect to
   PostgreSQL/Supabase and run a persisted ingestion without reading source
   code.
2. **Given** the documentation is inspected, **When** checked for the
   storage-backend selection mechanism, **Then** it explains how to choose
   CSV, in-memory, or PostgreSQL via configuration and the CLI, and how to
   invoke replay via `--run <run-name-or-id>`.
3. **Given** IngestionRun is the Feature 002 replay and lineage unit, **When**
   the ADR log is inspected, **Then** an ADR exists recording that decision,
   the deferral of DatasetVersion/Dataset grouping to a future Dataset
   Engineering feature, and the run naming convention, with a reference to
   ADR-012.
4. **Given** the database persistence strategy introduces architectural
   choices, **When** needed, **Then** an ADR is added (persistence strategy
   and transaction boundaries) rather than modifying Feature 001 artifacts.

---

### Edge Cases

- A listing re-observed in a later run has a canonical hash equal to
  `Listing.canonicalHash` — only `lastSeenAt` and `lastSeenRunId` are
  refreshed, `canonicalHash` is unchanged, and no ListingSnapshot is
  created.
- A listing re-observed in a later run differs only in a non-meaningful way
  (e.g., whitespace, ordering of equivalent values that produce the same
  canonical hash) — the change is not treated as meaningful and no
  snapshot is created; meaningfulness is determined by canonical hash
  comparison, not by ad-hoc field diffing.
- A run is interrupted before completion — the IngestionRun retains a
  non-terminal status (e.g., RUNNING) and partial output is not presented as
  a complete run; the run may be re-run safely without duplicating listings.
- The database is unreachable at the start of a run — the pipeline fails fast
  with a clear storage error and does not produce a partial silent output.
- The database becomes unreachable mid-run — the in-flight listing
  persistence transaction rolls back (no partial listing state is written),
  the run fails gracefully, the failure is recorded, and the IngestionRun
  status and run report reflect the failure; already-committed listing
  units remain consistent with the run report.
- A RawListing's payload is identical to one already stored under the same
  source + uuid in the same run — duplicate handling is deterministic and the
  duplicate is counted, consistent with Feature 001 FR-033.
- Replay is invoked with a run name or id that does not match any
  IngestionRun — replay completes with zero listings and a clear message,
  rather than erroring.
- Two ingestion runs generated in the same scope and same UTC second would
  produce the same run name — run-name uniqueness is enforced by a unique
  constraint and a disambiguator (e.g., a short hash or sequence suffix) is
  appended when a collision would occur, keeping run names unique and still
  human-readable.
- The operator selects the PostgreSQL backend but the schema is not applied
  — the pipeline fails fast with a clear message identifying the missing
  schema/migrations.
- A canonical listing references a RawListing whose payload cannot be
  re-normalized under a new normalization version (e.g., a field is absent) —
  replay skips the record with a reason and continues, consistent with
  Feature 001 validation behavior.

## Requirements *(mandatory)*

### Functional Requirements

**Persistence Layering**

- **FR-001**: The pipeline MUST persist output through a `PersistenceService`
  that sits between ingestion and the storage backend. The flow is:
  Pipeline → `PersistenceService` → `StorageAdapter` → storage backend.
  The ingestion pipeline MUST NOT depend directly on any database client,
  ORM, query builder, or concrete persistence implementation.
- **FR-002**: A `PostgresStorageAdapter` MUST be added that conforms to the
  `StorageAdapter` interface and satisfies the same contract as
  `CsvStorageAdapter` and `InMemoryStorageAdapter`. It is the relational
  database persistence implementation for PostgreSQL/Supabase and owns only
  backend-specific implementation: database calls and database transactions
  as requested by the `PersistenceService`. The specific ORM, query builder,
  or database library used inside the adapter is an implementation decision
  for the implementation plan, not this specification. The adapter MUST
  contain no marketplace-specific logic, no ingestion/normalization/
  canonicalization logic, and no duplicated business rules.
- **FR-003**: The storage backend MUST be selectable by configuration (e.g.,
  an environment variable or config value) with no code change to ingestion
  logic; `CsvStorageAdapter` and `InMemoryStorageAdapter` MUST remain
  available and passing their existing tests.
- **FR-004**: The CLI MUST support selecting the storage backend so the
  operator can choose CSV, in-memory, or PostgreSQL without editing code.
- **FR-005**: The `PersistenceService` MUST own all business persistence
  rules: deduplication by source + uuid, newest-wins logic,
  meaningful-change detection, the `ListingSnapshot` creation decision,
  per-listing transaction orchestration, and replay run resolution by run
  name or run id. These rules MUST NOT be duplicated inside any storage
  adapter. The `PersistenceService` MUST NOT own any DatasetVersion/Dataset
  grouping responsibility — that is deferred to a future feature.
- **FR-006**: The `StorageAdapter` interface MUST expose only the
  persistence contract required by the `PersistenceService` — the
  insert/update/read operations the service needs — plus backend-specific
  transaction control as requested by the service. It MUST NOT encode
  business rules.

**Persistence of Concepts**

- **FR-010**: The system MUST persist a `MarketplaceSource` record
  identifying each marketplace independently of marketplace-internal field
  names, with code, name, country, and base URL.
- **FR-011**: Each ingestion run MUST create an `IngestionRun` record
  carrying a unique readable run name (`name`), marketplace source,
  marketplace, condition, make, status, started/completed timestamps, pages
  scraped, listings extracted, listings skipped, failures count, duration,
  configuration snapshot, and the run report. The run name is the
  human-readable identifier used by replay (`--run <run-name-or-id>`).
- **FR-011a**: The IngestionRun run name MUST be unique and generated by a
  deterministic naming convention of the form
  `run_<marketplace>_<condition>_<make-or-scope>_<yyyyMMdd>_<HHmmss>` in UTC
  (e.g., `run_dubizzle_used_mercedes-benz_20260704_090000`). A unique
  constraint MUST enforce run-name uniqueness; when a collision would occur
  (same scope and same UTC second), a short disambiguator (hash or sequence
  suffix) MUST be appended so the name remains unique and still
  human-readable. The exact slug rules and disambiguator MUST be defined
  during planning and recorded in an ADR.
- **FR-012**: Each extracted listing MUST persist a `RawListing` record with
  the marketplace source, `ingestionRunId` (the run it belongs to), source,
  uuid, the raw marketplace payload preserved verbatim, a content hash of the
  raw payload, the extraction timestamp, the adapter version (`adapterVersion`)
  that produced it, and the marketplace payload/schema version
  (`marketplaceSchemaVersion`, or `marketplacePayloadVersion` when a schema
  version is not available) if the marketplace exposes one. These ingestion
  metadata fields support debugging when the marketplace payload structure
  changes.
- **FR-013**: Each validated canonical listing MUST persist a `Listing`
  record with marketplace source, source, uuid, title, make, model, trim,
  year, price, mileage, condition, location, seller type, url, a simple
  `status` (`ACTIVE` for listings observed in a run; Feature 002 does NOT
  infer disappearance, removal, or `SOLD` from absence in a later run),
  `firstSeenAt` and `lastSeenAt` timestamps, `firstSeenRunId` and
  `lastSeenRunId` (run lineage, not only timestamps), the current raw
  listing, `canonicalHash` (the canonical hash of the current
  row), `normalizationVersion` (the normalization logic that generated the
  canonical listing currently stored; replay under a newer normalization
  version MAY update this value), and created/updated timestamps. The
  `canonicalHash` is the deterministic basis for meaningful-change
  detection: a re-observed listing whose canonical hash equals
  `canonicalHash` is treated as unchanged.
- **FR-014**: Feature 002 MUST NOT introduce `DatasetVersion`,
  `DatasetVersionRun`, `datasetKey`, or any Dataset grouping / composition
  concept. The IngestionRun is the primary replay and lineage unit.
  DatasetVersion / Dataset grouping is deferred to a future Dataset
  Engineering / Analytics / ML feature and MAY later group multiple
  IngestionRuns without breaking the Feature 002 schema.
- **FR-015**: RawListings MUST be linked directly to their IngestionRun via
  `ingestionRunId`. Replay selects RawListings directly by
  `ingestionRunId` / run name — there is no intermediate dataset mapping
  table in Feature 002.

**Deduplication and Change History**

- **FR-020**: The `PersistenceService` MUST deduplicate listings by the
   composite key of source + uuid. Re-observing the same source + uuid
   across runs MUST update the existing Listing row, not create a duplicate.
- **FR-021**: The `PersistenceService` MUST apply newest-wins logic: when a
  re-observed listing differs from the current row, the current row is
  updated to reflect the newest values.
- **FR-022**: When the new canonical hash differs from
  `Listing.canonicalHash` (a meaningful change), the `PersistenceService`
  MUST create a `ListingSnapshot` record storing: `id`, `listingId`,
  `ingestionRunId`, `rawListingId`, `snapshotHash`, a single
  `canonicalPayload` (JSON/JSONB) containing the prior canonical listing
  state, the `changedFields` list (JSON), `capturedAt`, and `createdAt`.
  The snapshot MUST NOT duplicate individual canonical fields as separate
  columns unless explicitly needed for a later analytics feature.
- **FR-023**: The canonical hash MUST be deterministically generated from
  the complete canonical listing state. It MUST be order-independent where
  applicable, and any meaningful change to the canonical listing state MUST
  produce a different canonical hash. Meaningful-change detection compares
  the newly generated canonical hash against `Listing.canonicalHash`. The
  exact list of canonical fields participating in the hash is an
  implementation detail determined during planning and documented if
  necessary; it MUST NOT be hardcoded in the specification.
- **FR-024**: A re-observed listing whose canonical hash equals
  `Listing.canonicalHash` (no meaningful change) MUST NOT create a
  ListingSnapshot; only `lastSeenAt` and `lastSeenRunId` are refreshed on
  the Listing row, and `canonicalHash` is left unchanged.
- **FR-025**: The first observation of a listing (no prior row) MUST create
  a Listing row with `canonicalHash` set to the initial canonical
  snapshot hash and MUST NOT create a ListingSnapshot (the initial state is
  the current state).
- **FR-026**: The `PersistenceService` MUST update `canonicalHash` on
  the Listing row whenever a meaningful change is persisted, so that the
  next run's comparison is against the new current state.

**Replay**

- **FR-030**: Replay MUST resolve an IngestionRun by run name or run id via
  `replay --run <run-name-or-id> --normalization-version <version>`. Replay
  run resolution logic MUST live in the `PersistenceService`, not in any
  storage adapter. `DatasetVersion`/`datasetKey` MUST NOT be used as a
  replay handle in Feature 002.
- **FR-031**: Replay MUST rebuild listings from stored RawListings without
  contacting the marketplace.
- **FR-032**: Replay MUST load only the RawListings linked to the selected
  IngestionRun via `ingestionRunId`.
- **FR-033**: Replay MUST remain deterministic: the same IngestionRun plus
  the same selected normalization version MUST produce identical rebuilt
  Listings across replay executions.
- **FR-034**: Replay MUST require an explicitly selected normalization
  version and MUST NOT implicitly use the current normalization version.
- **FR-035**: Replay invoked with a run name or id that does not match any
  IngestionRun MUST complete with zero listings and a clear message rather
  than erroring.
- **FR-036**: Replay is not an operational workflow requiring its own
  persisted execution history in Feature 002. A `ReplayRun` entity/record
  is explicitly **out of scope** for this feature. Replay MUST simply
  resolve the selected IngestionRun, load its RawListings, rebuild Listings
  using the selected normalization version, and produce deterministic
  transient output. Future features MAY introduce `ReplayRun` if replay
  execution history becomes valuable; until then, no `ReplayRun` row is
  created.

**Schema and Migrations**

- **FR-040**: Schema changes MUST be applied through migrations, not by
  ad-hoc schema modification.
- **FR-041**: Migrations MUST be able to create the full schema from an empty
  database, including all tables, primary keys, foreign keys, and the
  source + uuid uniqueness constraint used for deduplication.
- **FR-042**: Migrations MUST be idempotent and ordered.

**Validation, Logging, and Run Reports**

- **FR-050**: Strong validation MUST run before persistence; invalid records
  MUST be logged with a reason and counted as skipped, and MUST NOT be
  persisted, consistent with Feature 001.
- **FR-051**: Structured logging MUST be preserved across all storage
  backends, and logs MUST NOT contain secrets.
- **FR-052**: Every ingestion run MUST produce a run report with the basic
  and extended metrics defined in Feature 001, and the run report MUST be
  stored on the IngestionRun record when the PostgreSQL backend is used.
- **FR-053**: Failure handling MUST be clear and testable: storage errors,
  missing configuration, and missing schema each produce a distinct,
  named failure mode.

**Transaction Atomicity**

- **FR-054**: The `PersistenceService` MUST orchestrate a single atomic
  transaction per listing across the following units, all of which succeed
  or roll back together: `RawListing` persistence, `Listing` insert/update,
  `ListingSnapshot` creation when required, the current raw listing
  reference update, the `canonicalHash` update, and the
  `firstSeen`/`lastSeen` lineage update.
- **FR-055**: If any part of a listing's persistence unit fails, the whole
  unit MUST roll back; no partial listing state is persisted.
- **FR-056**: The `IngestionRun` status and run report MUST reflect partial
  failure clearly: a per-listing persistence failure is recorded, the run
  continues with remaining listings where possible, and the run report and
  `IngestionRun.status` reflect the failures (consistent with Feature 001
  partial-failure behavior).

**Architecture and Modularity**

- **FR-060**: The ingestion pipeline and `PersistenceService` MUST remain
  decoupled from any specific ORM, query builder, database library, and from
  the database schema; the pipeline depends only on the `PersistenceService`,
  which in turn depends only on the `StorageAdapter` interface.
- **FR-061**: Marketplace-specific logic MUST NOT leak into the
  `PersistenceService` or any storage adapter; the `PersistenceService`
  operates on marketplace-agnostic domain objects and the storage adapter
  persists them. Business persistence rules (deduplication, newest-wins,
  meaningful-change detection, snapshot creation, replay run resolution,
  transaction orchestration) MUST NOT be duplicated inside any storage
  adapter.
- **FR-062**: Existing Feature 001 behavior MUST NOT break: CSV and
  in-memory storage tests MUST continue to pass unchanged.
- **FR-063**: Feature 001 documentation, PRD, Constitution, SAD, Feature 001
  spec, plan, and tasks MUST NOT be modified by this feature except where
  absolutely required; architectural decisions MUST be recorded as ADRs.

**Documentation**

- **FR-070**: Documentation MUST explain how to configure Supabase/PostgreSQL
  connectivity, how to select a storage backend via configuration and the
  CLI, and how to invoke replay via `--run <run-name-or-id>
  --normalization-version <version>`.
- **FR-071**: An ADR MUST be added recording that the IngestionRun is the
  Feature 002 replay and lineage unit, that `DatasetVersion` / Dataset
  grouping is deferred to a future Dataset Engineering feature, and the run
  naming convention — with a reference to ADR-012.
- **FR-072**: An ADR MUST be added for the database persistence strategy
  (PersistenceService/StorageAdapter layering, transaction boundaries,
  upsert-by-source-+-uuid, snapshot trigger via `canonicalHash`) where an
  architectural decision is required.

### Non-Functional Requirements

- **NFR-001 (Source of Truth)**: After an ingestion run with the PostgreSQL
  backend, the database MUST be the authoritative source of the run's
  listings, raw payloads, snapshots, and run metadata (the IngestionRun
  record and its run report).
- **NFR-002 (Substitutability)**: The `PostgresStorageAdapter` MUST satisfy
  the same storage contract as the CSV and in-memory adapters; substituting
  backends MUST require changes only within the storage layer and its wiring.
- **NFR-003 (No Coupling)**: No import of a database client, ORM, query
  builder, or schema-generated module MAY appear in ingestion, extraction,
  normalization, canonicalization, or validation code, or in the
  `PersistenceService`. The ingestion pipeline and `PersistenceService` MUST
  remain independent of any specific ORM, query builder, or database library.
  Business persistence rules (deduplication, newest-wins, meaningful-change
  detection, snapshot creation, replay run resolution) MAY appear only in
  the `PersistenceService` and MUST NOT appear in any storage adapter.
- **NFR-004 (Data Integrity)**: A run's persisted counts MUST reconcile with
  its run report; partial silent output MUST NOT be possible.
- **NFR-005 (Determinism)**: Replay over a fixed IngestionRun and a fixed
  normalization version MUST be reproducible — identical output on repeated
  replay executions.
- **NFR-006 (Observability)**: A run's outcome MUST be reconstructable from
  structured logs and the stored run report alone.
- **NFR-007 (Secret Hygiene)**: No secret material MAY appear in source
  code, logs, or run reports; database credentials MUST be supplied via
  configuration.
- **NFR-008 (Backward Compatibility)**: All Feature 001 acceptance and
  contract tests MUST continue to pass without modification.
- **NFR-009 (Testability)**: The `PersistenceService` MUST have unit tests
  covering deduplication, newest-wins, meaningful-change detection (via
  `canonicalHash`), snapshot creation, and replay run resolution by run
  name or run id. The `PostgresStorageAdapter` MUST have unit/integration
  tests covering the backend persistence operations, transaction control as
  requested by the service, and replay-from-ingestion-run. No business rule
  is tested through an adapter alone.
- **NFR-010 (Atomicity)**: Per-listing persistence MUST be atomic with
  rollback on failure (FR-054, FR-055); rollback behavior MUST be tested.
- **NFR-011 (No Disappearance Inference)**: Feature 002 MUST NOT infer
  listing disappearance, removal, or `SOLD` from absence in a later run.
  Runs are scoped (marketplace/make/condition), so absence does not imply
  disappearance; listing lifecycle management is deferred to a future
  feature with scheduled ingestion and complete marketplace coverage.
  Feature 002 preserves historical observations only.
- **NFR-012 (No Scope Creep)**: This feature MUST NOT introduce
  `DatasetVersion`, `DatasetVersionRun`, `datasetKey`, Dataset grouping, or
  dataset composition from multiple runs; nor a data warehouse / ML training
  dataset management layer; nor `ReplayRun`; nor scheduling; nor a search
  API, analytics dashboard, AI assistant, ML/price prediction,
  authentication, admin UI, or a public API.

### Key Entities *(include if feature involves data)*

- **PersistenceService**: The component that owns all business persistence
  rules: deduplication by source + uuid, newest-wins logic,
  meaningful-change detection (canonical hash vs
  `Listing.canonicalHash`), the `ListingSnapshot` creation decision,
  per-listing transaction orchestration, and replay run resolution by run
  name or run id. Sits between the ingestion pipeline and the
  `StorageAdapter`. Contains no marketplace-specific logic and no
  backend-specific logic. This is a **logical service boundary**: its
  internal implementation MAY later be decomposed into smaller services
  (e.g., `ListingPersistenceService`, `DatasetService`, `ReplayResolver`)
  without changing the external contract with the ingestion pipeline or the
  `StorageAdapter`. This clarification is architectural only; no
  implementation split is required for Feature 002.
- **MarketplaceSource**: An external data provider (e.g., Dubizzle)
  identified independently of marketplace-internal field names. Attributes:
  code, name, country, base URL, created/updated timestamps. Parent of
  IngestionRuns, RawListings, and Listings for that source. (Reference /
  seeded data: MarketplaceSource records are seeded or upserted by the
  PersistenceService when a run targets a known marketplace.)
- **IngestionRun**: A single execution of the ingestion pipeline scoped by
  marketplace, condition, and make. Carries a unique readable run `name`
  (the replay handle), run status, timing, page/record counts, duration,
  configuration snapshot, and the run report. Linked to a MarketplaceSource.
  The primary replay and lineage unit for Feature 002.
- **RawListing**: The immutable, verbatim original marketplace listing
  preserved exactly as received, with a content hash, the adapter version
  that produced it, the marketplace payload/schema version when available,
  the extraction timestamp, and an `ingestionRunId` linking it to its
  IngestionRun. Linked to a MarketplaceSource and an IngestionRun. The ground
  truth for replay, re-derivation, and debugging when the marketplace
  payload structure changes.
- **Listing (Canonical)**: The platform's marketplace-independent
  representation of a vehicle listing, deduplicated by source + uuid. The
  current row always reflects the newest data. Tracks `firstSeenAt` and
  `lastSeenAt` timestamps plus `firstSeenRunId` and `lastSeenRunId` run
  lineage, `canonicalHash` (the canonical hash of the current
  row, used as the deterministic change-detection baseline), a simple
  `status` (`ACTIVE` for listings observed in a run; Feature 002 does not
  infer disappearance or `SOLD`), and `normalizationVersion` (the
  normalization logic that generated the canonical listing currently
  stored; replay under a newer normalization version MAY update this
  value, giving every canonical Listing complete lineage independent of
  any Dataset concept). Linked to a MarketplaceSource, the last
  IngestionRun that observed it, and the current RawListing it was derived
  from.
- **ListingSnapshot**: A point-in-time capture of a Listing's prior
  canonical state at the moment a meaningful change was detected. Stores the
  prior canonical listing state in a single `canonicalPayload` (JSON/JSONB)
  — not duplicated field columns — plus the `changedFields` list, a
  `snapshotHash`, the `listingId`, the `ingestionRunId` that triggered the
  change, the `rawListingId` reference, `capturedAt`, and `createdAt`.
  Append-only history.

## Persistence Pipeline Model

> Conceptual model only. Describes responsibilities and data flow, not
> implementation details (no frameworks, libraries, or file layouts).

```text
Feature 001 Ingestion Pipeline
    ↓ (unchanged: extraction, normalization, canonicalization, validation)
PersistenceService (business persistence rules)
    ↓
Storage Adapter (interface — selected by config/CLI)
    ↓
PostgresStorageAdapter (PostgreSQL/Supabase relational implementation)
    ↓
MarketplaceSource · IngestionRun · RawListing · Listing · ListingSnapshot
```

Stage responsibilities (additions only — Feature 001 stages are unchanged):

- **PersistenceService**: owns all business persistence rules —
  deduplication by source + uuid, newest-wins logic, meaningful-change
  detection (comparing the new canonical hash against
  `Listing.canonicalHash`), the `ListingSnapshot` creation decision,
  per-listing transaction orchestration, and replay run resolution by run
  name or run id. Operates on marketplace-agnostic domain objects. Contains
  no marketplace-specific logic and no backend-specific logic.
- **Storage Adapter (interface)**: exposes only the persistence contract
  required by the `PersistenceService` — insert/update/read operations and
  transaction control as requested by the service. No business rules live
  here. Unchanged in spirit from Feature 001.
- **PostgresStorageAdapter**: a new conforming implementation that owns only
  the relational database persistence implementation for PostgreSQL/Supabase
  — database calls and database transactions as requested by the
  `PersistenceService`. The ORM/query builder/library choice is internal to
  the adapter and is decided in the implementation plan. Contains no
  marketplace-specific logic, no ingestion/normalization/canonicalization
  logic, and no duplicated business rules.
- **Replay**: resolves an IngestionRun (by run name or run id) and loads its
  RawListings from the database, then rebuilds Listings using the selected
  normalization version without marketplace access.

## IngestionRun as the Replay and Lineage Unit

This feature makes the **IngestionRun** the primary replay and lineage unit,
correcting the ADR-012 gap where Feature 001's `--dataset` argument actually
resolved by run id. Feature 002 makes that run orientation explicit and
removes the DatasetVersion indirection.

```text
IngestionRun
    │
    ▼
RawListings (selected by ingestionRunId)
    │
    ▼
Replay rebuilds Listings (selected normalization version)
```

- An IngestionRun is produced by exactly one ingestion execution and carries
  a unique readable run name.
- Replay resolves the selected IngestionRun (by run name or run id), then
  loads only the RawListings linked to that run via `ingestionRunId`.
- `DatasetVersion` / Dataset grouping is **not** introduced in Feature 002;
  it is deferred to a future Dataset Engineering / Analytics / ML feature
  that may later group multiple IngestionRuns without breaking this schema.
- The replay CLI is run-oriented: `replay --run <run-name-or-id>
  --normalization-version <version>`.

The detailed decision (IngestionRun as the unit, deferral of DatasetVersion,
and the run naming convention) and its relationship to ADR-012 MUST be
recorded in a new ADR (FR-071).

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A real ingestion run persisted via the PostgreSQL backend
  produces, in the database, one IngestionRun with a unique readable run
  name, one RawListing per extracted listing (raw payload preserved verbatim,
  linked by `ingestionRunId`), one Listing per validated listing (with
  `firstSeenRunId` and `lastSeenRunId` set), and a run report on the
  IngestionRun — all reconciling with the run report's counts.
- **SC-002**: Re-running ingestion for the same scope produces zero duplicate
  Listing rows per source + uuid; the current Listing row reflects the newest
  data and its `canonicalHash` is updated; a ListingSnapshot (storing
  the prior canonical state in a single `canonicalPayload`, not duplicated
  field columns) is created for every run in which the canonical hash
  changed, and only for those runs.
- **SC-003**: Replay invoked with `--run <run-name-or-id>
  --normalization-version <version>` rebuilds listings from the
  database-backed RawListings of the selected IngestionRun only, with zero
  marketplace network access, and produces identical output when run twice
  against the same IngestionRun and normalization version.
- **SC-004**: All Feature 001 CSV and in-memory storage tests pass
  unchanged, and the Feature 001 storage contract test passes for the
  PostgresStorageAdapter. Business persistence rules (deduplication,
  newest-wins, meaningful-change detection, snapshot creation, replay run
  resolution, transaction orchestration) are tested at the
  `PersistenceService` level; the `PostgresStorageAdapter` is tested as a
  backend implementation, and no business rule is duplicated inside any
  adapter.
- **SC-005**: Applying the migration set to an empty database creates the
  full schema (MarketplaceSource, IngestionRun, RawListing, Listing,
  ListingSnapshot — keys, foreign keys, the source + uuid uniqueness
  constraint, and a unique constraint on IngestionRun.name) with no manual
  steps. The `ListingSnapshot` table has a single `canonicalPayload` column
  for the prior canonical state and no duplicated per-field snapshot
  columns. No `DatasetVersion` or `DatasetVersionRun` table exists.
- **SC-006**: Selecting CSV, in-memory, or PostgreSQL via configuration/CLI
  yields equivalent persisted output for each backend with zero changes to
  ingestion, extraction, normalization, canonicalization, or validation
  code.
- **SC-007**: A grep of the ingestion, extraction, normalization,
  canonicalization, and validation modules, and of any storage adapter,
  finds zero imports of a database client, ORM, query builder, or
  schema-generated module; the same grep confirms no business persistence
  rule (deduplication, newest-wins, snapshot creation, replay run
  resolution) is implemented inside an adapter.
- **SC-008**: Following the configuration documentation from a clean
  environment, an operator can connect to Supabase/PostgreSQL and run a
  persisted ingestion without reading source code.
- **SC-009**: An ADR exists recording IngestionRun as the Feature 002 replay
  and lineage unit, the deferral of DatasetVersion/Dataset grouping to a
  future Dataset Engineering feature, and the run naming convention
  (referencing ADR-012); and an ADR exists for the database persistence
  strategy (PersistenceService/StorageAdapter layering, transaction
  boundaries, upsert-by-source-+-uuid, snapshot trigger via `canonicalHash`)
  where an architectural decision was required.
- **SC-010**: Per-listing persistence is atomic: forcing a failure partway
  through a listing's persistence unit leaves no partial listing state in the
  database (rollback is verified), and the IngestionRun status and run report
  reflect the per-listing failure clearly.
- **SC-011**: Every persisted canonical Listing records its
  `normalizationVersion`, and replay under a newer normalization version
  updates that value — giving every Listing complete lineage independent of
  DatasetVersion.

## Assumptions

- The implementation language and runtime remain those of Feature 001
  (Python). This feature adds database persistence to the existing pipeline
  rather than reimplementing it.
- PostgreSQL/Supabase is the production relational database target. A
  relational persistence implementation MUST sit behind the `StorageAdapter`.
  The choice of ORM, query builder, or database library is an implementation
  decision selected in the implementation plan, not fixed in this
  specification; the ingestion pipeline and `PersistenceService` MUST remain
  independent of that choice.
- The `StorageAdapter` interface defined in Feature 001 (ADR-009) is
  preserved; this feature introduces a `PersistenceService` layer between
  ingestion and the adapter. The adapter interface exposes the
  insert/update/read operations and transaction control the service needs; if
  an extension is required, it is made in a backward-compatible way and
  recorded in an ADR.
- The Feature 001 `StorageAdapter` contract operations (`write_raw`,
  `write_listings`, `write_report`, `read_raw`) remain the baseline surface;
  the exact method set may be extended only if required by the
  `PersistenceService` and only in a backward-compatible, ADR-documented
  manner.
- The canonical hash is deterministically generated from the complete
  canonical listing state. It is order-independent where applicable, and any
  meaningful change to the canonical listing state produces a different
  canonical hash. Meaningful-change detection compares the newly generated
  canonical hash against `Listing.canonicalHash`. The exact list of canonical
  fields participating in the hash is an implementation detail determined
  during planning and documented if necessary; it is not fixed in this
  specification.
- `ListingSnapshot` stores the prior canonical listing state in a single
  `canonicalPayload` (JSON/JSONB). Individual canonical fields are NOT
  duplicated as separate snapshot columns in this feature unless explicitly
  needed for a later analytics feature.
- Feature 002 uses the **IngestionRun** as its primary replay and lineage
  unit. `DatasetVersion`, `DatasetVersionRun`, `datasetKey`, and Dataset
  grouping/composition are NOT introduced in this feature; they are deferred
  to a future Dataset Engineering / Analytics / ML feature that may later
  group multiple IngestionRuns without breaking the Feature 002 schema.
- Each IngestionRun carries a unique readable run name generated by a
  deterministic naming convention of the form
  `run_<marketplace>_<condition>_<make-or-scope>_<yyyyMMdd>_<HHmmss>` in UTC
  (e.g., `run_dubizzle_used_mercedes-benz_20260704_090000`), with a
  disambiguator appended on collision. The exact slug rules and
  disambiguator are defined during planning and recorded in an ADR.
- The first observation of a listing is treated as the current state
  (sets `canonicalHash`) and produces no ListingSnapshot; snapshots
  capture only subsequent meaningful changes.
- Feature 002 does NOT infer listing disappearance, removal, or `SOLD`.
  Runs are scoped (marketplace/make/condition), so absence from a later run
  does not imply the listing disappeared; `Listing.status` stays simple
  (`ACTIVE` for observed listings), and historical observations are
  preserved. Listing lifecycle management is deferred to a future feature
  with scheduled ingestion and complete marketplace coverage.
- Replay writes transient output only; `ReplayRun` (a persisted replay
  execution-history entity) is explicitly out of scope for Feature 002
  (FR-036). Future features MAY introduce it if replay execution history
  becomes valuable.
- Every canonical Listing records its `normalizationVersion`. Replay under a
  newer normalization version MAY update a Listing's `normalizationVersion`,
  giving every canonical Listing complete lineage independent of any future
  Dataset concept.
- Database credentials and connection parameters are supplied exclusively
  via configuration (environment variables), consistent with Feature 001
  secret hygiene.
- Execution remains single-process and run-on-demand; scheduling,
  orchestration, and continuous ingestion remain out of scope.
- The operator has network access to a provisioned PostgreSQL/Supabase
  instance and permission to apply migrations.
- Feature 001 is frozen; any architectural decision arising during this
  feature is recorded as a new ADR rather than by editing Feature 001
  artifacts.

## Risks

- **R-001 (Business rule leakage into adapters)**: Business persistence
  rules could be duplicated inside `PostgresStorageAdapter` (or any adapter),
  re-coupling the pipeline to a backend and breaking swappability. Mitigation:
  all such rules live in the `PersistenceService` (FR-005, FR-061); SC-007
  greps adapters to confirm no deduplication, newest-wins, snapshot, or
  mapping logic is implemented there; the contract test covers all adapters.
- **R-001a (Adapter contract mismatch)**: The Feature 001 `StorageAdapter`
  interface may not cleanly express the operations the `PersistenceService`
  needs (upsert, snapshot insert, transaction control, dataset-resolution
  reads). Mitigation: extend the interface only in a backward-compatible way,
  keep the contract test green for all three adapters, and record the
  decision in an ADR (FR-072).
- **R-002 (Coupling leakage)**: A database client, ORM, query builder, or
  schema-generated module may accidentally be imported into ingestion logic
  or the `PersistenceService`. Mitigation: SC-007 grep check in
  tests/review; the pipeline and `PersistenceService` depend only on the
  `StorageAdapter` interface (FR-060, NFR-003).
- **R-003 (Snapshot noise or loss)**: A wrong change-detection basis can
  either flood the snapshot table with no-op changes or silently drop real
  changes. Mitigation: meaningful-change detection is a single deterministic
  canonical hash compared against `Listing.canonicalHash`
  (FR-023, FR-026), with tests for both changed and unchanged re-observation.
- **R-004 (Non-deterministic replay)**: Replay over a single IngestionRun
  could still be order-dependent if RawListing iteration is non-deterministic.
  Mitigation: deterministic RawListing load order and deterministic rebuild
  (FR-032, FR-033); tested by running replay twice against the same run and
  normalization version.
- **R-005 (Partial silent output)**: A mid-run database failure could leave
  inconsistent counts or partial listing state. Mitigation: per-listing
  atomic transactions with rollback on failure (FR-054, FR-055), clear
  failure modes (FR-053), run-status reconciliation (NFR-004), and IngestionRun
  status/run report reflecting per-listing failures (FR-056, SC-010).
- **R-006 (Schema drift)**: Ad-hoc schema changes could break migrations or
  environments. Mitigation: migrations only (FR-040), idempotent and
  ordered (FR-042), create-from-scratch verified (SC-005).
- **R-007 (Feature 001 regression)**: Adding the PostgreSQL backend could
  break CSV/in-memory behavior. Mitigation: Feature 001 tests run unchanged
  (FR-062, NFR-008, SC-004); the contract test covers all adapters.
- **R-008 (Replay contract change)**: Feature 001 replay used `--dataset`
  which actually resolved by run id (ADR-012). Feature 002 makes run
  orientation explicit with `--run <run-name-or-id>` and removes the
  DatasetVersion indirection. Mitigation: the new behavior is part of this
  feature's acceptance (US3) and documented in an ADR (FR-071); Feature 001
  replay tests are not modified — the new behavior is covered by new tests.
- **R-009 (Run-name collision)**: Two runs in the same scope and same UTC
  second would produce identical run names. Mitigation: a unique constraint
  on IngestionRun.name plus a short disambiguator appended on collision
  (FR-011a), keeping names unique and human-readable.

## Dependencies

- Feature 001 (Data Ingestion Foundation) — frozen. The ingestion pipeline,
  `StorageAdapter` interface, `CsvStorageAdapter`, `InMemoryStorageAdapter`,
  Replay, CLI, structured logging, run reports, and acceptance/contract
  tests are the foundation this feature builds on.
- ADR-009 (Storage Abstraction Design) — the `StorageAdapter` interface
  contract this feature extends.
- ADR-012 (Replay Dataset Identification Strategy) — the gap this feature
  corrects by making IngestionRun the explicit replay/lineage unit; the new
  ADR (FR-071) references it.
- Approved PRD, SAD, and Constitution. This feature conforms to the
  Constitution principles invoked by Feature 001 (modularity, clean layered
  architecture, data engineering principles: UUID-based deduplication,
  historical/raw-payload preservation, reproducible ETL) and adds durable
  persistence as the source of truth.
- A provisioned PostgreSQL/Supabase instance reachable from the run
  environment, with credentials supplied via configuration.
- The Feature 001 toolchain and runtime (Python) plus a relational database
  persistence implementation introduced in this feature (the specific ORM,
  query builder, or database library is selected in the implementation plan).

## Out of Scope

The following are explicitly out of scope for Feature 002:

- `DatasetVersion`, `DatasetVersionRun`, and `datasetKey`
- Dataset grouping and dataset composition from multiple runs
- Data warehouse dataset management
- ML training datasets and dataset engineering management
- `ReplayRun` (persisted replay execution history)
- Scheduling and continuous ingestion
- Listing disappearance / lifecycle inference (`SOLD`, `NOT_SEEN_IN_LATEST_RUN`,
  `REMOVED_OR_EXPIRED`)
- Search API
- Analytics dashboard
- AI assistant
- ML / price prediction
- Authentication
- Admin UI
- Public API
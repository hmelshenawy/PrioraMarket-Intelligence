# Module Interface Contracts: Data Ingestion Foundation

**Feature**: 001-data-ingestion-foundation
**Date**: 2026-07-04

This feature is an internal pipeline with no external API. The contracts
below are the **internal module interfaces** that enforce the spec's
Separation of Responsibilities and storage replaceability. They are
language-agnostic behavioral contracts (not code). Implementation will
express them as Python `Protocol`/`ABC` types; the behaviors here are
authoritative.

## 1. Configuration (`config`)

**Provides**: a validated configuration object.

- **Inputs**: environment variables / `.env`.
- **Behavior**:
  - Loads all required values (marketplace endpoint, credentials, output
    paths, retry, rate limit, timeout).
  - Fails fast with a named message if a required value is missing.
  - Exposes typed accessors; no hardcoded secrets or paths.
  - Exposes feature flags for operational debugging: `EnableValidation`,
    `EnableCanonicalization`, `EnableReplay`, `EnableStructuredLogging`,
    `EnableCsvStorage`. Flags are configuration-driven; business logic
    MUST NEVER depend on them.
- **Consumers**: adapter, storage, logger, runner.

## 2. MarketplaceAdapter (`adapter`)

**Interface**: per-marketplace (e.g., `DubizzleAdapter`).

- **Inputs**: configuration; scope (marketplace, condition, make).
- **Behavior**:
  - Constructs requests, paginates, retries with backoff, rate-limits,
    parses responses.
  - Delegates payload→RawListing parsing to the **extractor**.
  - Progressively yields RawListings as pages are processed (streaming /
    iterable interface preferred) — reduces memory and enables future
    queue/worker compatibility. Does NOT require asynchronous execution.
  - Emits page-level fetch metadata (for metrics).
  - Contains NO business logic (no normalization/canonicalization/
    validation).
- **Outputs**: a stream/iterable of `RawListing` + page metadata.
- **Contract test**: against recorded marketplace responses (no live
  network in CI); verifies pagination, retry, rate-limit, verbatim
  RawListing production.

## 3. Extractor (`extractor`)

**Interface**: marketplace-specific (lives in the marketplace package).

- **Inputs**: a raw marketplace hit/payload.
- **Behavior**:
  - Parses the payload into a `RawListing`.
  - Preserves the raw payload verbatim.
  - Extracts fields without leaking marketplace field names upward.
- **Outputs**: `RawListing`.
- **Consumers**: the adapter.

## 4. Normalizer (`normalizer`)

**Interface**:

- **Inputs**: `RawListing`, `NormalizationVersion`.
- **Behavior**:
  - Maps RawListing → platform `Listing` object shape.
  - Deterministic, marketplace-independent.
  - Does NOT standardize business values.
- **Outputs**: normalized `Listing` (not yet canonicalized).
- **Consumers**: pipeline, replayer.

## 5. Canonicalizer (`canonicalizer`)

**Interface**:

- **Inputs**: normalized `Listing`, `NormalizationVersion` (binds
  canonical-value mapping version).
- **Behavior**:
  - Standardizes business values (make, model, fuel, transmission,
    regional spec, body type) to canonical values.
  - Deterministic and marketplace-independent.
- **Outputs**: canonicalized `Listing`.
- **Consumers**: pipeline, replayer.

## 6. Validator (`validator`)

**Interface**:

- **Inputs**: canonicalized `Listing`; run-level dedup index.
- **Behavior**:
  - Validates uuid, required fields, numeric values, basic consistency.
  - Deduplicates by uuid (newest wins; duplicate counter incremented).
  - Invalid/duplicate records are logged, not fatal.
- **Outputs**: `ValidationResult` (accepted/rejected + reason; duplicate
  flag).
- **Consumers**: pipeline, replayer.

## 7. StorageAdapter (`storage`)

**Interface** (the critical replaceability contract — FR-050/051):

- **Inputs**: RawListings, canonicalized Listings, run metadata.
- **Behavior**:
  - `write_raw(raw_listings)` — persist RawListings (verbatim).
  - `write_listings(listings)` — persist canonicalized Listings.
  - `write_report(report)` — persist RunReport.
  - `read_raw(scope/filter)` — return stored RawListings (for replay).
  - Confirms writes; surfaces storage errors (no silent partial output).
- **Outputs**: written artifacts + write confirmation.
- **Contract test**: CSV adapter AND a substitute (in-memory/test) adapter
  both satisfy this interface; ingestion results are identical across
  both (SC-008).
- **Consumers**: pipeline, replayer.
- **Rule**: ingestion code depends ONLY on this interface, never on CSV
  specifics.

## 8. Logger (`logger`)

**Interface**:

- **Behavior**: structured (JSON) logging; run correlation id on every
  record; secret scrubbing.
- **Consumers**: all modules.

## 9. Pipeline (`pipeline`)

**Interface**:

- **Inputs**: configuration; scope; adapter; stage handlers; storage;
  run report builder.
- **Behavior**:
  - Drives the stage chain per page:
    fetch → extract → normalize → canonicalize → validate/dedup → store.
  - Implements the state machine; isolates page/record failures.
  - Records per-stage counters/timers.
- **Outputs**: a run reaching a terminal state (COMPLETED /
  PARTIAL_FAILED / FAILED).
- **Consumers**: runner (CLI).

## 10. RunReport (`run_report`)

**Interface**:

- **Inputs**: per-stage counters/timers; run scope; versions.
- **Behavior**: assembles basic + extended + optional metrics; assigns
  DatasetVersion; binds NormalizationVersion; attaches lineage.
- **Outputs**: a structured, persistable `RunReport`.

## 11. Replayer (`replayer`)

**Interface**:

- **Inputs**: stored RawListings (via `StorageAdapter.read_raw`); an
  explicitly selected `NormalizationVersion`; normalizer/canonicalizer/
  validator.
- **Behavior**:
  - Rebuilds Listings/ValidationResults/DatasetVersion from RawListings.
  - NO marketplace access (no adapter).
  - Never modifies RawListings.
  - Deterministic under the same RawListings + same NormalizationVersion.
- **Outputs**: regenerated derived artifacts.
- **Consumers**: runner (CLI replay command).

## Cross-Cutting Interface Rules

- Modules communicate ONLY through the interfaces above.
- No module imports another module's internal helpers/private state.
- Marketplace-specific code is confined to `marketplaces/<name>/`;
  everything else is marketplace-agnostic.
- The pipeline orchestrator is the only component that wires stages;
  stages do not call each other directly.
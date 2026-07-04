# Research: Data Ingestion Foundation

**Feature**: 001-data-ingestion-foundation
**Date**: 2026-07-04
**Status**: Phase 0 complete — all technical decisions resolved.

This document records the decisions that turn the approved specification
into an executable plan. The spec contained no `[NEEDS CLARIFICATION]`
markers; the research below resolves technology choices, patterns, and
best practices within the approved scope (no DB, no API, no AI/ML, no UI).

## Decision 1 — Implementation language and runtime

- **Decision**: Python 3.11.
- **Rationale**: The existing prototype (`dubizzle_full_scrape_v2.py`) is
  Python. The spec (Assumptions) mandates refactoring that script, not
  reimplementing in a new language. Python 3.11 is current, stable, and
  matches the prototype's dependencies (`requests`, `dotenv`, `csv`,
  `json`).
- **Alternatives considered**: Rewriting in TypeScript/Node or Go —
  rejected: violates "refactor, not reimplement" and adds risk with no
  in-scope benefit.

## Decision 2 — HTTP client and marketplace adapter pattern

- **Decision**: Keep `requests` for HTTP; implement the Dubizzle adapter
  behind a `MarketplaceAdapter` interface (Protocol/ABC). The adapter owns
  transport, pagination, retry/backoff, rate limiting, response parsing,
  and marketplace-specific field mapping; it produces `RawListing` objects
  via a dedicated extractor. No business logic in the adapter.
- **Rationale**: Constitution Principles IV (clean layers), XI
  (scalability), XIII (modularity), and spec FR-010–015 require an
  isolated, marketplace-agnostic adapter. `requests` is already used by
  the prototype, preserving behavior (parity, SC-001).
- **Alternatives considered**: `httpx` (async) — rejected: async adds
  complexity with no in-scope benefit for a single-process, rate-limited
  scraper; YAGNI (Principle XVI).

## Decision 3 — Configuration

- **Decision**: `python-dotenv` + a centralized `config` module exposing a
  typed configuration object; fail-fast on missing required values.
- **Rationale**: FR-001–003 and NFR-003/007 require env-driven config with
  no hardcoded secrets/paths. `dotenv` matches the prototype.
- **Alternatives considered**: `pydantic-settings` — acceptable but adds a
  dependency; a small typed dataclass + fail-fast loader is simpler
  (Principle XVI). Revisit if config complexity grows.

## Decision 4 — Structured logging

- **Decision**: `structlog` emitting JSON, with a run correlation
  identifier on every record and secret scrubbing in the formatter.
- **Rationale**: FR-060/062 and Constitution Cross-Cutting Requirements
  (structured logging, no secrets in logs).
- **Alternatives considered**: stdlib `logging` with a JSON formatter —
  acceptable; `structlog` chosen for richer structured context with
  minimal code.

## Decision 5 — Storage abstraction

- **Decision**: A `StorageAdapter` interface (Protocol/ABC) with a CSV
  implementation as the initial adapter. Ingestion code depends only on
  the interface, never on CSV specifics.
- **Rationale**: FR-050–052 and NFR-006 require storage to be replaceable
  by a database in a future feature without changing ingestion logic.
  Contract tests against the interface prove substitutability (SC-008).
- **Alternatives considered**: Writing directly to CSV — rejected: would
  bake storage into ingestion and break future DB swap.

## Decision 6 — Normalization vs Canonicalization separation

- **Decision**: Two distinct modules. The **normalizer** maps a
  `RawListing` to the platform `Listing` object shape (marketplace-
  independent, deterministic, no value standardization). The
  **canonicalizer** standardizes business values (make, model, fuel,
  transmission, regional spec, body type) via versioned canonical-value
  mappings.
- **Rationale**: Spec FR-040–045 and the Domain Pipeline Model mandate
  these as separate responsibilities. Keeping them separate lets
  canonicalization evolve (new mappings → new Normalization Version)
  without touching object mapping.
- **Alternatives considered**: A single "normalize+canonicalize" step —
  rejected: violates the spec's explicit separation and blocks
  versioned replay of canonicalization changes.

## Decision 7 — Normalization Versioning

- **Decision**: A `NormalizationVersion` identifier binds the
  normalization ruleset + canonical-value mapping version used to produce
  a Listing. Replay always selects an explicit version; it never
  implicitly uses "current".
- **Rationale**: Spec Key Entities (Normalization Version) and Replay
  Rules require historical reproducibility. RawListing is immutable; only
  derived artifacts change with the version.
- **Alternatives considered**: Timestamp-based "current rules" — rejected:
  breaks reproducibility and the explicit-selection rule.

## Decision 8 — Dataset Versioning (concept only)

- **Decision**: Every successful run is assigned a `DatasetVersion`
  identifying scrape run + marketplace + execution timestamp + ingestion
  configuration, produced under a specific Normalization Version. This
  feature establishes the concept and the identifier; actual dataset
  persistence/management is deferred.
- **Rationale**: Spec Dataset Versioning section. Keeps future
  analytics/ML referencing a concrete, reproducible dataset.
- **Alternatives considered**: Full dataset registry now — rejected:
  out of scope (spec: concept only).

## Decision 9 — Pipeline state machine

- **Decision**: Implement the spec's states (CREATED, RUNNING, FETCHING,
  NORMALIZING, CANONICALIZING, VALIDATING, STORING, COMPLETED, FAILED,
  PARTIAL_FAILED) with the specified transitions; terminal states are
  absorbing.
- **Rationale**: Spec Pipeline State Machine. Provides observable,
  reconstructable run lifecycle (NFR-005).
- **Alternatives considered**: Ad-hoc run status — rejected: not
  reconstructable, violates the spec.

## Decision 10 — Parity strategy

- **Decision**: Record a fixture corpus from the current prototype's
  output for representative scopes; use it as the parity regression
  baseline (SC-001) and as replay fixtures.
- **Rationale**: SC-001 requires 100% listing parity vs. the prototype.
  A recorded corpus makes parity and replay tests deterministic and
  network-free in CI.
- **Alternatives considered**: Live parity comparison on every run —
  rejected: non-deterministic, network-dependent, slow.

## Decision 11 — Testing approach

- **Decision**: `pytest` + `pytest-mock`. Layers: unit (per module),
  integration (stage chain), contract (adapter interfaces), acceptance
  (US1–US5, SC-001–009). CI uses recorded fixtures; no live marketplace
  calls in automated tests.
- **Rationale**: Spec implies validation/parity/replay verification;
  Constitution Cross-Cutting Requirements mandate unit/integration/
  contract tests.
- **Alternatives considered**: `unittest` stdlib only — acceptable but
  `pytest` is the ecosystem standard and matches fixture-driven testing.

## Decision 12 — Error handling and resilience

- **Decision**: Retryable failures (transient network, rate-limit
  responses) are retried with backoff inside the adapter; non-retryable
  failures (malformed data) are logged and skipped. Page/record failures
  are recorded in the run report; the run continues (PARTIAL_FAILED) when
  usable output is produced.
- **Rationale**: FR-070–072, US2, SC-004/005, Constitution Principle XIV.
- **Alternatives considered**: Fail-fast on any error — rejected: violates
  the resilience requirement.

## Conclusion

All decisions stay within Feature 001 scope and conform to the
Constitution. No `[NEEDS CLARIFICATION]` items remain. Phase 1 (design
and contracts) can proceed.
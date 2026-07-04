# ADR-009: Storage abstraction behind a StorageAdapter interface

**Status:** Accepted
**Date:** 2026-07-04
**Feature:** 001 — Data Ingestion Foundation

## Context

Feature 001 must use CSV as temporary storage, but the platform's roadmap
requires PostgreSQL/Supabase persistence later without major
architectural changes. The Constitution (Principle XIII Modularity,
Principle IV Clean Layered Architecture) requires modules to communicate
only through public interfaces and persistence to be isolated in
repositories. If the pipeline wrote CSVs directly, migrating to a
database would require editing ingestion orchestration — exactly the
coupling the Constitution forbids.

## Decision

Define a `StorageAdapter` interface (`src/storage/interface.py`) as a
`Protocol` with four operations: `write_raw`, `write_listings`,
`write_report`, `read_raw`. The ingestion pipeline depends **only** on
this interface, never on a concrete backend.

Two conforming implementations ship in this feature:

- `CsvStorageAdapter` (`src/storage/csv_storage.py`) — the production
  backend for Feature 001 (JSONL raw, CSV listings, JSON report).
- `InMemoryStorageAdapter` (`src/storage/in_memory.py`) — the substitute
  used to prove substitutability (SC-008) and in tests.

A future `PostgresStorageAdapter` satisfies the same protocol and is
wired in at the runner boundary with **zero** changes to ingestion,
extraction, normalization, canonicalization, or validation code.

Contract tests (`tests/contract/test_storage_adapter.py`) verify both
adapters satisfy the protocol and behave identically for the operations
the pipeline relies on.

## Alternatives considered

- **Direct CSV writes in the pipeline.** Rejected: violates modularity
  and makes the database migration a cross-cutting rewrite.
- **An ORM/active-record layer now.** Rejected: out of scope (no DB in
  Feature 001) and would prematurely couple the interface to a schema.
- **A single concrete class with a "backend" flag.** Rejected: violates
  the interface-segregation principle and lets business logic depend on
  the flag.

## Consequences

- Any storage backend must preserve the four-operation contract and the
  "raw verbatim, listings derived" split.
- `read_raw` must return RawListings without marketplace access, which
  is what makes offline replay (US5) possible.
- Substitutability is continuously verified by the contract test, so the
  future database migration is mechanically a new adapter + a runner
  wiring change.
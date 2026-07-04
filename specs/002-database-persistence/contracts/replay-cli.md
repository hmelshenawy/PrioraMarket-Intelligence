# Contract: Replay CLI

**Feature**: 002 — Database Persistence Foundation
**Spec refs**: FR-030..036, FR-070, FR-071, NFR-005, SC-003, ADR-012

Feature 002 makes the **IngestionRun** the explicit replay and lineage unit,
correcting the ADR-012 gap where Feature 001's `--dataset` argument actually
resolved by run id.

## CLI surface

```bash
replay --run <run-name-or-id> --normalization-version <version> [--storage-backend <csv|in-memory|postgres>] [--env <path>]
```

- `--run` (required): the IngestionRun run **name** or run **id**. Replaces
  the Feature 001 `--dataset` argument as the primary replay handle.
- `--normalization-version` (required, no implicit default): the explicit
  normalization version to apply (FR-034). Replay MUST NOT implicitly use
  "whatever is current."
- `--storage-backend`: optional backend override (default from
  `STORAGE_BACKEND`).

> The Feature 001 `--dataset` path is **not deleted** (R-008); it is
> superseded by `--run` for the database backend. Feature 001 replay tests
> are not modified; the new behavior is covered by new tests.

## Behavioral contract

1. **Run resolution (FR-030)**: replay calls `PersistenceService.resolve_run`
   with the `--run` value (name or id). Resolution lives in the service, not
   in any adapter.
2. **Raw loading (FR-032)**: replay loads only the `RawListings` linked to
   the resolved `IngestionRun` via `ingestion_run_id`
   (`PersistenceService.load_raw_for_run`).
3. **No marketplace access (FR-031)**: replay never imports or calls a
   marketplace adapter; it reads only stored `RawListings`. Verified by a
   network-disabled test.
4. **Deterministic rebuild (FR-033, NFR-005)**: replay reuses the Feature 001
   `Normalizer` / `Canonicalizer` / `Validator` with the selected
   normalization version. `RawListings` are loaded in deterministic order
   (by `id`); the same run + version yields identical output across
   executions.
5. **Explicit normalization version (FR-034)**: missing
   `--normalization-version` is an error; replay never falls back to the
   current version.
6. **Unknown run (FR-035)**: replay with a name/id matching no
   `IngestionRun` completes with **zero listings and a clear message**,
   rather than erroring.
7. **No ReplayRun (FR-036)**: replay produces transient output only; no
   `ReplayRun` row is created.
8. **Normalization-version lineage (FR-013, SC-011)**: rebuilt listings
   record the selected `normalizationVersion`; replay under a newer
   normalization version MAY update a `Listing`'s `normalizationVersion`.

## Exit codes

- `0` — replay completed (including zero-listings unknown-run case).
- `2` — configuration error (missing `--normalization-version`, missing DB
  config when postgres selected).
- `1` — unexpected runtime failure.

## ADR

The decision (IngestionRun as the unit, deferral of `DatasetVersion`, run
naming) and the reference to ADR-012 are recorded in ADR-013 (FR-071).
# Contract: IngestionRun Run Naming

**Feature**: 002 — Database Persistence Foundation
**Spec refs**: FR-011, FR-011a, FR-071, R-009, SC-005

Each `IngestionRun` carries a unique readable run `name` that is the
human-readable replay handle (`replay --run <run-name-or-id>`).

## Format

```
run_<marketplace>_<condition>_<make-or-scope>_<yyyyMMdd>_<HHmmss>
```

- Timestamp is **UTC** of the run start (`yyyyMMdd_HHmmss`).
- Example: `run_dubizzle_used_mercedes-benz_20260704_090000`.

## Slug rules

- Each segment is lowercased and ASCII-slugged: non-alphanumeric characters
  are collapsed to a single `-`; leading/trailing `-` are stripped; empty
  segments are replaced by `unknown`.
- `<marketplace>`: the marketplace code (e.g., `dubizzle`).
- `<condition>`: the scope condition (e.g., `used`, `new`).
- `<make-or-scope>`: the make slug when present; otherwise a compact scope
  digest.
- `<yyyyMMdd>_<HHmmss>`: UTC timestamp of run start.

## Uniqueness & disambiguator

- A **unique constraint** on `ingestion_run.name` enforces uniqueness at the
  database level (Phase 2, SC-005).
- The `PersistenceService` generates the candidate name in
  `src/common/run_naming.py` (pure Python) and probes for an existing
  `ingestion_run.name` before insert.
- On collision (same scope and same UTC second), a short disambiguator
  `_<8-char hex>` is appended. The hex is derived deterministically from the
  candidate + run id (e.g., `sha1(candidate + run_id)[:8]`) so it is
  reproducible from the inputs (R-5).
- On a rare unique-constraint violation at insert time, the service retries
  with a fresh disambiguator (R-009).

## Generation location

- Run-name generation is pure Python in `src/common/run_naming.py`.
- The rule is owned by the `PersistenceService` (FR-005), not by any adapter.
- The `PostgresStorageAdapter` only persists the name and reports the unique
  constraint violation; it does not generate names.

## ADR

The run naming convention, the disambiguator, and the relationship to ADR-012
are recorded in ADR-013 (FR-071).

## Examples

```
run_dubizzle_used_toyota_20260704_090000
run_dubizzle_new_bmw_20260704_091530
run_dubizzle_used_mercedes-benz_20260704_090000_a1b2c3d4   # collision disambiguated
```
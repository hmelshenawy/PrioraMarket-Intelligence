# Quickstart: Database Persistence Foundation

**Feature**: 002 — Database Persistence Foundation
**Date**: 2026-07-04

This guide walks an operator from a clean environment to a persisted
ingestion and a DB-backed replay, without reading source code. It covers
local PostgreSQL (Docker) and Supabase, migration workflow, backend
selection, and replay.

> Feature 001 behavior remains the default (`STORAGE_BACKEND=csv`). Nothing
> in this guide modifies Feature 001.

## 1. Prerequisites

- Python 3.11+
- Docker (for local PostgreSQL) **or** a Supabase project
- Feature 001 dependencies installed (`pip install -e ".[dev]"`)

Install the Feature 002 database extras:

```bash
pip install -e ".[db]"
```

This installs the PostgreSQL driver (`psycopg` 3) and the migration tool
(`yoyo-migrations`) selected in `research.md`.

## 2. Configure environment

Copy `.env.example` to `.env` and fill in the Feature 001 marketplace values,
then add the Feature 002 database/backend values:

```dotenv
# Feature 002 — backend selection
STORAGE_BACKEND=postgres     # csv | in-memory | postgres

# Feature 002 — PostgreSQL/Supabase (required only when STORAGE_BACKEND=postgres)
DATABASE_URL=postgres://user:password@localhost:5432/prioramarket
DB_POOL_MIN=1
DB_POOL_MAX=5
DB_CONNECT_TIMEOUT=10
```

- For local Docker Postgres, use the URL shown above with your local
  credentials.
- For Supabase, use the project's connection string (Session Mode URL, not
  the pooled Transaction Mode URL, when using a per-process pool).
- Secrets must come from the environment only (NFR-007). Never commit `.env`.

If `STORAGE_BACKEND=postgres` and a required DB value is missing, the CLI
fails fast with a named `ConfigurationError` listing the missing value.

## 3. Start a local PostgreSQL (Docker)

```bash
docker run -d --name prioramarket-pg \
  -e POSTGRES_USER=prioramarket \
  -e POSTGRES_PASSWORD=prioramarket \
  -e POSTGRES_DB=prioramarket \
  -p 5432:5432 \
  postgres:16
```

Set `DATABASE_URL=postgres://prioramarket:prioramarket@localhost:5432/prioramarket`.

### Or use Supabase

1. Create a project at https://supabase.com.
2. Copy the connection string from **Project Settings → Database**.
3. Set `DATABASE_URL` to that string.

## 4. Apply migrations

Create the full schema from an empty database (US5, SC-005):

```bash
python -m src.db.migrate apply
```

Check status:

```bash
python -m src.db.migrate status
```

Rollback the last migration (reversible — Constitution "Migration Strategy"):

```bash
python -m src.db.migrate rollback
```

Re-applying is idempotent (FR-042):

```bash
python -m src.db.migrate apply   # safe to run again
```

### Marketplace reference data

The migration set seeds the initial `MarketplaceSource` reference row,
idempotently:

| code | name | country | base_url |
|---|---|---|---|
| `dubizzle_uae` | `Dubizzle UAE` | `UAE` | `https://dubizzle.com` |

After `python -m src.db.migrate apply`, the `marketplace_source` table
contains this row. `IngestionRun` records reference it; the
`PersistenceService` resolves it by `code` and does not create it per run.
To add a new marketplace later, add a new seed migration rather than creating
rows at run time.

## 5. Run an ingestion with the PostgreSQL backend

```bash
python -m ingestion.runner run \
  --marketplace dubizzle --condition used --make toyota \
  --storage-backend postgres
```

(Or omit `--storage-backend` and set `STORAGE_BACKEND=postgres` in `.env`.)

After the run, verify the database is the source of truth (US1, SC-001):

- One `ingestion_run` row with a unique readable `name`
  (e.g., `run_dubizzle_used_toyota_20260704_090000`).
- One `raw_listing` row per extracted listing, with the raw payload preserved
  verbatim and linked by `ingestion_run_id`.
- One `listing` row per validated listing, with `first_seen_run_id` and
  `last_seen_run_id` set.
- The run report stored on the `ingestion_run` row (`report_json`).

## 6. Re-run ingestion (idempotent upsert with history)

Run the same scope again, optionally with a changed marketplace state:

```bash
python -m ingestion.runner run \
  --marketplace dubizzle --condition used --make toyota \
  --storage-backend postgres
```

Expected (US2, SC-002):

- Still exactly one `listing` row per `(source, uuid)` — no duplicates.
- For listings whose canonical state changed: a `listing_snapshot` row with
  the prior `canonical_payload` (single JSONB), `changed_fields`,
  `snapshot_hash`; the `listing` row updated to newest data and
  `canonical_hash` updated.
- For unchanged listings: only `last_seen_at` / `last_seen_run_id` refreshed;
  no new snapshot.

## 7. Replay from a run (no marketplace access)

Resolve a run by name or id and rebuild listings offline (US3, SC-003):

```bash
python -m ingestion.runner replay \
  --run run_dubizzle_used_toyota_20260704_090000 \
  --normalization-version norm-1 \
  --storage-backend postgres
```

Expected:

- Replay resolves the `IngestionRun` by name (or id) and loads only its
  `raw_listing` rows.
- No marketplace network access occurs (disable network to verify).
- Running replay twice against the same run + normalization version produces
  identical output (deterministic — NFR-005).
- An unknown run name/id completes with zero listings and a clear message
  (FR-035).

## 8. Switch backends (configuration only)

Switching backends requires **no code change** (US4, SC-006):

```bash
# CSV (Feature 001 default)
STORAGE_BACKEND=csv python -m ingestion.runner run --marketplace dubizzle --condition used --make toyota

# In-memory (testing)
STORAGE_BACKEND=in-memory python -m ingestion.runner run --marketplace dubizzle --condition used --make toyota

# PostgreSQL (production)
STORAGE_BACKEND=postgres python -m ingestion.runner run --marketplace dubizzle --condition used --make toyota
```

Ingestion, extraction, normalization, canonicalization, and validation code
is identical across all three backends.

## 9. Run the tests

```bash
# Unit + contract (no DB needed for most)
pytest tests/unit tests/contract

# Integration (requires DATABASE_URL pointing at a running Postgres/Supabase)
DATABASE_URL=postgres://prioramarket:prioramarket@localhost:5432/prioramarket \
  pytest tests/integration
```

## 10. ADRs

See `docs/adr/` for:

- **ADR-013** — IngestionRun as the Replay and Lineage Unit (references
  ADR-012).
- **ADR-014** — Database Persistence Strategy (layering, transaction
  boundaries, upsert-by-source-+-uuid, snapshot trigger via
  `canonicalHash`, driver/migration choice).

Feature 001 artifacts are not modified by this feature (FR-063).
# Data Model: Database Persistence Foundation

**Feature**: 002 — Database Persistence Foundation
**Date**: 2026-07-04
**Spec**: [spec.md](./spec.md) | **Plan**: [plan.md](./plan.md) | **Research**: [research.md](./research.md)

This document defines the persisted entities, their fields, types,
relationships, constraints, and validation rules. It is the Phase 1 design
output. The schema is created by migrations (Phase 2) and accessed only
through the `PostgresStorageAdapter` (Phase 3). `DatasetVersion`,
`DatasetVersionRun`, `datasetKey`, and `ReplayRun` are **not** present
(spec FR-014, FR-036, NFR-012).

PostgreSQL types are used; `JSONB` is used for all JSON columns (R-4).
Timestamps are `TIMESTAMPTZ` (UTC). Surrogate primary keys are `BIGSERIAL` /
`UUID` per entity as noted; the deduplication key is the composite
`(source, uuid)` unique constraint on `listing`.

---

## Entity Relationship Diagram (logical)

```text
MarketplaceSource (reference/seeded)
    │ 1
    │
    │ N
IngestionRun ──(name unique)──▶ resolved by replay (--run)
    │ 1
    │
    │ N
RawListing ──(selected by ingestion_run_id for replay)
    │
    │
Listing ──(unique (source, uuid))──▶ deduplication key
    │ 1                                ▲
    │ N                                │ current_raw_listing_id
    │                                  │
ListingSnapshot (append-only, single canonical_payload)

VehicleGenerationCatalog (reference/catalog, no listing relationship yet)
```

- `MarketplaceSource` 1 — N `IngestionRun`
- `MarketplaceSource` 1 — N `RawListing`
- `MarketplaceSource` 1 — N `Listing`
- `IngestionRun` 1 — N `RawListing`
- `IngestionRun` 1 — N `Listing` (via `first_seen_run_id` / `last_seen_run_id`)
- `Listing` 1 — N `ListingSnapshot` (append-only)
- `RawListing` 1 — 0..1 `Listing` (via `listing.current_raw_listing_id`)
- `IngestionRun` 1 — N `ListingSnapshot` (the run that triggered the change)
- `VehicleGenerationCatalog` is standalone reference data for future vehicle
  generation classification and is not linked to listings in this phase.

---

## 1. MarketplaceSource

Reference / seeded data. Identifies an external data provider independently
of marketplace-internal field names (FR-010). Seeded by a migration
(idempotent `INSERT ... ON CONFLICT (code) DO NOTHING`); the
`PersistenceService` resolves it by `code` at run start and does **not**
create it per run. Initial seed row:

| code | name | country | base_url |
|---|---|---|---|
| `dubizzle_uae` | `Dubizzle UAE` | `UAE` | `https://dubizzle.com` |

| Column | Type | Constraints | Notes |
|---|---|---|---|
| `id` | `BIGSERIAL` | PK | Surrogate key. |
| `code` | `TEXT` | UNIQUE NOT NULL | Stable marketplace code, e.g. `dubizzle`. |
| `name` | `TEXT` | NOT NULL | Human-readable name. |
| `country` | `TEXT` | NOT NULL | Country code, e.g. `AE`. |
| `base_url` | `TEXT` | NOT NULL | Marketplace base URL. |
| `created_at` | `TIMESTAMPTZ` | NOT NULL DEFAULT now() | |
| `updated_at` | `TIMESTAMPTZ` | NOT NULL DEFAULT now() | Updated on upsert. |

**Indexes**: unique on `code`.
**Validation**: `code` non-empty slug; `name`, `country`, `base_url` non-empty.
**State transitions**: none (reference data; upsert by `code`).

---

## 1a. VehicleGenerationCatalog

Reference / catalog data for future market segmentation by market, canonical
make/model keys, generation, and body code. It is owned by the Python migration stream and does
not change ingestion, replay, backend APIs, frontend behavior, or current
listing tables. Schema is migrated separately from CSV reference imports.

| Column | Type | Constraints | Notes |
|---|---|---|---|
| `id` | `BIGSERIAL` | PK | Surrogate key. |
| `slug` | `TEXT` | UNIQUE NOT NULL | Stable catalog identifier including market, e.g. `global-mercedes-benz-c-class-w205`. |
| `market` | `TEXT` | NOT NULL DEFAULT `'global'` | Market release context such as `global`, `uae`, or `egypt`. |
| `make_key` | `TEXT` | NOT NULL | Canonical make key from `src.normalization.catalog_normalizer`, e.g. `mercedesbenz`. |
| `model_key` | `TEXT` | NOT NULL | Canonical model key from `src.normalization.catalog_normalizer`, e.g. `cclass`. |
| `generation` | `TEXT` | NOT NULL | Generation label or code. |
| `body_code` | `TEXT` | NULL | Manufacturer/internal body code when known. |
| `marketing_name` | `TEXT` | NULL | Public generation name when known. |
| `start_year` | `INTEGER` | NOT NULL | First model year in generation range. |
| `end_year` | `INTEGER` | NULL | Final model year; null for current/open-ended ranges. |
| `facelift_start_year` | `INTEGER` | NULL | First facelift model year when applicable. |
| `facelift_end_year` | `INTEGER` | NULL | Final facelift model year when applicable. |
| `aliases` | `JSONB` | NOT NULL DEFAULT `'[]'` | Alternate labels/body codes/search aliases. |
| `confidence` | `TEXT` | NOT NULL DEFAULT `'manual'` | Provenance/confidence label for catalog curation. |
| `created_at` | `TIMESTAMPTZ` | NOT NULL DEFAULT now() | |
| `updated_at` | `TIMESTAMPTZ` | NOT NULL DEFAULT now() | |

**Constraints**: unique on `slug`; unique on
`(market, make_key, model_key, generation, body_code)`.
**Indexes**: index on `(market, make_key, model_key)`; index on
`(market, make_key, model_key, start_year, end_year)`.
**Validation**: catalog rows should use non-empty `slug`, `make_key`, `model_key`,
`generation`; `aliases` is a JSONB array. Listing classification and catalog
backfills are explicitly deferred.
**CSV imports**: reference files live under `scrapper/vehicle_catalog/` with
one `.csv` per brand, such as `mercedes-benz.csv`, `bmw.csv`, and `toyota.csv`.
Import with `python -m src.db.seed_vehicle_catalog --path vehicle_catalog` from
the scraper project. CSV columns are `slug`, `market`, `make_key`, `model_key`,
`generation`, `body_code`, `marketing_name`, `start_year`, `end_year`,
`facelift_start_year`, `facelift_end_year`, `aliases`, and `confidence`.
The importer parses `aliases` as a JSON array, treats empty optional year
fields as null, and upserts rows by `slug`.

---

## 2. IngestionRun

A single ingestion execution scoped by marketplace, condition, and make.
The primary replay and lineage unit for Feature 002 (FR-011, FR-011a). Carries
a unique readable run `name` used by replay (`--run <run-name-or-id>`).

| Column | Type | Constraints | Notes |
|---|---|---|---|
| `id` | `BIGSERIAL` | PK | Surrogate key. |
| `name` | `TEXT` | UNIQUE NOT NULL | `run_<marketplace>_<condition>_<make-or-scope>_<yyyyMMdd>_<HHmmss>` UTC + disambiguator (R-5, FR-011a). |
| `marketplace_source_id` | `BIGINT` | FK → `marketplace_source.id` NOT NULL | |
| `marketplace` | `TEXT` | NOT NULL | Marketplace code (denormalized for query convenience). |
| `condition` | `TEXT` | NOT NULL | e.g. `used`, `new`. |
| `make` | `TEXT` | NOT NULL | Make slug. |
| `status` | `TEXT` | NOT NULL | `RUNNING` / `COMPLETED` / `FAILED` / `PARTIAL_FAILED` (Feature 001 `RunState`). |
| `started_at` | `TIMESTAMPTZ` | NOT NULL | Run start (UTC). |
| `completed_at` | `TIMESTAMPTZ` | NULL | Set on terminal state. |
| `pages_scraped` | `INTEGER` | NOT NULL DEFAULT 0 | |
| `listings_extracted` | `INTEGER` | NOT NULL DEFAULT 0 | |
| `listings_skipped` | `INTEGER` | NOT NULL DEFAULT 0 | |
| `failures_count` | `INTEGER` | NOT NULL DEFAULT 0 | |
| `duration_ms` | `INTEGER` | NULL | Run duration in ms. |
| `config_snapshot` | `JSONB` | NOT NULL | Non-secret config snapshot. |
| `report_json` | `JSONB` | NULL | Full run report (FR-052). |
| `created_at` | `TIMESTAMPTZ` | NOT NULL DEFAULT now() | |

**Indexes**: unique on `name`; index on `marketplace_source_id`; index on
`(marketplace, condition, make)` for replay lookup by scope.
**Cascade**: `RESTRICT` on `marketplace_source` delete (history preserved —
Constitution VII).
**Validation**: `name` matches the run-name format; `status` ∈ allowed set;
`started_at ≤ completed_at` when `completed_at` is set.
**State transitions**: `RUNNING` → `COMPLETED` | `FAILED` | `PARTIAL_FAILED`
(terminal). An interrupted run retains `RUNNING` (edge case: interrupted run).

---

## 3. RawListing

The immutable, verbatim original marketplace listing preserved exactly as
received (FR-012, Constitution "Raw JSON Preservation"). Ground truth for
replay, re-derivation, and debugging.

| Column | Type | Constraints | Notes |
|---|---|---|---|
| `id` | `BIGSERIAL` | PK | Surrogate key. |
| `marketplace_source_id` | `BIGINT` | FK → `marketplace_source.id` NOT NULL | |
| `ingestion_run_id` | `BIGINT` | FK → `ingestion_run.id` NOT NULL | The run this raw listing belongs to (FR-015). |
| `source` | `TEXT` | NOT NULL | Marketplace code. |
| `uuid` | `TEXT` | NOT NULL | Marketplace-independent listing id (Constitution "UUID-Based Deduplication"). |
| `raw_payload` | `JSONB` | NOT NULL | Verbatim marketplace payload. |
| `raw_hash` | `TEXT` | NOT NULL | Content hash of the raw payload (R-4). |
| `adapter_version` | `TEXT` | NOT NULL | Adapter version that produced it (FR-012). |
| `marketplace_schema_version` | `TEXT` | NULL | Marketplace payload/schema version when available (FR-012). |
| `marketplace_payload_version` | `TEXT` | NULL | Fallback when a schema version is not available. |
| `extracted_at` | `TIMESTAMPTZ` | NOT NULL | Extraction timestamp. |
| `created_at` | `TIMESTAMPTZ` | NOT NULL DEFAULT now() | |

**Indexes**: index on `ingestion_run_id` (replay selects by it — FR-032);
index on `(source, uuid)`; index on `raw_hash`.
**Cascade**: `RESTRICT` on `ingestion_run` delete (history preserved). On
`marketplace_source` delete: `RESTRICT`.
**Validation**: `raw_payload` is a non-null JSONB object; `uuid` non-empty;
`raw_hash` non-empty. `RawListing` is **immutable**: no update path exists
in the adapter (Constitution "Raw JSON Preservation", FR-031 replay rules).
**State transitions**: none (append-only immutable).

---

## 4. Listing (Canonical)

The platform's marketplace-independent listing representation, deduplicated by
`(source, uuid)` (FR-013, FR-020). The current row always reflects the
newest data (newest-wins — FR-021). Carries run lineage and `canonicalHash`
for meaningful-change detection.

| Column | Type | Constraints | Notes |
|---|---|---|---|
| `id` | `BIGSERIAL` | PK | Surrogate key. |
| `marketplace_source_id` | `BIGINT` | FK → `marketplace_source.id` NOT NULL | |
| `source` | `TEXT` | NOT NULL | Marketplace code. |
| `uuid` | `TEXT` | NOT NULL | Marketplace-independent listing id. |
| `title` | `TEXT` | NULL | |
| `make` | `TEXT` | NULL | Canonicalized. |
| `model` | `TEXT` | NULL | Canonicalized. |
| `trim` | `TEXT` | NULL | |
| `year` | `INTEGER` | NULL | |
| `price` | `NUMERIC(14, 2)` | NULL | AED. |
| `mileage` | `INTEGER` | NULL | km. |
| `condition` | `TEXT` | NULL | e.g. `used`, `new`. |
| `location` | `TEXT` | NULL | |
| `seller_type` | `TEXT` | NULL | |
| `url` | `TEXT` | NULL | |
| `status` | `TEXT` | NOT NULL DEFAULT 'ACTIVE' | `ACTIVE` for observed listings. Feature 002 does **not** infer `SOLD`/disappearance (NFR-011). |
| `first_seen_at` | `TIMESTAMPTZ` | NOT NULL | First observation timestamp. |
| `last_seen_at` | `TIMESTAMPTZ` | NOT NULL | Last observation timestamp. |
| `first_seen_run_id` | `BIGINT` | FK → `ingestion_run.id` NOT NULL | Run lineage (FR-013). |
| `last_seen_run_id` | `BIGINT` | FK → `ingestion_run.id` NOT NULL | Run lineage (FR-013). |
| `current_raw_listing_id` | `BIGINT` | FK → `raw_listing.id` NULL | The raw listing the current row was derived from. |
| `canonical_hash` | `TEXT` | NOT NULL | Canonical hash of the current row (R-4, FR-023). Meaningful-change baseline. |
| `normalization_version` | `TEXT` | NOT NULL | Normalization logic that produced the current row (FR-013, SC-011). Replay under a newer version MAY update it. |
| `created_at` | `TIMESTAMPTZ` | NOT NULL DEFAULT now() | |
| `updated_at` | `TIMESTAMPTZ` | NOT NULL DEFAULT now() | Updated on newest-wins / lineage refresh. |

**Constraints**: **UNIQUE `(source, uuid)`** — the deduplication key
(FR-041, SC-005, FR-020).
**Indexes**: unique on `(source, uuid)`; index on `canonical_hash`; index on
`last_seen_run_id`; index on `marketplace_source_id`.
**Cascade**: `RESTRICT` on `marketplace_source` delete. `RESTRICT` on
`first_seen_run_id`/`last_seen_run_id` delete (history preserved). On
`current_raw_listing_id` delete: `SET NULL` (a listing may outlive a raw
deletion, though deletion is not performed in this feature).
**Validation**: `(source, uuid)` non-empty; `status` ∈ allowed set;
`first_seen_at ≤ last_seen_at`; `canonical_hash` non-empty;
`normalization_version` non-empty.
**State transitions** (per re-observation):
- **No prior row** → insert with `canonical_hash` = initial hash,
  `first_seen_*` = `last_seen_*` = current run, `status = ACTIVE`. No
  snapshot (FR-025).
- **Prior row, new hash == `canonical_hash`** → refresh `last_seen_at` and
  `last_seen_run_id` only. No snapshot. `canonical_hash` unchanged (FR-024).
- **Prior row, new hash != `canonical_hash`** → create `ListingSnapshot`
  with prior state; update row to newest data; update `canonical_hash`;
  refresh `last_seen_at`/`last_seen_run_id` (FR-022, FR-026, US2-AC2).

---

## 5. ListingSnapshot

A point-in-time capture of a Listing's **prior** canonical state at the
moment a meaningful change was detected (FR-022). Append-only history
(Constitution VII). Stores a single `canonical_payload` (no duplicated
per-field columns — SC-005).

| Column | Type | Constraints | Notes |
|---|---|---|---|
| `id` | `BIGSERIAL` | PK | Surrogate key. |
| `listing_id` | `BIGINT` | FK → `listing.id` NOT NULL | The listing this snapshot belongs to. |
| `ingestion_run_id` | `BIGINT` | FK → `ingestion_run.id` NOT NULL | The run that triggered the change. |
| `raw_listing_id` | `BIGINT` | FK → `raw_listing.id` NULL | The prior raw listing reference. |
| `snapshot_hash` | `TEXT` | NOT NULL | Hash of the prior canonical payload (R-4). |
| `canonical_payload` | `JSONB` | NOT NULL | The prior canonical listing state (single JSONB — FR-022, SC-005). |
| `changed_fields` | `JSONB` | NOT NULL DEFAULT '[]' | List of changed field names. |
| `captured_at` | `TIMESTAMPTZ` | NOT NULL | When the change was detected. |
| `created_at` | `TIMESTAMPTZ` | NOT NULL DEFAULT now() | |

**Indexes**: index on `listing_id`; index on `(listing_id, captured_at)` for
history queries; index on `ingestion_run_id`.
**Cascade**: `CASCADE` on `listing` delete (snapshots are owned by the
listing; listing deletion is not performed in this feature — Constitution VII).
`RESTRICT` on `ingestion_run` delete.
**Validation**: `canonical_payload` is a non-null JSONB object; `changed_fields`
is a JSONB array; `snapshot_hash` non-empty.
**State transitions**: none (append-only; no update or delete path —
Constitution "Historical Snapshots").

---

## canonicalHash: participating fields (implementation detail)

Per R-4, the canonical hash is computed in pure Python over the canonical
`Listing`'s meaningful fields in stable canonical form
(`json.dumps(..., sort_keys=True, separators=(",", ":"))` → `sha256` hex).
**Volatile metadata is excluded** so re-observation of an otherwise-unchanged
listing does not create a snapshot.

Participating fields (may be refined during implementation; refinements
recorded here):
- Included: `uuid`, `marketplace`, `make`, `model`, `condition`, `price`,
  `currency`, `year`, `kilometers`, `fuel_type`, `transmission`,
  `regional_spec`, `body_type`, `seller_type`, `location`, `photos_count`,
  `source_url`, `normalization_version`.
- Excluded (volatile): `fetched_at`, `first_seen_at`, `last_seen_at`,
  `first_seen_run_id`, `last_seen_run_id`, `current_raw_listing_id`,
  `dataset_version` (Feature 001 concept, not persisted in Feature 002),
  row timestamps.

Order-independence: dict keys are sorted; list-valued fields of equivalent
values are sorted before hashing where applicable (FR-023).

---

## Count reconciliation (NFR-004, SC-001)

For a run persisted via the PostgreSQL backend:
- `IngestionRun.listings_extracted` == count of `Listing` rows with
  `last_seen_run_id` = this run's id.
- `RawListing` count for `ingestion_run_id` == number of extracted listings.
- `ListingSnapshot` count for `ingestion_run_id` == number of listings whose
  canonical hash changed in this run.
- `listings_skipped` + `failures_count` reconcile with the run report's
  skipped/failure counters.

These invariants are enforced by integration tests (Phase 8).

---

## Out of scope (not modeled)

- `DatasetVersion`, `DatasetVersionRun`, `datasetKey` (FR-014, NFR-012).
- `ReplayRun` (FR-036).
- Vehicle generation classification/linkage from listings to
  `vehicle_generation_catalog`.
- Listing disappearance / lifecycle status (`SOLD`, `REMOVED_OR_EXPIRED`,
  `NOT_SEEN_IN_LATEST_RUN`) (NFR-011).
- Search, analytics, AI, ML, auth, admin UI, public API (NFR-012).

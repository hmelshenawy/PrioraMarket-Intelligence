# Data Model: Data Ingestion Foundation

**Feature**: 001-data-ingestion-foundation
**Date**: 2026-07-04

This document defines the domain entities for the ingestion pipeline per
the spec's Key Entities, Functional Requirements, Domain Pipeline Model,
Pipeline State Machine, and Dataset Versioning sections. It is a logical
model — field types are indicative, not implementation code. Storage in
this feature is CSV via a `StorageAdapter` interface; no database is
introduced.

## Entity Overview

```text
MarketplaceSource 1──* RawListing
RawListing 1──1 Listing (normalized/canonicalized)   [derived]
IngestionRun 1──* RawListing
IngestionRun 1──* Listing
IngestionRun 1──1 RunReport
IngestionRun 1──1 DatasetVersion
NormalizationVersion 1──* Listing                    [rules that produced it]
Listing 1──1 ValidationResult
```

## RawListing

The original marketplace listing exactly as received. Immutable. Ground
truth for all downstream derivation.

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| `marketplace` | enum/string | yes | e.g., `dubizzle` |
| `marketplace_listing_id` | string | yes | native id from the marketplace |
| `uuid` | string | yes | marketplace-native uuid; dedup key |
| `raw_payload` | object (verbatim) | yes | preserved exactly, no transformation |
| `extracted_fields` | object | yes | marketplace-specific fields pulled out for normalization |
| `fetched_at` | timestamp | yes | when the adapter received it |
| `scrape_run_id` | string | yes | id of the ingestion run that fetched it |
| `marketplace` scope (`condition`, `make_slug`) | string | yes | scope used to fetch |

**Rules**:
- Immutable after creation (FR-020/021, Key Entities).
- `raw_payload` MUST be preserved verbatim — no truncation, enrichment, or
  transformation.
- Replay MUST NEVER modify a RawListing (Replay Rules).

## Listing (Normalized / Canonicalized)

The platform's internal, marketplace-independent representation. Derived
from a RawListing via the normalizer, then canonicalized. Never received
directly from a marketplace.

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| `uuid` | string | yes | carried from RawListing; dedup key |
| `marketplace` | enum/string | yes | source marketplace |
| `marketplace_listing_id` | string | yes | native id |
| `make` | string (canonical) | yes | canonicalized |
| `model` | string (canonical) | yes | canonicalized |
| `condition` | string | yes | used/new |
| `price` | numeric | yes | numeric value validated |
| `currency` | string | yes | e.g., `AED` |
| `year` | integer | no | numeric if present |
| `kilometers` | numeric | no | numeric if present |
| `fuel_type` | string (canonical) | no | canonicalized |
| `transmission` | string (canonical) | no | canonicalized |
| `regional_spec` | string (canonical) | no | canonicalized |
| `body_type` | string (canonical) | no | canonicalized |
| `source_url` | string | yes | listing URL |
| `seller_type` | string | no | |
| `location` | string | no | neighborhood/Places |
| `photos_count` | integer | no | |
| `fetched_at` | timestamp | yes | from RawListing |
| `normalization_version` | string | yes | ruleset that produced this Listing |
| `dataset_version` | string | yes | dataset it belongs to |
| `lineage` | object | yes | references for traceability (see below) |

**Lineage (FR-023)** — every Listing MUST carry:
- `marketplace`
- `raw_listing_ref` (reference to the RawListing)
- `ingestion_run_id`
- `dataset_version`
- `normalization_version`

**Rules**:
- Canonical fields (make, model, fuel_type, transmission, regional_spec,
  body_type) MUST hold canonical values (FR-043–045).
- A Listing is only persisted after passing validation + dedup.

## ValidationResult

Outcome of validating a canonicalized Listing.

| Field | Type | Notes |
|-------|------|-------|
| `listing_uuid` | string | subject |
| `accepted` | boolean | |
| `reason` | string | rejection reason if not accepted |
| `missing_fields` | list[string] | if applicable |
| `duplicate` | boolean | true if suppressed as duplicate |
| `duplicate_of` | string | uuid that won, when `duplicate` |

## IngestionRun

A single execution scoped by marketplace, condition, make.

| Field | Type | Notes |
|-------|------|-------|
| `run_id` | string | unique |
| `marketplace` | string | |
| `condition` | string | |
| `make` | string | (or "all makes" for a full sweep) |
| `normalization_version` | string | active version |
| `dataset_version` | string | assigned on success |
| `state` | enum | state machine state |
| `started_at` / `ended_at` | timestamp | |
| `config_snapshot` | object | ingestion configuration used |

## RunReport

Structured outcome of a run (basic + extended + optional metrics).

| Field | Type | Source |
|-------|------|--------|
| `run_id` | string | IngestionRun |
| `marketplace` | string | scope |
| `condition` | string | scope |
| `make` | string | scope |
| `state` | enum | terminal state |
| `dataset_version` | string | |
| `normalization_version` | string | |
| **Basic metrics** | | FR-061 |
| `pages_processed` | integer | |
| `listings_extracted` | integer | |
| `listings_skipped` | integer | |
| `execution_duration` | duration | |
| `failures` | integer | |
| **Extended metrics** | | FR-063 |
| `retry_count` | integer | |
| `duplicate_count` | integer | |
| `validation_failures` | integer | |
| `pages_per_second` | float | |
| `listings_per_second` | float | |
| `fetch_duration` | duration | |
| `processing_duration` | duration | |
| `storage_duration` | duration | |
| **Optional operational metrics** | | FR-064 |
| `start_time` | timestamp | |
| `end_time` | timestamp | |
| `total_duration` | duration | |
| `peak_memory` | integer | |
| `peak_cpu` | float | |

## DatasetVersion

Identifies the data produced by a successful run.

| Field | Type | Notes |
|-------|------|-------|
| `identifier` | string | e.g., `dataset_2026_07_04_001` |
| `scrape_run_id` | string | |
| `marketplace` | string | |
| `execution_timestamp` | timestamp | |
| `ingestion_config` | object | config snapshot |
| `normalization_version` | string | active version |

**Concept only**: persistence/management deferred to a future feature.

## NormalizationVersion

Identifies the rules that produced a Listing.

| Field | Type | Notes |
|-------|------|-------|
| `identifier` | string | e.g., `norm-1` |
| `normalizer_ruleset` | string/ref | object-mapping rules |
| `canonical_mapping_version` | string/ref | canonical-value tables |
| `created_at` | timestamp | |

**Rule**: Replay MUST always select an explicit NormalizationVersion.

## MarketplaceSource

An external data provider accessed through an adapter.

| Field | Type | Notes |
|-------|------|-------|
| `name` | string | e.g., `dubizzle` |
| `adapter` | string | adapter identifier |

## Validation Rules (FR-030–033)

- `uuid` MUST be present (reject "missing uuid").
- Required fields MUST be present (reject with `missing_fields`).
- Numeric fields (`price`, `year`, `kilometers`) MUST be numeric when
  present (reject "non-numeric <field>").
- Basic data consistency MUST hold (reject "inconsistent <detail>").
- Duplicates within a run MUST be deduplicated by `uuid` (newest
  occurrence wins; `duplicate_count` incremented).

## State Transitions (Pipeline State Machine)

| From | To | Trigger |
|------|----|---------|
| CREATED | RUNNING | execution starts |
| RUNNING | FETCHING / NORMALIZING / CANONICALIZING / VALIDATING / STORING | stage progress (may interleave per page) |
| FETCHING / NORMALIZING / CANONICALIZING / VALIDATING / STORING | COMPLETED | all pages processed, no unrecoverable failure |
| FETCHING / NORMALIZING / CANONICALIZING / VALIDATING / STORING | PARTIAL_FAILED | run completes with recorded page/record failures |
| Any | FAILED | unrecoverable error prevents usable output |

- A run MUST NOT transition back to CREATED.
- Terminal states (COMPLETED, FAILED, PARTIAL_FAILED) are absorbing.

## Storage Mapping (CSV, interim)

- RawListings persisted to a CSV/raw artifact (raw_payload serialized as
  JSON text within the CSV row, or a sidecar JSONL — decided at
  implementation time within the storage layer).
- Canonicalized Listings persisted to a listings CSV.
- RunReport persisted to a report artifact (JSON or CSV).
- All access goes through `StorageAdapter`; CSV specifics do not leak into
  ingestion logic.
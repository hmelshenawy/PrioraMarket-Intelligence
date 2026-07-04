# Run Report & Dataset Version Schema: Data Ingestion Foundation

**Feature**: 001-data-ingestion-foundation
**Date**: 2026-07-04

The RunReport is the structured, persistable outcome of every ingestion
run (FR-061, FR-063, FR-064) and the carrier of dataset-version and
lineage metadata. This contract defines its shape. It is a data contract,
not implementation code.

## RunReport

```text
RunReport
├── run_id            : string          (unique run identifier)
├── state             : enum            (COMPLETED | FAILED | PARTIAL_FAILED)
├── scope
│   ├── marketplace   : string
│   ├── condition     : string
│   └── make          : string
├── dataset_version       : string      (assigned on success)
├── normalization_version : string      (active ruleset)
│
├── basic_metrics                     (FR-061, required)
│   ├── pages_processed       : integer
│   ├── listings_extracted    : integer
│   ├── listings_skipped      : integer
│   ├── execution_duration    : duration
│   └── failures              : integer
│
├── extended_metrics                  (FR-063, required)
│   ├── retry_count           : integer
│   ├── duplicate_count       : integer
│   ├── validation_failures   : integer
│   ├── pages_per_second      : float
│   ├── listings_per_second   : float
│   ├── fetch_duration        : duration
│   ├── processing_duration   : duration
│   └── storage_duration      : duration
│
└── operational_metrics (optional)    (FR-064, MAY be omitted)
    ├── start_time     : timestamp
    ├── end_time       : timestamp
    ├── total_duration : duration
    ├── peak_memory    : integer
    └── peak_cpu       : float
```

**Rules**:
- A report is emitted for every run, regardless of terminal state.
- On `FAILED`, basic metrics reflect progress up to the failure; extended
  metrics are populated where measurable.
- Operational metrics are optional and not required for run correctness.
- No secrets appear anywhere in the report (FR-062).

## DatasetVersion

```text
DatasetVersion
├── identifier            : string   (e.g., dataset_2026_07_04_001)
├── scrape_run_id         : string
├── marketplace           : string
├── execution_timestamp   : timestamp
├── ingestion_config      : object   (config snapshot)
└── normalization_version : string
```

**Rules**:
- Assigned to successful runs (state COMPLETED or PARTIAL_FAILED with
  usable output).
- Future analytics/ML MUST reference a specific DatasetVersion for
  reproducibility.
- This feature establishes the concept and the identifier only;
  persistence/management (storage, indexing, retention, lineage
  registries) is deferred to a future feature.

## Per-Listing Lineage (FR-023)

Every persisted canonicalized Listing MUST carry:

```text
Lineage
├── marketplace           : string
├── raw_listing_ref       : string   (reference to the RawListing)
├── ingestion_run_id      : string
├── dataset_version       : string
└── normalization_version : string
```

**Rule**: the platform MUST be able to reconstruct how a normalized
Listing was produced from these references + the immutable RawListing.

## Replay Output

Replay (US5) regenerates derived artifacts from stored RawListings under
an explicitly selected `NormalizationVersion`:

```text
ReplayOutput
├── source_dataset_version   : string   (input RawListings' dataset)
├── applied_normalization_version : string  (explicitly selected)
├── regenerated_listings     : List[Listing]
├── regenerated_validation   : List[ValidationResult]
└── produced_dataset_version : string   (new dataset version for output)
```

**Rules**:
- Replay MUST NEVER modify RawListings.
- Replay MUST NOT access the marketplace.
- The same RawListings + same NormalizationVersion MUST yield identical
  regenerated_listings (deterministic).
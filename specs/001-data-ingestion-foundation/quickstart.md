# Quickstart: Data Ingestion Foundation

**Feature**: 001-data-ingestion-foundation
**Date**: 2026-07-04

This quickstart describes how an operator sets up and runs the ingestion
pipeline and the replay capability for Feature 001. It is a usage guide,
not implementation code. All behavior is driven by environment
configuration; no hardcoded secrets or paths are used.

## Prerequisites

- Python 3.11 installed.
- Network access to the Dubizzle search endpoint (for ingestion only;
  replay does not require it).
- A writable local output directory (path supplied via configuration).

## 1. Configure the environment

Copy the provided `.env.example` to `.env` and fill in the required
values:

- Marketplace endpoint / index name.
- Credentials (if required by the marketplace).
- Output directory path for RawListings, Listings, and RunReports.
- Retry policy (attempts, backoff).
- Rate limit (delay between requests).
- Request timeout.

If any required value is missing, the pipeline fails fast with a named
message (FR-003).

## 2. Run an ingestion

Run the pipeline CLI entry point scoped by marketplace, condition, and
make (or a full sweep):

```text
run --marketplace dubizzle --condition used --make <make>
```

Expected outcome:
- The pipeline fetches pages via the Dubizzle adapter, with retry/backoff
  and rate limiting.
- Each hit is preserved as an immutable RawListing (raw payload verbatim).
- RawListings are normalized → canonicalized → validated/deduplicated.
- Valid canonicalized Listings and RawListings are persisted via the
  storage adapter (CSV in this feature).
- A RunReport is emitted containing basic, extended, and (optionally)
  operational metrics, plus the assigned DatasetVersion and active
  NormalizationVersion.

Verify:
- Listing count matches the current prototype scraper for the same scope
  (SC-001, parity).
- Each persisted Listing has an accompanying raw payload (SC-002).
- The RunReport contains all required metrics (SC-006).

## 3. Observe resilience

If a page or record fails (transient network error, malformed payload,
invalid record), the run continues:
- The failed page/record is logged and recorded in the RunReport.
- The run ends in `PARTIAL_FAILED` with usable output, or `COMPLETED` if
  no failures occurred (SC-004, SC-005).

## 4. Replay existing raw data

Rebuild normalized Listings from previously stored RawListings without
contacting the marketplace, using an explicitly selected Normalization
Version:

```text
replay --dataset <source-dataset-version> --normalization-version <version>
```

Expected outcome:
- RawListings are read from src.storage (no marketplace access).
- Listings/ValidationResults are regenerated under the selected
  NormalizationVersion.
- RawListings are never modified.
- Running replay twice with the same inputs yields identical Listings
  (deterministic).

Use replay to apply improved normalization/canonicalization rules to
historical raw data without re-scraping.

## 5. Run tests

- Unit tests: per-module (config, models, extractor, normalizer,
  canonicalizer, validator, storage, run report, replayer).
- Integration tests: stage chain over recorded fixtures.
- Contract tests: `StorageAdapter` interface (CSV + substitute adapter).
- Acceptance tests: US1–US5 and SC-001–SC-009, including parity
  regression against the recorded prototype fixture corpus.

Tests use recorded fixtures; no live marketplace calls are made in the
automated test suite.

## Definition of Done (operator-facing)

- A scoped run produces parity listings + raw payloads + a complete
  RunReport.
- Invalid records are skipped and logged, never fatal.
- Configuration is fully env-driven; no secrets/paths in source.
- Storage is substitutable without ingestion changes.
- Replay is offline and deterministic with an explicit Normalization
  Version.
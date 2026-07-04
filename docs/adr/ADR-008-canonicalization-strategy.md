# ADR-008: Canonicalization as a separate pipeline stage

**Status:** Accepted
**Date:** 2026-07-04
**Feature:** 001 — Data Ingestion Foundation

## Context

The Constitution mandates "separation of responsibilities" and a Clean
Layered Architecture. The prototype scraper flattened marketplace fields
directly into CSV columns with no distinction between (a) reading a
value off the marketplace payload and (b) standardizing it to a
platform-wide business value. Mixing these two concerns makes future
marketplaces and analytics inconsistent: "GCC Specs", "Gulf Specs", and
"gcc" would all persist as distinct values even though they denote the
same regional specification.

Two transformations are needed:

1. **Normalization** — object mapping: turning a marketplace-specific
   RawListing into a marketplace-independent Listing (types, currency,
   field renaming). Deterministic and versioned.
2. **Canonicalization** — business-value standardization: mapping
   free-text business values (fuel, transmission, regional spec, body
   type, make, model) to a canonical enum.

## Decision

Implement normalization and canonicalization as **two separate stages**
with separate, independently-versioned rulesets:

- `src/ingestion/normalizer.py` — `Normalizer` + `NORMALIZER_RULESET`.
- `src/ingestion/canonicalizer.py` — `Canonicalizer` +
  `CANONICAL_MAPPING_VERSION` and versioned mapping tables.

The combined version (normalization version + canonical mapping version)
is exposed as the pipeline's `Normalization Version` and stamped on every
Listing, so replay can deterministically reproduce output for any past
ruleset.

Canonicalization is gated by the `EnableCanonicalization` feature flag
for operational control, but business logic never depends on the flag.

## Alternatives considered

- **Single combined "normalize" stage.** Rejected: couples object mapping
  to business-value rules, so any change to a fuel alias would force a
  full normalization-version bump and re-replay of all data.
- **Canonicalize at storage time.** Rejected: violates separation of
  concerns and makes the storage adapter aware of business semantics.
- **No canonicalization in Feature 001.** Rejected: analytics quality
  (Constitution X) depends on consistent business values from the start;
  retrofitting later would require re-canonicalizing historical data.

## Consequences

- Two version stamps must travel together for full reproducibility.
- Adding a marketplace that supplies already-canonical values is trivial:
  its canonicalizer can be a passthrough.
- Canonical mapping tables are a maintained asset; changes require a
  `CANONICAL_MAPPING_VERSION` bump.
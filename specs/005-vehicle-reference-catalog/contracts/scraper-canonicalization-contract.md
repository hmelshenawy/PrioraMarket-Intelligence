# Contract: Scraper Canonicalization

## Owner

Python scraper / Data Ingestion bounded context.

## Inputs

- Extracted marketplace categorical values.
- Market context.
- Current or explicitly selected canonicalization rule version.
- Vehicle Reference Catalog records and aliases from the synchronized database copy.

## Outputs

- Canonical keys for supported categorical fields.
- Canonicalization or normalization rule version associated with the processed listing.
- Normalization statistics for known, unknown, alias-resolved, and catalog-resolved values.

## Rules

- Canonicalization is deterministic.
- Formatting differences are removed while semantic letters and numbers are preserved.
- Catalog aliases are applied only from Vehicle Reference Catalog records.
- Unknown values are canonicalized deterministically, reported, and allowed through ingestion.
- No fuzzy matching, AI matching, guessing, OCR, VIN decoding, valuation, or generation classification is allowed.

## Compatibility

Live ingestion, replay, and backfill must use the same canonicalization behavior for a selected rule version.

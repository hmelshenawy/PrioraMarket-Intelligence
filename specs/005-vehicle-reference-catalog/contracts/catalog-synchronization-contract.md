# Contract: Vehicle Reference Catalog Synchronization

## Owner

Python scraper database tooling.

## Source

Curated CSV reference files are authoritative.

## Target

`vehicle_reference_catalog` in PostgreSQL is the synchronized operational copy.

## Required Catalog Content

- Market
- Make key and display value
- Model key and display value
- Generation
- Body code
- Start/end year
- Facelift start/end year
- Aliases owned by the catalog record
- Confidence
- Lightweight synchronization provenance

## Synchronization Behavior

- Validate CSV structure and row values before applying changes.
- Apply idempotent inserts/updates.
- Preserve canonical key immutability.
- Record when catalog records were last synchronized from CSV.
- Report inserted, updated, unchanged, rejected, and conflicting rows.
- Treat manual database edits as non-authoritative when they conflict with CSV.

## Out Of Scope

- Full catalog history/versioning.
- Separate alias database.
- Catalog management UI.

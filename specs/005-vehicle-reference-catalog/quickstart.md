# Quickstart: Canonical Data Model & Vehicle Reference Catalog

This quickstart describes the intended implementation and validation sequence. It does not provide implementation code.

## Prerequisites

- Final approved spec: `specs/005-vehicle-reference-catalog/spec.md`
- Plan artifacts in `specs/005-vehicle-reference-catalog/`
- Existing scraper environment with PostgreSQL migration capability
- Existing backend environment with Prisma generation/build capability
- Curated CSV reference files for the initial Vehicle Reference Catalog content

## Recommended Execution Sequence

1. Review `research.md`, `data-model.md`, and contracts before generating tasks.
2. Design scraper migrations for `vehicle_reference_catalog`, catalog provenance, listing canonical fields, and canonicalization version metadata.
3. Define canonicalization rule version naming and ensure live ingestion, replay, and backfill can use the same rule boundary.
4. Prepare CSV catalog files and validation rules before synchronization.
5. Apply migrations in a local PostgreSQL environment and confirm rollback is available.
6. Synchronize the Vehicle Reference Catalog from CSV and verify repeated synchronization is idempotent.
7. Validate live ingestion on representative records with known aliases and unknown values.
8. Validate replay with fixed raw listings and explicit canonicalization version.
9. Run a backfill dry-run/report before mutating existing listing values.
10. Run batched backfill and validate identifiers, raw payloads, and history are preserved.
11. Synchronize backend Prisma schema after scraper migrations are stable.
12. Verify backend build, repository compatibility, search/filter compatibility, and absence of backend normalization logic.
13. Confirm presentation consumers can receive catalog display values and are not expected to reconstruct names.

## Expected Commands

- Apply scraper migrations from `scrapper/` using the existing migration entry point after creating `scrapper/src/db/migrations/202607050001_vehicle_reference_catalog.sql`.
- Roll back scraper migrations from `scrapper/` using the existing migration rollback workflow and `scrapper/src/db/migrations/202607050001_vehicle_reference_catalog.rollback.sql`.
- Synchronize the Vehicle Reference Catalog from CSV with `python -m src.db.migrate sync-catalog --catalog-path data/reference/vehicle_reference_catalog.csv` from `scrapper/` after migrations are applied.
- Run a canonical backfill dry-run with `python -m src.ingestion.runner backfill --dry-run --batch-size 500 --canonicalization-version canonical-key-1` from `scrapper/`.
- Execute canonical backfill with `python -m src.ingestion.runner backfill --execute --batch-size 500 --resume-after-id <last_processed_id>` when the dry-run report is acceptable.
- Run focused Python tests from `scrapper/` with `pytest tests/unit tests/contract tests/integration -q`.
- Generate backend Prisma client from `backend/` with `npm run prisma:generate` after SQL migrations and `backend/prisma/schema.prisma` are synchronized.
- Build backend from `backend/` with `npm run build` after Prisma generation succeeds.
- Do not run frontend canonicalization logic; presentation consumers must receive catalog display values from backend/catalog data.

## Validation Checklist

- Migrations apply and roll back cleanly.
- `raw_listing` data remains unchanged.
- CSV synchronization is repeatable and reports inserted/updated/unchanged/rejected rows.
- Catalog records expose last synchronization traceability.
- Canonical examples match the spec exactly.
- Unknown values are reported and do not block ingestion.
- Normalized listings retain canonicalization rule version metadata.
- Replay is deterministic for fixed raw inputs and versions.
- Backfill is idempotent and non-destructive.
- Backend Prisma generation and build succeed.
- Backend does not duplicate normalization or marketplace-specific logic.
- Presentation consumers use catalog display values.

## Vehicle Reference Catalog CSV Ownership

CSV files under `scrapper/data/reference/` are the authoritative source for Vehicle Reference Catalog content. PostgreSQL is a synchronized operational copy. Manual database edits are non-authoritative; synchronization reports conflicts and refreshes provenance using the applied CSV source file and row hash.

## Canonical Backfill

Backfill reuses the shared canonicalization engine and updates only canonical fields on existing `listing` rows. It does not read from marketplaces and does not mutate `raw_listing`. Use `--dry-run` first, then `--execute`; reruns with the same inputs and canonicalization version are idempotent. If a run stops, resume with `--resume-after-id` using the last processed listing id from the progress output.

## Final Validation Evidence

- Python validation: `pytest tests/unit tests/contract tests/integration tests/regression -q` from `scrapper/` passed.
- Python lint for final regression/storage updates: `ruff check src/storage/csv_storage.py tests/regression/test_no_generation_classification.py` passed.
- Backend Prisma generation: `npm run prisma:generate` from `backend/` passed.
- Backend build: `npm run build` from `backend/` passed.
- Backend compatibility/regression tests: `npm test -- --runTestsByPath test/integration/vehicle-reference-catalog.prisma.spec.ts test/integration/listing-canonical-read.compat.spec.ts test/unit/no-marketplace-normalization.spec.ts` passed.
- Frontend typecheck: `npm run typecheck` from `frontend/` passed.

## Raw Payload Leakage Review

`scrapper/src/reporting/normalization_statistics.py` stores field-level raw categorical values and canonical keys only. It does not accept or log full `raw_payload` objects, marketplace HTML, credentials, or raw listing JSON. Backfill reporting records counts, failed listing ids, progress markers, and normalization statistics; it does not serialize raw payloads.

## Completion Criteria Evidence

- Vehicle Reference Catalog CSV synchronization is idempotent and reports inserted, updated, unchanged, rejected, and conflict counts.
- Canonicalization uses deterministic keys and preserves semantic letters/numbers.
- Backfill is dry-run capable, resumable, idempotent for unchanged inputs, and updates only listing canonical fields.
- Backend reads persisted canonical values and schema metadata without marketplace normalization dictionaries.
- Presentation contract exposes optional catalog display values and does not require client-side reconstruction.
- Scoped-out generation classification regression coverage is present in `scrapper/tests/regression/test_no_generation_classification.py`.

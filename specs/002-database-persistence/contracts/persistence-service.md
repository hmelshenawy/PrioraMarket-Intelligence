# Contract: PersistenceService

**Feature**: 002 — Database Persistence Foundation
**Spec refs**: FR-001, FR-005, FR-020..026, FR-030, FR-054..056, FR-060, FR-061, NFR-003, NFR-009, NFR-010

The `PersistenceService` is the business-rule layer between the Feature 001
ingestion pipeline and the `StorageAdapter` interface. It owns **all**
business persistence rules and **no** backend logic. It imports no database
client, ORM, query builder, or schema-generated module (NFR-003, SC-007).

## Public surface (domain operations)

The service operates on marketplace-agnostic domain objects (the Feature 001
`RawListing`, `Listing`, `RunReport`, `Scope`, plus a `RunName`). It depends
only on the `StorageAdapter` interface.

```python
class PersistenceService:
    def __init__(self, storage: StorageAdapter, ...): ...

    # Run lifecycle
    def begin_run(self, scope: Scope, config_snapshot: dict, run_started_at: datetime) -> RunContext: ...
    def finalize_run(self, ctx: RunContext, report: RunReport) -> None: ...

    # Per-listing atomic persistence (FR-054/055)
    def persist_listing(self, ctx: RunContext, raw: RawListing, listing: Listing) -> PersistOutcome: ...

    # Replay resolution (FR-030)
    def resolve_run(self, run_name_or_id: str) -> Optional[RunContext]: ...
    def load_raw_for_run(self, run_name_or_id: str) -> Iterable[RawListing]: ...
```

`RunContext` carries the resolved `IngestionRun` id, the unique run `name`,
and the `MarketplaceSource` id. `PersistOutcome` carries
`{created, updated, snapshot_created, skipped, reason}`.

## Behavioral contract

1. **Deduplication (FR-020)**: `persist_listing` resolves the existing
   `Listing` by `(source, uuid)`. Re-observation updates the existing row;
   it never creates a duplicate.
2. **Newest-wins (FR-021)**: when the new canonical state differs, the
   current row is updated to the newest values.
3. **Meaningful-change detection (FR-023, FR-024, FR-026)**: the service
   computes the new canonical hash (pure Python, via
   `src/common/canonical_hash.py`) and compares it to the stored
   `Listing.canonical_hash`:
   - equal → refresh only `last_seen_at` / `last_seen_run_id`; no snapshot;
     `canonical_hash` unchanged.
   - not equal → create one `ListingSnapshot` with the prior
     `canonical_payload`, `changed_fields`, `snapshot_hash`,
     `raw_listing_id`, `ingestion_run_id`; update the `Listing` to newest
     data; update `canonical_hash`; refresh `last_seen_at` / `last_seen_run_id`.
   - no prior row → insert `Listing` with `canonical_hash` = initial hash,
     `first_seen_*` = `last_seen_*` = current run, `status = ACTIVE`; no
     snapshot (FR-025).
4. **Atomicity (FR-054/055, NFR-010)**: all of the above for one listing
   happen in a single transaction requested from the adapter
   (`begin_listing_unit` / `commit` / `rollback`). Any failure rolls back
   the whole listing unit; no partial listing state is persisted.
5. **Run reconciliation (FR-056, SC-010)**: a per-listing failure is
   recorded; the run continues with remaining listings where possible; the
   `IngestionRun.status` and run report reflect the failures
   (`PARTIAL_FAILED` when failures occurred but data was produced).
6. **Replay resolution (FR-030, FR-032)**: `resolve_run` resolves by run
   name or run id; `load_raw_for_run` loads only the `RawListings` linked to
   that run via `ingestion_run_id`. Resolution logic lives in the service,
   not in any adapter.
7. **MarketplaceSource resolution (FR-010)**: `begin_run` resolves the
   `MarketplaceSource` by `code` (e.g., `dubizzle_uae`) from the seeded
   reference data. The service MUST NOT create marketplace source data per
   run; if the required `MarketplaceSource` is missing, the run fails fast
   with a clear, named error and no partial run is created.
8. **No DatasetVersion (FR-014)**: the service never creates or resolves
   `DatasetVersion`/`datasetKey`. No `ReplayRun` (FR-036).
9. **No disappearance inference (NFR-011)**: `status` stays `ACTIVE` for
   observed listings; absence in a later run is never interpreted.

## Non-functional contract

- No imports of a database client / ORM / query builder / schema-generated
  module (SC-007).
- No marketplace-specific logic (FR-061); operates on domain objects only.
- No business rule is delegated to or duplicated in any adapter (R-001).
- Secrets never appear in logs or reports (NFR-007).

## Test contract (NFR-009)

The service MUST have unit tests covering deduplication, newest-wins,
meaningful-change detection (via `canonical_hash`), snapshot creation, and
replay run resolution by name and by id — against a fake/in-memory adapter,
with no database.
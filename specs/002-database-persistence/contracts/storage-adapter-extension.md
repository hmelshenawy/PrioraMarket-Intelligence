# Contract: StorageAdapter Interface Extension

**Feature**: 002 — Database Persistence Foundation
**Spec refs**: FR-002, FR-006, FR-060, FR-061, NFR-002, NFR-003, R-001a, FR-072

The Feature 001 `StorageAdapter` interface (ADR-009) defines four operations:
`write_raw`, `write_listings`, `write_report`, `read_raw`. Feature 002 extends
it **additively and backward-compatibly** so the `PersistenceService` can
express upsert/snapshot/transaction/run-resolution without breaking CSV or
in-memory adapters or the Feature 001 contract test.

## Extended interface (additive only)

The four Feature 001 operations remain unchanged. The following operations are
added with default/no-op implementations so existing adapters conform without
behavior changes:

```python
class StorageAdapter(Protocol):
    # --- Feature 001 (unchanged) ---
    def write_raw(self, raw_listings: Iterable[RawListing]) -> int: ...
    def write_listings(self, listings: Iterable[Listing]) -> int: ...
    def write_report(self, report: RunReport) -> None: ...
    def read_raw(self, dataset_version: str | None = None) -> Iterable[RawListing]: ...

    # --- Feature 002 (additive) ---
    def upsert_marketplace_source(self, code: str, name: str, country: str, base_url: str) -> int: ...
    def find_listing_by_source_uuid(self, source: str, uuid: str) -> Optional[ListingRow]: ...
    def insert_listing(self, row: ListingRow) -> int: ...
    def update_listing(self, listing_id: int, row: ListingRow) -> None: ...
    def insert_snapshot(self, snap: SnapshotRow) -> int: ...
    def resolve_run(self, run_name_or_id: str) -> Optional[RunRow]: ...
    def read_raw_for_run(self, run_name_or_id: str) -> Iterable[RawListing]: ...
    def insert_ingestion_run(self, run: RunRow) -> int: ...
    def finalize_ingestion_run(self, run_id: int, report: RunReport, status: str, completed_at: datetime) -> None: ...

    # Transaction control as requested by the PersistenceService
    def begin_listing_unit(self) -> None: ...
    def commit_listing_unit(self) -> None: ...
    def rollback_listing_unit(self) -> None: ...
```

`ListingRow`, `SnapshotRow`, `RunRow` are marketplace-agnostic DTOs defined in
`src/common/models.py` (no DB imports). They carry only the fields the service
needs; they are not ORM entities and not schema-generated.

## Behavioral contract

- The interface **encodes no business rules** (FR-006). It exposes only the
  insert/update/read operations and transaction control the service needs.
- `read_raw_for_run` returns only the `RawListings` linked to the resolved
  `IngestionRun` via `ingestion_run_id` (FR-032), in deterministic order
  (by `id`).
- Transaction control is per-listing-unit (FR-054); the service calls
  `begin_listing_unit` before a listing's persistence and `commit`/`rollback`
  at its end.
- CSV and in-memory adapters provide conforming no-op/trivial implementations
  so substitutability (NFR-002, SC-004) and the Feature 001 contract test
  remain green.

## Conformance

- `PostgresStorageAdapter` conforms (Phase 3).
- `CsvStorageAdapter` and `InMemoryStorageAdapter` conform without changing
  Feature 001 behavior (FR-062, NFR-008).
- The extended contract test (`tests/contract/test_storage_adapter.py`) is
  parametrized over `csv` / `in-memory` / `postgres`.

## ADR

The extension shape and rationale are recorded in ADR-014 (FR-072, R-001a).
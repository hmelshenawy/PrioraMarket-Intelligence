# Research: Canonical Data Model & Vehicle Reference Catalog

## Decision: Keep Canonicalization In The Scraper/Data Ingestion Context

**Rationale**: The scraper already owns extraction, normalization, replay, persistence, schema migrations, and raw payload preservation. Keeping canonicalization there preserves the required Raw Marketplace → Extraction → Normalization → Canonicalization → Catalog Lookup → Persistence flow and prevents backend/frontend duplication.

**Alternatives considered**: Backend normalization was rejected because the backend is read-only and must not contain marketplace-specific logic. Frontend normalization was rejected because presentation consumers must not implement business logic. A separate normalization service was rejected as over-engineering for this foundation.

## Decision: Use Deterministic Canonicalization With Catalog-Owned Aliases

**Rationale**: Deterministic string processing satisfies replay, backfill, and auditability requirements. Aliases remain on Vehicle Reference Catalog records, avoiding a separate alias database and keeping the current stage lightweight.

**Alternatives considered**: Fuzzy matching and AI matching were rejected by scope. A standalone alias table was rejected because the specification explicitly assigns alias ownership to catalog records.

## Decision: Version Canonicalization Rules As Processing Metadata

**Rationale**: Listing records need traceability to the rule set used during processing for deterministic replay, safe future rule changes, debugging, and repeatable backfills. The plan does not prescribe the exact storage mechanism, only the requirement that processed records retain the version.

**Alternatives considered**: No versioning was rejected because it would make replay and future rule changes unsafe. A full rule registry/service was rejected as unnecessary infrastructure.

## Decision: CSV Files Are Catalog Source Of Truth

**Rationale**: CSV ownership gives data stewards a reviewable, environment-portable, repeatable catalog source. PostgreSQL remains the synchronized operational copy used by ingestion/backend reads.

**Alternatives considered**: Manual database editing was rejected because it is not authoritative or repeatable. A catalog management application was rejected as out of scope.

## Decision: Lightweight Synchronization Provenance Only

**Rationale**: The feature needs traceability for when catalog records were last synchronized, not a full catalog history/versioning platform. Last-sync metadata and sync reporting satisfy operational needs without adding complexity.

**Alternatives considered**: Full catalog versioning/history tables were rejected as over-engineering. No provenance was rejected because synchronization would be hard to audit.

## Decision: Backfill Reuses Live Canonicalization Path

**Rationale**: Reusing the same canonicalization engine ensures backfill, live ingestion, and replay produce consistent canonical values for the same inputs and rule version.

**Alternatives considered**: A separate backfill-specific mapper was rejected because it would drift. Direct SQL-only transformations were rejected because alias resolution, statistics, and versioning must stay consistent with live ingestion.

## Decision: Backend Compatibility Through Prisma Synchronization Only

**Rationale**: The backend should continue to read PostgreSQL with minimal changes. Prisma schema updates are needed to reflect scraper-owned migrations, but no backend business normalization should be introduced.

**Alternatives considered**: Backend service-level canonicalization was rejected. New API versions are not required unless future display-contract changes become breaking.

## Decision: Presentation Consumers Use Supplied Display Values

**Rationale**: Display names belong to the Vehicle Reference Catalog. Presentation consumers should receive or request display values and never reconstruct names from canonical keys.

**Alternatives considered**: Client-side formatting or title-casing canonical keys was rejected because it produces incorrect labels such as `Mercedesbenz`.

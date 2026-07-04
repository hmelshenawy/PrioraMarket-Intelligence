# Research: Backend Search API

## Decision: Create a Dedicated NestJS Backend Service

**Rationale**: The monorepo now separates ingestion (`scrapper/`) from API concerns (`backend/`). A dedicated backend preserves scraper behavior and gives future frontend, AI, analytics, and integration clients a versioned API surface.

**Alternatives considered**: Add HTTP endpoints to the Python scraper; rejected because it mixes ingestion and serving responsibilities. Create frontend-first data access; rejected by backend-centric business logic principle.

## Decision: Use Prisma as the Backend Persistence Adapter

**Rationale**: The requested architecture explicitly includes Prisma between repository and PostgreSQL. Prisma provides typed database access while remaining isolated in the repository layer. The database already exists, so Prisma should model or introspect current tables rather than own ingestion behavior.

**Alternatives considered**: Direct SQL through `pg`; rejected because the requested architecture specifies Prisma. Full ORM entities exposed to services; rejected because raw persistence models must not leak past repository/domain boundaries.

## Decision: Preserve Existing PostgreSQL Tables as Source of Truth

**Rationale**: Feature 002 created `marketplace_source`, `ingestion_run`, `raw_listing`, `listing`, and `listing_snapshot`. Search should prefer `listing` for current state and read snapshot canonical JSON only when detail fields are absent from `listing`.

**Alternatives considered**: Create duplicate search tables; rejected as ingestion duplication and schema drift risk. Read live marketplace data; rejected by constitution and feature scope.

## Decision: Use Strict Layering with Search Query Builder

**Rationale**: The expected filter set will grow. Isolating query construction behind `ISearchQueryBuilder` keeps Search Service focused on orchestration and business rules, keeps Listing Repository focused on execution/mapping, and enables future Prisma/OpenSearch/Elasticsearch/Meilisearch query-builder replacement.

**Alternatives considered**: Build Prisma queries in service; rejected because it mixes business orchestration and persistence concerns. Build search decisions in repository; rejected because repositories must not contain business/search decision logic.

## Decision: Page-Based Pagination for v1

**Rationale**: The API contract requires page, limit, total, and totalPages. Page-based pagination is simple for UI consumers and aligns with the spec.

**Alternatives considered**: Cursor pagination; rejected for v1 because it would change the requested contract. It can be added later as an additive endpoint or optional mode.

## Decision: Relevance Sort Falls Back to Newest Without Free Text

**Rationale**: Relevance has no meaningful score without a query. The spec assumption chooses fallback rather than rejection to keep consumer behavior predictable.

**Alternatives considered**: Return 400 for `sort=relevance` without `q`; rejected because fallback was already selected in the spec and reduces client branching.

## Decision: PostgreSQL-Backed Relevance for v1

**Rationale**: PostgreSQL can support acceptable full-text search over title, make, model, and trim with planned indexes. Keeping search in PostgreSQL avoids adding a new infrastructure dependency in v1 while preserving future replacement via query builder/repository abstraction.

**Alternatives considered**: Elasticsearch/OpenSearch/Meilisearch now; rejected as premature complexity for the current read-only API. Basic `ILIKE` only; acceptable as a fallback but less scalable and weaker for relevance ranking.

## Decision: Short TTL Cache for Filter Metadata

**Rationale**: Filter metadata requires distinct and range aggregates that should not run on every request. A 30-60 second TTL bounds staleness after ingestion updates while preserving read-only behavior.

**Alternatives considered**: Persist metadata tables; rejected because this feature must avoid database writes. Background refresh job; rejected as a non-goal.

## Decision: Additive Index Plan, Not Scraper Migration Changes During Planning

**Rationale**: Search needs indexes for performance, but scraper migrations own the existing persistence schema. The plan documents additive, reversible indexes and avoids modifying scraper migrations without explicit approval.

**Alternatives considered**: Change existing scraper migrations; rejected because completed feature migrations should remain stable. No indexes; rejected because performance targets depend on indexed search fields.

## Decision: Stable DTOs and Domain Mapping

**Rationale**: API consumers need stable contracts independent of table layout. Mapping database rows to domain objects and then DTOs through explicit mapper classes prevents raw model leakage, keeps large field-by-field mapping out of services/controllers/repositories, and supports future persistence changes.

**Alternatives considered**: Return Prisma models directly; rejected by constitution and spec. Map in controllers; rejected because controllers should remain HTTP-only.

## Decision: Health Endpoint Does Not Query Database

**Rationale**: The requested health endpoint is a basic availability check with a 50ms target. Avoiding database calls keeps it fast and separates liveness from future readiness checks.

**Alternatives considered**: Database-backed health check; useful for readiness but unnecessary for this endpoint and may violate the latency target during DB incidents.

## Decision: No Authentication in Feature 003

**Rationale**: The user explicitly excluded authentication unless already required by existing architecture. The backend remains ready for future auth but does not introduce it now.

**Alternatives considered**: Add API keys/JWT now; rejected as out of scope.

# Implementation Plan: Backend Search API

**Branch**: `003-backend-search-api` | **Date**: 2026-07-04 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/003-backend-search-api/spec.md`

**Planning Scope**: Planning only. This artifact defines the technical design for Feature 003 and intentionally does not include implementation code or task lists.

## Summary

Create a new `backend/` NestJS API that exposes read-only `/api/v1` search, detail, filters, stats, and health endpoints over the canonical listing database produced by Features 001 and 002. The backend uses strict layered architecture: Controller to Search Service to Search Query Builder to Listing Repository to Prisma to PostgreSQL. The design preserves existing scraper behavior, avoids ingestion duplication, returns stable DTOs instead of database models, and prepares the search implementation for future replacement with Elasticsearch, OpenSearch, or Meilisearch without changing controllers or API contracts.

## Technical Context

**Language/Version**: TypeScript targeting Node.js 20 LTS or newer.

**Primary Dependencies**: NestJS, Prisma Client, `class-validator`, `class-transformer`, Jest, Supertest, dotenv-compatible configuration, optional Nest cache manager for in-process short TTL metadata caching.

**Storage**: Existing PostgreSQL/Supabase database using Feature 002 tables: `marketplace_source`, `ingestion_run`, `raw_listing`, `listing`, and `listing_snapshot`. Prisma introspects or models the existing schema from `DATABASE_URL`; the backend does not own ingestion tables or mutate listing data.

**Testing**: Jest for unit and integration tests; Supertest for HTTP/contract tests; Prisma test client against an isolated test database or transaction-reset test schema.

**Target Platform**: Server-side web API running as a standalone backend service in the monorepo.

**Project Type**: Backend web service inside `backend/`, alongside existing `scrapper/` ingestion project.

**Performance Goals**: Listing search p95 under 300ms with planned indexes; listing detail p95 under 100ms; cached filter metadata p95 under 100ms; health p95 under 50ms.

**Constraints**: Strictly read-only search API; no frontend; no authentication or authorization in this feature; no scraping, replay, normalization, ingestion, background jobs, WebSockets, or database mutation endpoints; controllers must not access Prisma; repositories must not contain search decision logic.

**Scale/Scope**: Current canonical listing inventory plus expected growth in filters, marketplaces, and analytics consumers. Query design must support additional filters and future search engines without changing HTTP contracts.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Check | Status |
|-----------|-------|--------|
| I. Documentation First | Spec, plan, research, data model, contracts, and quickstart are updated before implementation. | PASS |
| II. Design Before Implementation | This is a planning-only phase; no code or tasks are generated. | PASS |
| III. Domain-Driven Architecture | Feature belongs to Search bounded context and consumes Marketplace Listings through read contracts over the internal database. | PASS |
| IV. Clean Layered Architecture | Plan enforces Controller, Service, Query Builder, Repository, DTO, Prisma separation. | PASS |
| V. API First | All capabilities are documented as versioned `/api/v1` REST contracts. | PASS |
| VI. Database as Source of Truth | Search reads internal canonical listing tables, never external marketplaces. | PASS |
| VII. Historical Data Preservation | No listing, snapshot, raw, or ingestion records are modified or deleted. | PASS |
| VIII. AI Assists, Never Invents | Future AI consumers can use deterministic backend APIs; this feature does not introduce AI. | PASS |
| IX. Analytics Before AI | Stats endpoint is deterministic and read-only; no AI-generated analytics. | PASS |
| X. Machine Learning as a Product Feature | Not applicable; no model behavior is introduced. | PASS |
| XI. Data Quality Before Intelligence | Responses expose canonical data and consistent null/empty values; no data cleaning is performed in the API. | PASS |
| XII. Scalability by Design | Query Builder and repository abstraction allow future search-engine replacement and additional marketplaces/filters. | PASS |
| XIII. Backend-Centric Business Logic | Filtering, sorting, pagination, and search rules execute in backend services. | PASS |
| XIV. Modularity | Backend module boundaries are explicit and communicate through interfaces/DTOs. | PASS |
| XV. Security by Default | Inputs are validated; secrets come from environment; no stack traces or secrets leak in responses/logs. Authentication is deferred by spec. | PASS |
| XVI. Simplicity Over Complexity | Uses a single backend service and Prisma over the existing database; no search engine is introduced until needed. | PASS |

**Gate Result**: PASS. No constitution violations require Complexity Tracking.

## Project Structure

### Documentation (this feature)

```text
specs/003-backend-search-api/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── openapi.yaml
└── checklists/
    └── requirements.md
```

### Source Code (repository root)

```text
backend/
├── package.json
├── tsconfig.json
├── tsconfig.build.json
├── nest-cli.json
├── .env.example
├── prisma/
│   └── schema.prisma
├── src/
│   ├── main.ts
│   ├── app.module.ts
│   ├── config/
│   │   ├── configuration.ts
│   │   └── validation.ts
│   ├── db/
│   │   ├── prisma.module.ts
│   │   └── prisma.service.ts
│   ├── health/
│   │   ├── health.controller.ts
│   │   └── dto/
│   │       └── health-response.dto.ts
│   ├── search/
│   │   ├── search.module.ts
│   │   ├── search.controller.ts
│   │   ├── search.service.ts
│   │   ├── listings.repository.ts
│   │   ├── listings.repository.interface.ts
│   │   ├── search-query-builder.interface.ts
│   │   ├── search-query.builder.ts
│   │   ├── dto/
│   │   │   ├── search-listings-query.dto.ts
│   │   │   ├── listing-search-result-response.dto.ts
│   │   │   ├── listing-detail-response.dto.ts
│   │   │   ├── pagination-meta-response.dto.ts
│   │   │   ├── filter-metadata-response.dto.ts
│   │   │   └── inventory-stats-response.dto.ts
│   │   ├── mappers/
│   │   │   ├── listing-response.mapper.ts
│   │   │   ├── filter-metadata-response.mapper.ts
│   │   │   └── inventory-stats-response.mapper.ts
│   │   └── domain/
│   │       ├── listing.domain.ts
│   │       ├── listing-filters.domain.ts
│   │       └── listing-stats.domain.ts
│   │   ├── stats.controller.ts
│   │   └── stats.service.ts
│   └── common/
│       ├── errors/
│       │   ├── api-error-response.dto.ts
│       │   └── domain-errors.ts
│       ├── filters/
│       │   └── http-exception.filter.ts
│       └── logging/
│           └── request-logging.interceptor.ts
└── test/
    ├── unit/
    ├── integration/
    └── contract/
```

**Structure Decision**: Create a new backend service under `backend/`. Keep scraper code and migrations unchanged except for separately planned additive index migrations if accepted during implementation. The main feature module is `SearchModule` because the bounded context is Search; listings are the read model/data source consumed by the Search API. Stats remain inside the Search module rather than a separate bounded context.

## Detailed Technical Plan

### 1. Module Structure

`AppModule` imports configuration, Prisma database access, `HealthModule`, and `SearchModule`. `SearchModule` owns search listings, listing detail, filter metadata, inventory stats, repository interfaces, query builder interfaces, concrete query builders, DTOs, response mappers, and domain objects. Stats are part of the Search bounded context and reuse the same listing repository abstraction.

### 2. Folder Structure

Use the `backend/` tree documented above. Keep API DTOs under `search/dto/`, response mappers under `search/mappers/`, domain objects under `search/domain/`, Prisma integration under `db/`, and cross-cutting error/logging concerns under `common/`.

### 3. Controllers

Controllers are HTTP-only and contain no business rules or Prisma access.

- `HealthController`: `GET /api/v1/health`, returns health response DTO.
- `SearchController`: `GET /api/v1/listings`, `GET /api/v1/listings/filters`, `GET /api/v1/listings/:id`.
- `StatsController`: `GET /api/v1/stats`, optional but planned inside `SearchModule`.

Controllers accept validated query/path DTOs, call services, and return response DTOs. They do not construct Prisma queries or inspect table names.

### 4. DTOs

Request DTOs:

- `SearchListingsQueryDto`: `q`, `condition`, `make`, `model`, `yearFrom`, `yearTo`, `priceMin`, `priceMax`, `kmMin`, `kmMax`, `location`, `sellerType`, `page`, `limit`, `sort`.
- Path parameter DTO for listing `id` if needed to validate numeric or string identifier format.

Validation rules:

- `page` defaults to 1 and must be positive integer.
- `limit` defaults to 20, must be positive integer, and must not exceed 100.
- Numeric filters must be valid numbers and use sensible non-negative ranges where applicable.
- `condition` must be `used` or `new` when present.
- `sort` must be one of `relevance`, `newest`, `price_asc`, `price_desc`, `year_asc`, `year_desc`, `km_asc`, `km_desc`.
- Empty strings normalize to absent filters.

### 5. Response DTOs

Stable response DTOs must be defined and returned from services/controllers. Raw Prisma models must never be exposed.

- `HealthResponseDto`: `{ status: "ok" }`.
- `ListingSearchResultResponseDto`: id, externalId, title, make, model, trim, year, priceAed, km, condition, location, sellerType, url, photosCount, firstSeenAt, lastSeenAt.
- `PaginationMetaResponseDto`: page, limit, total, totalPages.
- `SearchListingsResponseDto`: data array plus meta.
- `ListingDetailResponseDto`: full canonical detail and lineage fields from the spec.
- `FilterMetadataResponseDto`: makes, models, price, year, km, conditions, sellerTypes.
- `InventoryStatsResponseDto`: totalListings, usedListings, newListings, totalMakes, totalModels, averagePriceAed, minPriceAed, maxPriceAed, lastUpdatedAt.
- `ApiErrorResponseDto`: stable error envelope for validation, not found, and infrastructure failures.

Optional fields map to `null`; collection fields map to `[]`; object maps map to `{}`.

### 6. Services

`SearchService` orchestrates listing search, detail, and filter metadata. It coordinates validation outcomes, enforces business rules such as relevance fallback, calculates pagination metadata, depends on `ISearchQueryBuilder` rather than a concrete implementation, calls `ListingRepository`, and delegates domain-to-response conversion to mappers.

`StatsService` lives inside `SearchModule`, orchestrates inventory stats retrieval through the same listing repository abstraction, and delegates domain-to-response conversion to mappers. It remains read-only and does not compute client-side stats from paginated search responses.

Services do not manually map large response objects field by field. The response flow is Repository to Domain to Mapper to Response DTO.

### 7. Search Query Builder

`ISearchQueryBuilder` defines the query construction contract used by `SearchService`. `SearchQueryBuilder` is the Prisma/PostgreSQL implementation for v1 and converts validated search criteria into persistence query objects. This abstraction allows future Prisma, OpenSearch, Elasticsearch, or Meilisearch query builders to replace the implementation without changing service orchestration, controllers, or API contracts.

`SearchQueryBuilder` owns persistence-query construction only:

- `where` filters for condition, make, model, year, price, mileage, location, seller type, and status/current listing constraints.
- Free-text conditions over title/name, make, model, and trim.
- Relevance expression strategy where feasible with Prisma/PostgreSQL, otherwise a safe fallback ordering documented in research.
- `orderBy` clauses from the sort whitelist.
- `skip` and `take` pagination values.
- `select`, `include`, or equivalent projection definitions for search rows, detail reads, count queries, filter metadata, and stats queries.

It contains no HTTP decorators, no response DTO mapping, no validation decorators, and no repository execution.

### 8. Repository

`ListingRepositoryInterface` defines read methods:

- `search(query: BuiltListingSearchQuery): Promise<{ rows: ListingDomain[]; total: number }>`
- `findDetailById(id: string): Promise<ListingDetailDomain | null>`
- `getFilterMetadata(): Promise<FilterMetadataDomain>`
- `getInventoryStats(): Promise<InventoryStatsDomain>`

`PrismaListingRepository` executes query objects produced by `SearchQueryBuilder`, including projection definitions, joins or fetches related source data as instructed by the built query, maps Prisma records to domain objects, and returns domain data only. It does not choose filters, sort modes, relevance fallback, response projections, or validation behavior.

### 9. Prisma Interactions

Prisma is the persistence adapter only. The backend will define Prisma models for existing tables using mapped names if necessary: `marketplace_source`, `ingestion_run`, `raw_listing`, `listing`, and `listing_snapshot`. Queries should prefer `listing` for current canonical fields and use `marketplace_source` for marketplace display fields. `listing_snapshot.canonical_payload` may be read only for detail fields not present in `listing`, such as bodyType, fuel, transmission, color, specs, seller, verification flags, agent flags, neighbourhood, and photos count if those values are stored only in canonical payload.

No Prisma create, update, upsert, delete, or transaction writes are part of API handlers. Additive index migrations, if implemented later, must be explicitly separated from API runtime behavior and must not mutate listing or ingestion records.

### 10. Validation Strategy

Use global validation pipe with transformation enabled and whitelist behavior. DTO classes normalize empty strings to undefined and coerce numeric query parameters safely. Invalid numeric values, unsupported conditions, unsupported sort values, and limit values above 100 return 400 responses with stable error DTOs.

### 11. Error Handling Strategy

Use categorized errors:

- Validation errors: 400 with field-level messages.
- Listing not found: 404.
- Persistence/connectivity failures: 503 or 500 depending on recoverability, with internal details hidden.
- Unexpected errors: 500 with correlation ID.

Controllers use a global exception filter to produce consistent error responses. Services raise domain-specific errors and do not swallow exceptions silently.

### 12. Pagination Strategy

Page-based pagination is required for the public contract. Calculate `skip = (page - 1) * limit`, `take = limit`, and `totalPages = Math.ceil(total / limit)`. For empty results, return `total = 0` and `totalPages = 0`. Search repository should execute row query and count query using the same `where` object.

### 13. Search Strategy

Search reads current listings from `listing`, constrained to active/current records where applicable. Filters are combined with AND semantics. Free-text search is applied across title/name, make, model, and trim. Empty filters are ignored. Sorting defaults to `newest` unless explicitly provided.

### 14. Relevance Search Approach

Initial relevance support should use PostgreSQL-compatible full-text or weighted similarity approach while remaining behind `SearchQueryBuilder`. Preferred path:

- Build a text-search condition from `title`, `make`, `model`, and `trim`.
- Weight title highest, then make/model, then trim.
- Use a stable secondary sort by newest timestamp and id.
- If `sort=relevance` is requested without `q`, service falls back to `newest` before query building.

Because Prisma support for computed relevance ordering can be limited, the plan allows repository execution through safe parameterized raw read queries only when Prisma query objects cannot express the relevance order. Raw queries must still be produced through the query builder abstraction and must never concatenate unsafe user input.

### 15. Filter Metadata Generation

Filter metadata is derived from current listings:

- Distinct makes sorted alphabetically.
- Distinct models grouped by make and sorted alphabetically.
- Min/max price from non-null prices.
- Min/max year from non-null years.
- Min/max mileage from non-null mileage.
- Distinct conditions and seller types excluding empty values.

For empty inventory, return stable empty arrays/maps and null numeric ranges where no values exist.

### 16. Metadata Caching Strategy

Cache filter metadata for 30 to 60 seconds in the backend process. Cache key can be a fixed key for global filter metadata because no request-specific filters are required. Refresh is lazy on expiry and safe after ingestion updates because the TTL bounds staleness. Do not write cache state to listing or ingestion tables. If multiple backend instances are deployed later, this can move to Redis or another shared cache without changing API contracts.

### 17. Inventory Stats Strategy

Stats are read-only aggregate queries over current listings:

- total count.
- condition counts for used/new.
- distinct make/model counts.
- average/min/max price.
- latest update from `last_seen_at` or equivalent current listing timestamp.

Stats may optionally share the same short TTL cache pattern later if aggregate queries become expensive. This is future-compatible only and must not introduce background jobs.

### 18. Health Endpoint

`GET /api/v1/health` returns `{ "status": "ok" }` without requiring a database query, keeping it below 50ms under normal conditions. The current API contract is `status: "ok"`; `version` and `uptime` are acceptable future additive fields if the contract is updated without breaking existing consumers. A deeper readiness check can be introduced later as a separate endpoint if needed.

### 19. Query Optimization Strategy

Use selective filters and ordered indexes to support common query shapes. Keep search result projection limited to required response fields. For detail, use primary key lookup and targeted related reads. For filter metadata, rely on caching. For stats, use aggregate queries over indexed fields.

### 20. Required Database Indexes

Existing Feature 002 indexes include source/uuid, marketplace source, canonical hash, run references, and snapshot lookup indexes. Plan additive indexes for search performance:

- `listing(condition)`
- `listing(make)`
- `listing(model)`
- `listing(year)`
- `listing(price)`
- `listing(mileage)`
- `listing(seller_type)`
- `listing(location)`
- `listing(last_seen_at)` for newest sorting
- `listing(first_seen_at)` if newest semantics or analytics require first seen ordering
- Composite candidates: `(condition, make, model)`, `(make, model)`, `(last_seen_at DESC, id DESC)`
- Text-search index over `title`, `make`, `model`, and `trim`, preferably a PostgreSQL GIN index on a weighted `tsvector` expression or generated column if schema governance allows it

Index additions must be additive, reversible, and coordinated with database schema ownership. They must not alter scraper behavior or mutate listing data.

### 21. Repository Interfaces

Use TypeScript interfaces or abstract provider tokens for repository replacement. Services depend on `ListingRepositoryInterface`, not Prisma. Services also depend on `ISearchQueryBuilder`, not the concrete Prisma query builder. Query builder output should be represented by typed built-query objects that include filters, sorting, pagination, and projections and can later be translated to Elasticsearch/OpenSearch/Meilisearch request bodies without changing controllers.

### 22. Dependency Relationships

Dependency direction:

```text
Controller -> Service -> ISearchQueryBuilder -> ListingRepositoryInterface -> PrismaListingRepository -> PrismaService
```

Controllers depend on services and DTOs only. Services depend on `ISearchQueryBuilder`, `ListingRepositoryInterface`, domain types, and response mappers. Query builder implementations depend on validated DTO/domain criteria only. Repository implementation depends on Prisma and database-to-domain mappers. Response mappers convert domain objects to response DTOs. Prisma depends on `DATABASE_URL`.

### 23. Logging Approach

Use structured request logging with correlation/request ID, bounded context `Search`, operation name, route, status, duration, error category, rowsReturned, cacheHit, sortType, and whether freeText search was used. Do not log database URLs, secrets, raw payloads, raw query objects, sensitive values, or full search text; log normalized metadata such as `freeTextUsed: true` rather than the query contents.

### 24. Testing Strategy

Tests follow the constitution: unit tests for services/query builder, integration tests for repository and database mapping, contract tests for HTTP endpoints, and performance validation for key paths. Tests must cover required acceptance scenarios and validation errors.

### 25. Unit Testing Plan

Unit tests cover:

- Search DTO transformation and validation.
- Search service pagination defaults and totalPages calculation.
- Relevance fallback to newest when no free text exists.
- Invalid sort, condition, numeric filter, and limit behavior.
- Query builder where/orderBy/pagination construction.
- Query builder projection construction through `select`, `include`, or equivalent descriptors.
- Service dependency on `ISearchQueryBuilder` abstraction rather than concrete query builder.
- Repository interface usage by service without Prisma access.
- Response DTO mapping and null/empty consistency.
- Filter metadata cache hit/miss behavior using fake timers.

Mapper unit tests cover domain-to-response DTO mapping for search results, detail, pagination metadata, filter metadata, stats, and null/empty value consistency.

### 26. Integration Testing Plan

Integration tests use a test PostgreSQL database or isolated schema with seeded marketplace/listing/snapshot records. They verify Prisma repository reads existing tables, maps detail fields and lineage correctly, executes filter/search/sort queries, returns filter metadata, and never performs writes during API operations.

Repository tests are a dedicated integration test group. They verify database reads, marketplace/source joins, latest snapshot mapping, aggregate queries for stats, filter metadata queries, projection execution from built query objects, and that no create/update/upsert/delete operations are performed by repository methods.

### 27. API Contract Verification

Contract tests use Supertest against the Nest app and compare response shapes to `contracts/openapi.yaml`. Required checks:

- `GET /api/v1/health` returns status ok.
- `GET /api/v1/listings` returns data/meta with defaults.
- Search filters and supported sorts, including relevance, behave as specified.
- Invalid inputs produce stable 400 responses.
- `GET /api/v1/listings/:id` returns detail or 404.
- `GET /api/v1/listings/filters` returns stable metadata shape.
- `GET /api/v1/stats` returns stable stats shape.

### 28. Performance Validation Strategy

Use seeded representative inventory and measure p95 endpoint durations locally or in CI performance smoke tests where feasible. Validate query plans for search filters, newest sorting, detail lookup, text search, and metadata aggregate queries. Cached filter metadata tests should assert cache-hit behavior avoids repeated aggregate repository calls.

### 29. Risks

- Existing `listing` table lacks some detail fields; mitigation is read latest canonical JSON from `listing_snapshot` or `raw_listing` where needed while keeping response DTO stable.
- Prisma may not express relevance sorting cleanly; mitigation is parameterized raw read queries isolated behind query builder/repository boundaries.
- Additive indexes may be owned by scraper/database schema governance; mitigation is document them as planned search indexes and avoid modifying scraper migrations without explicit approval.
- In-process cache is per instance; mitigation is short TTL and future replacement with shared cache if horizontal scaling requires it.
- Large offset pagination may degrade at high page numbers; mitigation is acceptable for v1 contract, with cursor pagination reserved for a future additive API.

### 30. Future Extensibility

The controller and response DTOs remain stable if the repository implementation changes. Future search engines can be introduced by replacing the `ISearchQueryBuilder` implementation and `ListingRepository` implementation while preserving service behavior and API contracts.

Room is preserved for saved searches, favorites, compare vehicles, similar listings, AI recommendations, market analytics, aggregations, geographic search, and full-text search improvements. These future features should add services/modules and contracts without placing business logic in controllers or persistence logic in services.

## Phase 0: Research Summary

Research decisions are recorded in [research.md](./research.md). No unresolved `NEEDS CLARIFICATION` items remain.

## Phase 1: Design Summary

Design artifacts generated:

- [data-model.md](./data-model.md)
- [contracts/openapi.yaml](./contracts/openapi.yaml)
- [quickstart.md](./quickstart.md)

## Post-Design Constitution Check

| Principle | Result |
|-----------|--------|
| Documentation and design gates | PASS: Plan, research, data model, contracts, and quickstart are complete before tasks/code. |
| Layered architecture | PASS: Controller, service, query builder interface, repository, mappers, DTO, and Prisma roles are explicitly separated. |
| API-first and versioning | PASS: Versioned `/api/v1` OpenAPI contract is documented. |
| Database source of truth | PASS: Existing PostgreSQL canonical tables are the only data source. |
| Read-only historical preservation | PASS: No runtime writes or mutation endpoints are planned. |
| Security/configuration/logging | PASS: Validation, environment config, stable errors, and structured logging are planned. |
| Simplicity | PASS: No external search engine, auth, frontend, jobs, or WebSockets are introduced in v1. |

**Post-Design Gate Result**: PASS. No unresolved clarifications or constitution violations.

## Complexity Tracking

No constitution violations require justification.

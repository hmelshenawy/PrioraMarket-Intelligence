# Tasks: Backend Search API

**Input**: Design documents from `/specs/003-backend-search-api/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/openapi.yaml, quickstart.md

**Tests**: Tests are included because the feature specification explicitly requires tests for health, pagination defaults, limit validation, invalid sort, invalid numeric filters, filtered search, detail not found, and filter metadata response shape.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1, US2, US3, US4, US5)
- Every task includes an exact file path

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Initialize the NestJS backend project and shared tooling.

- [X] T001 Create backend project directory structure in backend/src, backend/prisma, and backend/test
- [X] T002 Create backend/package.json with NestJS, Prisma, ConfigModule, validation, Jest, Supertest, build, start, and test scripts
- [X] T003 Create TypeScript and Nest configuration in backend/tsconfig.json, backend/tsconfig.build.json, and backend/nest-cli.json
- [X] T004 [P] Create backend/.env.example with DATABASE_URL, PORT, NODE_ENV, LOG_LEVEL, and FILTER_METADATA_CACHE_TTL_SECONDS placeholders
- [X] T005 [P] Create backend/.gitignore for node_modules, dist, coverage, .env, and Prisma generated artifacts
- [X] T006 [P] Configure Jest for unit, integration, and contract test locations in backend/jest.config.ts
- [X] T007 [P] Create initial app bootstrap files in backend/src/main.ts and backend/src/app.module.ts

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core configuration, database, DI tokens, cache abstraction, domain, interfaces, mappers, validation, errors, and logging required before any user story implementation.

**CRITICAL**: No user story work can begin until this phase is complete.

- [X] T008 Create environment configuration loader exposing DATABASE_URL, PORT, NODE_ENV, LOG_LEVEL, and FILTER_METADATA_CACHE_TTL_SECONDS in backend/src/config/configuration.ts
- [X] T009 Create environment validation rules for DATABASE_URL, PORT, NODE_ENV, LOG_LEVEL, and FILTER_METADATA_CACHE_TTL_SECONDS in backend/src/config/validation.ts
- [X] T010 Configure Nest ConfigModule with validation and ConfigService availability in backend/src/app.module.ts
- [X] T011 Create Prisma schema for existing Feature 002 tables in backend/prisma/schema.prisma
- [X] T012 Create Prisma module and PrismaService using ConfigService DATABASE_URL in backend/src/db/prisma.module.ts and backend/src/db/prisma.service.ts
- [X] T013 Create SearchModule shell for Search bounded context providers in backend/src/search/search.module.ts
- [X] T014 [P] Create listing domain types in backend/src/search/domain/listing.domain.ts
- [X] T015 [P] Create filter metadata domain types in backend/src/search/domain/listing-filters.domain.ts
- [X] T016 [P] Create inventory stats domain types in backend/src/search/domain/listing-stats.domain.ts
- [X] T017 [P] Create search criteria and operation-specific built query domain types BuiltListingSearchQuery, BuiltListingDetailQuery, BuiltFilterMetadataQuery, and BuiltInventoryStatsQuery in backend/src/search/domain/search-query.domain.ts
- [X] T018 [P] Create ListingReadRepositoryInterface with search(query: BuiltListingSearchQuery), findDetail(query: BuiltListingDetailQuery), getFilterMetadata(query: BuiltFilterMetadataQuery), and getInventoryStats(query: BuiltInventoryStatsQuery) in backend/src/search/listing-read.repository.interface.ts
- [X] T019 [P] Create ISearchQueryBuilder interface in backend/src/search/search-query-builder.interface.ts
- [X] T020 [P] Create DI provider tokens LISTING_READ_REPOSITORY and SEARCH_QUERY_BUILDER in backend/src/search/search.tokens.ts
- [X] T021 [P] Create IFilterMetadataCache interface in backend/src/search/cache/filter-metadata-cache.interface.ts
- [X] T022 [P] Create in-process read-only TTL filter metadata cache implementation in backend/src/search/cache/in-memory-filter-metadata.cache.ts
- [X] T023 [P] Create filter metadata cache provider token FILTER_METADATA_CACHE in backend/src/search/cache/filter-metadata-cache.token.ts
- [X] T024 [P] Create API error response DTO in backend/src/common/errors/api-error-response.dto.ts
- [X] T025 [P] Create domain error classes in backend/src/common/errors/domain-errors.ts
- [X] T026 Create global HTTP exception filter in backend/src/common/filters/http-exception.filter.ts
- [X] T027 Create request logging interceptor with requestId, duration, rowsReturned, cacheHit, sortType, and freeTextUsed fields in backend/src/common/logging/request-logging.interceptor.ts
- [X] T028 [P] Create search listing query DTO with validation and transform rules in backend/src/search/dto/search-listings-query.dto.ts
- [X] T029 [P] Create listing search result response DTO in backend/src/search/dto/listing-search-result-response.dto.ts
- [X] T030 [P] Create pagination metadata response DTO in backend/src/search/dto/pagination-meta-response.dto.ts
- [X] T031 [P] Create listing detail response DTO in backend/src/search/dto/listing-detail-response.dto.ts
- [X] T032 [P] Create filter metadata response DTO in backend/src/search/dto/filter-metadata-response.dto.ts
- [X] T033 [P] Create inventory stats response DTO in backend/src/search/dto/inventory-stats-response.dto.ts
- [X] T034 [P] Create health response DTO in backend/src/health/dto/health-response.dto.ts
- [X] T035 [P] Create listing response mapper in backend/src/search/mappers/listing-response.mapper.ts
- [X] T036 [P] Create filter metadata response mapper in backend/src/search/mappers/filter-metadata-response.mapper.ts
- [X] T037 [P] Create inventory stats response mapper in backend/src/search/mappers/inventory-stats-response.mapper.ts
- [X] T038 Create PrismaListingReadRepository skeleton in backend/src/search/listing-read.repository.ts
- [X] T039 Create Prisma search query builder skeleton in backend/src/search/search-query.builder.ts
- [X] T040 Create SearchService skeleton injecting LISTING_READ_REPOSITORY, SEARCH_QUERY_BUILDER, FILTER_METADATA_CACHE, ConfigService, and mappers in backend/src/search/search.service.ts
- [X] T041 Create StatsService skeleton injecting LISTING_READ_REPOSITORY and mappers inside SearchModule in backend/src/search/stats.service.ts
- [X] T042 Create SearchController skeleton for listings routes in backend/src/search/search.controller.ts
- [X] T043 Create StatsController skeleton for /api/v1/stats in backend/src/search/stats.controller.ts
- [X] T044 Create HealthController skeleton in backend/src/health/health.controller.ts
- [X] T045 Register PrismaListingReadRepository under LISTING_READ_REPOSITORY plus concrete providers for SEARCH_QUERY_BUILDER and FILTER_METADATA_CACHE in backend/src/search/search.module.ts
- [X] T046 Wire HealthController and SearchModule into AppModule in backend/src/app.module.ts
- [X] T047 [P] Create DI wiring unit tests asserting LISTING_READ_REPOSITORY, SEARCH_QUERY_BUILDER, FILTER_METADATA_CACHE, PrismaListingReadRepository, and concrete query builder providers in backend/test/unit/search-module.di.spec.ts
- [X] T048 [P] Create ConfigModule unit tests for required ConfigService values in backend/test/unit/configuration.spec.ts

**Checkpoint**: Foundation ready - user story implementation can now begin.

---

## Phase 3: User Story 1 - Search Current Vehicle Listings (Priority: P1) MVP

**Goal**: Retrieve paginated current vehicle listings with filters, sorting, relevance behavior, validation, stable DTOs, and no database writes.

**Independent Test**: Request `/api/v1/listings` with default, filtered, sorted, relevance, and invalid query combinations and verify data/meta shape, validation errors, ordering behavior, DI abstractions, and read-only database state.

### Tests for User Story 1

- [X] T049 [P] [US1] Create contract tests for GET /api/v1/listings response and validation behavior in backend/test/contract/listings-search.contract.spec.ts
- [X] T050 [P] [US1] Create SearchService unit tests for pagination defaults, relevance fallback, invalid sort, invalid condition, invalid numeric filters, limit max behavior, and ListingReadRepositoryInterface injection through LISTING_READ_REPOSITORY in backend/test/unit/search.service.spec.ts
- [X] T051 [P] [US1] Create SearchQueryBuilder unit tests for BuiltListingSearchQuery where, orderBy, select/include, skip, take, free-text, and relevance descriptors in backend/test/unit/search-query.builder.spec.ts
- [X] T052 [P] [US1] Create golden fixture tests for listing search response mapper and null/empty consistency in backend/test/unit/golden/listing-search-response.mapper.golden.spec.ts
- [X] T053 [P] [US1] Create read repository integration tests for search reads, filters, sorting, projection execution, counts, and no writes in backend/test/integration/listing-read.repository.search.spec.ts

### Implementation for User Story 1

- [X] T054 [US1] Implement SearchListingsQueryDto validation transforms for empty filters, numeric filters, page, limit, condition, and sort in backend/src/search/dto/search-listings-query.dto.ts
- [X] T055 [US1] Implement SearchQueryBuilder search query construction returning BuiltListingSearchQuery for filters, free-text, relevance, sorting, pagination, and projection descriptors in backend/src/search/search-query.builder.ts
- [X] T056 [US1] Implement PrismaListingReadRepository search(query: BuiltListingSearchQuery) execution and database-to-domain mapping in backend/src/search/listing-read.repository.ts
- [X] T057 [US1] Implement ListingResponseMapper for search result DTOs and pagination metadata in backend/src/search/mappers/listing-response.mapper.ts
- [X] T058 [US1] Implement SearchService search orchestration using SEARCH_QUERY_BUILDER, LISTING_READ_REPOSITORY, and mapper abstractions in backend/src/search/search.service.ts
- [X] T059 [US1] Implement GET /api/v1/listings in SearchController in backend/src/search/search.controller.ts
- [X] T060 [US1] Add structured search logging metadata for duration, rowsReturned, sortType, cacheHit false, and freeTextUsed in backend/src/common/logging/request-logging.interceptor.ts
- [X] T061 [US1] Add additive search index migration plan file for condition, make, model, year, price, mileage, seller_type, location, last_seen_at, first_seen_at, composites, and text search in backend/prisma/migrations/README-search-indexes.md

**Checkpoint**: User Story 1 is independently functional and testable as the MVP.

---

## Phase 4: User Story 2 - Read Listing Details (Priority: P2)

**Goal**: Retrieve one listing by id with canonical detail fields, latest available lineage data, stable null handling, and 404 for missing listings.

**Independent Test**: Request `/api/v1/listings/{id}` for a known listing and an unknown listing and verify detail fields, lineage fields, response DTO shape, 404 behavior, and read-only database state.

### Tests for User Story 2

- [X] T062 [P] [US2] Create contract tests for GET /api/v1/listings/{id} success and 404 responses in backend/test/contract/listing-detail.contract.spec.ts
- [X] T063 [P] [US2] Create SearchService detail unit tests for ListingReadRepositoryInterface abstraction usage, mapper usage, and not-found behavior in backend/test/unit/search-detail.service.spec.ts
- [X] T064 [P] [US2] Create golden fixture tests for listing detail response mapper with canonical, optional, lineage, null, and empty values in backend/test/unit/golden/listing-detail-response.mapper.golden.spec.ts
- [X] T065 [P] [US2] Create read repository integration tests for detail reads, marketplace joins, latest snapshot mapping, raw fallback mapping, and no writes in backend/test/integration/listing-read.repository.detail.spec.ts

### Implementation for User Story 2

- [X] T066 [US2] Extend SearchQueryBuilder with detail query descriptors returning BuiltListingDetailQuery and projections in backend/src/search/search-query.builder.ts
- [X] T067 [US2] Implement PrismaListingReadRepository findDetail(query: BuiltListingDetailQuery) with marketplace join, latest snapshot fallback, raw fallback, and domain mapping in backend/src/search/listing-read.repository.ts
- [X] T068 [US2] Implement ListingResponseMapper detail mapping in backend/src/search/mappers/listing-response.mapper.ts
- [X] T069 [US2] Implement SearchService detail orchestration and NotFoundError handling through abstractions in backend/src/search/search.service.ts
- [X] T070 [US2] Implement GET /api/v1/listings/:id in SearchController in backend/src/search/search.controller.ts

**Checkpoint**: User Story 2 is independently functional and does not break User Story 1.

---

## Phase 5: User Story 3 - Discover Available Filters (Priority: P3)

**Goal**: Return available filter metadata derived from current listings with short TTL caching through a cache abstraction and stable response shape.

**Independent Test**: Request `/api/v1/listings/filters` and verify makes, grouped models, price/year/km ranges, conditions, sellerTypes, cache abstraction behavior, empty-data shape, and read-only database state.

### Tests for User Story 3

- [X] T071 [P] [US3] Create contract tests for GET /api/v1/listings/filters response shape in backend/test/contract/filter-metadata.contract.spec.ts
- [X] T072 [P] [US3] Create SearchService filter metadata cache unit tests for IFilterMetadataCache usage, cache miss, cache hit, TTL expiry, and cacheHit logging metadata in backend/test/unit/filter-metadata-cache.service.spec.ts
- [X] T073 [P] [US3] Create golden fixture tests for filter metadata response mapper with sorted arrays, grouped models, null ranges, and empty inventory shape in backend/test/unit/golden/filter-metadata-response.mapper.golden.spec.ts
- [X] T074 [P] [US3] Create read repository integration tests for distinct values, ranges, grouped models, aggregate reads, and no writes in backend/test/integration/listing-read.repository.filters.spec.ts
- [X] T075 [P] [US3] Create in-memory filter metadata cache unit tests for TTL, get, set, clear, and read-only behavior in backend/test/unit/in-memory-filter-metadata.cache.spec.ts

### Implementation for User Story 3

- [X] T076 [US3] Extend SearchQueryBuilder with filter metadata query descriptors returning BuiltFilterMetadataQuery and projections in backend/src/search/search-query.builder.ts
- [X] T077 [US3] Implement PrismaListingReadRepository getFilterMetadata(query: BuiltFilterMetadataQuery) aggregate reads and domain mapping in backend/src/search/listing-read.repository.ts
- [X] T078 [US3] Implement FilterMetadataResponseMapper in backend/src/search/mappers/filter-metadata-response.mapper.ts
- [X] T079 [US3] Implement in-process TTL cache using FILTER_METADATA_CACHE_TTL_SECONDS without listing or ingestion table writes in backend/src/search/cache/in-memory-filter-metadata.cache.ts
- [X] T080 [US3] Implement SearchService filter metadata orchestration through IFilterMetadataCache, SEARCH_QUERY_BUILDER, and LISTING_READ_REPOSITORY in backend/src/search/search.service.ts
- [X] T081 [US3] Implement GET /api/v1/listings/filters in SearchController in backend/src/search/search.controller.ts
- [X] T082 [US3] Add filter metadata cacheHit logging support in backend/src/common/logging/request-logging.interceptor.ts

**Checkpoint**: User Story 3 is independently functional and cached metadata meets the contract.

---

## Phase 6: User Story 4 - Verify Service Availability (Priority: P4)

**Goal**: Provide a fast basic health endpoint returning status ok without database dependency.

**Independent Test**: Request `/api/v1/health` and verify `{ "status": "ok" }`, stable DTO shape, and response path does not require database access.

### Tests for User Story 4

- [X] T083 [P] [US4] Create contract tests for GET /api/v1/health response shape and status code in backend/test/contract/health.contract.spec.ts
- [X] T084 [P] [US4] Create HealthController unit tests for status ok response in backend/test/unit/health.controller.spec.ts

### Implementation for User Story 4

- [X] T085 [US4] Implement HealthResponseDto with status ok contract in backend/src/health/dto/health-response.dto.ts
- [X] T086 [US4] Implement HealthController GET /api/v1/health without database dependency in backend/src/health/health.controller.ts

**Checkpoint**: User Story 4 is independently functional and fast.

---

## Phase 7: User Story 5 - View Inventory Stats (Priority: P5)

**Goal**: Return optional high-level read-only inventory stats from current listings under the Search bounded context.

**Independent Test**: Request `/api/v1/stats` and verify totals, condition counts, make/model counts, price summaries, lastUpdatedAt, empty inventory behavior, and read-only database state.

### Tests for User Story 5

- [X] T087 [P] [US5] Create contract tests for GET /api/v1/stats response shape in backend/test/contract/inventory-stats.contract.spec.ts
- [X] T088 [P] [US5] Create StatsService unit tests for LISTING_READ_REPOSITORY token injection, mapper usage, empty inventory behavior, and optional cache compatibility in backend/test/unit/stats.service.spec.ts
- [X] T089 [P] [US5] Create golden fixture tests for inventory stats response mapper with count, price summary, lastUpdatedAt, null, and empty fields in backend/test/unit/golden/inventory-stats-response.mapper.golden.spec.ts
- [X] T090 [P] [US5] Create read repository integration tests for stats aggregate reads and no writes in backend/test/integration/listing-read.repository.stats.spec.ts

### Implementation for User Story 5

- [X] T091 [US5] Extend SearchQueryBuilder with inventory stats aggregate query descriptors returning BuiltInventoryStatsQuery and projections in backend/src/search/search-query.builder.ts
- [X] T092 [US5] Implement PrismaListingReadRepository getInventoryStats(query: BuiltInventoryStatsQuery) aggregate reads and domain mapping in backend/src/search/listing-read.repository.ts
- [X] T093 [US5] Implement InventoryStatsResponseMapper in backend/src/search/mappers/inventory-stats-response.mapper.ts
- [X] T094 [US5] Implement StatsService orchestration through LISTING_READ_REPOSITORY and mapper abstractions in backend/src/search/stats.service.ts
- [X] T095 [US5] Implement GET /api/v1/stats in StatsController inside SearchModule in backend/src/search/stats.controller.ts
- [X] T096 [US5] Register StatsController and StatsService providers inside SearchModule without creating a StatsModule in backend/src/search/search.module.ts

**Checkpoint**: User Story 5 is independently functional and remains inside SearchModule.

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Validation, performance, documentation, and cross-story hardening.

- [X] T097 [P] Add OpenAPI contract verification helper using specs/003-backend-search-api/contracts/openapi.yaml in backend/test/contract/openapi-contract.spec.ts
- [X] T098 [P] Add read-only safety integration test comparing listing and ingestion row counts before and after API calls in backend/test/integration/read-only-safety.spec.ts
- [X] T099 [P] Add performance smoke tests for search, detail, cached filters, and health targets in backend/test/integration/performance-smoke.spec.ts
- [X] T100 [P] Add query plan notes for expected indexes and relevance search in backend/docs/search-query-optimization.md
- [X] T101 [P] Update backend README with setup, DATABASE_URL, PORT, NODE_ENV, LOG_LEVEL, FILTER_METADATA_CACHE_TTL_SECONDS, validation commands, and quickstart checks in backend/README.md
- [X] T102 Run npm install validation for backend/package.json and backend/package-lock.json
- [X] T103 Run npm run build and resolve build errors in backend/src
- [X] T104 Run npm run test and resolve test failures in backend/test
- [X] T105 Verify quickstart smoke checks from specs/003-backend-search-api/quickstart.md against the running backend

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately.
- **Foundational (Phase 2)**: Depends on Setup completion - blocks all user stories.
- **User Stories (Phases 3-7)**: All depend on Foundational phase completion.
- **Polish (Phase 8)**: Depends on all desired user stories being complete.

### User Story Dependencies

- **US1 Search Current Vehicle Listings (P1)**: Can start after Foundational; MVP scope.
- **US2 Read Listing Details (P2)**: Can start after Foundational; reuses SearchModule and read repository abstractions from foundation.
- **US3 Discover Available Filters (P3)**: Can start after Foundational; reuses SearchService, ListingReadRepositoryInterface, and IFilterMetadataCache.
- **US4 Verify Service Availability (P4)**: Can start after Foundational; independent from database-backed stories.
- **US5 View Inventory Stats (P5)**: Can start after Foundational; reuses SearchModule and ListingReadRepositoryInterface.

### Within Each User Story

- Tests are written before implementation tasks.
- Query builder and repository work precedes service orchestration.
- Mappers precede service response completion.
- Controller endpoint wiring follows service completion.
- Story checkpoint validates independent behavior before moving to the next priority.

---

## Parallel Opportunities

- Setup tasks T004-T007 can run in parallel after T001-T003 are understood.
- Foundational domain, interface, token, DTO, cache abstraction, and mapper tasks T014-T037 can run in parallel because they touch separate files.
- DI wiring tests T047 and configuration tests T048 can run in parallel after provider skeletons exist.
- Each story's contract, service, golden mapper, query builder, and repository tests can be drafted in parallel.
- After Phase 2, US1-US5 can be implemented by separate developers if shared files are coordinated.
- Polish tasks T097-T101 can run in parallel after relevant story endpoints exist.

---

## Parallel Example: User Story 1

```text
Task: "T049 Contract tests in backend/test/contract/listings-search.contract.spec.ts"
Task: "T050 SearchService unit tests in backend/test/unit/search.service.spec.ts"
Task: "T051 SearchQueryBuilder unit tests in backend/test/unit/search-query.builder.spec.ts"
Task: "T052 Golden listing search mapper tests in backend/test/unit/golden/listing-search-response.mapper.golden.spec.ts"
Task: "T053 Read repository integration tests in backend/test/integration/listing-read.repository.search.spec.ts"
```

## Parallel Example: User Story 2

```text
Task: "T062 Contract tests in backend/test/contract/listing-detail.contract.spec.ts"
Task: "T063 SearchService detail unit tests in backend/test/unit/search-detail.service.spec.ts"
Task: "T064 Golden listing detail mapper tests in backend/test/unit/golden/listing-detail-response.mapper.golden.spec.ts"
Task: "T065 Read repository detail integration tests in backend/test/integration/listing-read.repository.detail.spec.ts"
```

## Parallel Example: User Story 3

```text
Task: "T071 Contract tests in backend/test/contract/filter-metadata.contract.spec.ts"
Task: "T072 Filter metadata cache service tests in backend/test/unit/filter-metadata-cache.service.spec.ts"
Task: "T073 Golden filter metadata mapper tests in backend/test/unit/golden/filter-metadata-response.mapper.golden.spec.ts"
Task: "T074 Read repository filters integration tests in backend/test/integration/listing-read.repository.filters.spec.ts"
Task: "T075 In-memory cache tests in backend/test/unit/in-memory-filter-metadata.cache.spec.ts"
```

## Parallel Example: User Story 4

```text
Task: "T083 Health contract tests in backend/test/contract/health.contract.spec.ts"
Task: "T084 HealthController unit tests in backend/test/unit/health.controller.spec.ts"
```

## Parallel Example: User Story 5

```text
Task: "T087 Stats contract tests in backend/test/contract/inventory-stats.contract.spec.ts"
Task: "T088 StatsService unit tests in backend/test/unit/stats.service.spec.ts"
Task: "T089 Golden inventory stats mapper tests in backend/test/unit/golden/inventory-stats-response.mapper.golden.spec.ts"
Task: "T090 Read repository stats integration tests in backend/test/integration/listing-read.repository.stats.spec.ts"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1 setup.
2. Complete Phase 2 foundation.
3. Complete Phase 3 User Story 1 search.
4. Validate `GET /api/v1/listings` defaults, filtering, sorting, relevance fallback, invalid inputs, DI abstraction wiring, mapper golden outputs, and read-only behavior.
5. Stop and demo/deploy MVP if appropriate.

### Incremental Delivery

1. Setup + Foundational -> architecture, DI tokens, cache abstraction, ConfigModule, and test harness ready.
2. US1 Search -> MVP discovery API.
3. US2 Detail -> complete listing read experience.
4. US3 Filters -> UI-ready metadata and cache abstraction.
5. US4 Health -> deployment liveness check.
6. US5 Stats -> optional inventory summaries.
7. Polish -> contract, read-only, performance, docs, build, and test verification.

### Parallel Team Strategy

1. Team completes Setup and Foundational phases together.
2. One developer owns US1 because it creates the core search path.
3. Other developers can prepare US2-US5 tests in parallel after foundation.
4. Shared files requiring coordination: backend/src/search/search.service.ts, backend/src/search/search-query.builder.ts, backend/src/search/listing-read.repository.ts, backend/src/search/search.module.ts.

---

## Notes

- All runtime API behavior must remain read-only.
- Do not add frontend, authentication, authorization, scraping, replay, normalization, mutation endpoints, background jobs, or WebSockets.
- Do not modify scraper behavior or completed scraper migrations unless explicitly approved for additive database indexes.
- Keep controllers HTTP-only and free of Prisma access.
- Keep services dependent on `LISTING_READ_REPOSITORY`, `SEARCH_QUERY_BUILDER`, and `FILTER_METADATA_CACHE` abstraction tokens.
- Keep read repository methods free of search decision logic and database writes.

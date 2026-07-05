# Tasks: Market Snapshot Dashboard

**Input**: Design documents from `/specs/006-market-snapshot-dashboard/`

**Prerequisites**: spec.md (approved), research.md, data-model.md, contracts/, quickstart.md, plan.md. The specification, implementation plan (Constitution Check + API Design), contracts, data-model, and research.md all explicitly include Data Freshness (FR-032/FR-033, SC-009).

**Tests**: Included. The constitution testing strategy (unit, integration, contract, data-quality) and `quickstart.md` both require tests; the repo already has `backend/test/unit/golden/` and `frontend/test/{unit,component,integration,e2e}/` conventions to match.

**Organization**: Tasks grouped by user story (US1 P1, US2 P2, US3 P3, US4 P4) in priority order. Backend, frontend, and tests are sequenced within each story in dependency order.

**Preserved architecture**: `AnalyticsModule` · `MarketSnapshotService` · `FilterOptionsService` · `SnapshotAggregationService` · `SnapshotReadRepository` · `FilterReadRepository` · `MarketMetric` domain terminology · separate `/api/v1/market/snapshot` and `/api/v1/market/filter-options` endpoints · backend returns raw values only · frontend owns formatting · `DashboardShell` / `MarketFilterBar` / `SnapshotMetrics` / per-metric components · no scraper changes · no valuation / AI / forecasting / trends / marketplace browsing / new infrastructure.

**Data Freshness (approved requirement)**: The spec (FR-032/FR-033, SC-009), plan, `contracts/market-snapshot-api.md`, `contracts/filter-options-api.md`, and `data-model.md` (Freshness entity + `freshness` field on `MarketSnapshot`) explicitly require every Market Snapshot and Filter Options response to expose `freshness { lastUpdated, datasetVersion, scrapeRunId }` per Constitution 1.1.0 Data Freshness. Tasks below implement this approved requirement; they do not introduce a new feature. `generatedAt` (FR-005, "As of") remains distinct from `freshness.lastUpdated`.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies on incomplete tasks)
- **[Story]**: Which user story this task belongs to (US1, US2, US3, US4)
- Exact file paths are included in every task

## Path Conventions

- **Backend**: `backend/src/analytics/...` (NestJS module mirroring `backend/src/search/`)
- **Backend tests**: `backend/test/{contract,integration,unit,unit/golden}/...`
- **Frontend**: `frontend/features/market/...` (feature-sliced, mirroring `frontend/features/search/`) + `frontend/app/market/page.tsx`
- **Frontend tests**: `frontend/test/{unit,component,integration,e2e}/...`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Create the AnalyticsModule scaffolding registered with the app.

- [X] T001 Create AnalyticsModule scaffolding in `backend/src/analytics/analytics.module.ts` (empty module, controllers/providers arrays, imports PrismaModule) and register it in `backend/src/app.module.ts`
- [X] T002 [P] Create dependency-injection tokens in `backend/src/analytics/analytics.tokens.ts` (SNAPSHOT_READ_REPOSITORY, FILTER_READ_REPOSITORY)

**Checkpoint**: AnalyticsModule compiles and boots; `/api/v1/market/` route group is reserved.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Domain types, DTOs, repository interfaces, and query validation that ALL user stories depend on. No user story work can begin until this phase is complete.

- [X] T003 [P] Verify `specs/006-market-snapshot-dashboard/` artifacts already include Data Freshness (spec FR-032/FR-033 + SC-009, `contracts/market-snapshot-api.md` + `contracts/filter-options-api.md` Data Freshness sections, `data-model.md` Freshness entity) so implementation targets the approved contract
- [X] T004 [P] Create MarketMetric domain type in `backend/src/analytics/domain/market-metric.domain.ts` (discriminated union: activeListings, medianPrice, typicalPriceRange, inventoryChange, priceDrops; each with its payload fields from data-model.md)
- [X] T005 [P] Create MetricSupportStatus domain type in `backend/src/analytics/domain/metric-support-status.domain.ts` (supported, unsupported, unavailable, partial; reason, dataAvailable)
- [X] T006 [P] Create SnapshotPeriod domain type in `backend/src/analytics/domain/snapshot-period.domain.ts` (days int, label; default 7)
- [X] T007 [P] Create AppliedMarketFilters domain type with hierarchy validation in `backend/src/analytics/domain/applied-market-filters.domain.ts` (optional make/model/trim, optional int year, periodDays default 7; model requires make, trim requires make+model, year requires make+model+trim; no normalization)
- [X] T008 [P] Create MarketScope domain type in `backend/src/analytics/domain/market-scope.domain.ts` (level: overall|make|model|trim|year, label, canonical object)
- [X] T009 [P] Create Freshness domain type in `backend/src/analytics/domain/freshness.domain.ts` (lastUpdated ISO, datasetVersion string, scrapeRunId; nullable fields allowed when underlying data missing)
- [X] T010 [P] Create FilterOption domain type in `backend/src/analytics/domain/filter-option.domain.ts` (value, displayName, activeListingCount optional)
- [X] T011 [P] Create MarketSnapshot domain aggregate in `backend/src/analytics/domain/market-snapshot.domain.ts` (scope, filters, ordered metrics, supportStatuses map, period, freshness, generatedAt)
- [X] T012 [P] Create market-snapshot query DTO with validation in `backend/src/analytics/dto/market-snapshot-query.dto.ts` (make/model/trim strings, year int, periodDays int default 7; hierarchy validation reusing AppliedMarketFilters rules; invalid shape returns existing backend validation error)
- [X] T013 [P] Create filter-options query DTO with validation in `backend/src/analytics/dto/filter-options-query.dto.ts` (make/model/trim strings, year int; same hierarchy rules; year accepted only as selected state)
- [X] T014 [P] Create Freshness DTO in `backend/src/analytics/dto/freshness.dto.ts` (lastUpdated, datasetVersion, scrapeRunId)
- [X] T015 [P] Create MarketSnapshot response DTO in `backend/src/analytics/dto/market-snapshot-response.dto.ts` (scope, filters, period, metrics array, supportStatuses map, freshness, generatedAt; raw numeric values only, no formatted strings)
- [X] T016 [P] Create FilterOptions response DTO in `backend/src/analytics/dto/filter-options-response.dto.ts` (filters, options{makes,models,trims,years}, freshness, generatedAt)
- [X] T017 Create SnapshotReadRepository interface and token wiring in `backend/src/analytics/snapshot-read.repository.interface.ts` (methods: countActiveListings, fetchPricesForStats, fetchFirstSeenInPeriod, fetchRemovedInPeriod, fetchPriceDrops, getFreshness; all scoped by AppliedMarketFilters; data-access only, no calculations)
- [X] T018 Create FilterReadRepository interface and token wiring in `backend/src/analytics/filter-read.repository.interface.ts` (methods: listMakes, listModels(make), listTrims(make,model), listYears(make,model,trim), getFreshness; each returning FilterOption with activeListingCount; data-access only)
- [X] T019 [P] Create MarketSnapshotResponseMapper skeleton in `backend/src/analytics/mappers/market-snapshot-response.mapper.ts` (domain MarketSnapshot → response DTO; raw values only)
- [X] T020 [P] Create FilterOptionsResponseMapper skeleton in `backend/src/analytics/mappers/filter-options-response.mapper.ts` (domain options → response DTO)

**Checkpoint**: All domain types, DTOs, repository interfaces exist and match the approved contracts (including freshness); module compiles. User story implementation can now begin.

---

## Phase 3: User Story 1 — Overall Market Snapshot (Priority: P1) 🎯 MVP

**Goal**: A user opens the dashboard with no filters and sees a generated overall market snapshot with five cards in the required order, an "As of" timestamp, freshness metadata, and clear unsupported states for history-dependent metrics.

**Independent Test**: Open `/market` with no filters; confirm cards render in order Active Listings, Median Price, Typical Price Range, Inventory Change, Price Drops; active listings / median / price range show real values; inventory change shows active inventory with new/removed/net unsupported; price drops shows unsupported; header shows "Overall UAE Used Cars" and "As of <timestamp>"; response includes `freshness`.

### Tests for User Story 1

> Write tests first; ensure they fail before implementation.

- [X] T021 [P] [US1] Contract test for `GET /api/v1/market/snapshot` (overall, no filters) in `backend/test/contract/market-snapshot.contract.spec.ts` (assert scope.level=overall, scope.label="Overall UAE Used Cars", metric order, `freshness.lastUpdated/datasetVersion/scrapeRunId` present, raw values only, generatedAt present)
- [X] T022 [P] [US1] Unit test for SnapshotAggregationService pure aggregation in `backend/test/unit/market-snapshot.aggregator.spec.ts` (active listings count, median, P25/P75 vs min/max fallback by sample size, sample-size inclusion, unsupported-by-default for new/removed/net/priceDrops)
- [X] T023 [P] [US1] Golden dataset test for overall snapshot aggregation in `backend/test/unit/golden/market-snapshot.golden.spec.ts` (fixed canonical listing fixture → expected snapshot JSON across supported/unsupported/empty scopes, including freshness derived from fixture listing timestamps)
- [X] T024 [P] [US1] Frontend unit test for market formatting helpers in `frontend/test/unit/marketFormat.test.ts` (AED labels, thousand separators, percentages, "As of" timestamp rendering from raw ISO)
- [X] T025 [P] [US1] Frontend component test for SnapshotMetrics card order and unsupported states in `frontend/test/component/snapshotMetrics.test.tsx`

### Backend Implementation for User Story 1

- [X] T026 [US1] Implement SnapshotReadRepository in `backend/src/analytics/snapshot-read.repository.ts` (Prisma read-only queries over `listing` where status='ACTIVE' scoped by canonical make/model/trim/year; countActiveListings, fetchPricesForStats, getFreshness from max(lastSeenAt)/lastSeenRunId/normalizationVersion over the scoped active listings; no writes)
- [X] T027 [US1] Implement SnapshotAggregationService in `backend/src/analytics/aggregation/market-snapshot.aggregator.ts` (activeListings count; medianPrice with sampleSize; typicalPriceRange with P25/P75 when sample sufficient else min/max fallback, sampleSize, method="typical-range"; inventoryChange activeInventory real + newListings/removedListings/netChange null with unsupported status by default; priceDrops null with unsupported status; produce MetricSupportStatus per metric; pure, no DB access)
- [X] T028 [US1] Implement MarketSnapshotService in `backend/src/analytics/market-snapshot.service.ts` (orchestrate: build AppliedMarketFilters from query DTO, call repository, call aggregator, build MarketScope label="Overall UAE Used Cars" for overall, populate `freshness` from repository getFreshness, set generatedAt, delegate to mapper; no business calculations)
- [X] T029 [US1] Implement MarketSnapshotController in `backend/src/analytics/market-snapshot.controller.ts` (`GET /api/v1/market/snapshot`; validate query DTO; return DTO; no business logic)
- [X] T030 [US1] Wire SnapshotReadRepository provider into `backend/src/analytics/analytics.module.ts` and register MarketSnapshotController/MarketSnapshotService
- [X] T031 [US1] Finalize MarketSnapshotResponseMapper in `backend/src/analytics/mappers/market-snapshot-response.mapper.ts` (map domain snapshot to response DTO including `freshness` and ordered metrics; raw values only)
- [X] T032 [US1] Add integration test for MarketSnapshotService + SnapshotReadRepository in `backend/test/integration/market-snapshot.service.spec.ts` (overall scope end-to-end against a seeded Prisma test DB; assert freshness populated from seeded listing timestamps)

### Frontend Implementation for User Story 1

- [X] T033 [P] [US1] Create market API client in `frontend/features/market/api/market-api.client.ts` (axios GET snapshot + filter-options; raw response passthrough)
- [X] T034 [P] [US1] Create zod schemas in `frontend/features/market/schemas/market-snapshot.schema.ts` and `frontend/features/market/schemas/filter-options.schema.ts` (validate backend response shapes including `freshness`)
- [X] T035 [P] [US1] Create market types in `frontend/features/market/types/market.types.ts` (TypeScript types matching response DTOs including freshness)
- [X] T036 [P] [US1] Create market constants in `frontend/features/market/constants/market.ts` (metric order, period default 7, query keys)
- [X] T037 [P] [US1] Create market formatting utils in `frontend/features/market/utils/market-format.ts` (formatAed, formatNumber, formatPercent, formatAsOf; presentation only; MUST NOT present freshness as a real-time reading)
- [X] T038 [P] [US1] Create MetricState shared component in `frontend/features/market/components/MetricState.tsx` (loading, empty, unsupported, error states; distinguishes unsupported from true zero)
- [X] T039 [P] [US1] Create per-metric components in `frontend/features/market/components/ActiveListingsCard.tsx`, `MedianPriceCard.tsx`, `TypicalPriceRangeCard.tsx`, `InventoryChangeCard.tsx`, `PriceDropsCard.tsx` (presentation only; render raw values via market-format; show sample sizes; show unsupported states via MetricState)
- [X] T040 [US1] Create SnapshotMetrics component in `frontend/features/market/components/SnapshotMetrics.tsx` (renders the five metric components in the required order)
- [X] T041 [US1] Create AsOfTimestamp and ScopeLabel components in `frontend/features/market/components/AsOfTimestamp.tsx` and `frontend/features/market/components/ScopeLabel.tsx`
- [X] T042 [US1] Create DashboardShell component in `frontend/features/market/components/DashboardShell.tsx` (page frame, header with ScopeLabel + AsOfTimestamp, SnapshotMetrics placement)
- [X] T043 [US1] Create useMarketSnapshot hook in `frontend/features/market/hooks/use-market-snapshot.ts` (TanStack Query; query key includes canonical filters + period; no client-side analytics)
- [X] T044 [US1] Create market dashboard page route in `frontend/app/market/page.tsx` (compose DashboardShell + useMarketSnapshot for the overall scope; dark-mode compatible)
- [X] T045 [US1] Create market snapshot mapper in `frontend/features/market/mappers/market-snapshot-mapper.ts` (raw response → view model for presentation; no recalculation; freshness carried as metadata, not displayed as real-time)

**Checkpoint**: User Story 1 fully functional and independently testable. Overall dashboard loads with five ordered cards, "As of" timestamp, freshness metadata, and unsupported states for history-dependent metrics.

---

## Phase 4: User Story 2 — Filtered Vehicle Snapshot (Priority: P2)

**Goal**: A user selects make, model, trim, and year from cascading dropdowns and the same cards update for the selected scope without a full page reload; invalid lower-level selections are cleared or disabled.

**Independent Test**: Select a make; confirm all cards update for that make and model options are limited to that make; add model/trim/year; confirm cards update and scope label reflects the selection; change a higher-level filter and confirm lower-level selections are cleared/disabled before cards update; no full page reload; filter-options response includes `freshness`.

### Tests for User Story 2

- [X] T046 [P] [US2] Contract test for `GET /api/v1/market/snapshot` with make/model/trim/year in `backend/test/contract/market-snapshot.contract.spec.ts` (extend: filtered scope, canonical filters echoed, hierarchy validation errors, freshness present)
- [X] T047 [P] [US2] Contract test for `GET /api/v1/market/filter-options` cascading in `backend/test/contract/filter-options.contract.spec.ts` (options constrained by higher-level filters; filters echoed; `freshness` present)
- [X] T048 [P] [US2] Frontend integration test for cascading filters + no-reload refresh in `frontend/test/integration/marketFilters.test.tsx` (filter change updates snapshot via TanStack Query; lower-level cleared on higher-level change; no full reload)

### Backend Implementation for User Story 2

- [X] T049 [US2] Extend SnapshotReadRepository in `backend/src/analytics/snapshot-read.repository.ts` to scope all reads (including getFreshness) by canonical make/model/trim/year from AppliedMarketFilters (no normalization; exact canonical match)
- [X] T050 [US2] Extend SnapshotAggregationService in `backend/src/analytics/aggregation/market-snapshot.aggregator.ts` to accept the selected scope and produce scope-relative metrics (reuse US1 calculation paths)
- [X] T051 [US2] Extend MarketSnapshotService scope-label generation in `backend/src/analytics/market-snapshot.service.ts` (build level + canonical scope label from canonical values; canonical fallback for labels in US2 — catalog display names added in US3)
- [X] T052 [US2] Implement FilterReadRepository in `backend/src/analytics/filter-read.repository.ts` (Prisma distinct canonical make/model/trim/year where status='ACTIVE' scoped by higher-level filters; activeListingCount per option; getFreshness over scoped active listings; displayName = canonical fallback in US2)
- [X] T053 [US2] Implement FilterOptionsService in `backend/src/analytics/filter-options.service.ts` (orchestrate repository by FilterOptionsQuery DTO; build options per level; populate `freshness` from repository getFreshness; set generatedAt; delegate to mapper)
- [X] T054 [US2] Implement FilterOptionsController in `backend/src/analytics/filter-options.controller.ts` (`GET /api/v1/market/filter-options`; validate query DTO; return DTO; no business logic)
- [X] T055 [US2] Wire FilterReadRepository + FilterOptionsService + FilterOptionsController into `backend/src/analytics/analytics.module.ts`
- [X] T056 [US2] Finalize FilterOptionsResponseMapper in `backend/src/analytics/mappers/filter-options-response.mapper.ts` (include `freshness`)
- [X] T057 [US2] Add integration test for FilterReadRepository cascading in `backend/test/integration/filter-read.repository.spec.ts` (model options limited to selected make; trim limited to make+model; counts match active listings; freshness scoped correctly)

### Frontend Implementation for User Story 2

- [X] T058 [US2] Create useFilterOptions hook in `frontend/features/market/hooks/use-filter-options.ts` (TanStack Query; query key includes selected higher-level filters; parallel with snapshot query)
- [X] T059 [US2] Create MarketFilterBar component in `frontend/features/market/components/MarketFilterBar.tsx` (cascading make/model/trim/year selects; options from useFilterOptions; clear/disable invalid lower-level selections on higher-level change; display active listing counts as "Toyota (4,381)")
- [X] T060 [US2] Add URL query-param state for filters in `frontend/features/market/hooks/use-market-snapshot.ts` and `frontend/app/market/page.tsx` (filters in URL; TanStack Query re-fetches on key change; no full page reload)
- [X] T061 [US2] Compose MarketFilterBar into DashboardShell in `frontend/features/market/components/DashboardShell.tsx` and wire filter state to useMarketSnapshot query keys

**Checkpoint**: User Stories 1 AND 2 both work independently. Filtered dashboard updates for make/model/trim/year without a full page reload; cascading options constrain correctly; invalid lower-level selections are cleared/disabled.

---

## Phase 5: User Story 3 — Catalog-Based Display Names (Priority: P3)

**Goal**: Dropdowns and dashboard labels show clean Vehicle Reference Catalog display names while the system internally uses canonical vehicle values; values without a catalog display name fall back to the canonical value without new normalization.

**Independent Test**: Compare dropdown labels and scope labels against `vehicle_reference_catalog` for vehicles that have display names; confirm the displayed name matches the catalog display name; for a value without a catalog display name, confirm the canonical value is shown unchanged.

### Tests for User Story 3

- [X] T062 [P] [US3] Integration test for catalog display-name resolution in `backend/test/integration/filter-read.repository.spec.ts` (extend: options carry catalog displayName when available; canonical fallback when absent)
- [X] T063 [P] [US3] Frontend component test for display-name rendering in `frontend/test/component/marketFilterBar.test.tsx` (options render displayName; counts shown; no hardcoded names)

### Backend Implementation for User Story 3

- [X] T064 [US3] Extend FilterReadRepository to join `vehicle_reference_catalog` in `backend/src/analytics/filter-read.repository.ts` (resolve displayName per make/model/trim from catalog; canonical fallback when no catalog row; no new normalization)
- [X] T065 [US3] Add display-name resolution for scope label in `backend/src/analytics/market-snapshot.service.ts` (build scope label from catalog display names when available, canonical fallback otherwise; e.g., "Toyota Corolla XLI 2023")
- [X] T066 [US3] Add golden dataset test for catalog display-name fallback in `backend/test/unit/golden/filter-options.golden.spec.ts` (fixture with and without catalog display names → expected options + scope labels)

### Frontend Implementation for User Story 3

- [X] T067 [US3] Update MarketFilterBar to render `displayName` from API in `frontend/features/market/components/MarketFilterBar.tsx` (use API displayName; never hardcode vehicle names; keep counts)
- [X] T068 [US3] Update ScopeLabel to render API-provided scope label in `frontend/features/market/components/ScopeLabel.tsx` (no hardcoded names; no canonical-value transformation)

**Checkpoint**: User Stories 1, 2, AND 3 work independently. Display names come from the Vehicle Reference Catalog with canonical fallback; no hardcoded names; no new normalization.

---

## Phase 6: User Story 4 — Market Activity and Price Drops (Priority: P4)

**Goal**: The Inventory Change card shows active inventory, new listings, removed listings (when supported), and net change; the Price Drops card shows count, average drop percentage, and sample size; both show clear unsupported/unavailable states when the underlying history is unavailable, never fabricated values.

**Independent Test**: For a scope with first-seen data, confirm the Inventory Change card shows active inventory + new listings for the period; when removal tracking is unavailable, confirm removed listings and net change show unsupported; when price history is insufficient, confirm Price Drops shows unsupported with null values; when price history exists, confirm price-drop count, average drop percentage, and sample size match the data.

### Tests for User Story 4

- [ ] T069 [P] [US4] Unit test for inventory-change and price-drop aggregation in `backend/test/unit/market-snapshot.aggregator.spec.ts` (extend: netChange present only when both new+removed supported; partial status; priceDrops count/avg/sampleSize; unsupported vs true-zero distinction)
- [ ] T070 [P] [US4] Golden dataset test for inventory change + price drops in `backend/test/unit/golden/market-snapshot.golden.spec.ts` (extend: fixtures covering supported/partial/unsupported for inventoryChange and priceDrops → expected JSON)
- [ ] T071 [P] [US4] Frontend component test for InventoryChangeCard + PriceDropsCard states in `frontend/test/component/inventoryAndPriceDrops.test.tsx` (supported values, partial unsupported, full unsupported, empty)

### Backend Implementation for User Story 4

- [ ] T072 [US4] Implement new-listings query in `backend/src/analytics/snapshot-read.repository.ts` (count listings with firstSeenAt within selected periodDays scoped to filters; supported only if first-seen metadata exists; else unsupported)
- [ ] T073 [US4] Implement removed-listings query in `backend/src/analytics/snapshot-read.repository.ts` (identify removals in period from listing status/lifecycle when tracking available; if unavailable, repository signals unsupported — no fabrication)
- [ ] T074 [US4] Implement price-drops query in `backend/src/analytics/snapshot-read.repository.ts` (from `listing_snapshot` price changes within period when price history exists; count, average drop percentage, sample size; if unavailable, signal unsupported)
- [ ] T075 [US4] Extend SnapshotAggregationService for history metrics in `backend/src/analytics/aggregation/market-snapshot.aggregator.ts` (inventoryChange: activeInventory + newListings + removedListings (null when unsupported) + netChange = new-removed only when both supported, else null; priceDrops: count + averageDropPercentage + sampleSize or null with unsupported/partial status; distinguish unsupported from real zero)
- [ ] T076 [US4] Wire history-metric support detection through MarketSnapshotService in `backend/src/analytics/market-snapshot.service.ts` (map repository support signals to MetricSupportStatus; never fabricate; pass through to mapper)
- [ ] T077 [US4] Update MarketSnapshotResponseMapper for full inventory-change + price-drops payloads in `backend/src/analytics/mappers/market-snapshot-response.mapper.ts` (null values + status + reason for unsupported; raw values for supported)

### Frontend Implementation for User Story 4

- [ ] T078 [US4] Finalize InventoryChangeCard in `frontend/features/market/components/InventoryChangeCard.tsx` (render activeInventory, newListings, removedListings, netChange with unsupported/unavailable states via MetricState; period label)
- [ ] T079 [US4] Finalize PriceDropsCard in `frontend/features/market/components/PriceDropsCard.tsx` (render count, averageDropPercentage, sampleSize with unsupported state via MetricState; period label)

**Checkpoint**: All four user stories work independently. History-dependent metrics show real values when data exists and clear unsupported/unavailable states otherwise; no fabricated values.

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Cross-story quality, constitution compliance, documentation alignment, and final validation.

- [ ] T080 [P] Add read-only safety test in `backend/test/integration/market-endpoints.read-only.spec.ts` (assert calling `/api/v1/market/snapshot` and `/api/v1/market/filter-options` does not mutate `listing`, `raw_listing`, `listing_snapshot`, catalog, or lifecycle rows — FR-025, FR-026, contract Read-Only Guarantee)
- [ ] T081 [P] Add e2e test for overall + filtered dashboard in `frontend/test/e2e/marketDashboard.spec.ts` (overall snapshot load; filtered snapshot load; no full page reload on filter change; dark mode renders)
- [ ] T082 [P] Review query plans and add indexes only if measurable benefit in `backend/prisma/schema.prisma` (candidate indexes on status + canonical make/model/trim/year + price; add only with EXPLAIN evidence; reversible migration with up/down per constitution Migration Strategy)
- [ ] T083 [P] Update API documentation (API_SPEC / DATA_MODEL) to include `/api/v1/market/snapshot`, `/api/v1/market/filter-options`, freshness metadata, and metric contracts (constitution Documentation Alignment)
- [ ] T084 [P] Reconcile `specs/006-market-snapshot-dashboard/plan.md` remaining sections (Project Structure / Technical Approach already reflect freshness in Constitution Check + API Design; remove chat-log preamble if a clean plan file is desired)
- [ ] T085 Run `quickstart.md` validation checklist (overall load, filtered no-reload, metric order, sample sizes, unsupported states, freshness fields present, raw values, no normalization, read-only safety, dark mode)
- [ ] T086 [P] Run lint + format + typecheck for backend (`backend/`) and frontend (`frontend/`); fix all violations (constitution Coding Conventions)
- [ ] T087 [P] Run full backend test suite (`npm run test:unit`, `test:integration`, `test:contract`) and frontend suite (`npm run test`, `npm run e2e`, `npm run build`); ensure green

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: No dependencies — start immediately.
- **Phase 2 (Foundational)**: Depends on Phase 1 — BLOCKS all user stories.
- **Phase 3 (US1)**: Depends on Phase 2. MVP target.
- **Phase 4 (US2)**: Depends on Phase 2; builds on US1 components (SnapshotMetrics, DashboardShell, useMarketSnapshot). Independently testable.
- **Phase 5 (US3)**: Depends on Phase 2 + US2 backend (FilterReadRepository, scope-label generation). Refines display names.
- **Phase 6 (US4)**: Depends on Phase 2 + US1 aggregator/repository skeleton. Fills in history-dependent metrics.
- **Phase 7 (Polish)**: Depends on all desired user stories being complete.

### User Story Dependencies

- **US1 (P1)**: Starts after Phase 2. No dependencies on other stories. MVP.
- **US2 (P2)**: Starts after Phase 2. Reuses US1 frontend components (DashboardShell, SnapshotMetrics, useMarketSnapshot) and US1 backend aggregator/repository; extends them.
- **US3 (P3)**: Starts after US2 (needs FilterReadRepository + scope-label generation to refine).
- **US4 (P4)**: Starts after US1 (needs the aggregator/repository skeleton + inventory-change/price-drops card components from US1's unsupported-default rendering).

### Within Each User Story

- Tests written first and FAIL before implementation (Red-Green).
- Domain types before repositories/services.
- Repositories (data-access) before aggregator (calculations) before service (orchestration) before controller (transport).
- Backend endpoint before frontend client/hooks.
- Frontend hooks before components before page route.

### Parallel Opportunities

- All Phase 2 tasks marked [P] can run in parallel (independent files).
- Within US1, tasks T033–T039 (frontend client/schemas/types/constants/formatting/MetricState/per-metric components) are independent and [P].
- US3 and US4 can be worked on in parallel by different developers once their respective predecessors (US2, US1) are complete, since they touch different metric paths and components.
- Phase 7 polish tasks T080–T084, T086, T087 are [P] (independent files/concerns).

---

## Parallel Example: User Story 1

```bash
# Launch US1 tests together (fail first):
Task T021: "Contract test for GET /api/v1/market/snapshot in backend/test/contract/market-snapshot.contract.spec.ts"
Task T022: "Unit test for SnapshotAggregationService in backend/test/unit/market-snapshot.aggregator.spec.ts"
Task T023: "Golden dataset test in backend/test/unit/golden/market-snapshot.golden.spec.ts"
Task T024: "Frontend market-format unit test in frontend/test/unit/marketFormat.test.ts"
Task T025: "Frontend SnapshotMetrics component test in frontend/test/component/snapshotMetrics.test.tsx"

# Then launch independent frontend building blocks together:
Task T033: "market API client in frontend/features/market/api/market-api.client.ts"
Task T034: "zod schemas in frontend/features/market/schemas/"
Task T035: "market types in frontend/features/market/types/market.types.ts"
Task T036: "market constants in frontend/features/market/constants/market.ts"
Task T037: "market formatting utils in frontend/features/market/utils/market-format.ts"
Task T038: "MetricState component in frontend/features/market/components/MetricState.tsx"
Task T039: "per-metric components in frontend/features/market/components/"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1 (Setup).
2. Complete Phase 2 (Foundational) — CRITICAL, blocks all stories.
3. Complete Phase 3 (US1).
4. STOP and VALIDATE: test US1 independently (overall dashboard, five ordered cards, "As of" timestamp, freshness, unsupported states).
5. Demo if ready.

### Incremental Delivery

1. Setup + Foundational → foundation ready.
2. Add US1 → test independently → demo (MVP).
3. Add US2 → test filtered scope + no-reload → demo.
4. Add US3 → test catalog display names + fallback → demo.
5. Add US4 → test history metrics + unsupported states → demo.
6. Polish (Phase 7) → read-only safety, golden tests, e2e, docs, validation.

### Parallel Team Strategy

With multiple developers after Phase 2:
- Developer A: US1 (backend snapshot path + frontend dashboard).
- Developer B (after US1): US2 (filter query path + filter bar + URL state).
- Developer C (after US1): US4 (history metrics — independent of US2/US3).
- Developer D (after US2): US3 (catalog display names).
- Polish tasks shared once stories land.

---

## Notes

- [P] tasks = different files, no dependencies on incomplete tasks.
- [Story] label maps task to its user story for traceability.
- Each user story is independently completable and testable.
- Tests fail before implementation (Red-Green).
- Commit after each task or logical group; run the relevant focused tests.
- Stop at any checkpoint to validate a story independently.
- Backend returns raw values only; frontend owns all formatting (AED, separators, percentages, "As of").
- No scraper changes; no valuation, AI, forecasting, trends, marketplace browsing, or new infrastructure.
- Data Freshness (`freshness`: `lastUpdated`, `datasetVersion`, `scrapeRunId`) is an approved requirement (FR-032/FR-033, SC-009; Constitution 1.1.0 Data Freshness), explicitly present in the spec, plan, contracts, and data-model before task generation. `generatedAt` remains distinct from `freshness.lastUpdated`.
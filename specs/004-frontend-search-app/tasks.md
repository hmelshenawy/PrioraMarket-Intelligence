# Tasks: Frontend Search Application

**Input**: Design documents from `/specs/004-frontend-search-app/`

**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/, quickstart.md

**Tests**: Test tasks are included because `plan.md` defines a full Testing Strategy (Unit, Component, Integration, E2E, Accessibility, Responsive, Theme, Error-State). Tests are written per story and mocked via MSW/Playwright; no live backend is required.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story. The frontend lives under `frontend/`. Every feature folder follows the standard internal structure: `api/`, `components/`, `hooks/`, `mappers/`, `schemas/`, `types/`, `constants/`, `utils/`, plus a root `index.ts` public API. Feature internals are private unless exported through `index.ts`.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies on incomplete tasks)
- **[Story]**: Which user story this task belongs to (e.g., US0, US1, US2...)
- Include exact file paths in descriptions

## Path Conventions

- **Web app**: `frontend/` root with `app/`, `features/`, `lib/`, `components/`, `styles/`, `test/`, `public/`
- Backend lives under `backend/` and is NOT modified by Feature 004
- All backend communication goes through typed API modules in `frontend/features/*/api/` and the shared Axios client in `frontend/lib/api/`; pages never call Axios directly

---

## Phase 1: Setup (Project Initialization)

**Purpose**: Create the isolated `frontend/` Next.js App Router project and tooling.

- [x] T001 Create `frontend/` project structure per plan.md (directories: `app/`, `features/{search,listings,filters,stats,health,theme,shared}/`, `lib/{api,constants,config,formatting,mappers,query,routing,seo,validation}/`, `components/{layout,ui}/`, `styles/`, `test/{unit,component,integration,e2e,fixtures,mocks}/`, `public/`)
- [x] T002 Initialize Next.js App Router + TypeScript project in `frontend/` with dependencies: React, Next.js, Tailwind CSS, TanStack Query, React Hook Form, Zod, Axios, Lucide icons, next/font, ESLint, Prettier
- [x] T003 [P] Configure ESLint and Prettier in `frontend/` (`.eslintrc`, `.prettierrc`, scripts in `package.json`)
- [x] T004 [P] Configure Tailwind CSS + design token theme config in `frontend/tailwind.config.ts` mapping plan tokens (color, typography, spacing, radius, shadow, z-index, breakpoints) to semantic tokens for light/dark
- [x] T005 [P] Configure Vitest + React Testing Library + jest-dom in `frontend/` (`vitest.config.ts`, `test/setup.ts`)
- [x] T006 [P] Configure Playwright in `frontend/` (`playwright.config.ts` with desktop/laptop/tablet/mobile viewports)
- [x] T007 [P] Create `frontend/.env.example` documenting `NEXT_PUBLIC_API_BASE_URL` (required) and optional metadata site URL, indexing toggle, health polling interval with non-secret placeholders
- [x] T008 [P] Add build/lint/test/format scripts to `frontend/package.json` per plan "Build And Validation Commands"

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Cross-cutting infrastructure that MUST be complete before ANY user story can be implemented.

**⚠️ CRITICAL**: No user story work can begin until this phase is complete. These foundations are reused by every story and every future frontend feature.

- [x] T009 Implement typed environment validation with Zod in `frontend/lib/config/env.ts` (validates `NEXT_PUBLIC_API_BASE_URL`, fails clearly on invalid/missing required values, safe local default only when documented)
- [x] T010 Implement centralized Axios instance in `frontend/lib/api/client.ts` (base URL from env, `/api/v1` path, timeout, JSON handling, error normalization to `ApiError`, no secrets/auth headers)
- [x] T011 Implement API error normalization in `frontend/lib/api/errors.ts` mapping Axios/network/backend errors to UI categories (network, offline, 400, 404, unexpected) per `frontend/lib/api/types.ts`
- [x] T012 Implement query key factory in `frontend/lib/query/keys.ts` (feature-scoped keys for listings, listing detail, filters, stats, health; listings/search keys derived from normalized URL state)
- [x] T013 Implement TanStack Query `QueryClient` + provider in `frontend/lib/query/QueryProvider.tsx` (read-only defaults, selective retries, no mutations, health refetch independent)
- [x] T014 Implement URL search state parser/serializer/normalization in `frontend/lib/routing/searchState.ts` with Zod schema in `frontend/lib/validation/searchStateSchema.ts` (parses q, make, model, condition, sellerType, priceMin/Max, kmMin/Max, yearFrom/To, sort, page, limit; omits invalid/empty; range min<=max; page>=1)
- [x] T015 Implement formatting utilities in `frontend/lib/formatting/` (`currency.ts` AED, `mileage.ts` km, `date.ts` absolute, `relativeDate.ts` recency, `number.ts` locale grouping, `emptyValue.ts` consistent placeholder) — deterministic, null-safe, tested
- [x] T016 [P] Implement shared UI primitives in `frontend/components/ui/`: Button, IconButton, Input, SearchInput, Select, RangeInput, Card, Badge, Tag, Divider (semantic tokens, light/dark, accessible, server-compatible where static; Select/SearchInput/RangeInput client)
- [x] T017 [P] Implement shared UI primitives in `frontend/components/ui/`: Spinner, Skeleton, EmptyState, ErrorState, Alert (semantic tokens, light/dark, accessible status announcements)
- [x] T018 [P] Implement shared UI primitives in `frontend/components/ui/`: Pagination, Modal, Drawer, Tooltip, StatusIndicator (client components, focus management, keyboard accessible, semantic tokens, light/dark)
- [x] T019 Implement `ThemeProvider` in `frontend/features/theme/` (light/dark/system modes, system preference detection, persistence of mode only, safe pre-hydration default, no reload on switch) exporting public API via `frontend/features/theme/index.ts`
- [x] T020 Implement application shell in `frontend/components/layout/` (`AppShell.tsx`, `TopNav.tsx`, `Footer.tsx`, `Container.tsx`, `SkipToContent.tsx`) with responsive container, skip-to-content, reserved nav space, no feature-specific data fetching
- [x] T021 Implement `frontend/app/layout.tsx` (global HTML, next/font Inter/Geist, metadata defaults, global providers composition, theme bootstrapping, AppShell wrapping, skip-to-content target)
- [x] T022 Implement `frontend/app/error.tsx` global error boundary (recovery UI, no stack traces, preserves URL search state)
- [x] T023 Implement `frontend/app/not-found.tsx` for unknown routes
- [x] T024 Implement SEO metadata foundation in `frontend/lib/seo/` plus `frontend/app/robots.ts` and `frontend/app/sitemap.ts` (default metadata, favicon, OpenGraph defaults, canonical for `/` and `/listings/[id]`, robots indexing toggle)
- [x] T025 Implement shared constants in `frontend/lib/constants/` (`pagination.ts` default page size, `sort.ts` sort options aligned to Feature 003 enum, `debounce.ts` duration, `breakpoints.ts`, `emptyValue.ts` labels, `health.ts` polling interval, `query.ts` stale/retry defaults, `zIndex.ts`)
- [x] T026 Implement MSW handlers and fixtures in `frontend/test/mocks/` for the five allowed Feature 003 endpoints only (`handlers.ts`, `fixtures/` for success, empty, 400, 404, network failure, offline, missing optional fields, missing image URLs)

**Checkpoint**: Foundation ready — shell, providers, theme, API client, query layer, formatting, shared UI, routing, SEO, error boundary, and test mocks all in place. User story implementation can now begin.

---

## Phase 3: User Story 0 - Establish Application Foundation (Priority: P0)

**Goal**: Deliver a reusable frontend foundation (shell, providers, routing, theme, API client, responsive layout, global error boundary) that all current and future features reuse, testable with no business-specific content.

**Independent Test**: Render the app with no business content and confirm shared shell, top navigation, main content area, footer, theme provider, global providers, routing foundation, API client foundation, responsive layout, and global error boundary are available and reusable.

### Tests for User Story 0

- [ ] T027 [P] [US0] Component test for AppShell/TopNav/Footer rendering and skip-to-content in `frontend/test/component/shell.test.tsx`
- [ ] T028 [P] [US0] Component test for ThemeProvider light/dark/system switching without reload in `frontend/test/component/theme.test.tsx`
- [ ] T029 [P] [US0] Component test for global error boundary recovery in `frontend/test/component/errorBoundary.test.tsx`
- [ ] T030 [P] [US0] Unit test for environment validation in `frontend/test/unit/env.test.ts`

### Implementation for User Story 0

- [ ] T031 [US0] Compose global providers in `frontend/app/providers.tsx` (ThemeProvider + QueryProvider + client-only responsive/route providers) keeping providers generic and free of search logic
- [ ] T032 [US0] Wire `frontend/app/layout.tsx` to providers + AppShell + metadata defaults + theme bootstrapping (no business content)
- [ ] T033 [US0] Add reserved future-navigation space and accessible top nav (logo, Search/Home link to `/`, theme switcher mount point, health indicator mount point) in `frontend/components/layout/TopNav.tsx`
- [ ] T034 [US0] Verify foundation reusability: confirm a minimal placeholder page renders inside the shell using only shared foundations (no feature-specific imports) in `frontend/app/page.tsx` (temporary, replaced in US1)

**Checkpoint**: Application foundation is functional and independently testable. Shell, providers, theme, API client, routing, responsive layout, and error boundary work end-to-end with no business content.

---

## Phase 4: User Story 1 - Search Current Listings (Priority: P1) 🎯 MVP

**Goal**: Users can open the homepage, search listings with free text, refine with filters, choose sort, paginate, clear filters, and return to the same filtered view via the URL.

**Independent Test**: Open homepage, apply a search term and multiple filters, change sort and page, refresh the page, and confirm the same result state is preserved and usable. Browser Back/Forward restores prior states.

### Tests for User Story 1

- [ ] T035 [P] [US1] Unit tests for URL search state parse/serialize/normalize in `frontend/test/unit/searchState.test.ts`
- [ ] T036 [P] [US1] Unit tests for Zod search state schema in `frontend/test/unit/searchStateSchema.test.ts`
- [ ] T037 [P] [US1] Unit test for `search.api.ts` error normalization with MSW in `frontend/test/unit/searchApi.test.ts`
- [ ] T038 [P] [US1] Integration test for home page search journey (text, filters, sort, pagination, clear) with MSW in `frontend/test/integration/homeSearch.test.tsx`
- [ ] T039 [P] [US1] E2E test for search + filters + sort + pagination + Back/Forward in `frontend/test/e2e/search.spec.ts`

### Implementation for User Story 1

- [ ] T040 [P] [US1] Create search types and Zod response schema in `frontend/features/search/types/` and `frontend/features/search/schemas/searchResponseSchema.ts` (ListingSearchRequest, SearchListingsResponse, ListingSearchResult, PaginationMeta per data-model.md)
- [ ] T041 [P] [US1] Implement `search.api.ts` in `frontend/features/search/api/search.api.ts` consuming `GET /api/v1/listings` via shared Axios client with typed request/response
- [ ] T042 [US1] Implement search DTO→UI model mapper in `frontend/features/search/mappers/searchResultMapper.ts` (centralize null handling, naming normalization, fallback labels, image placeholder decisions)
- [ ] T043 [US1] Implement `useSearchResults` hook in `frontend/features/search/hooks/useSearchResults.ts` (TanStack Query keyed by normalized URL state, mapper usage, loading/error derivation)
- [ ] T044 [US1] Implement `useSearchUrlState` hook in `frontend/features/search/hooks/useSearchUrlState.ts` (reads/writes URL query params, debounce for text, filter/sort/page updates, clear filters, history-preserving URL updates)
- [ ] T045 [US1] Implement `SearchToolbar` client component in `frontend/features/search/components/SearchToolbar.tsx` (debounced SearchInput, sort entry point, Clear Filters affordance) using React Hook Form for temporary form interaction only
- [ ] T046 [US1] Implement `FilterSidebar` client component skeleton in `frontend/features/search/components/FilterSidebar.tsx` (make/model/condition/sellerType/price/km/year controls wired to URL state via RHF; options initially static placeholders, upgraded to dynamic metadata in US4)
- [ ] T047 [US1] Implement `ResultsGrid` component in `frontend/features/search/components/ResultsGrid.tsx` rendering skeleton/empty/error/data states (cards rendered via ListingCard from US2; temporary minimal card until US2)
- [ ] T048 [US1] Implement `Pagination` integration in `frontend/features/search/components/SearchPagination.tsx` using backend `PaginationMeta` and URL `page`/`limit`, scroll-to-top on page change
- [ ] T049 [US1] Implement browser Back/Forward synchronization and scroll restoration in `frontend/features/search/hooks/useSearchUrlState.ts` and `frontend/lib/routing/scrollRestore.ts` (history state scroll capture; restore filters/text/page/scroll on return)
- [ ] T050 [US1] Compose `frontend/app/page.tsx` (Server Component) mounting MarketOverview slot (US5), SearchToolbar, FilterSidebar, ResultsGrid, Pagination; no direct Axios calls
- [ ] T051 [US1] Export search feature public API from `frontend/features/search/index.ts` (hooks, components, types needed by pages/other features only)

**Checkpoint**: User Story 1 fully functional — searchable, filterable, sortable, paginated homepage with URL as source of truth and browser navigation working. This is the MVP.

---

## Phase 5: User Story 2 - Browse Listing Cards (Priority: P2)

**Goal**: Users scan consistent listing cards summarizing vehicle, price, seller, location, and recency information with image/fallback, handling loading, empty, and error states.

**Independent Test**: View a result set with multiple listings and confirm each card displays available image, make, model, trim, year, price, mileage, location, seller type, first seen, last seen; verify loading, empty, and error states.

### Tests for User Story 2

- [ ] T052 [P] [US2] Component test for ListingCard with all fields present in `frontend/test/component/listingCard.test.tsx`
- [ ] T053 [P] [US2] Component test for ListingCard with missing optional fields (fallbacks, no misleading data) in `frontend/test/component/listingCardFallbacks.test.tsx`
- [ ] T054 [P] [US2] Component test for ResultsGrid loading/empty/error states in `frontend/test/component/resultsGrid.test.tsx`
- [ ] T055 [P] [US2] Unit tests for listing card mapper null handling in `frontend/test/unit/listingCardMapper.test.ts`

### Implementation for User Story 2

- [ ] T056 [P] [US2] Implement listing card UI model type and mapper in `frontend/features/listings/mappers/listingCardMapper.ts` and `frontend/features/listings/types/ListingCardModel.ts` (currency/mileage/date/relative-date/empty formatting via shared formatting utils; image placeholder decision; external URL validation)
- [ ] T057 [US2] Implement `ListingCard` component in `frontend/features/listings/components/ListingCard.tsx` (image/fallback with fixed aspect ratio, make/model/trim/year/price/mileage/location/sellerType/firstSeen/lastSeen, keyboard focus, clickable target linking to `/listings/[id]` preserving return state)
- [ ] T058 [US2] Implement `ListingCardSkeleton` in `frontend/features/listings/components/ListingCardSkeleton.tsx` preserving card dimensions
- [ ] T059 [US2] Implement image placeholder/fallback in `frontend/features/listings/components/ListingImage.tsx` (fixed aspect ratio, skeleton while loading, accessible alt text that does not imply a real photo, surface `photosCount` as metadata only)
- [ ] T060 [US2] Wire `ResultsGrid` (from US1) to render `ListingCard`/`ListingCardSkeleton`/`EmptyState`/`ErrorState` based on query state
- [ ] T061 [US2] Export listings feature public API from `frontend/features/listings/index.ts`

**Checkpoint**: User Stories 1 AND 2 work independently — searchable homepage with rich, consistent, accessible listing cards and scoped loading/empty/error states.

---

## Phase 6: User Story 3 - View Listing Details (Priority: P2)

**Goal**: Users select a listing and open a dedicated detail page showing all available information with a way to open the original marketplace listing.

**Independent Test**: Open a listing from search results and confirm the detail page displays the complete available record, a working external listing action, not-found/error handling, and restoration of filters/text/pagination/scroll on return.

### Tests for User Story 3

- [ ] T062 [P] [US3] Unit test for listing detail mapper (grouping, fallbacks, unknown `specs` keys) in `frontend/test/unit/listingDetailMapper.test.ts`
- [ ] T063 [P] [US3] Unit test for `listings.api.ts` (success, 404, network failure) with MSW in `frontend/test/unit/listingsApi.test.ts`
- [ ] T064 [P] [US3] Integration test for detail page composition with mocked response in `frontend/test/integration/listingDetail.test.tsx`
- [ ] T065 [P] [US3] E2E test for open detail + return restores state + scroll in `frontend/test/e2e/listingDetail.spec.ts`
- [ ] T066 [P] [US3] Component test for Marketplace Action hidden/disabled when URL missing/invalid in `frontend/test/component/marketplaceAction.test.tsx`

### Implementation for User Story 3

- [ ] T067 [P] [US3] Create listing detail types and Zod response schema in `frontend/features/listings/types/` and `frontend/features/listings/schemas/listingDetailSchema.ts` (ListingDetailResponse per data-model.md)
- [ ] T068 [P] [US3] Implement `listings.api.ts` in `frontend/features/listings/api/listings.api.ts` consuming `GET /api/v1/listings/:id` via shared Axios client
- [ ] T069 [US3] Implement listing detail DTO→UI model mapper in `frontend/features/listings/mappers/listingDetailMapper.ts` (grouping into gallery/summary/specifications/seller-source, safe fallbacks, unknown `specs` keys as additional specifications)
- [ ] T070 [US3] Implement `useListingDetail` hook in `frontend/features/listings/hooks/useListingDetail.ts` (TanStack Query keyed by normalized id, mapper usage, 404→not-found handling)
- [ ] T071 [US3] Implement `ImageGallery` in `frontend/features/listings/components/ImageGallery.tsx` (placeholder/fallback visuals, fixed aspect ratio, skeleton; ready for future image URLs)
- [ ] T072 [US3] Implement `VehicleSummary` in `frontend/features/listings/components/VehicleSummary.tsx` (make/model/trim/year/price/mileage/condition/location/sellerType/recency with formatting utils)
- [ ] T073 [US3] Implement `VehicleSpecifications` in `frontend/features/listings/components/VehicleSpecifications.tsx` (all additional available fields with labels, grouped display)
- [ ] T074 [US3] Implement `MarketplaceAction` in `frontend/features/listings/components/MarketplaceAction.tsx` (validates `url`, opens original listing in new browser context, hidden/disabled when missing/invalid, safe external link)
- [ ] T075 [US3] Implement `frontend/app/listings/[id]/page.tsx` (Server Component) composing gallery/summary/specifications/marketplace action via `useListingDetail`; no direct Axios
- [ ] T076 [US3] Implement `frontend/app/listings/[id]/loading.tsx` detail skeleton and `frontend/app/listings/[id]/error.tsx` scoped detail error boundary
- [ ] T077 [US3] Implement listing-not-found UX for 404 responses and missing detail data (recoverable error state with path back to search)
- [ ] T078 [US3] Implement scroll restoration on return to search (capture scroll on card click, restore on back navigation) in `frontend/lib/routing/scrollRestore.ts`

**Checkpoint**: User Stories 1, 2, AND 3 work independently — full search → card → detail → return journey with state and scroll preserved.

---

## Phase 7: User Story 4 - Use Dynamic Filters (Priority: P3)

**Goal**: Filter options and numeric ranges derive from current listing metadata rather than fixed values, keeping filters accurate as inventory changes.

**Independent Test**: Load the homepage with known filter metadata and confirm dropdowns and ranges reflect available makes, models, conditions, seller types, and numeric bounds; dependent model options update with make; filter failure shows scoped error without blocking search.

### Tests for User Story 4

- [ ] T079 [P] [US4] Unit test for `filters.api.ts` with MSW in `frontend/test/unit/filtersApi.test.ts`
- [ ] T080 [P] [US4] Unit test for filter metadata mapper in `frontend/test/unit/filterMetadataMapper.test.ts`
- [ ] T081 [P] [US4] Integration test for dynamic filter population and dependent model behavior in `frontend/test/integration/dynamicFilters.test.tsx`
- [ ] T082 [P] [US4] Component test for filter scoped error state (metadata failure keeps search usable) in `frontend/test/component/filterError.test.tsx`

### Implementation for User Story 4

- [ ] T083 [P] [US4] Create filter metadata types and Zod schema in `frontend/features/filters/types/` and `frontend/features/filters/schemas/filterMetadataSchema.ts` (FilterMetadataResponse, NumericRange per data-model.md)
- [ ] T084 [P] [US4] Implement `filters.api.ts` in `frontend/features/filters/api/filters.api.ts` consuming `GET /api/v1/listings/filters`
- [ ] T085 [US4] Implement filter metadata DTO→UI model mapper in `frontend/features/filters/mappers/filterMetadataMapper.ts` (makes, models by make, price/year/km ranges, conditions, sellerTypes; null bounds softening)
- [ ] T086 [US4] Implement `useFilterMetadata` hook in `frontend/features/filters/hooks/useFilterMetadata.ts` (TanStack Query, stable key, scoped error state)
- [ ] T087 [US4] Upgrade `FilterSidebar` (from US1) to populate all controls from dynamic metadata; dependent model options limited by selected make; range controls validate min<=max before URL update
- [ ] T088 [US4] Implement `FilterSkeleton` and scoped filter error state inside `FilterSidebar` (search remains usable when metadata fails)
- [ ] T089 [US4] Implement mobile filter `Drawer` integration (focus trap, Escape close, focus restore to trigger, screen-reader accessible) using shared `Drawer` from `frontend/components/ui/Drawer.tsx`
- [ ] T090 [US4] Export filters feature public API from `frontend/features/filters/index.ts`

**Checkpoint**: Filters are now dynamic, accessible, and resilient; search remains usable even when filter metadata fails.

---

## Phase 8: User Story 5 - View Market Overview (Priority: P3)

**Goal**: Users view a concise inventory summary (total listings, used, new, makes, models, average price, last updated) at a glance.

**Independent Test**: Open the homepage and confirm summary metrics appear, are labeled clearly, show loading placeholders, and communicate unavailability gracefully when stats fail.

### Tests for User Story 5

- [ ] T091 [P] [US5] Unit test for `stats.api.ts` with MSW in `frontend/test/unit/statsApi.test.ts`
- [ ] T092 [P] [US5] Unit test for stats mapper (null average price, missing last updated) in `frontend/test/unit/statsMapper.test.ts`
- [ ] T093 [P] [US5] Component test for MarketOverview loading/empty/error/data states in `frontend/test/component/marketOverview.test.tsx`

### Implementation for User Story 5

- [ ] T094 [P] [US5] Create stats types and Zod schema in `frontend/features/stats/types/` and `frontend/features/stats/schemas/statsSchema.ts` (InventoryStatsResponse per data-model.md)
- [ ] T095 [P] [US5] Implement `stats.api.ts` in `frontend/features/stats/api/stats.api.ts` consuming `GET /api/v1/stats`
- [ ] T096 [US5] Implement stats DTO→UI model mapper in `frontend/features/stats/mappers/statsMapper.ts` (formatting via shared utils; null-safe average price and last updated)
- [ ] T097 [US5] Implement `useMarketStats` hook in `frontend/features/stats/hooks/useMarketStats.ts` (TanStack Query, stable key, scoped loading/error)
- [ ] T098 [US5] Implement `MarketOverview` component in `frontend/features/stats/components/MarketOverview.tsx` (total, used, new, makes, models, average price, last updated; `SummarySkeleton`; scoped `ErrorState`; missing values via formatting utils not hard-coded placeholders)
- [ ] T099 [US5] Mount `MarketOverview` in `frontend/app/page.tsx` (independent of search/results; one section's loading/error does not block others)
- [ ] T100 [US5] Export stats feature public API from `frontend/features/stats/index.ts`

**Checkpoint**: Market Overview renders independently and degrades gracefully without blocking search.

---

## Phase 9: User Story 6 - Monitor Backend Availability (Priority: P4)

**Goal**: Users see whether the underlying listing service is available so they understand whether stale, missing, or failed data may be temporary.

**Independent Test**: Simulate available and unavailable service states and confirm the indicator changes without blocking normal page interaction or keyboard navigation.

### Tests for User Story 6

- [ ] T101 [P] [US6] Unit test for `health.api.ts` (ok, failure, timeout) with MSW in `frontend/test/unit/healthApi.test.ts`
- [ ] T102 [P] [US6] Component test for StatusIndicator available/unavailable/degraded states + announcements in `frontend/test/component/statusIndicator.test.tsx`
- [ ] T103 [P] [US6] Integration test for health polling independence from search/stats in `frontend/test/integration/healthPolling.test.tsx`

### Implementation for User Story 6

- [ ] T104 [P] [US6] Create health types and Zod schema in `frontend/features/health/types/` and `frontend/features/health/schemas/healthSchema.ts` (HealthResponse `{ status: "ok" }` per data-model.md)
- [ ] T105 [P] [US6] Implement `health.api.ts` in `frontend/features/health/api/health.api.ts` consuming `GET /api/v1/health`; request failure/timeout → unavailable
- [ ] T106 [US6] Implement health DTO→availability mapper in `frontend/features/health/mappers/healthMapper.ts` (BackendAvailability: checking/available/unavailable/degraded)
- [ ] T107 [US6] Implement `useBackendHealth` hook in `frontend/features/health/hooks/useBackendHealth.ts` (TanStack Query with periodic refetch, independent of other queries)
- [ ] T108 [US6] Mount `StatusIndicator` in `frontend/components/layout/TopNav.tsx` using `useBackendHealth`; accessible text for available/unavailable/degraded; non-blocking
- [ ] T109 [US6] Export health feature public API from `frontend/features/health/index.ts`

**Checkpoint**: All user stories (US0–US6) are independently functional. Backend availability is visible and does not interrupt search or keyboard navigation.

---

## Phase 10: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories and final hardening before delivery.

- [ ] T110 [P] Accessibility pass: keyboard-only flows, focus management on route changes/drawer/error recovery, ARIA labels, status announcements, visible focus in both themes in `frontend/features/**` and `frontend/components/**`
- [ ] T111 [P] Responsive pass: verify no horizontal scrolling and correct filter sidebar/drawer behavior at desktop/laptop/tablet/mobile breakpoints in `frontend/test/e2e/responsive.spec.ts`
- [ ] T112 [P] Theme pass: light/dark/system coverage for shell, forms, cards, drawers, modals, tooltips, skeletons, empty/error states, status indicators in `frontend/test/component/themeCoverage.test.tsx`
- [ ] T113 [P] Performance pass: review build output for bundle growth, confirm client islands are minimal, lazy-load mobile filter drawer/modal dialogs where practical, Lucide icons imported selectively in `frontend/` build config
- [ ] T114 [P] SEO/metadata polish: home page metadata, listing detail dynamic metadata with safe fallbacks, canonical URLs, robots/sitemap validation in `frontend/lib/seo/` and `frontend/app/robots.ts`/`sitemap.ts`
- [ ] T115 [P] Error-state pass: network failures per endpoint, backend offline via health, empty results, listing 404, unexpected UI error isolation, retry + Clear Filters accessibility in `frontend/test/e2e/errorStates.spec.ts`
- [ ] T116 Document frontend integration limitations (missing image URLs, minimal health payload, missing optional fields) in `frontend/INTEGRATION.md` per spec FR-021
- [ ] T117 Run `frontend/quickstart.md` manual verification flow end-to-end
- [ ] T118 Final lint, type-check, build, unit/component/integration/E2E run from `frontend/`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — can start immediately.
- **Foundational (Phase 2)**: Depends on Phase 1 — BLOCKS all user stories.
- **US0 (Phase 3, P0)**: Depends on Phase 2 — formalizes the foundation as a testable increment.
- **US1 (Phase 4, P1)**: Depends on Phase 2 + US0 — MVP search journey.
- **US2 (Phase 5, P2)**: Depends on US1 (ResultsGrid mount point) — cards rendered inside US1's grid.
- **US3 (Phase 6, P2)**: Depends on US1 + US2 (card link target + return state) — detail page.
- **US4 (Phase 7, P3)**: Depends on US1 (FilterSidebar skeleton) — upgrades static filters to dynamic.
- **US5 (Phase 8, P3)**: Depends on US0 (page composition slot) — independent of US1.
- **US6 (Phase 9, P4)**: Depends on US0 (TopNav slot) — independent of search.
- **Polish (Phase 10)**: Depends on all desired user stories being complete.

### User Story Dependencies

- **US0 (P0)**: After Foundational. No other-story dependencies.
- **US1 (P1)**: After Foundational + US0. No dependencies on other stories (uses minimal placeholder card until US2).
- **US2 (P2)**: After US1. Integrates into US1's ResultsGrid.
- **US3 (P2)**: After US1 + US2. Uses listings feature shared with US2.
- **US4 (P3)**: After US1. Replaces static filter options with dynamic metadata.
- **US5 (P3)**: After US0. Fully independent of search/results.
- **US6 (P4)**: After US0. Fully independent of search/stats.

### Within Each User Story

- Tests (if included) written and FAIL before implementation
- Types/schemas before API modules
- API modules before hooks
- Mappers before hooks/components
- Hooks before feature components
- Feature components before page composition
- Story complete before next priority

### Parallel Opportunities

- All Setup tasks marked [P] (T003–T008) run in parallel.
- Foundational shared UI primitives (T016–T018) run in parallel.
- Within a story, types/schemas + API modules marked [P] run in parallel.
- US5 and US6 can run in parallel with US1/US2/US3/US4 (independent of search) once Foundational + US0 are done.
- Polish tasks (T110–T115) run in parallel across dimensions.

---

## Parallel Example: User Story 1

```bash
# Launch all US1 tests together:
Task: "Unit tests for URL search state in frontend/test/unit/searchState.test.ts"
Task: "Unit tests for Zod search state schema in frontend/test/unit/searchStateSchema.test.ts"
Task: "Unit test for search.api.ts with MSW in frontend/test/unit/searchApi.test.ts"

# Launch US1 types + schema + API module together (different files):
Task: "Create search types and Zod response schema in frontend/features/search/types/ and schemas/"
Task: "Implement search.api.ts in frontend/features/search/api/search.api.ts"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL — blocks all stories)
3. Complete Phase 3: US0 (foundation verified)
4. Complete Phase 4: US1 (searchable homepage with URL state + browser nav)
5. **STOP and VALIDATE**: Test US1 independently (search, filters, sort, pagination, Back/Forward, refresh)
6. Deploy/demo if ready

### Incremental Delivery

1. Setup + Foundational + US0 → Foundation ready
2. Add US1 → Test independently → Deploy/Demo (**MVP!**)
3. Add US2 → Rich listing cards → Deploy/Demo
4. Add US3 → Listing detail + return restoration → Deploy/Demo
5. Add US4 → Dynamic filters → Deploy/Demo
6. Add US5 → Market Overview → Deploy/Demo
7. Add US6 → Backend availability indicator → Deploy/Demo
8. Polish → Final hardening → Release

### Parallel Team Strategy

With multiple developers after Foundational + US0:

- Developer A: US1 → US2 → US3 (search/card/detail chain)
- Developer B: US5 (Market Overview, independent)
- Developer C: US6 (Health, independent)
- US4 follows US1 with the same developer or a teammate

---

## Notes

- [P] tasks = different files, no dependencies on incomplete tasks
- [Story] label maps task to specific user story for traceability
- Each user story is independently completable and testable
- Verify tests fail before implementing
- Commit after each task or logical group
- Stop at any checkpoint to validate a story independently
- Feature internals are private unless exported via the feature's `index.ts`; cross-feature imports go through feature root public APIs only
- Backend (Feature 003) is consumed as-is; never modified. Missing optional fields use safe UI fallbacks and are documented in `frontend/INTEGRATION.md`
- Avoid: vague tasks, same-file conflicts, cross-story dependencies that break independence, direct Axios calls from pages, leaking backend DTOs into deep components
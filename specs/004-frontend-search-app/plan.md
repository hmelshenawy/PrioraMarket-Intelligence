# Implementation Plan: Frontend Search Application

**Branch**: `003-backend-search-api` | **Date**: 2026-07-04 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `specs/004-frontend-search-app/spec.md`

## Summary

Feature 004 creates the first production PrioraMarket frontend and establishes the reusable frontend foundation for future features. The application will be a frontend-only Next.js App Router application that consumes the existing Feature 003 Backend Search API through typed API modules. It will provide search, dynamic filters, sorting, pagination, listing details, Market Overview metrics, backend health status, light/dark/system themes, responsive layouts, accessible UX patterns, reusable design system components, and shared frontend standards without changing backend contracts.

The implementation approach is layered: Pages → Layouts → Feature Components → Shared UI Components → Custom Hooks → Typed API Layer → Feature 003 Backend API. Pages must never call Axios directly. Business-relevant search, filter, sort, and pagination behavior remains backend-driven; the frontend manages presentation, URL state, forms, accessibility, formatting, loading, and error handling.

The current plan is strong enough to produce a working frontend, but the additional boundaries in this revision are necessary to keep the frontend maintainable as PrioraMarket adds future features. Without explicit rendering, mapping, query-key, constants, environment, and feature-public-API decisions, Feature 004 could still function initially but would be more likely to accumulate hidden coupling, cache fragmentation, duplicated null handling, and broad `use client` usage as the frontend grows.

## Data Flow Reference

```text
URL Query Params
→ URL State Parser
→ Feature Hook
→ TanStack Query
→ Typed API Client
→ Feature 003 Backend API
→ DTO Mapper
→ UI Model
→ Feature Components
```

- URL query parameters remain the source of truth for search state.
- Feature hooks orchestrate state parsing, query key selection, data fetching, loading, error, and mapper usage.
- Typed API modules return backend DTOs that match Feature 003 contracts.
- DTO mappers convert backend DTOs into frontend-safe UI models before data reaches feature components.
- Feature components render UI models and do not normalize backend response shapes themselves.

## Technical Context

**Language/Version**: TypeScript 5.x with React and Next.js latest stable App Router.

**Primary Dependencies**: Next.js App Router, React, Tailwind CSS, TanStack Query, React Hook Form, Zod, Axios, Lucide icons, next/font using Inter or Geist, ESLint, Prettier.

**Storage**: No application database or persisted business data. Browser storage is limited to non-sensitive theme preference. Search state is persisted in URL query parameters only.

**Testing**: Vitest or Jest for unit tests, React Testing Library for component and integration tests, Playwright for end-to-end, responsive, theme, and browser navigation tests. Accessibility checks should use Testing Library queries, jest-dom assertions, Playwright accessibility-oriented checks, and axe-compatible tooling where configured.

**Target Platform**: Web browsers on desktop, laptop, tablet, and mobile. Desktop is the primary UX target; mobile must remain fully usable.

**Project Type**: Frontend web application added alongside the existing backend project.

**Performance Goals**: 95% of ordinary searches present a usable loading, result, empty, or error state within 2 seconds on typical broadband; theme switching occurs without reload; pagination and filter changes update without full page refresh; mobile layouts avoid horizontal scrolling.

**Constraints**: Frontend-only; no scraper, ingestion, replay, backend contract, authentication, account, favorites, saved search, compare, AI recommendation, admin, listing creation, listing editing, WebSocket, or background job work. Existing Feature 003 endpoints and response shapes are consumed as-is. Missing optional backend fields must use safe UI fallbacks and be documented as integration limitations.

**Scale/Scope**: Two routes for Feature 004: `/` and `/listings/[id]`. The foundation includes app shell, global providers, theme architecture, design system, typed API layer, feature-based organization, formatting utilities, SEO metadata foundation, loading/error patterns, and test strategy for future frontend features.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Gate 1: Pre-Research

- **I. Documentation First**: PASS. The plan is generated from the approved Feature 004 specification and records frontend architecture before implementation.
- **II. Design Before Implementation**: PASS. This is planning only; no implementation code or task list is generated.
- **III. Domain-Driven Architecture**: PASS. Frontend feature areas align to search, listings, filters, stats, health, theme, and shared foundations without crossing backend bounded-context internals.
- **IV. Clean Layered Architecture**: PASS. Frontend layers are explicitly separated, and pages cannot call Axios directly.
- **V. API First**: PASS. The frontend consumes only versioned Feature 003 REST APIs.
- **VI. Database as Source of Truth**: PASS. The frontend reads backend API data only and never calls external marketplaces for search or analytics.
- **VII. Historical Data Preservation**: PASS. No writes, migrations, or data mutation are introduced.
- **VIII. AI Assists, Never Invents**: PASS. No AI functionality is introduced.
- **IX. Analytics Before AI**: PASS. Market Overview metrics are consumed from deterministic backend stats, not inferred client-side.
- **X. Machine Learning as a Product Feature**: PASS. No ML functionality is introduced.
- **XI. Data Quality Before Intelligence**: PASS. The frontend preserves backend-provided nullability and exposes safe empty-value states rather than inventing values.
- **XII. Scalability by Design**: PASS. Shared shell, design system, API layer, and feature-based organization support future features without redesign.
- **XIII. Backend-Centric Business Logic**: PASS. Search, filtering, sorting, pagination, and stats remain backend responsibilities; the frontend sends criteria and renders responses.
- **XIV. Modularity**: PASS. Feature modules communicate through typed contracts and shared foundations; shared UI does not depend on feature-specific logic.
- **XV. Security by Default**: PASS. No secrets in code; environment-driven API base URL; no auth/account scope; safe external links; no sensitive data persisted.
- **XVI. Simplicity Over Complexity**: PASS. Scope is limited to two routes and reusable foundations needed by the approved spec.

### Gate 2: Post-Design Recheck

- **Status**: PASS. Phase 0 and Phase 1 artifacts preserve the same constraints. No constitution violations require Complexity Tracking.

## Project Structure

### Documentation (this feature)

```text
specs/004-frontend-search-app/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   ├── api-client-contract.md
│   ├── routes-and-state-contract.md
│   └── ui-contract.md
└── tasks.md
```

`tasks.md` is intentionally not created by this planning phase.

**Documentation Scope Decision**: Keep contracts documentation only where it directly guides implementation: API client boundaries, route/state behavior, and shared UI expectations. Avoid adding additional planning files that duplicate the approved specification or this plan. Future task generation should reference this plan and the existing contracts instead of creating bureaucratic intermediate documents.

### Source Code (repository root)

```text
backend/
└── existing Feature 003 backend application

frontend/
├── app/
│   ├── layout.tsx
│   ├── page.tsx
│   ├── error.tsx
│   ├── not-found.tsx
│   ├── robots.ts
│   ├── sitemap.ts
│   └── listings/
│       └── [id]/
│           ├── page.tsx
│           ├── loading.tsx
│           └── error.tsx
├── features/
│   ├── search/
│   ├── listings/
│   ├── filters/
│   ├── stats/
│   ├── health/
│   ├── theme/
│   └── shared/
├── lib/
│   ├── api/
│   ├── constants/
│   ├── config/
│   ├── formatting/
│   ├── mappers/
│   ├── query/
│   ├── routing/
│   ├── seo/
│   └── validation/
├── components/
│   ├── layout/
│   └── ui/
├── styles/
├── test/
│   ├── unit/
│   ├── component/
│   ├── integration/
│   ├── e2e/
│   ├── fixtures/
│   └── mocks/
└── public/
```

**Structure Decision**: Add a dedicated `frontend/` application beside the existing `backend/` project. Use Next.js App Router under `frontend/app`, feature-based modules under `frontend/features`, centralized cross-cutting utilities under `frontend/lib`, and reusable shell/UI components under `frontend/components`. This preserves backend isolation and keeps frontend foundations reusable for future features.

## Feature Public API Boundaries

- Each feature folder exposes approved public exports through its own `index.ts`.
- Other features must import from the feature root public API, not deep internal paths such as `features/search/internal/...`.
- Internal hooks, mappers, components, schemas, and helpers remain private unless explicitly exported from the feature root.
- Shared UI components must never import feature-specific modules.
- Shared foundations may be imported by features, but shared foundations must not depend on features.
- This boundary is required for refactoring safety, clearer ownership, and prevention of hidden feature coupling.

## Next.js App Router Structure

- `app/layout.tsx` owns global HTML structure, font setup, metadata defaults, global providers, theme bootstrapping, and application shell wrapping.
- `app/page.tsx` is the search homepage route at `/` and composes feature components only; it does not call Axios.
- `app/listings/[id]/page.tsx` is the listing detail route and loads detail state through listing hooks/API modules.
- `app/error.tsx` is the global route-level recovery UI for unexpected UI errors.
- `app/not-found.tsx` handles unknown application routes and missing listing detail flows where applicable.
- `app/listings/[id]/loading.tsx` provides route-level detail skeleton behavior.
- `app/robots.ts` and `app/sitemap.ts` establish metadata compatibility without adding backend requirements.

## Rendering Strategy: Server Components Vs Client Components

- Default to Server Components for route files, layouts, static shell structure, static metadata, SEO defaults, robots/sitemap metadata routes, mostly static footer content, and non-interactive layout composition.
- Use Client Components only where browser interactivity or client-only state is required.
- Client Components are required for interactive search controls, debounced search input, dynamic filter controls, pagination controls, theme switcher, mobile filter drawer, modal/drawer focus management, TanStack Query hooks, browser Back/Forward synchronization, scroll restoration, and other browser-only behavior.
- Avoid placing `use client` at broad route or layout boundaries unless the whole boundary truly needs client behavior.
- Prefer small client islands inside server-rendered page structure so static shell, metadata, and layout can remain server-rendered where possible.
- Feature hooks that use TanStack Query, browser APIs, URL mutation, media queries, or local interactive state are client-only and should be consumed by client feature components.
- Presentational shared UI components may be server-compatible when they are static; interactive variants such as Select, Drawer, Modal, Tooltip, SearchInput, and Pagination are client components.

## Application Shell

- The shell wraps all current and future pages.
- It includes global app layout, top navigation, main content area, footer, responsive container, consistent spacing, and breakpoint-aware layout behavior.
- The shell must be visually neutral enough to support future features while optimized for an automotive marketplace feel.
- The shell must expose skip-to-content behavior for keyboard and screen reader users.
- The shell must not contain feature-specific data fetching beyond reusable health/theme/navigation behavior.

## Top Navigation

- Includes PrioraMarket logo and brand mark.
- Includes Search/Home navigation linked to `/`.
- Includes a theme switcher for light, dark, and system modes.
- Includes backend availability indicator sourced from the health feature hook.
- Includes reserved layout space for future navigation items without implementing future features.
- Must remain accessible on desktop, laptop, tablet, and mobile.

## Footer

- Provides a consistent end-of-page landmark and lightweight product context.
- May include product name, current year, non-interactive metadata, and future reserved link space.
- Must not introduce account, admin, or marketplace-management capabilities.

## Theme Architecture

- Use a `ThemeProvider` in the global providers layer.
- Supported modes: `light`, `dark`, and `system`.
- Theme state is presentation-only and may persist in browser storage.
- System mode tracks the user's operating system/browser color-scheme preference.
- Theme changes update the document theme without reloading the page.
- Design tokens must define color roles for both themes rather than hard-coded component colors.

## Light, Dark, And System Theme Behavior

- Light theme is optimized for high-contrast marketplace browsing in bright environments.
- Dark theme is a required deliverable, not a placeholder, and must cover shell, navigation, forms, cards, drawers, modals, tooltips, skeletons, empty states, error states, and status indicators.
- System theme delegates active appearance to the user's system preference and updates when that preference changes.
- Components must not assume one theme; they consume semantic tokens.

## Theme Persistence

- Persist only the selected mode: `light`, `dark`, or `system`.
- Do not persist search state in browser storage; search state belongs in the URL.
- Use a safe default before hydration to avoid unreadable flashes.
- Persistence failure should fall back to system or light mode without breaking the app.

## Global Providers

- Global providers are composed once near the app root.
- Required providers: ThemeProvider, TanStack Query provider, error boundary integration, and any client-only provider needed for responsive or route interaction behavior.
- Providers must remain generic and reusable by future features.
- Providers must not contain search-specific business logic.

## TanStack Query Provider Setup

- Configure a shared QueryClient with sensible defaults for read-only API data.
- Use distinct query keys by feature area: listings, listing detail, filters, stats, and health.
- Disable mutation patterns for Feature 004 because all consumed capabilities are read-only.
- Use retries selectively: short retry for transient network failures, no aggressive retry for 400/404 responses.
- Health query should refetch periodically and remain independent from search/listing queries.
- Query errors are normalized before reaching UI components.

## Query Key Factory

- Use centralized query key factories instead of ad hoc query key strings or inline arrays.
- Define query keys for listings search, listing detail, filter metadata, market stats, and health.
- Listings search keys are derived from normalized URL state, not raw query parameter order or unvalidated values.
- Listing detail keys are derived from the normalized listing id.
- Filter metadata, market stats, and health keys have stable feature-scoped keys.
- Query key factories prevent accidental cache fragmentation, make invalidation/refetch behavior predictable, and keep tests consistent.
- Query key factories live in the relevant feature module or shared query utility and are exported only through approved feature public APIs when needed.

## API Client Setup

- Create a centralized Axios instance in the typed API layer.
- API base URL comes from environment configuration and defaults safely for local development.
- The client owns request timeout, base path, JSON handling, and error normalization.
- Do not attach secrets or authentication headers for Feature 004.
- Do not call external marketplace URLs except when the user explicitly opens an original listing link in a new browser context.

## API Module Boundaries

- `search.api.ts`: consumes `GET /api/v1/listings` for paginated search results.
- `listings.api.ts`: consumes `GET /api/v1/listings/:id` for detail pages.
- `filters.api.ts`: consumes `GET /api/v1/listings/filters` for dynamic filter metadata.
- `stats.api.ts`: consumes `GET /api/v1/stats` for Market Overview metrics.
- `health.api.ts`: consumes `GET /api/v1/health` for backend availability.
- Modules expose typed functions and request/response models; UI components and pages do not import Axios.

## Typed Request And Response Models

- Models are TypeScript types derived from Feature 003 OpenAPI semantics and validated where appropriate with Zod at trust boundaries.
- Search request supports `q`, `condition`, `make`, `model`, `yearFrom`, `yearTo`, `priceMin`, `priceMax`, `kmMin`, `kmMax`, `location`, `sellerType`, `page`, `limit`, and `sort`.
- Search response contains `data` listing results and `meta` pagination data.
- Listing result/detail models preserve nullable backend fields.
- Filter metadata model includes makes, models by make, price/year/km ranges, conditions, and seller types.
- Stats model includes total listings, used listings, new listings, total makes, total models, average/min/max AED price, and last updated timestamp.
- Health model supports the existing `{ status: "ok" }` shape and treats request failure as unavailable.

## DTO To Mapper To UI Model Layer

- API modules return backend DTOs that match Feature 003 response contracts.
- Backend DTO shapes must not leak directly into deeply nested UI components.
- Feature mappers convert DTOs into frontend-safe UI models for listing cards, listing details, filters, Market Overview, pagination, and backend availability.
- Mappers centralize null handling, naming normalization, fallback labels, external URL validation, display grouping, and image placeholder decisions.
- UI models should contain values ready for rendering, including safe fallback values where appropriate.
- Presentational components consume UI models and avoid inspecting backend-specific nullability or raw DTO details.
- Formatting utilities remain separate from mappers; mappers may call formatting utilities or prepare raw display fields according to feature needs.
- If a backend field is missing from Feature 003, the mapper produces a safe fallback and the limitation is documented rather than requiring backend changes.

## Search State URL Synchronization

- URL query parameters are the single source of truth for search state.
- Supported URL state: text query, make, model, condition, seller type, price range, mileage range, year range, sort, page, and limit.
- Invalid values are normalized or omitted before API requests.
- Clearing filters removes filter parameters and returns sort/page defaults.
- URL updates should preserve browser history naturally for meaningful user navigation.

## Browser Back/Forward Behavior

- Browser Back restores the previous URL search state and refreshes visible UI from that state.
- Browser Forward restores the next URL search state.
- No hidden global state is required to reconstruct filters, sort, pagination, or search text.
- Query keys must be derived from normalized URL state so browser navigation triggers the correct data request.

## Scroll Restoration Behavior

- Changing result pages scrolls to the top of the result area or page content.
- Opening a listing from search results records the current scroll position in browser history state or an equivalent route-scoped mechanism.
- Returning from detail restores filters, search text, pagination, and scroll position.
- Scroll restoration must not depend on backend state and must degrade safely if the browser cannot restore it.

## Search Interaction Behavior

- Initial page load reads URL state and requests data immediately.
- Text search changes use a short debounce before URL/API refresh.
- Filter changes refresh automatically and reset page to 1 unless the changed control is pagination.
- Sort changes refresh automatically and reset page to 1.
- Pagination changes load the requested page automatically and scroll to top.
- No explicit Search button is required after the initial page, but forms must remain accessible and keyboard-friendly.

## Debounced Text Search

- Debounce applies to free-text changes only.
- Debounce duration should balance responsiveness and request volume, with a target around typical web-search interactions.
- The visible input updates immediately; URL/API state updates after the debounce interval.
- Clearing text should update promptly and return to non-text search results.

## Auto-Refresh Filters And Sort Changes

- Filter controls update URL state directly after valid selection.
- Range controls validate min/max before updating URL state.
- Dependent model choices should update when make changes based on filter metadata.
- Sort changes map UI labels to backend sort enum values.

## Pagination Behavior

- Pagination uses backend pagination metadata.
- Page numbers outside available bounds are normalized to valid values or show an empty/error-safe state.
- Page size defaults to the backend default unless explicitly exposed later.
- Pagination must be keyboard accessible and screen-reader understandable.

## Design System Strategy

- Establish shared UI components before building feature-specific compositions.
- Components use semantic design tokens and support light/dark themes.
- Components expose accessible defaults and allow feature-level composition without embedding feature logic.
- Components should be documented through tests and predictable props rather than ad hoc styling.

## Design Tokens

- Colors: background, surface, elevated surface, text, muted text, border, accent, success, warning, danger, focus, skeleton, overlay.
- Typography: font family, heading sizes, body sizes, label sizes, line heights, weights.
- Spacing: consistent scale for shell, sections, cards, controls, gaps, and responsive containers.
- Border radius: control, card, modal/drawer, pill/tag.
- Shadows: card, dropdown, drawer, modal, focus ring where appropriate.
- Z-index: navigation, dropdown, tooltip, drawer, modal, toast/alert if introduced later.
- Transitions: color, background, transform, opacity, drawer/modal entrance, focus states.
- Breakpoints: mobile below 768px, tablet 768-1023px, laptop 1024-1279px, desktop 1280px and wider.

## Constants Strategy

- Centralize reusable constants in shared constants modules or clearly owned feature constants files.
- Constants include default page size, supported sort options, debounce duration, responsive breakpoints, empty value labels, health polling interval, query stale times, retry defaults, and z-index levels where applicable.
- Avoid magic numbers, repeated string literals, and duplicated enum-like lists inside components.
- Backend enum mappings, such as sort options, must stay aligned with Feature 003 contracts.
- Constants that are part of public feature behavior should be exported through the feature public API; private constants remain internal.

## Component Composition Rules

- Pages compose layouts and feature components.
- Layouts provide shell and responsive structure; they do not contain feature-specific search logic.
- Feature components compose shared UI components and feature hooks.
- Shared UI components use design tokens and must not import feature modules.
- API modules are not called directly from pages.
- Feature modules should not depend on unrelated feature modules.
- Formatting logic stays in formatting utilities, not inside components.
- Backend response fallback decisions are centralized in mappers or formatting utilities where possible.

## Component Responsibility Rules

- Components should remain small, composable, and focused on rendering or local interaction.
- Presentational components must avoid business logic, API calls, backend DTO normalization, and cross-feature orchestration.
- Feature hooks own state/data orchestration, including URL state, TanStack Query usage, mappers, loading/error derivation, and browser-only behavior.
- Avoid prop drilling beyond reasonable depth; introduce feature composition components or context only when it reduces coupling and remains feature-scoped.
- Shared components stay generic and reusable, with no imports from feature modules.
- Feature components can compose shared UI components and feature hooks but should not import unrelated feature internals.
- Complex sections should be split by responsibility only when it improves readability or reuse; avoid unnecessary abstraction for one-off markup.

## Shared UI Components

- Button and IconButton for primary, secondary, ghost, destructive, and link-like actions.
- Input and SearchInput for labeled text entry and search affordances.
- Select and RangeInput for dynamic filter controls.
- Card, Badge, Tag, Divider for visual structure and metadata.
- Pagination for paged result navigation.
- Spinner and Skeleton for loading states.
- EmptyState and ErrorState for recoverable non-data and failure states.
- Alert for inline notifications.
- Modal and Drawer for overlays, with Drawer used for mobile filters.
- Tooltip for supplemental information, avoiding critical-only content.
- StatusIndicator for backend availability and similar state signals.

## Feature Component Hierarchy

- HomePage → MarketOverview → SearchToolbar → FilterSidebar → ResultsGrid → ListingCard → Pagination.
- Listing Detail Page → Image Gallery → Vehicle Summary → Vehicle Specifications → Marketplace Action.
- Navigation and footer sit in the application shell around page content.

## Home Page Composition

- Home page reads normalized URL search state.
- MarketOverview loads independently from stats.
- SearchToolbar manages text search, sort entry point, and clear filters affordance.
- FilterSidebar uses dynamic metadata and becomes a Drawer on mobile.
- ResultsGrid renders skeleton, error, empty, and data states.
- ListingCard links to listing detail while preserving return behavior.
- Pagination uses backend meta and URL state.

## Listing Detail Page Composition

- Detail page resolves by listing id only.
- Image Gallery uses available image-related fields when present; otherwise it shows consistent fallback visuals.
- Vehicle Summary highlights make, model, trim, year, price, mileage, condition, location, seller type, and recency.
- Vehicle Specifications displays all additional available fields returned by the backend.
- Marketplace Action opens the original listing URL when valid.
- Missing detail data renders a listing-not-found or recoverable error state.

## Market Overview Integration

- Market Overview consumes `GET /api/v1/stats` through `stats.api.ts` and a stats feature hook.
- Displays total listings, used listings, new listings, makes, models, average price, and last updated.
- Summary skeleton and error state are scoped to the Market Overview section.
- Missing numeric values use formatting utilities rather than hard-coded placeholders.

## Dynamic Filter Metadata Integration

- Filter controls consume `GET /api/v1/listings/filters` through `filters.api.ts`.
- Makes, models, conditions, seller types, and numeric ranges are generated from metadata.
- No filter option values are hardcoded except UI labels for control names.
- If metadata fails, listing search remains usable where possible and filters display a scoped error state.

## Backend Health Integration

- Health indicator consumes `GET /api/v1/health` through `health.api.ts`.
- Success status means available; request failure, timeout, or unexpected payload means unavailable/degraded.
- Health polling is independent from listing, filters, stats, and details.
- Indicator must be visible in navigation and accessible to screen readers.

## Listing Card UX

- Cards show image/fallback, make, model, trim, year, price, mileage, location, seller type, first seen, and last seen.
- Cards remain visually consistent when optional fields are missing.
- Cards have a clear clickable target and keyboard focus behavior.
- Cards avoid presenting unknown values as facts.
- Cards use formatting utilities for currency, mileage, dates, relative dates, and empty values.

## Listing Detail UX

- Detail page displays all available backend fields with readable labels.
- Information is grouped into image gallery, summary, specifications, seller/source information, and marketplace action.
- External marketplace action is hidden or disabled when URL is missing/invalid.
- External links must be safe and should not replace the current PrioraMarket search context.

## Image Handling Strategy

- Feature 003 contract exposes `photosCount` but does not expose actual image URLs in the documented OpenAPI contract.
- Listing card and detail image areas must support future image URLs but use placeholder/fallback imagery for current contract limitations.
- Image containers use fixed aspect ratios to prevent layout shift.
- Image loading has skeleton states.
- Missing or invalid images render fallback visuals without changing card dimensions.

## Responsive Image Optimization

- Use responsive image rendering when image URLs become available.
- Constrain image dimensions to card/detail aspect ratios.
- Lazy-load below-the-fold listing images.
- Prioritize above-the-fold hero/detail imagery only when real image URLs are available.

## Placeholder/Fallback Image Strategy

- Provide a neutral automotive placeholder for listings without images.
- Use the same aspect ratio as real images.
- Include accessible alt text that does not imply an actual vehicle photo exists when only a placeholder is shown.
- Surface `photosCount` as metadata if useful, but do not infer image URLs from it.

## Loading Strategy

- Page Skeleton for initial route structure.
- Card Skeleton for listing results.
- Detail Skeleton for listing details.
- Summary Skeleton for Market Overview.
- Filter Skeleton for dynamic filter metadata.
- Health indicator uses compact pending/unavailable/available states without blocking navigation.
- Loading one section must not block unrelated sections.

## Error Strategy

- Normalize Axios/network/backend errors in the API layer.
- Map errors into UI categories: network error, backend offline, validation/bad request, listing not found, empty search, and unexpected error.
- Feature sections render scoped ErrorState components with retry where useful.
- 404 detail responses render listing-not-found UX.
- 400 search responses should result from invalid URL state only after normalization; if encountered, show a recoverable search error and offer Clear Filters.

## Global Error Boundaries

- App-level error boundary catches route-level unexpected UI errors.
- Feature-level boundaries may isolate complex sections such as results grid and detail content.
- Error boundaries must provide a recovery path and avoid losing URL search state.
- Unexpected error messages must not expose stack traces or internal details to users.

## Empty States

- Empty search results include friendly illustration or placeholder, explanation, Clear Filters action, and immediate search continuation.
- Missing image empty states use image fallback, not broken image icons.
- Missing optional fields use empty-value formatting.
- Empty filter metadata communicates temporary unavailability without blocking listing search.

## Mobile Filter Drawer Behavior

- Desktop and laptop use persistent filter sidebar where space allows.
- Tablet may use an adaptive sidebar or drawer depending on available width.
- Mobile uses Drawer for filters.
- Drawer must trap focus while open, close via explicit close action and Escape, restore focus to the opener, and remain screen-reader understandable.
- Applying filters from the drawer updates URL state and results automatically.

## Responsive Layout Strategy

- Desktop: persistent filters, multi-column cards, full Market Overview, full navigation.
- Laptop: reduced spacing/columns while preserving desktop structure.
- Tablet: simplified grid density and accessible filter access.
- Mobile: single-column cards, filter drawer, compact summary, accessible navigation, no horizontal scrolling.
- Responsive containers use shared shell tokens rather than page-specific widths.

## Accessibility Strategy

- Use semantic landmarks for header, navigation, main, and footer.
- All form controls require labels or accessible names.
- Status changes for loading, errors, empty results, and backend availability must be announced where appropriate.
- Interactive elements need visible focus states in both themes.
- Color must not be the only indicator of state.
- Light and dark themes must maintain sufficient contrast.

## Keyboard Navigation

- Users can reach navigation, theme switcher, health indicator context, search input, filters, drawer controls, listing cards, pagination, detail actions, and external listing action by keyboard.
- Pagination and cards have predictable tab order.
- Drawer, modal, tooltip-triggered controls, selects, and range inputs support keyboard behavior consistent with web accessibility expectations.

## Focus Management

- Route changes should move focus to the main content heading or equivalent page landmark.
- Opening the mobile filter drawer moves focus into the drawer.
- Closing the drawer restores focus to the trigger.
- Error recovery and clear filters actions should keep focus in a useful location.
- Returning from detail should restore scroll position and avoid unexpected focus loss.

## ARIA And Screen-Reader Behavior

- Use ARIA labels only where native semantics are insufficient.
- Loading states should communicate progress without excessive announcements.
- Empty and error states should be readable as meaningful status messages.
- Backend availability indicator should expose available/unavailable/degraded text.
- Dialogs and drawers must expose accessible names and modal semantics.

## Formatting Utilities

- Central formatting utilities live under `frontend/lib/formatting` or a shared feature foundation.
- Components receive raw values and call formatting utilities or receive preformatted display values from feature mappers.
- Formatting utilities must be deterministic and testable.
- Formatting utilities handle null/undefined consistently.

## Currency, Mileage, Date, Relative Date, Number, And Empty-Value Formatting

- AED currency: format with AED label/symbol convention consistently; null values display the empty-value placeholder.
- Mileage: format as kilometers with grouping and unit label.
- Dates: format absolute dates consistently for first seen, last seen, and last updated.
- Relative dates: use friendly recency labels where useful while preserving access to absolute dates in details or tooltips.
- Numbers: use locale-aware grouping for counts and metrics.
- Empty values: use one consistent placeholder such as “Not available” or a compact dash depending on context, never misleading fabricated data.

## SEO And Metadata Strategy

- Define default app metadata with title, description, favicon, and Open Graph defaults.
- Home page metadata describes PrioraMarket vehicle search and market overview.
- Listing detail metadata uses available listing make/model/year/title when available and safe fallbacks otherwise.
- Canonical URLs should omit noisy transient parameters where appropriate but preserve meaningful route identity.
- Robots and sitemap compatibility are established through Next.js metadata route conventions.

## Favicon, OpenGraph, Canonical, Robots, And Sitemap Compatibility

- Favicon assets live in `frontend/public` or app metadata locations.
- Open Graph metadata uses brand-safe defaults; no backend image dependency is required for Feature 004.
- Canonical route generation should support `/` and `/listings/[id]`.
- Robots defaults should allow normal discoverability unless environment configuration disables indexing.
- Sitemap support can list current public routes and be extensible for future dynamic listing strategies without requiring backend changes.

## Testing Strategy

- Tests are organized by unit, component, integration, end-to-end, accessibility, responsive, theme, and error-state coverage.
- API calls are mocked for frontend tests; tests must not require live backend availability except optional local quickstart verification.
- Tests should validate behavior from user perspective and contracts from Feature 003.

## Unit Testing Plan

- Formatting utilities for currency, mileage, dates, relative dates, numbers, and empty values.
- URL search state parsing/serialization/normalization.
- Zod schemas and typed response normalization.
- API error normalization.
- Theme preference resolution.

## Component Testing Plan

- Shared UI components across light and dark themes.
- SearchInput debounce interaction.
- Select, RangeInput, Pagination, Drawer, Modal, Tooltip, StatusIndicator accessibility behavior.
- ListingCard fallback and optional-field rendering.
- EmptyState and ErrorState action behavior.

## Integration Testing Plan

- Home page composition with mocked listings, filters, stats, and health responses.
- Detail page composition with mocked listing detail response.
- Dynamic filters populated from metadata.
- URL state changes trigger expected query keys and section updates.
- Independent loading and error states do not block unrelated sections.

## End-To-End Testing Plan

- Search homepage loads and displays Market Overview, filters, results, and health indicator.
- User searches text, applies filters, changes sort, paginates, clears filters.
- Browser Back/Forward restores search state.
- User opens detail and returns with filters, page, and scroll position restored.
- Mobile user opens filter drawer, applies filters, views single-column cards, and opens detail.

## Accessibility Testing Plan

- Keyboard-only completion of search, filtering, pagination, detail navigation, drawer usage, theme switching, and external listing action.
- Focus management for route changes, drawer open/close, clear filters, and error recovery.
- Screen reader labels and status announcements for loading, errors, empty states, and health.
- Contrast checks in light and dark themes.

## Responsive Viewport Testing Plan

- Desktop at 1280px and wider.
- Laptop at 1024-1279px.
- Tablet at 768-1023px.
- Mobile below 768px.
- Verify no horizontal scrolling, usable navigation, correct filter drawer/sidebar behavior, and readable cards.

## Theme Testing Plan

- Light mode visual and accessibility coverage.
- Dark mode visual and accessibility coverage.
- System mode follows mocked system preference.
- Theme switcher updates without page reload and preserves current route/search state.
- Shared UI components render correctly in both themes.

## API Mocking Strategy

- Use MSW or equivalent request mocking for unit/integration/component tests.
- Use Playwright route mocking for E2E tests where a live backend is not required.
- Mock the five allowed Feature 003 endpoints only.
- Include fixtures for success, empty, 400, 404, network failure, backend offline, missing optional fields, and missing image URLs.

## Error-State Testing Strategy

- Simulate network failures per endpoint.
- Simulate backend offline through health failure.
- Simulate empty search results with zero totals.
- Simulate listing 404.
- Simulate unexpected UI error inside a feature section and verify boundary isolation.
- Verify retry and Clear Filters actions remain accessible.

## Performance Strategy

- Keep route bundles small through feature boundaries and client/server component discipline.
- Avoid loading heavy overlay/dialog logic until needed where practical.
- Use lazy image behavior and fixed aspect ratios.
- Avoid expensive client-side filtering over large result sets; rely on backend search.
- Use TanStack Query caching to prevent unnecessary refetches while keeping URL state authoritative.

## Bundle Size And Rendering Performance

- Prefer shared UI primitives over large component libraries.
- Use Lucide icons selectively and import only used icons.
- Keep TanStack Query provider scoped globally but data fetching scoped by feature hooks.
- Avoid unnecessary client components; only interactive components need client behavior.
- Monitor build output during implementation and address unexpected bundle growth.

## Environment Configuration

- Frontend environment variables must be documented with non-secret placeholders.
- Required variable: `NEXT_PUBLIC_API_BASE_URL`, the frontend-visible base URL for Feature 003 backend.
- Optional variables: metadata site URL, indexing toggle, health polling interval if needed.
- Missing required configuration should fail clearly during development/build or fall back only to safe local defaults.

## Environment Validation

- Validate frontend environment configuration through a typed strategy, preferably Zod, before API modules depend on it.
- `NEXT_PUBLIC_API_BASE_URL` is required unless a local development default is explicitly documented.
- Invalid URL values must fail clearly with an actionable configuration error.
- Safe local defaults are allowed only for documented local development workflows and must not hide production misconfiguration.
- Environment validation must not introduce secrets or authentication requirements.

## CORS / API Base URL Strategy

- Local development may run frontend and backend on separate origins; backend CORS must already allow the configured frontend origin or requests must be proxied through Next.js configuration without changing backend contracts.
- Production base URL is environment-driven.
- API modules use the same base URL and `/api/v1` path conventions as Feature 003.
- Do not introduce new backend routes, headers, or auth requirements.

## Build And Validation Commands

- Install frontend dependencies from `frontend/`.
- Validate static quality with lint and format checks.
- Validate types with TypeScript checking.
- Validate production build with Next.js build.
- Run unit/component/integration tests with Vitest or Jest.
- Run E2E tests with Playwright.
- Run accessibility and responsive coverage through component/E2E test suites.

## Risks And Mitigations

- **Strong but incomplete architecture without this revision**: The previous plan could produce a functional frontend, but long-term maintainability would suffer as future features add more client components, duplicated constants, ad hoc query keys, direct DTO usage, and hidden feature coupling. This revision mitigates that by adding explicit boundaries before task generation.
- **Missing listing image URLs in Feature 003 contract**: Use placeholder/fallback visuals and document the limitation; do not require backend changes.
- **Unknown exact frontend package baseline**: Create isolated `frontend/` project to avoid disturbing backend package setup.
- **URL state complexity**: Centralize parsing/serialization and test browser navigation thoroughly.
- **Cache fragmentation from inconsistent query keys**: Use query key factories derived from normalized state.
- **DTO leakage into UI**: Use feature mappers and UI models so backend nullability and naming do not spread through component trees.
- **Excessive Client Component usage**: Default to Server Components and isolate browser-only behavior in small client components.
- **Configuration drift**: Validate `NEXT_PUBLIC_API_BASE_URL` and documented optional variables through typed environment validation.
- **Magic numbers and repeated literals**: Centralize constants for pagination, debounce, breakpoints, empty values, sort options, and polling intervals.
- **Theme hydration mismatch**: Use a root theme initialization strategy and semantic tokens.
- **Mobile filter complexity**: Treat Drawer as a shared UI primitive with focus management and tests.
- **Backend unavailable during frontend development**: Use API mocks and fixtures for tests; quickstart may point to local backend for manual verification.
- **Future feature drift**: Document reuse standards in this plan and contracts, keep shared foundations feature-agnostic, and keep Feature 003 untouched unless real API limitations appear during integration.

## Future Extensibility

- Future features must reuse the application shell, design system, theme provider, API layer, formatting utilities, accessibility patterns, loading patterns, and error patterns.
- Future features may add routes and navigation items by extending the shell rather than replacing it.
- Future capabilities such as favorites, saved searches, compare vehicles, AI insights, recommendations, market analytics, maps, authentication, and user profiles remain out of scope for Feature 004.
- The API layer can add modules for future versioned backend capabilities without pages importing HTTP clients directly.

## Complexity Tracking

No constitution violations or complexity exceptions are required.

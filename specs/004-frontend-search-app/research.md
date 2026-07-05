# Research: Frontend Search Application

## Decision: Add A Dedicated `frontend/` Next.js Application

**Rationale**: The existing repository contains a backend project. A dedicated `frontend/` app isolates frontend dependencies, build commands, and tests while preserving backend behavior and Feature 003 contracts.

**Alternatives considered**: Adding frontend files at repository root was rejected because it would mix backend and frontend package concerns. Adding frontend inside `backend/` was rejected because it would violate modularity and make deployment boundaries unclear.

## Decision: Use Next.js App Router With Two Feature Routes

**Rationale**: App Router supports route-level layouts, metadata, loading states, error boundaries, and nested routes that match the required shell and detail page behavior.

**Alternatives considered**: A single-page React app was rejected because it would require additional routing/metadata conventions. Pages Router was rejected because App Router is the requested modern Next.js approach.

## Decision: Use URL Query Parameters As Search State Source Of Truth

**Rationale**: The specification requires refreshable, shareable, browser-navigation-compatible search state. URL state naturally supports Back/Forward and bookmarks.

**Alternatives considered**: Global client state was rejected because it would not survive refresh/share by default. Browser storage was rejected because it would make shared URLs ambiguous.

## Decision: Use TanStack Query For Server State

**Rationale**: The frontend consumes read-only backend data from five endpoints and needs independent loading, caching, refetching, retry, and error states. TanStack Query fits these server-state needs without a global state library.

**Alternatives considered**: Manual `useEffect` fetching was rejected because it scatters loading/error/cache behavior. Redux or another global store was rejected as unnecessary for read-only server state and URL-driven search state.

## Decision: Centralize Axios Behind Typed API Modules

**Rationale**: The architecture requires pages never call Axios directly. A central client and modules for search, listings, filters, stats, and health preserve API compatibility and isolate error normalization.

**Alternatives considered**: Calling Axios in hooks or pages was rejected because it weakens boundaries. Generated API clients may be considered later, but hand-maintained typed modules are sufficient for five endpoints.

## Decision: Use Zod At Frontend Trust Boundaries

**Rationale**: Zod validates URL query parsing and backend response assumptions without moving business logic into the frontend. It helps normalize invalid URL state and safely handle nullable backend fields.

**Alternatives considered**: TypeScript-only types were rejected because they do not validate runtime data. Heavy schema generation was rejected as unnecessary for the current endpoint set.

## Decision: Use React Hook Form For Filter Forms

**Rationale**: Search and filter controls need accessible form state, range validation, and controlled updates into URL parameters. React Hook Form integrates with Zod and avoids unnecessary re-renders.

**Alternatives considered**: Local state per control was rejected because it would duplicate parsing and validation logic. A global form store was rejected as unnecessary.

## Decision: Theme Provider With Light, Dark, And System Modes

**Rationale**: Dark mode is required, and future frontend features must reuse a single theme architecture. A ThemeProvider centralizes persistence, system detection, and document theme application.

**Alternatives considered**: CSS-only system theme was rejected because explicit light/dark switching and persistence are required. Per-component theme logic was rejected because it would cause inconsistent behavior.

## Decision: Feature-Based Frontend Organization

**Rationale**: The spec requires feature modules and future extensibility. Feature-based organization keeps search, listings, filters, stats, health, theme, and shared foundations coherent.

**Alternatives considered**: Organizing only by technical type was rejected because it encourages cross-feature coupling and makes future features harder to isolate.

## Decision: Shared Design System With Semantic Tokens

**Rationale**: PrioraMarket needs reusable UI components that work across themes and future features. Semantic tokens prevent hard-coded colors and spacing.

**Alternatives considered**: Using an off-the-shelf component library was rejected for the initial plan because the required component set is modest and design ownership is important. Ad hoc feature components were rejected because they would not establish a foundation.

## Decision: Placeholder/Fallback Image Strategy For Current Contract

**Rationale**: Feature 003 OpenAPI exposes `photosCount` but not actual image URLs. The frontend must remain visually consistent and document this integration limitation without requiring backend changes.

**Alternatives considered**: Inferring image URLs from original listing URLs was rejected because it would depend on external marketplace behavior. Blocking image UI until backend changes was rejected because backend changes are out of scope.

## Decision: Independent Section Loading And Error States

**Rationale**: The spec requires Market Overview, filters, results, details, and health to load/fail independently. Independent TanStack Query hooks and scoped UI states meet this requirement.

**Alternatives considered**: A page-level loading/error gate was rejected because it would block usable sections unnecessarily.

## Decision: Testing With Unit, Component, Integration, E2E, Accessibility, Responsive, Theme, And Error Coverage

**Rationale**: The feature creates a reusable frontend foundation and search UX, so tests must verify utilities, components, API boundaries, URL state, browser navigation, mobile drawer behavior, and theme switching.

**Alternatives considered**: E2E-only testing was rejected because it would be slow and weak for utility edge cases. Unit-only testing was rejected because it would miss browser navigation and responsive behavior.

## Integration Limitations Documented

- Feature 003 does not document listing image URLs; Feature 004 will use placeholders/fallbacks while preserving image-ready containers.
- Feature 003 health response only documents `{ status: "ok" }`; frontend treats request failure as unavailable/degraded.
- Feature 003 stats response includes min/max price, but Feature 004 Market Overview only requires average price and count metrics. Extra fields may be typed and available but not necessarily displayed.
- Feature 003 does not provide authentication, favorites, saved searches, compare, AI recommendations, maps, or admin capabilities; Feature 004 must not add them.

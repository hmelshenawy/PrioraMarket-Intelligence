# Frontend Integration Limitations

This document records the frontend integration requirements of Feature 004 (Frontend Search Application) that cannot be fully satisfied by the existing Feature 003 Backend Search API contract without changing that contract. It is required by spec FR-021.

Feature 004 consumes only the five allowed Feature 003 endpoints and does not change any backend contract. The limitations below are accepted as-is and handled with graceful frontend fallbacks. None of them require backend changes in this feature.

## 1. Missing image URLs

The Feature 003 listing DTOs (`ListingSearchResultDto`, `ListingDetailDto`) do not include an image URL field. The listings own a `photosCount` integer but no addressable photo URLs.

**Frontend behavior:**

- `ListingImage` renders a deterministic placeholder visual instead of an `<img>` for every card and detail gallery item.
- `ImageGallery` uses the same placeholder behavior on listing detail pages; it does not render an `<img>` unless the backend contract is explicitly expanded in the future.
- A `photosCount` badge is shown when present so the user knows photos may exist on the source marketplace.
- The placeholder is accessible (`sr-only` text: "No photo available for {title}").
- No image is fabricated and no broken-image icon is shown.
- The frontend does not derive, guess, or construct image URLs from the source listing URL.

**Resolution without backend change:** Accepted. Missing image URLs are the normal current path. If the backend later exposes explicit image URL fields, the mapper and image components should be updated together with tests that verify invalid or missing URLs still render the placeholder.

## 2. Minimal health payload

The Feature 003 health endpoint returns `{ status: "ok" }` only. There is no degraded state, latency, version, or per-subsystem breakdown in the contract.

**Frontend behavior:**

- `useBackendHealth` treats a successful `{ status: "ok" }` response as `available`.
- Any request failure, timeout, or schema-invalid payload is treated as `unavailable`.
- The `StatusIndicator` UI models four states (`checking`, `available`, `unavailable`, `degraded`) for future-proofing, but only `checking`/`available`/`unavailable` are reachable against the current contract.
- Color is never the only signal: a text label always accompanies the dot.

**Resolution without backend change:** Accepted. A richer health payload can be consumed later by extending `healthMapper` without changing the UI contract.

## 3. Missing optional fields

Listing DTOs use nullable/optional fields throughout (e.g., `trim`, `location`, `sellerType`, `specs`, `averagePriceAed`, `minPriceAed`, `maxPriceAed`, `lastUpdatedAt`). Any field may be absent on any given listing or stats response.

**Frontend behavior:**

- All DTO fields are typed with `| null` where the data model allows null, and parsed with Zod at the API trust boundary.
- Mappers soften missing values through shared formatting utilities (`formatAed`, `formatNumber`, `formatDate`, `formatRelativeDate`) which return the consistent `EMPTY_VALUE` placeholder (`—`) for null/undefined/invalid input — never a fabricated value.
- The detail page groups fields into gallery/summary/specifications/seller-source/marketplace-action sections and omits empty rows rather than rendering blank lines.
- Market Overview shows `—` for a null average price or missing last-updated timestamp.
- The listing detail page renders a not-found state for a 404 and a recoverable error state for 500/network failures.

**Resolution without backend change:** Accepted. Optional-field absence is a normal data condition, not an integration gap.

## 4. No search-state persistence contract

The backend search endpoint is stateless; pagination/sort/filter state lives only in the URL. This is by design (URL is the single source of truth) and is not a backend limitation.

## 5. Allowed endpoints (restatement)

Feature 004 consumes only:

- `GET /api/v1/listings`
- `GET /api/v1/listings/:id`
- `GET /api/v1/listings/filters`
- `GET /api/v1/stats`
- `GET /api/v1/health`

No other endpoints are called, and no Server Actions are used.

## 6. Environment requirements

- `NEXT_PUBLIC_API_BASE_URL` (required, no trailing slash): base URL for the Feature 003 API.
- `NEXT_PUBLIC_SITE_URL` (optional): public site URL for canonical/OpenGraph/sitemap.
- `NEXT_PUBLIC_ALLOW_INDEXING` (optional, default `true`): robots indexing toggle.
- `NEXT_PUBLIC_HEALTH_POLLING_INTERVAL` (optional, default 30000 ms): health polling cadence.

No secrets are required for Feature 004.

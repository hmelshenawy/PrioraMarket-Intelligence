# Contract: Frontend API Client

## Purpose

Define the frontend-only API client contract for consuming Feature 003 Backend Search API without changing backend contracts.

## Allowed Endpoints

- `GET /api/v1/listings`
- `GET /api/v1/listings/:id`
- `GET /api/v1/listings/filters`
- `GET /api/v1/stats`
- `GET /api/v1/health`

No other backend endpoints are required or introduced by Feature 004.

## API Modules

### `search.api.ts`

Capability: Search current listings.

Endpoint: `GET /api/v1/listings`

Request model:

- `q?: string`
- `condition?: "used" | "new"`
- `make?: string`
- `model?: string`
- `yearFrom?: number`
- `yearTo?: number`
- `priceMin?: number`
- `priceMax?: number`
- `kmMin?: number`
- `kmMax?: number`
- `location?: string`
- `sellerType?: string`
- `page?: number`
- `limit?: number`
- `sort?: "relevance" | "newest" | "price_asc" | "price_desc" | "year_asc" | "year_desc" | "km_asc" | "km_desc"`

Response model: `SearchListingsResponse` from Feature 003.

### `listings.api.ts`

Capability: Read one listing detail.

Endpoint: `GET /api/v1/listings/:id`

Request model:

- `id: string`

Response model: `ListingDetailResponse` from Feature 003.

### `filters.api.ts`

Capability: Read dynamic filter metadata.

Endpoint: `GET /api/v1/listings/filters`

Request model: none.

Response model: `FilterMetadataResponse` from Feature 003.

### `stats.api.ts`

Capability: Read Market Overview metrics.

Endpoint: `GET /api/v1/stats`

Request model: none.

Response model: `InventoryStatsResponse` from Feature 003.

### `health.api.ts`

Capability: Read backend availability.

Endpoint: `GET /api/v1/health`

Request model: none.

Response model: `HealthResponse` from Feature 003.

## Error Contract

- Backend 400 errors map to validation/search-state errors.
- Backend 404 errors on listing detail map to Listing Not Found.
- Network failures map to Network Error or Backend Offline depending on affected feature.
- Unexpected payloads map to Unexpected Error for the affected section.
- API layer must normalize errors before feature hooks consume them.

## Boundary Rules

- Pages must not import Axios or call HTTP clients directly.
- Feature components must not call API modules directly when a feature hook exists.
- API modules must not contain UI formatting or component logic.
- API modules must not require backend contract changes.

# Data Model: Frontend Search Application

## Overview

This data model describes frontend-facing state, API DTOs, UI entities, and validation rules for Feature 004. It does not introduce persistence tables or backend schema changes. All business data is read from Feature 003 Backend Search API.

## API Data Entities

### ListingSearchRequest

Represents normalized URL search state sent to `GET /api/v1/listings`.

Fields:

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
- `page: number`
- `limit: number`
- `sort: "relevance" | "newest" | "price_asc" | "price_desc" | "year_asc" | "year_desc" | "km_asc" | "km_desc"`

Validation rules:

- Empty strings are omitted.
- Numeric values must be finite and non-negative where applicable.
- Range minimums must not exceed range maximums.
- `page` must be at least 1.
- `limit` must remain within backend-supported bounds.
- Unsupported sort values normalize to the default sort.

### SearchListingsResponse

Represents paginated listing results from Feature 003.

Fields:

- `data: ListingSearchResult[]`
- `meta: PaginationMeta`

Rules:

- Empty `data` with `total = 0` drives empty search UX.
- Non-empty `data` drives ResultsGrid rendering.

### ListingSearchResult

Represents one listing card.

Fields:

- `id: string`
- `externalId: string | null`
- `title: string | null`
- `make: string | null`
- `model: string | null`
- `trim: string | null`
- `year: number | null`
- `priceAed: number | null`
- `km: number | null`
- `condition: string | null`
- `location: string | null`
- `sellerType: string | null`
- `url: string | null`
- `photosCount: number | null`
- `firstSeenAt: string | null`
- `lastSeenAt: string | null`

Rules:

- Null fields render through empty-value formatting.
- `photosCount` does not imply image URLs exist.
- `url` must be validated before showing original marketplace action.

### ListingDetailResponse

Represents listing detail data from `GET /api/v1/listings/:id`.

Fields:

- All `ListingSearchResult` fields.
- `marketplace: string | null`
- `bodyType: string | null`
- `fuel: string | null`
- `transmission: string | null`
- `color: string | null`
- `specs: object | null`
- `seller: string | null`
- `isVerified: boolean | null`
- `isAgent: boolean | null`
- `neighbourhood: string | null`
- `firstSeenRunId: string | null`
- `lastSeenRunId: string | null`
- `canonicalHash: string | null`

Rules:

- Display all available fields with labels.
- Omit or mark unavailable missing optional values consistently.
- Unknown `specs` keys are displayed safely as additional specifications.

### PaginationMeta

Fields:

- `page: number`
- `limit: number`
- `total: number`
- `totalPages: number`

Rules:

- Pagination UI uses this entity as source of truth.
- `totalPages = 0` is treated as empty results.

### FilterMetadataResponse

Fields:

- `makes: string[]`
- `models: Record<string, string[]>`
- `price: NumericRange`
- `year: NumericRange`
- `km: NumericRange`
- `conditions: string[]`
- `sellerTypes: string[]`

Rules:

- Dropdowns and ranges are generated from this metadata.
- No categorical values are hardcoded.
- Model options may depend on selected make when available.

### NumericRange

Fields:

- `min: number | null`
- `max: number | null`

Rules:

- Null bounds disable or soften range constraints.
- UI must prevent invalid min/max submissions.

### InventoryStatsResponse

Fields:

- `totalListings: number`
- `usedListings: number`
- `newListings: number`
- `totalMakes: number`
- `totalModels: number`
- `averagePriceAed: number | null`
- `minPriceAed: number | null`
- `maxPriceAed: number | null`
- `lastUpdatedAt: string | null`

Rules:

- Market Overview displays total listings, used listings, new listings, makes, models, average price, and last updated.
- Additional min/max price fields may be typed but are not required for display.

### HealthResponse

Fields:

- `status: "ok"`

Rules:

- Successful response means available.
- Failed request, timeout, or invalid response means unavailable/degraded.

### ApiErrorResponse

Fields:

- `statusCode: number`
- `error: string`
- `message: string | string[]`
- `requestId: string | null`

Rules:

- API layer normalizes backend and network errors to consistent frontend error categories.
- Internal stack traces must not be displayed.

## Frontend State Entities

### SearchUrlState

Represents query parameters in the browser URL.

Fields:

- `q`, `make`, `model`, `condition`, `sellerType`
- `priceMin`, `priceMax`, `kmMin`, `kmMax`, `yearFrom`, `yearTo`
- `sort`, `page`, `limit`

State transitions:

- Initial load: URL → normalized state → API request.
- Text change: local input → debounce → URL update → API request.
- Filter/sort change: control value → URL update → API request.
- Clear filters: current URL state → default URL state → API request.
- Back/Forward: browser history URL → normalized state → API request.

### ThemePreference

Fields:

- `mode: "light" | "dark" | "system"`
- `resolvedTheme: "light" | "dark"`

State transitions:

- Default: system or safe default.
- User switch: selected mode persists and updates document theme.
- System preference change: updates resolved theme only when mode is `system`.

### BackendAvailability

Fields:

- `state: "checking" | "available" | "unavailable" | "degraded"`
- `lastCheckedAt: string | null`

Rules:

- Rendered in top navigation.
- Does not block other page sections.

### ScrollReturnState

Fields:

- `route: string`
- `search: string`
- `scrollY: number`

Rules:

- Used only to restore scroll position after returning from listing detail.
- Must not replace URL search state as the source of truth.

## UI Entities

### ApplicationShell

Fields/slots:

- Top navigation
- Main content area
- Footer
- Responsive container
- Theme context
- Global error boundary

Rules:

- Reused by all pages.
- No feature-specific business logic.

### DesignSystemComponent

Components:

- Button, IconButton, Input, SearchInput, Select, RangeInput, Card, Badge, Tag, Pagination, Spinner, Skeleton, EmptyState, ErrorState, Alert, Modal, Drawer, Tooltip, StatusIndicator, Divider.

Rules:

- Uses design tokens.
- Supports light and dark themes.
- Does not depend on feature-specific logic.

### FormattedValue

Types:

- AED currency
- Mileage
- Date
- Relative date
- Number
- Empty value

Rules:

- Formatting is centralized and tested.
- Components do not duplicate formatting logic.

## Relationships

- SearchUrlState maps to ListingSearchRequest.
- ListingSearchRequest returns SearchListingsResponse.
- ListingSearchResult renders through ListingCard.
- ListingDetailResponse renders through listing detail feature components.
- FilterMetadataResponse configures SearchToolbar and FilterSidebar controls.
- InventoryStatsResponse renders MarketOverview.
- HealthResponse maps to BackendAvailability and StatusIndicator.
- ThemePreference controls design token resolution for ApplicationShell and DesignSystemComponent.

## Integration Limitations

- Current Feature 003 contract does not expose image URLs. UI must use placeholders/fallbacks while remaining ready for future image URL fields.
- Current Feature 003 health payload is minimal. Frontend availability detail is limited to reachable/unreachable/degraded based on request outcome.
- Feature 004 cannot require backend metadata beyond the five approved endpoints.

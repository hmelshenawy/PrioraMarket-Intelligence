# Data Model: Backend Search API

## Existing Persistence Tables Consumed

### marketplace_source

Represents a marketplace provider.

Fields used:

- `id`: internal source identifier.
- `code`: stable marketplace code.
- `name`: display marketplace name.
- `country`: source country.
- `base_url`: source base URL.

Relationships:

- One marketplace source has many listings, raw listings, and ingestion runs.

### ingestion_run

Represents one ingestion execution.

Fields used:

- `id`: run identifier.
- `name`: unique run name.
- `marketplace_source_id`: source relationship.
- `marketplace`, `condition`, `make`: run scope.
- `status`, `started_at`, `completed_at`: run state and timing.

Relationships:

- Referenced by listing first and last seen run IDs.

### listing

Current canonical listing record and primary source for search.

Fields used:

- `id`: internal listing identifier.
- `source`: marketplace/source code.
- `uuid`: stable external listing identifier.
- `title`, `make`, `model`, `trim`: text and vehicle identity fields.
- `year`: model year.
- `price`: current price in AED.
- `mileage`: current mileage in km.
- `condition`: used/new.
- `location`: location text.
- `seller_type`: owner/dealer/etc.
- `url`: source listing URL.
- `status`: current listing status.
- `first_seen_at`, `last_seen_at`: current listing freshness and newest sorting fields.
- `first_seen_run_id`, `last_seen_run_id`: lineage.
- `current_raw_listing_id`: link to current raw payload.
- `canonical_hash`: current canonical hash.
- `normalization_version`: source normalization version.

Validation and mapping rules:

- `price` maps to `priceAed` as number or null.
- `mileage` maps to `km` as number or null.
- Missing optional scalar fields map to null.
- `uuid` maps to `externalId`.

### listing_snapshot

Immutable listing observation snapshot.

Fields used:

- `listing_id`: parent listing.
- `ingestion_run_id`: snapshot run.
- `canonical_payload`: JSON canonical data for fields not present in `listing`.
- `captured_at`: snapshot timestamp.

Usage:

- Detail endpoint may read the latest snapshot for body type, fuel, transmission, color, specs, seller, verification flags, agent flags, neighbourhood, and photo count when absent from `listing`.
- Search should not depend on historical snapshot scans.

### raw_listing

Raw marketplace payload record.

Fields used only if required for detail fallback:

- `id`, `raw_payload`, `extracted_at`.

Usage:

- Read-only fallback for fields unavailable in canonical listing/snapshot data.

## Domain Objects

### ListingSearchCriteria

Validated search input independent of HTTP decorators.

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

- Empty strings are treated as absent.
- Numeric values must be valid and non-negative where applicable.
- `page >= 1`, `1 <= limit <= 100`.
- `relevance` without `q` is normalized to `newest` by service business rule before query construction.

### BuiltListingSearchQuery

Persistence-specific query object produced by Search Query Builder.

Fields:

- `where`: Prisma-compatible filters or safe raw-query descriptor.
- `orderBy`: Prisma-compatible sort or safe raw relevance order descriptor.
- `skip`: offset.
- `take`: limit.
- `select`: projection descriptor for fields needed by the current query, when applicable.
- `include`: relationship/include descriptor for marketplace source, snapshots, or raw fallback data, when applicable.
- `requiresRawRead?: boolean`: true only when relevance cannot be expressed through Prisma query API.
- `parameters`: safe parameter values for any raw read query.

Rules:

- Produced only from validated criteria.
- Contains no HTTP concepts.
- Contains no response DTOs.

### ISearchQueryBuilder

Interface for translating validated search criteria into built persistence queries.

Methods:

- Build search query descriptors.
- Build detail query descriptors.
- Build filter metadata query descriptors.
- Build inventory stats query descriptors.

Rules:

- Services depend on this interface, not a concrete query builder.
- Implementations may target Prisma, Elasticsearch, OpenSearch, or Meilisearch in future features.

### ResponseMapper

Mapper layer for converting domain objects into response DTOs.

Responsibilities:

- Convert `ListingDomain` to listing search result DTO.
- Convert `ListingDetailDomain` to listing detail DTO.
- Convert `PaginationMeta` to pagination metadata DTO.
- Convert `FilterMetadataDomain` to filter metadata DTO.
- Convert `InventoryStatsDomain` to inventory stats DTO.

Rules:

- Services call mappers rather than manually mapping large response objects field by field.
- Controllers and repositories do not perform response DTO mapping.

### ListingDomain

Domain representation for search results.

Fields:

- `id`, `externalId`, `title`, `make`, `model`, `trim`, `year`, `priceAed`, `km`, `condition`, `location`, `sellerType`, `url`, `photosCount`, `firstSeenAt`, `lastSeenAt`.

### ListingDetailDomain

Domain representation for listing detail.

Fields:

- `id`, `externalId`, `marketplace`, `title`, `make`, `model`, `trim`, `year`, `priceAed`, `km`, `condition`, `bodyType`, `fuel`, `transmission`, `color`, `specs`, `sellerType`, `seller`, `isVerified`, `isAgent`, `neighbourhood`, `location`, `url`, `photosCount`, `firstSeenRunId`, `lastSeenRunId`, `firstSeenAt`, `lastSeenAt`, `canonicalHash`.

### PaginationMeta

Fields:

- `page`, `limit`, `total`, `totalPages`.

Rules:

- `totalPages = ceil(total / limit)`.
- `totalPages = 0` when `total = 0`.

### FilterMetadataDomain

Fields:

- `makes: string[]`
- `models: Record<string, string[]>`
- `price: { min: number | null; max: number | null }`
- `year: { min: number | null; max: number | null }`
- `km: { min: number | null; max: number | null }`
- `conditions: string[]`
- `sellerTypes: string[]`

Rules:

- Exclude null/empty categorical values.
- Sort categorical arrays alphabetically.
- Preserve stable response shape for empty inventory.

### InventoryStatsDomain

Fields:

- `totalListings`
- `usedListings`
- `newListings`
- `totalMakes`
- `totalModels`
- `averagePriceAed`
- `minPriceAed`
- `maxPriceAed`
- `lastUpdatedAt`

Rules:

- Empty inventory returns zero counts and null price/update summaries.

## State Transitions

This feature introduces no state transitions. All API capabilities are read-only.

## Index Model

Planned additive indexes for search-read performance:

- Single-column filters: condition, make, model, year, price, mileage, seller_type, location.
- Sort/freshness: last_seen_at, optionally first_seen_at.
- Composite search patterns: make/model, condition/make/model, last_seen_at/id.
- Text search: weighted title/make/model/trim expression or generated tsvector with GIN index.

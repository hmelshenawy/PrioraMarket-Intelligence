# Data Model: Market Snapshot Dashboard

## Overview

The primary domain entity is `MarketSnapshot`. It is generated on demand from canonical listing data and Vehicle Reference Catalog display names. Listings are input records only; the dashboard represents a generated snapshot, not listing data.

## Entities

### MarketSnapshot

Represents the generated market-status view returned to presentation clients.

Fields:

- `scope`: `MarketScope`
- `filters`: `AppliedMarketFilters`
- `metrics`: ordered list of `MarketMetric`
- `supportStatuses`: list or map of `MetricSupportStatus`
- `period`: `SnapshotPeriod`
- `freshness`: `Freshness`
- `generatedAt`: ISO-8601 timestamp

Validation rules:

- `generatedAt` is set at snapshot generation time.
- `freshness` is always present and exposes `lastUpdated`, `datasetVersion`, and `scrapeRunId` (Constitution Data Freshness). It is distinct from `generatedAt`.
- `metrics` are always ordered: Active Listings, Median Price, Typical Price Range, Inventory Change, Price Drops.
- `filters` contain canonical values only.
- `scope.label` is human-readable and catalog-backed when display names exist.

Relationships:

- Generated from matching `ListingInput` records.
- Uses `VehicleReferenceCatalogEntry` for display labels.

### MarketScope

Represents the selected market segment.

Fields:

- `level`: `overall | make | model | trim | year`
- `label`: human-readable label, such as `Overall UAE Used Cars` or `Toyota Corolla XLI 2023`
- `canonical`: object containing canonical `make`, `model`, `trim`, and `year` where selected

Validation rules:

- `overall` has no canonical vehicle filters.
- `model` requires `make`.
- `trim` requires `make` and `model`.
- `year` requires `make`, `model`, and `trim`.
- Labels use Vehicle Reference Catalog display names when available and canonical fallback when unavailable.

### AppliedMarketFilters

Represents canonical filters supplied by the user.

Fields:

- `make`: optional canonical string
- `model`: optional canonical string
- `trim`: optional canonical string
- `year`: optional integer
- `periodDays`: integer, default `7`

Validation rules:

- Vehicle values are not normalized by backend or frontend.
- Query shape is validated for hierarchy and type only.
- `periodDays` defaults to 7 and should be bounded by implementation-defined validation appropriate for MVP.

### MarketMetric

Represents one domain metric in a generated Market Snapshot. Cards are a frontend presentation of metrics, not the backend domain model.

Common fields:

- `type`: `activeListings | medianPrice | typicalPriceRange | inventoryChange | priceDrops`
- `title`: display title
- `status`: `MetricSupportStatus`
- `sampleSize`: optional integer when applicable

Card-specific payloads:

- Active Listings: `count`, `scopeLabel`
- Median Price: `amount`, `currency`, `sampleSize`
- Typical Price Range: `method`, `currency`, `medianAmount`, `lowerAmount`, `upperAmount`, `minAmount`, `maxAmount`, `sampleSize`
- Inventory Change: `activeInventory`, `newListings`, `removedListings`, `netChange`, `periodDays`
- Price Drops: `count`, `averageDropPercentage`, `sampleSize`, `periodDays`

Validation rules:

- Price metrics include sample size even when price value is unavailable due to zero usable priced listings.
- Typical Price Range exposes a business-level lower/upper range; the internal method may use quartiles, percentiles, IQR, or another deterministic approach without changing the snapshot contract.
- Inventory `netChange` is present only when both new listings and removed listings are supported.
- Unsupported history metrics use null metric values plus support status, not fabricated zero values.

### MetricSupportStatus

Represents whether a metric can be interpreted as real market data.

Fields:

- `status`: `supported | unsupported | unavailable | partial`
- `reason`: optional human-readable reason
- `dataAvailable`: boolean

Validation rules:

- `unsupported` means the platform lacks required tracking for the metric.
- `unavailable` means the metric is conceptually supported but no usable data exists for the selected scope/period.
- `supported` values may be zero only when zero is a real calculated result.
- UI must distinguish unsupported from true zero.

### SnapshotPeriod

Represents the selected activity window.

Fields:

- `days`: integer
- `label`: human-readable period label, such as `Last 7 days`

Validation rules:

- Defaults to 7 days.
- Applies to Inventory Change and Price Drops.

### Freshness

Represents data-recency metadata exposed on every analytical response (Constitution Data Freshness principle). Distinct from `generatedAt`.

Fields:

- `lastUpdated`: ISO-8601 timestamp of the most recent listing observation contributing to the response (max `listing.last_seen_at` over the scoped active listings).
- `datasetVersion`: canonical/normalization version that produced the underlying data (e.g., `listing.normalization_version`).
- `scrapeRunId`: identifier of the last ingestion run contributing to the data (max `listing.last_seen_run_id` over the scoped active listings).

Validation rules:

- Always present on Market Snapshot and Filter Options responses.
- If a field cannot be derived from underlying data, it is `null` rather than omitted; the response MUST NOT appear real-time.
- Raw values only; the frontend owns any presentation.

### FilterOption

Represents a selectable vehicle filter value.

Fields:

- `value`: canonical string or integer for year
- `displayName`: catalog-backed display name or canonical fallback
- `activeListingCount`: optional integer

Validation rules:

- Options cascade by selected higher-level filters.
- Option labels shown by frontend use `displayName`; frontend does not hardcode vehicle names.
- Counts represent active listings in that option under the current higher-level scope.

### VehicleReferenceCatalogEntry

Represents the source of truth for display names.

Fields used by this feature:

- canonical make/model/trim identifiers
- display make/model/trim names
- market or region when available

Validation rules:

- Used for display labels only.
- Does not trigger backend/frontend normalization.

### ListingInput

Represents an existing canonical listing row used as an input to snapshot generation.

Fields used by this feature:

- canonical make
- canonical model
- canonical trim
- year
- active/listing status
- price
- first-seen or created timestamp when available
- removal/lifecycle fields when available
- price-history fields when available

Validation rules:

- Read-only for this feature.
- Raw listing payload remains untouched.
- Listings are never returned as dashboard products in this feature.

## State And Support Behavior

Market Snapshots are generated on request and not persisted for MVP.

Future optimization may introduce materialized snapshots, scheduled snapshot generation, or cache layers behind the same public contract. Those options are explicitly out of implementation scope for this MVP.

Metric extensibility rules:

- Each `MarketMetric` is independently typed and can be added without redesigning the full snapshot contract.
- Future metrics such as Average Mileage, Median Mileage, Days on Market, or Inventory Velocity should be added as new metric types with their own payloads and support statuses.
- Existing metrics must remain backward compatible unless a future contract version explicitly changes them.

History-dependent metric support states:

- New listings: supported only if existing listing metadata can identify newly observed listings in the selected period.
- Removed listings: supported only if existing lifecycle/removal tracking can identify removals in the selected period.
- Net inventory change: supported only when both new and removed counts are supported.
- Price drops: supported only if existing price history can identify drops in the selected period and calculate average drop percentage.

## Data Integrity Rules

- Backend and frontend do not mutate `listing` or `raw_listing`.
- Backend and frontend do not normalize marketplace values.
- Display names come from Vehicle Reference Catalog when available.
- All price-related metrics include sample size.
- Snapshot responses include `generatedAt` and the frontend displays it as `As of <timestamp>`.
- Snapshot and filter-options responses include `freshness` (`lastUpdated`, `datasetVersion`, `scrapeRunId`), distinct from `generatedAt`, and never appear real-time when freshness is unknown.
- Backend returns raw values only; frontend owns AED formatting, separators, localized numbers, and timestamp display formatting.

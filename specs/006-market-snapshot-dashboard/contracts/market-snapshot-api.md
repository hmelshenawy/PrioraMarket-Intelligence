# Contract: Market Snapshot API

## Endpoint

`GET /api/v1/market/snapshot`

## Purpose

Return a generated Market Snapshot for the overall UAE used car market or a selected canonical vehicle scope.

## Query Parameters

| Name | Type | Required | Rules |
|------|------|----------|-------|
| `make` | string | No | Canonical make value. No normalization. |
| `model` | string | No | Canonical model value. Requires `make`. No normalization. |
| `trim` | string | No | Canonical trim value. Requires `make` and `model`. No normalization. |
| `year` | integer | No | Requires `make`, `model`, and `trim`. |
| `periodDays` | integer | No | Defaults to `7`; applies to inventory change and price drops. |

Invalid hierarchy or invalid primitive types return a validation error using existing backend error conventions.

## Response Shape

```json
{
  "scope": {
    "level": "trim",
    "label": "Toyota Corolla XLI",
    "canonical": {
      "make": "toyota",
      "model": "corolla",
      "trim": "xli",
      "year": null
    }
  },
  "filters": {
    "make": "toyota",
    "model": "corolla",
    "trim": "xli",
    "year": null,
    "periodDays": 7
  },
  "period": {
    "days": 7,
    "label": "Last 7 days"
  },
  "metrics": [
    {
      "type": "activeListings",
      "title": "Active Listings",
      "status": { "status": "supported", "dataAvailable": true },
      "count": 4381,
      "scopeLabel": "Toyota Corolla XLI"
    },
    {
      "type": "medianPrice",
      "title": "Median Price",
      "status": { "status": "supported", "dataAvailable": true },
      "amount": 165000,
      "currency": "AED",
      "sampleSize": 842
    },
    {
      "type": "typicalPriceRange",
      "title": "Typical Price Range",
      "status": { "status": "supported", "dataAvailable": true },
      "method": "typical-range",
      "currency": "AED",
      "medianAmount": 165000,
      "lowerAmount": 145000,
      "upperAmount": 190000,
      "minAmount": null,
      "maxAmount": null,
      "sampleSize": 842
    },
    {
      "type": "inventoryChange",
      "title": "Inventory Change",
      "status": { "status": "partial", "dataAvailable": true, "reason": "Removed listing tracking is not available" },
      "activeInventory": 4381,
      "newListings": 126,
      "removedListings": null,
      "netChange": null,
      "periodDays": 7
    },
    {
      "type": "priceDrops",
      "title": "Price Drops",
      "status": { "status": "unsupported", "dataAvailable": false, "reason": "Price history is not available" },
      "count": null,
      "averageDropPercentage": null,
      "sampleSize": null,
      "periodDays": 7
    }
  ],
  "supportStatuses": {
    "activeListings": { "status": "supported", "dataAvailable": true },
    "medianPrice": { "status": "supported", "dataAvailable": true },
    "typicalPriceRange": { "status": "supported", "dataAvailable": true },
    "inventoryChange": { "status": "partial", "dataAvailable": true },
    "priceDrops": { "status": "unsupported", "dataAvailable": false }
  },
  "freshness": {
    "lastUpdated": "2026-07-05T08:00:00.000Z",
    "datasetVersion": "canonical-2024.05",
    "scrapeRunId": 1042
  },
  "generatedAt": "2026-07-05T12:30:00.000Z"
}
```

## Required Metric Order

1. Active Listings
2. Median Price
3. Typical Price Range
4. Inventory Change
5. Price Drops

## Typical Price Range Rules

- Expose the business concept `Typical Price Range`, not statistical implementation details.
- `method` identifies the broad response shape, not the exact statistical formula.
- Internally, the backend may use quartiles, percentiles, IQR, or another deterministic method without changing this contract.
- Use lower/upper raw numeric amounts when a typical range can be calculated.
- Use min/max raw numeric amounts when insufficient priced listings exist for a typical range.
- Include `sampleSize` for every price-related metric.
- Listings without usable prices are excluded from price sample sizes.

## Raw Value Boundary

- Prices are raw numeric amounts plus currency code, not formatted strings.
- Percentages are raw numeric values, not localized strings.
- Timestamps are ISO-8601 strings.
- Frontend owns AED labels, thousand separators, localized numbers, and date formatting.

## Unsupported Metrics

- Unsupported values must be `null`, not fabricated.
- True calculated zeros are allowed only when `status.status` is `supported`.
- `reason` should be present for `unsupported` or `partial` states.

## Read-Only Guarantee

Calling this endpoint must not mutate `listing`, `raw_listing`, catalog, lifecycle, or price-history data.

## Data Freshness

Every response MUST expose a `freshness` object (Constitution Data Freshness principle) with:

- `lastUpdated`: ISO-8601 timestamp of the most recent listing observation contributing to the snapshot (e.g., max `listing.last_seen_at` over the matching scope). Distinct from `generatedAt`, which records when the snapshot was generated and is shown to users as "As of".
- `datasetVersion`: canonical/normalization version that produced the underlying data (e.g., `listing.normalization_version`).
- `scrapeRunId`: identifier of the last ingestion run contributing to the data (e.g., max `listing.last_seen_run_id` over the matching scope).

If a freshness field cannot be derived from underlying data, the response MUST still include the `freshness` block with the field set to `null` (and the snapshot MUST NOT appear real-time). Freshness fields are raw values; the frontend owns their presentation.

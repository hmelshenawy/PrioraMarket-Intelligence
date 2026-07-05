# Contract: Market Filter Options API

## Endpoint

`GET /api/v1/market/filter-options`

## Purpose

Return cascading vehicle filter options for the Market Snapshot dashboard. Options use canonical values internally and catalog-backed display names for presentation.

## Query Parameters

| Name | Type | Required | Rules |
|------|------|----------|-------|
| `make` | string | No | Limits model options to the selected canonical make. |
| `model` | string | No | Requires `make`; limits trim options. |
| `trim` | string | No | Requires `make` and `model`; limits year options. |
| `year` | integer | No | Accepted only as selected state; does not create deeper options. |

## Response Shape

```json
{
  "filters": {
    "make": "toyota",
    "model": "corolla",
    "trim": null,
    "year": null
  },
  "options": {
    "makes": [
      { "value": "toyota", "displayName": "Toyota", "activeListingCount": 4381 },
      { "value": "bmw", "displayName": "BMW", "activeListingCount": 2981 }
    ],
    "models": [
      { "value": "corolla", "displayName": "Corolla", "activeListingCount": 842 }
    ],
    "trims": [
      { "value": "xli", "displayName": "XLI", "activeListingCount": 214 }
    ],
    "years": [
      { "value": 2023, "displayName": "2023", "activeListingCount": 57 }
    ]
  },
  "freshness": {
    "lastUpdated": "2026-07-05T08:00:00.000Z",
    "datasetVersion": "canonical-2024.05",
    "scrapeRunId": 1042
  },
  "generatedAt": "2026-07-05T12:30:00.000Z"
}
```

## Rules

- `value` is canonical and must be submitted back to the snapshot endpoint unchanged.
- `displayName` comes from Vehicle Reference Catalog when available; canonical fallback is allowed when catalog display data is missing.
- `activeListingCount` is optional but should be included when available without extra frontend calls.
- Lower-level options are constrained by selected higher-level filters.
- Backend/frontend must not normalize values or hardcode display names.

## Read-Only Guarantee

Calling this endpoint must not mutate listing, raw listing, or catalog data.

## Data Freshness

Every response MUST expose a `freshness` object (Constitution Data Freshness principle) with `lastUpdated`, `datasetVersion`, and `scrapeRunId`, sourced from the listings that back the returned options (e.g., max `listing.last_seen_at`, `listing.normalization_version`, max `listing.last_seen_run_id` over the scoped active listings). If a field cannot be derived, it MUST be `null` and the response MUST NOT appear real-time. Distinct from `generatedAt`. Freshness fields are raw values; the frontend owns their presentation.

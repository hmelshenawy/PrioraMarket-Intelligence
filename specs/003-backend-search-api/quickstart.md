# Quickstart: Backend Search API

This quickstart describes how the planned backend should be validated after implementation. It is not an implementation script.

## Prerequisites

- PostgreSQL/Supabase database with Feature 002 schema and listing data.
- `DATABASE_URL` pointing to the existing canonical listing database.
- Node.js 20 LTS or newer.
- No scraper changes are required.

## Expected Setup

```powershell
Set-Location backend
npm install
Copy-Item .env.example .env
```

Set `.env` values:

```text
DATABASE_URL=postgresql://user:password@host:5432/database
PORT=3000
```

## Validation Commands

```powershell
npm run build
npm run test
```

## Manual API Smoke Checks

Health:

```text
GET /api/v1/health
```

Expected:

```json
{ "status": "ok" }
```

Default listing search:

```text
GET /api/v1/listings
```

Expected:

- `data` is an array.
- `meta.page` is `1`.
- `meta.limit` is `20`.
- `meta.total` and `meta.totalPages` are present.

Filtered listing search:

```text
GET /api/v1/listings?q=camry&make=Toyota&model=Camry&yearFrom=2018&priceMax=120000&sort=relevance
```

Expected:

- Results match filters.
- Relevance sort applies because `q` is present.

Relevance fallback:

```text
GET /api/v1/listings?sort=relevance
```

Expected:

- Request succeeds.
- Sorting falls back to newest.

Invalid sort:

```text
GET /api/v1/listings?sort=unknown
```

Expected:

- 400 response with stable error shape.

Listing detail:

```text
GET /api/v1/listings/{id}
```

Expected:

- Known id returns listing detail DTO.
- Unknown id returns 404.

Filter metadata:

```text
GET /api/v1/listings/filters
```

Expected:

- Stable metadata shape.
- Cached response path should avoid repeated expensive aggregate queries within 30-60 seconds.

Inventory stats:

```text
GET /api/v1/stats
```

Expected:

- Read-only high-level inventory stats.

## Performance Validation Targets

- Listing search p95 under 300ms with planned indexes.
- Listing detail p95 under 100ms.
- Cached filter metadata p95 under 100ms.
- Health p95 under 50ms.

## Read-Only Verification

API handlers must not call create, update, upsert, delete, or mutation operations against listing or ingestion tables. Integration tests should verify data counts/checksums remain unchanged before and after API calls.

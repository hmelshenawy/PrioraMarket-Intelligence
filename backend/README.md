# PrioraMarket Backend

NestJS read-only Search API for canonical vehicle listing data.

## Setup

```powershell
npm install
Copy-Item .env.example .env
```

Required environment variables:

- `DATABASE_URL`: PostgreSQL/Supabase connection string for the existing canonical listing database.
- `PORT`: HTTP port, defaults to `3000`.
- `NODE_ENV`: runtime environment, for example `development` or `test`.
- `LOG_LEVEL`: structured logging level, for example `info`.
- `FILTER_METADATA_CACHE_TTL_SECONDS`: short TTL for `/api/v1/listings/filters`, defaults to the configured value in source.

## Validation

```powershell
npm run build
npm run test
```

## Quickstart Checks

- `GET /api/v1/health` returns `{ "status": "ok" }` without database access.
- `GET /api/v1/listings` returns `{ data, meta }` with default `page=1` and `limit=20`.
- `GET /api/v1/listings?sort=relevance` succeeds and falls back to newest when no `q` is present.
- `GET /api/v1/listings?sort=unknown` returns a stable 400 error shape.
- `GET /api/v1/listings/{id}` returns listing detail for known ids and 404 for unknown ids.
- `GET /api/v1/listings/filters` returns stable filter metadata and uses short TTL caching.
- `GET /api/v1/stats` returns high-level read-only inventory stats.

The backend must not mutate listing, snapshot, raw listing, marketplace source, or ingestion records.

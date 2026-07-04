# Search Query Optimization

The Search API is read-only and relies on the canonical `listing` table as the source of truth. Query planning should stay aligned with `backend/prisma/migrations/README-search-indexes.md` and remain additive only.

## Expected Indexes

- `status`, because all current inventory reads constrain active/current listings.
- `condition`, `make`, `model`, `year`, `price`, `mileage`, `seller_type`, and `location` for filter predicates.
- `last_seen_at` and `first_seen_at` for newest and lifecycle ordering.
- Composite indexes for common filters such as `status + make + model`, `status + condition + price`, and `status + year + mileage`.
- Text-search support over `title`, `make`, `model`, and `trim` for relevance-backed `q` searches when PostgreSQL full text search is introduced.

## Query Behavior

- Controllers never access Prisma directly.
- `SearchQueryBuilder` owns persistence-query construction and keeps HTTP concerns out of query planning.
- `PrismaListingReadRepository` executes read projections only and maps database rows to domain objects.
- `sort=relevance` uses relevance ordering only when `q` is present; otherwise the service falls back to newest ordering.
- Filter metadata should be served from the short TTL cache where possible to avoid repeated wide reads.

## Validation Targets

- Listing search p95 under 300ms with planned indexes.
- Listing detail p95 under 100ms.
- Cached filter metadata p95 under 100ms.
- Health p95 under 50ms and without database dependency.

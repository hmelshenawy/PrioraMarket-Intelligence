# Search Index Plan

Feature 003 is read-only at runtime. These indexes are an additive plan for search performance and must be applied only through approved database migration governance.

Planned indexes:

- `listing(condition)`
- `listing(make)`
- `listing(model)`
- `listing(year)`
- `listing(price)`
- `listing(mileage)`
- `listing(seller_type)`
- `listing(location)`
- `listing(last_seen_at)`
- `listing(first_seen_at)` if first-seen ordering is needed
- Composite: `(condition, make, model)`
- Composite: `(make, model)`
- Composite: `(last_seen_at DESC, id DESC)`
- Text search: weighted GIN `tsvector` over `title`, `make`, `model`, and `trim`

Do not modify scraper behavior or mutate listing/ingestion records as part of this API feature.

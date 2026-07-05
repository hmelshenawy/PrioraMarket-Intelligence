# Quickstart: Market Snapshot Dashboard

This quickstart describes the intended implementation and validation sequence. It does not provide implementation code.

## Prerequisites

- Final approved spec: `specs/006-market-snapshot-dashboard/spec.md`
- Plan artifacts in `specs/006-market-snapshot-dashboard/`
- Feature 005 canonical listing fields and Vehicle Reference Catalog display names available in PostgreSQL
- Backend Prisma schema synchronized with the current database shape
- Frontend environment configured to call the backend API

## Recommended Execution Sequence

1. Review `research.md`, `data-model.md`, and contracts before generating tasks.
2. Confirm existing schema fields for active listing status, canonical make/model/trim/year, price, first-seen/created timestamp, removal tracking, and price history.
3. Create backend analytics domain/DTO/mapper shapes from `data-model.md`.
4. Add backend contract tests for `GET /api/v1/market/snapshot` and `GET /api/v1/market/filter-options`.
5. Implement `SnapshotReadRepository` and `FilterReadRepository` for read-only data access.
6. Implement the simple market aggregation layer and Market Snapshot service orchestration.
7. Add market controller endpoints and query validation.
8. Add backend repository, service, integration, contract, and read-only safety tests.
9. Add frontend market dashboard API client, schemas/types, query keys, and hooks.
10. Build dashboard UI with `DashboardShell`, `MarketFilterBar`, `SnapshotMetrics`, individual metric components, timestamp, loading/empty/unsupported states, and dark-mode-compatible styling.
11. Add frontend unit, component, interaction, and end-to-end tests.
12. Review whether indexes are needed using query plans; add only if measurable benefit is shown.
13. Update API documentation and run final validation.

## Expected Backend Commands

Run from `backend/`:

- `npm run prisma:generate`
- `npm run build`
- `npm run test:unit`
- `npm run test:integration`
- `npm run test:contract`

Focused tests should include market snapshot service tests, repository aggregation tests, endpoint contract tests, and read-only safety tests.

## Expected Frontend Commands

Run from `frontend/`:

- `npm run lint`
- `npm run typecheck`
- `npm run test`
- `npm run e2e`
- `npm run build`

When editing Next.js app structure, read the local Next.js documentation under `frontend/node_modules/next/dist/docs/` first because the project uses a newer Next.js version with breaking changes.

## Endpoint Smoke Checks

Overall snapshot:

```text
GET /api/v1/market/snapshot
```

Filtered snapshot:

```text
GET /api/v1/market/snapshot?make=toyota&model=corolla&trim=xli&year=2023&periodDays=7
```

Overall filter options:

```text
GET /api/v1/market/filter-options
```

Cascading filter options:

```text
GET /api/v1/market/filter-options?make=toyota&model=corolla
```

## Validation Checklist

- Overall dashboard loads with no filters.
- Filtered dashboard updates for make, model, trim, and year without full page reload.
- Snapshot response includes scope, canonical filters, metrics, support statuses, selected period, and `generatedAt`.
- Frontend displays `As of <timestamp>` from `generatedAt`.
- Metrics render as cards in the required order.
- Active listings, median price, price range, and sample sizes match canonical listing data.
- Typical Price Range exposes the business concept and does not require API consumers to know the internal statistical method.
- Inventory Change does not fabricate removed or net-change values when removal tracking is unsupported.
- Price Drops does not fabricate values when price history is unsupported.
- Filter options use API display names and include active listing counts when provided.
- Backend returns raw values; frontend owns currency, number, percentage, and timestamp formatting.
- No backend or frontend normalization logic is introduced.
- `listing` and `raw_listing` remain unchanged by market endpoint calls.
- Existing dark mode continues to work.

## Out-Of-Scope Guardrails

Do not implement vehicle valuation, fair-price score, AI insights, forecasting, trend prediction, trend charts, listing detail pages, marketplace browsing, scraper changes, normalization work, or historical analytics beyond the current snapshot contract.

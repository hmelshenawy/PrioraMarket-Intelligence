# PrioraMarket Intelligence

**Market intelligence for the UAE used-car market — built on structured, canonical marketplace data.**

PrioraMarket transforms vehicle listings into an analytics-oriented dataset, helping analysts, dealers, buyers, and sellers understand inventory, pricing, and market activity without treating the product as another listings marketplace.

> **Core question:** Not just *“Which cars are for sale?”* but *“What is happening in the market?”*

## Product capabilities

| Capability | Purpose |
| --- | --- |
| Market Snapshot Dashboard | View active inventory, median price, typical price range, inventory movement, and price-drop indicators |
| Cascading vehicle filters | Explore market segments by make, model, trim, and year |
| Vehicle Reference Catalog | Maintain canonical identifiers and readable vehicle display names |
| Marketplace ingestion | Collect source listing data for downstream processing |
| Replay and backfill | Reprocess historical data using versioned canonicalization logic |
| Data freshness | Distinguish snapshot generation time from the latest underlying listing observation |

**Data quality matters:** A missing or unsupported history-based metric is not represented as zero. Snapshot responses distinguish supported, partial, unavailable, and unsupported metrics.

## System architecture

```text
    Automotive Marketplace Sources
                  |
                  v
          Python Ingestion
          (Requests / BS4)
                  |
                  v
       Canonicalization Engine
       + Vehicle Reference Catalog
                  |
                  v
             PostgreSQL
       raw listings + canonical data
                  |
                  v
          NestJS Analytics API
          (read-only analytics)
                  |
                  v
           Next.js Dashboard
         (React / TanStack Query)
```

### Architecture boundaries

- **Python ingestion owns data quality:** scraping, canonicalization, catalog synchronization, replay, and backfill.
- **PostgreSQL separates source and analytical representations:** raw listing payloads are preserved while canonical listing fields can be reprocessed.
- **NestJS owns analytical queries and contracts:** the API consumes normalized data rather than implementing marketplace-specific normalization rules.
- **Next.js owns presentation:** dashboard cards and filters render catalog-backed display names and explicit data support states.

These boundaries help keep normalization deterministic and reusable as more data sources or analytical features are added.

## Market Snapshot

The dashboard is designed around five metrics:

1. **Active Listings** — the current observed inventory for a selected scope.
2. **Median Price** — the midpoint of usable listing prices.
3. **Typical Price Range** — a representative pricing interval, with sample-size context.
4. **Inventory Change** — recent new and removed listings, where lifecycle history supports the calculation.
5. **Price Drops** — seller price reductions, where price history is available.

Users can narrow the analysis from the overall UAE market to a specific make, model, trim, and year. Dependent filters use canonical catalog values, while users see readable labels.

Snapshots carry a generation timestamp and data-freshness metadata so users can distinguish **when the analysis was generated** from **when the underlying listings were last observed**.

## Technology stack

| Layer | Technologies |
| --- | --- |
| Data ingestion | Python, Requests, BeautifulSoup |
| Data processing | Versioned canonicalization, reference catalog, replay/backfill |
| Storage | PostgreSQL |
| Backend | NestJS, TypeScript, Prisma |
| Frontend | Next.js, React, TanStack Query, Tailwind CSS |
| Development approach | Specification-driven feature development |

## Repository structure

```text
scrapper/    # Ingestion, canonicalization, replay, backfill, catalog
backend/     # Analytics API and database access
frontend/    # Market dashboard and vehicle filters
specs/       # Feature specifications, design, and implementation plans
```

## Engineering highlights

### Canonical vehicle model
Marketplace-specific naming variations are mapped to canonical make, model, and trim values. A Vehicle Reference Catalog provides display names and a consistent vocabulary across ingestion and analytics.

### Replayable processing
Versioned normalization and replay/backfill workflows allow historical listings to be reprocessed without overwriting the original raw source records.

### Read-only analytical API
The backend operates on the canonical dataset; it does not silently re-normalize vehicles or mutate marketplace source data.

### Explicit analytical uncertainty
Missing history, insufficient price samples, and unsupported metrics are represented explicitly. This prevents a dashboard from presenting misleading precision.

### Scope-aware market analysis
The same analytical model supports both broad market snapshots and narrowly filtered vehicle segments.

## Getting started

Configure each service's required environment variables and ensure PostgreSQL is available.

**Backend**

```bash
cd backend
npm install
npm run start:dev
```

**Frontend**

```bash
cd frontend
npm install
npm run dev
```

**Ingestion**

```bash
cd scrapper
python -m src.ingestion.runner scrape
```

These commands assume the corresponding dependencies and database configuration are already in place. Consult the relevant service configuration and feature quickstarts before running ingestion against a live source.

## Testing

```bash
# Backend (from backend/)
npm test

# Frontend (from frontend/)
npm test

# Scraper (from scrapper/)
pytest
```

## Technical documentation

The [Market Snapshot feature specification](specs/006-market-snapshot-dashboard/spec.md) describes the intended user experience, edge cases, and support-status behavior. The [data model](specs/006-market-snapshot-dashboard/data-model.md) details the analytical response contract, filtering hierarchy, and freshness semantics.

## Roadmap

**Current project scope:** marketplace ingestion, canonical vehicle processing, reference catalog, replay/backfill workflows, and the Market Snapshot Dashboard.

**Future directions:** historical market trends, vehicle valuation, price benchmarks, and AI-assisted market insights. These are roadmap items, not claims of implemented AI functionality.

---

PrioraMarket is an **analytics platform, not an automotive classifieds marketplace**. Its purpose is to turn observed listing data into explainable market signals.

# Research: Market Snapshot Dashboard

## Decision: Generate Market Snapshots On Demand

**Rationale**: The MVP returns five market metrics for a selected scope and period. On-demand generation keeps the feature lightweight, avoids snapshot storage, and preserves clear freshness through `generatedAt`. It also matches the read-only backend requirement because no market data is mutated or persisted.

**Alternatives considered**: Persisted snapshot table was rejected because there is no proven performance need and it would add freshness, invalidation, and ownership questions. Scheduled pre-aggregation was rejected for the same reason. Redis caching was rejected because the request volume and query cost are not yet demonstrated to justify another service. Future materialized snapshots, scheduled generation, or cache layers may be introduced behind the same public APIs if evidence later justifies them.

## Decision: Use A Small Aggregation Layer Above Focused Read Repositories

**Rationale**: Controllers must not contain aggregation logic, services should orchestrate, and repositories should remain data-access only. A small `MarketSnapshotAggregator` owns reusable calculations while `SnapshotReadRepository` and `FilterReadRepository` provide focused read models.

**Alternatives considered**: Putting queries directly in the controller violates layered architecture. Putting all SQL and calculations in the service blurs orchestration and analytics. A single catch-all read repository was rejected because analytics will grow. Creating a generic analytics framework is too heavy for an MVP.

## Decision: New Backend `AnalyticsModule` Instead Of `MarketModule` Or Extending `search`

**Rationale**: Feature 006 is an Analytics bounded-context feature. `AnalyticsModule` is more future-proof than `MarketModule` for deterministic snapshots and future analytics capabilities while still implementing only the Market Snapshot MVP. Search/listing modules can remain listing-centric, while Analytics owns snapshot, metric, support-status, and aggregation concepts.

**Alternatives considered**: Extending `search` was rejected because it reinforces listing-first design and mixes analytics responsibilities with listing retrieval. `MarketModule` was rejected as too narrow for long-term analytics ownership, though public routes remain `/api/v1/market/...` to match the product surface.

## Decision: Backend Owns Analytics, Frontend Owns Presentation Only

**Rationale**: The constitution requires backend-centric business logic and analytics before AI. The frontend should not calculate median, percentiles, net inventory change, support statuses, or display-name resolution. It consumes stable snapshot contracts and renders them.

**Alternatives considered**: Client-side aggregation was rejected because it would require transferring listing-level data, duplicate business logic, and risk turning the UI into listing browsing. Shared frontend/backend analytics helpers were rejected as unnecessary and potentially boundary-blurring.

## Decision: Typical Price Range With Internal Statistical Flexibility

**Rationale**: The public contract should expose `Typical Price Range`, a business concept, rather than locking API consumers to quartiles or another statistical method. Internally, P25/P75 is a good MVP implementation when enough priced listings exist; for small samples, min/max is more honest than pretending percentile values are robust. Every price metric includes sample size so users can interpret confidence.

**Alternatives considered**: Exposing P25/P75 as the public business contract was rejected because it couples clients to one statistical implementation. Always min/max was rejected as too sensitive to outliers. Always P25/P75 was rejected for sparse scopes. Adding advanced outlier detection was rejected as beyond MVP.

## Decision: Keep Snapshot And Filter Options As Separate APIs

**Rationale**: Snapshot data and filter options have different responsibilities and refresh patterns. Keeping separate endpoints preserves separation of concerns, while frontend query caching and parallel requests avoid unnecessary repeated calls. Embedding all filter options in every snapshot would increase payload size and couple independent concerns.

**Alternatives considered**: A single combined endpoint was rejected for MVP because it makes snapshot contracts heavier and less focused. An optional expansion parameter can be considered later if evidence shows a real UX or performance benefit.

## Decision: API Returns Raw Values; Frontend Formats

**Rationale**: Backend contracts should return raw counts, numeric amounts, percentages, timestamps, and currency codes. Presentation formatting such as AED labels, thousand separators, localized numbers, and date formatting belongs entirely to the frontend.

**Alternatives considered**: Backend-formatted display strings were rejected because they reduce client flexibility, complicate localization, and mix presentation concerns into backend analytics.

## Decision: Unsupported Contracts For Missing History Metrics

**Rationale**: Removed-listing and price-drop metrics depend on lifecycle and price-history data. The product must not fabricate values. Returning explicit support statuses lets the UI communicate unavailable capability while preserving the card narrative.

**Alternatives considered**: Returning zero for all unsupported values was rejected because it can be misread as true market behavior. Hiding the cards was rejected because the spec requires graceful unsupported states and a stable dashboard narrative.

## Decision: No Pagination For Filter Options In MVP

**Rationale**: Make/model/trim/year option sets are bounded and selected through cascading filters. Including active listing counts in each option avoids extra frontend calls. Pagination would complicate UX and state without clear benefit.

**Alternatives considered**: Paginated options and typeahead search were rejected for MVP. They can be reconsidered if option counts become too large for responsive dropdowns.

## Decision: Indexes Only After Query-Plan Evidence

**Rationale**: Candidate indexes on active status, canonical vehicle dimensions, and price may improve aggregation, but adding indexes prematurely can slow ingestion writes and increase storage. The plan requires measuring query plans before adding schema changes.

**Alternatives considered**: Adding all suggested indexes by default was rejected as premature optimization. Adding no indexes regardless of evidence was rejected because snapshot queries must remain usable.

## Decision: Local URL/Query State For Dashboard Filters

**Rationale**: Filter state is local to the dashboard and naturally shareable via URL query parameters. TanStack Query can refresh snapshot and filter-option data using filter-dependent query keys without full page reloads.

**Alternatives considered**: Global state was rejected as unnecessary for a single dashboard surface. Server-only navigation for every filter change was rejected because the spec requires responsive updates without full reload.

## Decision: Expose Constitution Data Freshness Metadata On Every Analytical Response

**Rationale**: Constitution 1.1.0 (Data Engineering Principles → Data Freshness) mandates that every analytical response expose `last_updated`, `dataset_version`, and `scrape_run_id`, and that analytics must never appear real-time when generated from historical snapshots. The Market Snapshot and Filter Options responses are the platform's primary analytical responses, so the feature MUST include a `freshness` block. The schema already provides the sources: `listing.last_seen_at` → `lastUpdated`, `listing.normalization_version` → `datasetVersion`, `listing.last_seen_run_id` → `scrapeRunId`. `generatedAt` (already required by FR-005 for "As of") is generation time and remains distinct from `freshness.lastUpdated` (data recency).

**Alternatives considered**: Omitting freshness and relying only on `generatedAt` was rejected because it violates the Constitution Data Freshness principle and would let users act on stale intelligence as if it were current. Backfilling a separate freshness microservice was rejected as new infrastructure with no proven need; the fields are derived directly from existing listing columns. Making freshness a future-feature concern was rejected because the Constitution makes it mandatory from day one for every analytical response.

## Decision: No Scraper Changes For Feature 006

**Rationale**: The scraper owns ingestion, canonicalization, replay, backfill, Vehicle Reference Catalog, and PostgreSQL population, but Feature 006 consumes the completed Feature 005 data foundation. Planning scraper changes would expand scope into normalization or historical analytics work that is explicitly out of scope.

**Alternatives considered**: Adding scraper-derived materialized analytics was rejected for MVP because it introduces persistence and scheduling complexity. Any future historical analytics pipeline should be specified separately.

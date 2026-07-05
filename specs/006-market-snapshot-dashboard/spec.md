# Feature Specification: Market Snapshot Dashboard

**Feature Branch**: `006-market-snapshot-dashboard`

**Created**: 2026-07-05

**Status**: Draft

**Input**: User description: "Feature 006 - Market Snapshot Dashboard. Build PrioraMarket as a market intelligence dashboard, not an e-commerce or listings marketplace. Show generated market snapshots with aggregated analytics cards for overall and selected vehicle scopes using canonical listing data and Vehicle Reference Catalog display names."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Overall Market Snapshot (Priority: P1)

As a user, I want to see a high-level snapshot of the UAE used car market, so I can understand the current market status quickly without browsing individual listings.

**Why this priority**: This is the core product direction for PrioraMarket and provides immediate value as a market intelligence dashboard.

**Independent Test**: Can be fully tested by opening the dashboard with no filters and confirming that a generated market snapshot shows market-level cards in the intended order, includes an "As of" timestamp, and shows clear unsupported states where needed.

**Acceptance Scenarios**:

1. **Given** market listing data exists, **When** a user opens the dashboard without selecting filters, **Then** the dashboard shows a generated overall market snapshot with active listings, median price, price range, inventory change, and price drops in that order.
2. **Given** a required history-based metric is not supported, **When** the overall dashboard loads, **Then** the related card shows a clear unsupported or unavailable status instead of a fabricated value.
3. **Given** the overall market snapshot is shown, **When** the user reads the dashboard header, **Then** it displays a human-readable scope label such as "Overall UAE Used Cars" and an "As of" timestamp for when the snapshot was generated.

---

### User Story 2 - Filtered Vehicle Snapshot (Priority: P2)

As a user, I want to select make, model, trim, and year from dropdown filters, so the same dashboard cards update for the selected vehicle scope.

**Why this priority**: Vehicle-scoped snapshots allow users to move from broad market understanding to focused segment analysis while keeping the experience dashboard-first.

**Independent Test**: Can be fully tested by selecting valid cascading filter combinations and confirming the generated market snapshot updates to reflect only the selected scope without requiring a full page reload.

**Acceptance Scenarios**:

1. **Given** the dashboard is loaded, **When** a user selects a make, **Then** all cards update for that make and the available model options are limited to that make.
2. **Given** a make and model are selected, **When** a user selects a trim and year, **Then** all cards update for that make, model, trim, and year scope and the scope label reflects the selected vehicle display names.
3. **Given** a user changes a higher-level filter, **When** the selected lower-level filters no longer apply, **Then** invalid lower-level selections are cleared or made unavailable before cards update.

---

### User Story 3 - Catalog-Based Display Names (Priority: P3)

As a user, I want dropdowns and dashboard labels to show clean vehicle display names, while the system internally uses canonical vehicle values.

**Why this priority**: Clean labels improve user trust and readability while preserving canonical data integrity from the completed vehicle reference catalog.

**Independent Test**: Can be fully tested by comparing dropdown labels and scope labels against the vehicle reference catalog for vehicles that have catalog display names.

**Acceptance Scenarios**:

1. **Given** a catalog display name exists for a vehicle value, **When** the value appears in a filter or dashboard scope label, **Then** the display name shown to the user matches the catalog display name.
2. **Given** a vehicle value lacks a catalog display name, **When** it appears in the dashboard, **Then** the user still sees a readable fallback based on the existing canonical value without introducing new normalization rules.
3. **Given** filter options are shown, **When** active listing counts are available for those options, **Then** each option may include the count alongside its display name, such as "Toyota (4,381)".

---

### User Story 4 - Market Activity and Price Drops (Priority: P4)

As a user, I want to know whether the selected market scope is growing, shrinking, or showing seller price reductions during the recent period.

**Why this priority**: Activity and price-drop context adds market movement insight, but it depends on historical tracking that may not yet be fully available.

**Independent Test**: Can be fully tested by viewing the inventory change and price-drop cards for the default period and confirming they show supported values when available or clear unsupported states when not available.

**Acceptance Scenarios**:

1. **Given** recent new-listing data is available, **When** the dashboard loads for any supported scope, **Then** the inventory change card shows active inventory and new listings for the selected period.
2. **Given** removed-listing tracking is available, **When** the dashboard loads, **Then** the inventory change card shows removed listings and net inventory change calculated as new listings minus removed listings.
3. **Given** removed-listing tracking is unavailable, **When** the dashboard loads, **Then** the removed-listings and net-change values show unsupported status and are not fabricated.
4. **Given** price history is unavailable or incomplete, **When** the dashboard loads, **Then** the price-drops card shows null or unsupported values with a clear support status instead of fake counts or percentages.

### Edge Cases

- If no active listings match the selected scope, all count and price cards show empty-state values with sample size zero and no misleading price numbers.
- If matching listings exist but none have usable prices, price metrics show unavailable values while active-listing count remains visible.
- If insufficient priced listings exist for percentile-based price range, the price range falls back to min and max with the price sample size shown.
- If the selected period is missing, the dashboard uses the default recent period of 7 days.
- If the selected period is outside accepted bounds, the user receives a clear validation message or the value is constrained to an accepted range.
- If catalog display names are missing for a canonical value, the dashboard uses the canonical value as a fallback without transforming or normalizing it.
- If history-dependent metrics are unsupported, the dashboard distinguishes unsupported status from a true zero result.
- If a user selects filters in an unsupported hierarchy, lower-level selections are cleared or disabled so the active scope remains valid.
- If snapshot data refreshes after a filter change, the dashboard preserves the page context and updates the cards without a full page reload.
- If a freshness field cannot be derived from underlying data (for example, no ingestion run recorded), the response still exposes the freshness block with a null value and a clear reason rather than omitting the block, so analytics never appear real-time when freshness is unknown.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: PrioraMarket MUST present itself as a Market Intelligence platform where dashboard analytics are the primary experience, and MUST NOT present itself as an e-commerce or listings marketplace.
- **FR-002**: Listing browsing, if introduced by future features, MUST remain secondary and intended only for drill-down workflows, not as the primary product experience.
- **FR-003**: The system MUST generate a Market Snapshot as the primary domain object shown by the dashboard; listings are only an input source used to generate the snapshot.
- **FR-004**: Each Market Snapshot MUST include scope, applied canonical filters, analytics cards, metric support statuses, selected period, and generatedAt timestamp.
- **FR-005**: The dashboard MUST display the generatedAt timestamp as "As of <timestamp>" so users understand when the snapshot was generated.
- **FR-006**: The system MUST support an overall market scope with no vehicle filters selected.
- **FR-007**: The system MUST support filtered scopes at these levels: make; make plus model; make plus model plus trim; and make plus model plus trim plus year.
- **FR-008**: The Market Snapshot MUST expose both canonical filters and a human-readable scope label generated from Vehicle Reference Catalog display names when available.
- **FR-009**: Scope labels MUST follow the selected level, such as "Overall UAE Used Cars", "Toyota", "Toyota Corolla", "Toyota Corolla XLI", or "Toyota Corolla XLI 2023".
- **FR-010**: Analytics cards MUST appear in this order: Active Listings, Median Price, Price Range, Inventory Change, and Price Drops.
- **FR-011**: The system MUST calculate active listing count from canonical listing vehicle fields for the selected snapshot scope.
- **FR-012**: The system MUST calculate median price from available listing prices for the selected snapshot scope and include the number of listings used in the calculation.
- **FR-013**: Every price-related metric MUST include the number of listings used in that calculation.
- **FR-014**: Price range SHOULD use median, 25th percentile (P25), and 75th percentile (P75) when enough priced listings exist to support robust percentile values.
- **FR-015**: If insufficient priced listings exist for robust percentiles, price range MUST fall back to minimum and maximum price and include the price sample size.
- **FR-016**: The system MUST show an Inventory Change card with active inventory, new listings for the selected period, removed listings when supported, and net inventory change calculated as new listings minus removed listings when both inputs are supported.
- **FR-017**: The system MUST show removed-listing and net-change values with unsupported status when removal tracking is unavailable, and MUST NOT fabricate values.
- **FR-018**: The system MUST show the count of listings with price drops, average price-drop percentage, and price-drop sample size for the selected snapshot scope and period when sufficient price history exists.
- **FR-019**: The system MUST show price-drop metrics as null with a clear unsupported or unavailable status when sufficient price history does not exist.
- **FR-020**: The system MUST default inventory change and price-drop period calculations to the last 7 days when no period is selected.
- **FR-021**: The system MUST allow users to choose filter values from cascading dropdown options, where each lower-level option list is limited by the selected higher-level values.
- **FR-022**: Each selectable filter option MAY include canonical value, display name, and active listing count so users can understand option size before selection.
- **FR-023**: The system MUST display make, model, trim, and dashboard scope labels using Vehicle Reference Catalog display names when available.
- **FR-024**: The system MUST use canonical listing values for internal filtering and calculations, and MUST NOT introduce new marketplace normalization logic.
- **FR-025**: The system MUST NOT mutate listing data or raw listing data while producing dashboard analytics.
- **FR-026**: The system MUST preserve the raw listing record unchanged as an immutable source artifact for this feature.
- **FR-027**: The user interface MUST use display names provided by market data responses and MUST NOT hardcode vehicle display names.
- **FR-028**: The user interface MUST show unsupported and unavailable metric states gracefully, with language that distinguishes missing support from real zero values.
- **FR-029**: Changing filters MUST refresh the Market Snapshot and update dashboard cards without requiring a full page reload.
- **FR-030**: Existing light and dark visual modes MUST continue to work for the dashboard and all analytics cards.
- **FR-031**: The feature MUST exclude listing detail pages, e-commerce-style listing browsing, AI insights, vehicle valuation, fair-price scoring, market health scoring, forecasting, advanced trend charts, manual data updates, and new normalization behavior.
- **FR-032**: Every Market Snapshot and Filter Options analytical response MUST expose freshness metadata containing `lastUpdated`, `datasetVersion`, and `scrapeRunId`, per the Constitution Data Freshness principle, so users can distinguish a generated snapshot from a live market reading.
- **FR-033**: The dashboard MUST keep `generatedAt` (snapshot generation time, shown as "As of") and `freshness.lastUpdated` (underlying data recency) as distinct values, and MUST NOT present analytics as real-time when generated from historical snapshots.

### Key Entities *(include if feature involves data)*

- **Market Snapshot**: The primary domain entity for this feature. It represents a generated market-status view for a selected scope and includes scope, applied canonical filters, analytics cards, metric support statuses, selected period, and generatedAt timestamp.
- **Market Scope**: The vehicle segment selected by the user, ranging from the overall UAE used car market to make, model, trim, and year combinations, with both canonical filters and a human-readable scope label.
- **Analytics Card**: A dashboard metric block in the required narrative order: active listings, median price, price range, inventory change, and price drops.
- **Inventory Change**: A market movement summary containing active inventory, new listings, removed listings when supported, and net inventory change when both new and removed counts are supported.
- **Filter Option**: A selectable vehicle value with a canonical value, a catalog-sourced display name when available, and an optional active listing count.
- **Vehicle Reference Catalog Entry**: The source of truth for clean vehicle display names associated with canonical make, model, and trim values.
- **Listing**: An input source used to generate Market Snapshots through counting, filtering, and price calculations; it is not the primary entity represented by the dashboard.
- **Raw Listing**: The untouched original listing source record, which remains unchanged and is not used for presentation normalization.
- **Metric Support Status**: A status attached to metrics that may be fully supported, unsupported, unavailable, or partially available based on existing data coverage.
- **Freshness Metadata**: Metadata exposed on every analytical response describing how recent the underlying data is, including `lastUpdated` (most recent listing observation time), `datasetVersion` (canonical/normalization version that produced the data), and `scrapeRunId` (last ingestion run contributing to the data). Distinct from `generatedAt`, which records when the snapshot was generated.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 95% of users can identify active listings, median price, price range, inventory change status, and snapshot generation time for the overall market within 10 seconds of opening the dashboard.
- **SC-002**: 95% of users can apply a make, model, trim, and year filter sequence and see updated dashboard cards without a full page reload within 30 seconds.
- **SC-003**: For scopes with at least one active priced listing, active-listing count, median price, P25/P75 price range when supported, fallback min/max range when needed, and all price sample sizes match the available canonical listing data in 100% of validation checks.
- **SC-004**: For history-dependent metrics that are not supported, 100% of affected cards show a clear unsupported or unavailable status rather than fabricated market values.
- **SC-005**: 100% of vehicle labels shown in filters and scope labels use catalog display names when those names are available.
- **SC-006**: No raw listing records are changed by using or refreshing the dashboard in 100% of validation checks.
- **SC-007**: 90% of test users describe the experience as a market snapshot or analytics dashboard rather than a listings marketplace during usability review.
- **SC-008**: 100% of generated snapshots include scope, applied canonical filters, analytics cards, metric support statuses, selected period, and generatedAt timestamp in validation checks.
- **SC-009**: 100% of Market Snapshot and Filter Options responses include freshness metadata with `lastUpdated`, `datasetVersion`, and `scrapeRunId` in validation checks.

## Assumptions

- The primary user is any PrioraMarket visitor or stakeholder who wants a quick market-status summary, with no new role or permission distinctions introduced by this feature.
- The completed vehicle reference catalog contains canonical values and display names for at least the most important make, model, and trim values.
- Existing listing records contain canonical make, model, trim, year, active status, and price fields sufficient to generate baseline Market Snapshots.
- Newly observed listings can be identified from existing listing metadata; if not, the new-listings metric follows the same support-status pattern as other history-dependent metrics.
- Removed-listing and price-history coverage may be incomplete, so this feature prioritizes honest support statuses over estimated or synthetic values.
- Price metrics exclude listings without usable price values from price calculations while still counting them in active listings when they match the selected scope.
- Percentile-based price range requires enough usable priced listings to avoid misleading users; otherwise the snapshot returns min and max as the fallback range.
- The accepted period for v1 is expressed in days and defaults to 7 days.

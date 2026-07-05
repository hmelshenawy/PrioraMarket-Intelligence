# Contract: Frontend Market Dashboard

## Owner

Next.js frontend as presentation-only consumer of backend Market Snapshot APIs.

## Page Behavior

- The Market Snapshot Dashboard is the primary experience introduced by Feature 006; broader navigation and routing decisions remain outside this feature plan.
- The page displays a Market Snapshot, not listing products.
- The header shows the human-readable scope label and `As of <timestamp>` from `generatedAt`.
- Metrics render as cards in this order: Active Listings, Median Price, Typical Price Range, Inventory Change, Price Drops.
- Changing make/model/trim/year filters refreshes snapshot data without a full page reload.
- Changing a higher-level filter clears or disables invalid lower-level selections.

## State Contract

- Filter state may be stored in URL query parameters and local dashboard state.
- TanStack Query keys should include canonical filters and period.
- No global application state is required unless existing app conventions require it.
- Frontend does not calculate analytics or support statuses.

## Component Structure

- `DashboardShell` owns the page frame, header, scope label, and `As of <timestamp>` placement.
- `MarketFilterBar` owns cascading filter controls and selected filter display.
- `SnapshotMetrics` owns the ordered metric layout.
- Individual metric components own presentation for Active Listings, Median Price, Typical Price Range, Inventory Change, and Price Drops.
- Shared state components handle loading, empty, unsupported, and error states.

## Rendering Contract

- Use `displayName` from API for filter labels.
- Do not hardcode vehicle display names.
- Do not normalize canonical values.
- Show active listing counts in filter options when provided, such as `Toyota (4,381)`.
- Show price sample sizes, such as `Based on 842 listings`.
- Show unsupported metrics with clear explanatory text, not fake values.
- Format raw backend values in the frontend only, including AED labels, thousand separators, localized numbers, percentages, and `As of` timestamp display.
- Preserve existing dark mode behavior and responsive layout.
- `freshness` (`lastUpdated`, `datasetVersion`, `scrapeRunId`) is consumed as raw metadata and MUST NOT be presented to users as a real-time market reading; "As of <generatedAt>" remains the user-facing recency cue.

## Empty And Unsupported States

- Zero active listings: cards show empty-state values and sample size zero.
- No usable prices: price cards show unavailable values and sample size zero.
- Unsupported removed tracking: removed listings and net change show unsupported state.
- Unsupported price history: price drops show unsupported state.
- API errors: show a recoverable error state without navigating to listing browsing.

## Verification

- Component tests cover card order, timestamp, sample sizes, unsupported states, and dark-mode classes/variants where practical.
- Interaction tests cover filter changes and no full page reload.
- E2E tests cover overall snapshot load and filtered snapshot load.

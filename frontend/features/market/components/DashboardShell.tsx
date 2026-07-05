"use client"

import { SnapshotMetrics } from "./SnapshotMetrics"
import { ScopeLabel } from "./ScopeLabel"
import { AsOfTimestamp } from "./AsOfTimestamp"
import { MarketFilterBar } from "./MarketFilterBar"
import { useMarketFiltersFromUrl, useMarketSnapshot } from "../hooks/use-market-snapshot"
import type { MarketFilterSelectionDto } from "../types"

// Dashboard page frame: header (scope label + "As of" timestamp), the cascading filter
// bar, and the metrics grid. Filter selection lives in the URL via useMarketFiltersFromUrl;
// changing a select updates the URL client-side (no full page reload) and TanStack Query
// re-fetches the snapshot + filter-options because the canonical query key changes.
// Freshness metadata flows through the view model as raw metadata — never displayed as a
// real-time reading.
export function DashboardShell() {
  const { request, setFilters } = useMarketFiltersFromUrl()
  const { data, isLoading, isFetching, error, refetch } = useMarketSnapshot(request)

  const selection: MarketFilterSelectionDto = {
    make: request.make,
    model: request.model,
    trim: request.trim,
    year: request.year
  }

  function handleSelectionChange(next: MarketFilterSelectionDto) {
    // Preserve periodDays from the URL; filter changes update only the vehicle scope.
    setFilters({ ...next, periodDays: request.periodDays })
  }

  return (
    <section
      className="flex flex-col gap-6"
      aria-busy={isFetching && !isLoading ? "true" : undefined}
      aria-label="Market snapshot dashboard"
    >
      <header className="flex flex-wrap items-end justify-between gap-2">
        <ScopeLabel
          label={data?.scopeLabel ?? "Overall UAE Used Cars"}
          level={data?.scopeLevel ?? "overall"}
        />
        {data && <AsOfTimestamp asOf={data.asOf} />}
      </header>

      <MarketFilterBar selection={selection} onSelectionChange={handleSelectionChange} />

      <SnapshotMetrics
        data={data}
        isLoading={isLoading}
        error={error}
        onRetry={() => refetch()}
      />
    </section>
  )
}
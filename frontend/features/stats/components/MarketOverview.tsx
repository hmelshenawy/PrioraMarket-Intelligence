"use client"

import { Card } from "@/components/ui/Card"
import { ErrorState } from "@/components/ui/ErrorState"
import { useMarketStats } from "../hooks/useMarketStats"
import type { MarketStatsModel } from "../types"
import { SummarySkeleton } from "./SummarySkeleton"

// Metric tile descriptor — label + formatted value derived from the model
// through shared formatting utilities (no hard-coded placeholders here).
interface Metric {
  label: string
  value: string
}

function metricsFrom(m: MarketStatsModel): Metric[] {
  return [
    { label: "Total listings", value: m.totalListings },
    { label: "Used", value: m.usedListings },
    { label: "New", value: m.newListings },
    { label: "Makes", value: m.totalMakes },
    { label: "Models", value: m.totalModels },
    { label: "Avg. price", value: m.averagePrice },
  ]
}

// MarketOverview — concise inventory summary rendered independently of search.
// Loading, error, and data states are scoped to this section so a stats failure
// never blocks search/results.
export function MarketOverview() {
  const { data, isLoading, error, refetch } = useMarketStats()

  if (isLoading) {
    return (
      <section aria-label="Market overview" aria-busy="true">
        <SummarySkeleton />
      </section>
    )
  }

  if (error || !data) {
    return (
      <section aria-label="Market overview">
        <ErrorState
          title="Market overview unavailable"
          message="We couldn't load market summary. Search and listings still work."
          onRetry={() => refetch()}
        />
      </section>
    )
  }

  const metrics = metricsFrom(data)

  return (
    <section aria-label="Market overview">
      <Card className="p-4">
        <div className="grid grid-cols-2 gap-4 sm:grid-cols-3 lg:grid-cols-6">
          {metrics.map((m) => (
            <div key={m.label} className="flex flex-col gap-1">
              <span className="text-xs font-medium uppercase tracking-wide text-muted">{m.label}</span>
              <span className="text-xl font-semibold text-text">{m.value}</span>
            </div>
          ))}
        </div>
        <p className="mt-4 text-xs text-muted">
          Last updated: <span>{data.lastUpdated}</span>
        </p>
      </Card>
    </section>
  )
}
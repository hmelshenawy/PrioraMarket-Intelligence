import { Card } from "@/components/ui/Card"
import { ErrorState } from "@/components/ui/ErrorState"
import { Skeleton } from "@/components/ui/Skeleton"
import { METRIC_ORDER, type MetricType } from "../constants/market"
import type {
  MarketMetricDto,
  MarketSnapshotViewModel
} from "../types"
import type { ApiError } from "@/lib/api/types"
import { ActiveListingsCard } from "./ActiveListingsCard"
import { MedianPriceCard } from "./MedianPriceCard"
import { TypicalPriceRangeCard } from "./TypicalPriceRangeCard"
import { InventoryChangeCard } from "./InventoryChangeCard"
import { PriceDropsCard } from "./PriceDropsCard"

export interface SnapshotMetricsProps {
  data?: MarketSnapshotViewModel
  isLoading: boolean
  error: ApiError | null
  onRetry?: () => void
}

// Renders the five metric cards in the canonical METRIC_ORDER. Owns loading (5 card
// skeletons) and error (ErrorState with retry) at the grid level. Each card handles its
// own unsupported / unavailable / partial states via MetricState.
export function SnapshotMetrics({ data, isLoading, error, onRetry }: SnapshotMetricsProps) {
  if (isLoading && !data) {
    return (
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3" aria-busy="true" aria-label="Loading market snapshot">
        {Array.from({ length: METRIC_ORDER.length }, (_, i) => (
          <MetricSkeleton key={METRIC_ORDER[i]} />
        ))}
      </div>
    )
  }

  if (error && !data) {
    return (
      <ErrorState
        title="Couldn't load the market snapshot"
        message={error.message}
        onRetry={onRetry}
      />
    )
  }

  if (!data) return null

  const byType = new Map<MetricType, MarketMetricDto>(
    data.metrics.map((m) => [m.type, m] as [MetricType, MarketMetricDto])
  )

  return (
    <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3" role="list" aria-label="Market snapshot metrics">
      {METRIC_ORDER.map((type) => {
        const metric = byType.get(type)
        if (!metric) return null
        return <MetricCardRouter key={type} metric={metric} />
      })}
    </div>
  )
}

function MetricCardRouter({ metric }: { metric: MarketMetricDto }) {
  switch (metric.type) {
    case "activeListings":
      return <ActiveListingsCard metric={metric} />
    case "medianPrice":
      return <MedianPriceCard metric={metric} />
    case "typicalPriceRange":
      return <TypicalPriceRangeCard metric={metric} />
    case "inventoryChange":
      return <InventoryChangeCard metric={metric} />
    case "priceDrops":
      return <PriceDropsCard metric={metric} />
  }
}

function MetricSkeleton() {
  return (
    <Card className="flex flex-col gap-2 p-5">
      <Skeleton className="h-4 w-28" />
      <Skeleton className="h-8 w-24" />
      <Skeleton className="h-3 w-16" />
    </Card>
  )
}
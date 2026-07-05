// Market feature public surface. Components, hook, API client, mapper, schemas, and
// types are re-exported so consumers depend on the feature boundary, not internal paths.

export { DashboardShell } from "./components/DashboardShell"
export { SnapshotMetrics } from "./components/SnapshotMetrics"
export { ScopeLabel } from "./components/ScopeLabel"
export { AsOfTimestamp } from "./components/AsOfTimestamp"
export { MetricState } from "./components/MetricState"
export { MarketFilterBar } from "./components/MarketFilterBar"
export { ActiveListingsCard } from "./components/ActiveListingsCard"
export { MedianPriceCard } from "./components/MedianPriceCard"
export { TypicalPriceRangeCard } from "./components/TypicalPriceRangeCard"
export { InventoryChangeCard } from "./components/InventoryChangeCard"
export { PriceDropsCard } from "./components/PriceDropsCard"

export { useMarketSnapshot, type UseMarketSnapshotResult, useMarketFiltersFromUrl, type MarketFiltersUrlState } from "./hooks/use-market-snapshot"
export { useFilterOptions, type UseFilterOptionsResult } from "./hooks/use-filter-options"

export { fetchMarketSnapshot, fetchFilterOptions } from "./api/market-api.client"
export { mapMarketSnapshot } from "./mappers/market-snapshot-mapper"

export { marketSnapshotSchema } from "./schemas/market-snapshot.schema"
export { filterOptionsSchema } from "./schemas/filter-options.schema"
export { METRIC_ORDER, type MetricType, DEFAULT_PERIOD_DAYS, CURRENCY, marketQueryKeys } from "./constants/market"

export type {
  MarketSnapshotDto,
  FilterOptionsDto,
  FilterOptionDto,
  MarketMetricDto,
  ActiveListingsMetricDto,
  MedianPriceMetricDto,
  TypicalPriceRangeMetricDto,
  InventoryChangeMetricDto,
  PriceDropsMetricDto,
  MetricSupportStatusDto,
  FreshnessDto,
  MarketFilterSelectionDto,
  MarketSnapshotRequest,
  MarketSnapshotViewModel,
} from "./types/market.types"
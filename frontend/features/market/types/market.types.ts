// Market feature types. DTOs are inferred from the zod validation schemas; after the
// trust-boundary parse, the typed DTO flows through feature code without re-validation.

import type {
  ActiveListingsMetricParsed,
  FreshnessParsed,
  InventoryChangeMetricParsed,
  MarketFilterSelectionParsed,
  MarketMetricParsed,
  MarketSnapshotParsed,
  MedianPriceMetricParsed,
  MetricSupportStatusParsed,
  PriceDropsMetricParsed,
  TypicalPriceRangeMetricParsed
} from "../schemas/market-snapshot.schema"
import type { FilterOptionsParsed, FilterOptionParsed } from "../schemas/filter-options.schema"

export type MarketSnapshotDto = MarketSnapshotParsed
export type FilterOptionsDto = FilterOptionsParsed
export type FilterOptionDto = FilterOptionParsed
export type MarketMetricDto = MarketMetricParsed
export type ActiveListingsMetricDto = ActiveListingsMetricParsed
export type MedianPriceMetricDto = MedianPriceMetricParsed
export type TypicalPriceRangeMetricDto = TypicalPriceRangeMetricParsed
export type InventoryChangeMetricDto = InventoryChangeMetricParsed
export type PriceDropsMetricDto = PriceDropsMetricParsed
export type MetricSupportStatusDto = MetricSupportStatusParsed
export type FreshnessDto = FreshnessParsed
export type MarketFilterSelectionDto = MarketFilterSelectionParsed

export interface MarketSnapshotRequest {
  make?: string
  model?: string
  trim?: string
  year?: number
  periodDays?: number
}

// Presentation view model assembled by the market snapshot mapper. Raw values only;
// the frontend owns formatting. `freshness` is carried as metadata and MUST NOT be
// presented to users as a real-time market reading.
export interface MarketSnapshotViewModel {
  scopeLabel: string
  scopeLevel: MarketSnapshotDto["scope"]["level"]
  asOf: string
  generatedAt: string
  periodDays: number
  metrics: MarketMetricDto[]
  supportStatuses: MarketSnapshotDto["supportStatuses"]
  freshness: FreshnessDto
}
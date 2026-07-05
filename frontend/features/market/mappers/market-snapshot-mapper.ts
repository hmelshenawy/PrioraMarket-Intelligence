import { formatAsOf } from "../utils/market-format"
import type { MarketSnapshotDto, MarketSnapshotViewModel } from "../types"

// Map the validated Market Snapshot DTO to the presentation view model.
// No recalculation: metrics/supportStatuses/freshness pass through as raw values;
// only scopeLabel and the "As of" string are derived for the header. `freshness` is
// carried as metadata and MUST NOT be displayed as a real-time market reading.
export function mapMarketSnapshot(dto: MarketSnapshotDto): MarketSnapshotViewModel {
  return {
    scopeLabel: dto.scope.label,
    scopeLevel: dto.scope.level,
    asOf: formatAsOf(dto.generatedAt),
    generatedAt: dto.generatedAt,
    periodDays: dto.filters.periodDays,
    metrics: dto.metrics,
    supportStatuses: dto.supportStatuses,
    freshness: dto.freshness,
  }
}
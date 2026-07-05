import { formatAed, formatDate, formatNumber } from "@/lib/formatting"
import type { InventoryStatsResponseDto, MarketStatsModel } from "../types"

// Map the InventoryStatsResponse DTO to the display-ready MarketStatsModel.
// All values flow through shared formatting utilities so missing/null values
// resolve to the consistent empty placeholder (EMPTY_VALUE) rather than
// hard-coded strings. Never fabricates a value for missing data.
export function mapMarketStats(dto: InventoryStatsResponseDto): MarketStatsModel {
  return {
    totalListings: formatNumber(dto.totalListings),
    usedListings: formatNumber(dto.usedListings),
    newListings: formatNumber(dto.newListings),
    totalMakes: formatNumber(dto.totalMakes),
    totalModels: formatNumber(dto.totalModels),
    averagePrice: formatAed(dto.averagePriceAed, { compact: true }),
    lastUpdated: formatDate(dto.lastUpdatedAt),
  }
}
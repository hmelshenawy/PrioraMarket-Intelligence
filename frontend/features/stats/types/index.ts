// Stats feature types. DTOs mirror Feature 003 data-model.md (InventoryStatsResponse).

// Backend DTO returned by GET /api/v1/stats.
export interface InventoryStatsResponseDto {
  totalListings: number
  usedListings: number
  newListings: number
  totalMakes: number
  totalModels: number
  averagePriceAed: number | null
  minPriceAed: number | null
  maxPriceAed: number | null
  lastUpdatedAt: string | null
}

// Display-ready market overview model. Numeric/timestamp values are formatted
// via shared formatting utilities so missing values resolve to the consistent
// empty placeholder rather than a hard-coded string.
export interface MarketStatsModel {
  totalListings: string
  usedListings: string
  newListings: string
  totalMakes: string
  totalModels: string
  averagePrice: string
  lastUpdated: string
}
import { describe, expect, it } from "vitest"
import { mapMarketStats } from "@/features/stats/mappers/statsMapper"
import { formatAed, formatDate, formatNumber } from "@/lib/formatting"
import { EMPTY_VALUE } from "@/lib/formatting/emptyValue"
import type { InventoryStatsResponseDto } from "@/features/stats/types"

const dto: InventoryStatsResponseDto = {
  totalListings: 1200,
  usedListings: 1000,
  newListings: 200,
  totalMakes: 12,
  totalModels: 40,
  averagePriceAed: 85000,
  minPriceAed: 30000,
  maxPriceAed: 250000,
  lastUpdatedAt: "2024-07-04T08:00:00.000Z",
}

describe("mapMarketStats", () => {
  it("formats counts, average price, and last updated via shared utilities", () => {
    const model = mapMarketStats(dto)
    expect(model.totalListings).toBe(formatNumber(1200))
    expect(model.usedListings).toBe(formatNumber(1000))
    expect(model.newListings).toBe(formatNumber(200))
    expect(model.totalMakes).toBe(formatNumber(12))
    expect(model.totalModels).toBe(formatNumber(40))
    expect(model.averagePrice).toBe(formatAed(85000, { compact: true }))
    expect(model.lastUpdated).toBe(formatDate("2024-07-04T08:00:00.000Z"))
  })

  it("softens a null average price to the empty placeholder", () => {
    const model = mapMarketStats({ ...dto, averagePriceAed: null })
    expect(model.averagePrice).toBe(EMPTY_VALUE)
  })

  it("softens a missing last updated timestamp to the empty placeholder", () => {
    const model = mapMarketStats({ ...dto, lastUpdatedAt: null })
    expect(model.lastUpdated).toBe(EMPTY_VALUE)
  })
})
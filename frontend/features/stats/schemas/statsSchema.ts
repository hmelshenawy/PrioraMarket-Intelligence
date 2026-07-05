import { z } from "zod"

// Trust boundary: validate the InventoryStatsResponse payload from Feature 003
// before it enters feature code. Unknown future fields are ignored (passthrough).
// Null bounds (averagePriceAed / minPriceAed / maxPriceAed / lastUpdatedAt) are
// kept nullable so the mapper can soften them via formatting utilities.
export const inventoryStatsSchema = z.object({
  totalListings: z.number(),
  usedListings: z.number(),
  newListings: z.number(),
  totalMakes: z.number(),
  totalModels: z.number(),
  averagePriceAed: z.number().nullable(),
  minPriceAed: z.number().nullable(),
  maxPriceAed: z.number().nullable(),
  lastUpdatedAt: z.string().nullable(),
})

export type InventoryStatsParsed = z.infer<typeof inventoryStatsSchema>
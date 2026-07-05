import { getApiClient } from "@/lib/api/client"
import { inventoryStatsSchema } from "../schemas/statsSchema"
import type { InventoryStatsResponseDto } from "../types"

// GET /api/v1/stats — Market Overview metrics.
// The Axios response interceptor normalizes network/backend errors to ApiError.
export async function fetchMarketStats(): Promise<InventoryStatsResponseDto> {
  const client = getApiClient()
  const { data } = await client.get<unknown>("/stats")
  return inventoryStatsSchema.parse(data) as InventoryStatsResponseDto
}
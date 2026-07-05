import { getApiClient } from "@/lib/api/client"
import { healthSchema } from "../schemas/healthSchema"
import type { HealthResponseDto } from "../types"

// GET /api/v1/health — request failure/timeout/invalid payload means unavailable.
export async function fetchHealth(): Promise<HealthResponseDto> {
  const client = getApiClient()
  const { data } = await client.get<unknown>("/health")
  return healthSchema.parse(data)
}
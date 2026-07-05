import { getApiClient } from "@/lib/api/client"
import { filterMetadataSchema } from "../schemas/filterMetadataSchema"
import type { FilterMetadataDto } from "../types"

// GET /api/v1/listings/filters — dynamic filter metadata.
// The Axios response interceptor normalizes network/backend errors to ApiError.
export async function fetchFilterMetadata(): Promise<FilterMetadataDto> {
  const client = getApiClient()
  const { data } = await client.get<unknown>("/listings/filters")
  return filterMetadataSchema.parse(data) as FilterMetadataDto
}
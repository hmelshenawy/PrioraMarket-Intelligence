import { getApiClient } from "@/lib/api/client"
import { listingDetailSchema } from "../schemas/listingDetailSchema"
import type { ListingDetailDto } from "../types"

// GET /api/v1/listings/:id — read one listing detail.
// The Axios response interceptor normalizes network/backend errors to ApiError
// (404 → notFound, 500 → serverError, no response → network/offline).
export async function fetchListingDetail(id: string): Promise<ListingDetailDto> {
  const client = getApiClient()
  const { data } = await client.get<unknown>(`/listings/${encodeURIComponent(id)}`)
  return listingDetailSchema.parse(data) as ListingDetailDto
}
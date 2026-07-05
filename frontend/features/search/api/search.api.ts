import { getApiClient } from "@/lib/api/client"
import type { SearchUrlState } from "@/lib/routing/searchState"
import { searchListingsResponseSchema } from "../schemas/searchResponseSchema"
import type { ListingSearchRequestDto, SearchListingsResponseDto } from "../types"

// Build the API request from normalized URL state, omitting empty/undefined values
// so the backend never receives empty-string filters.
function buildRequest(state: SearchUrlState): ListingSearchRequestDto {
  const req: ListingSearchRequestDto = {
    page: state.page,
    limit: state.limit,
    sort: state.sort,
  }
  if (state.q) req.q = state.q
  if (state.condition) req.condition = state.condition
  if (state.make) req.make = state.make
  if (state.model) req.model = state.model
  if (state.sellerType) req.sellerType = state.sellerType
  if (state.location) req.location = state.location
  if (state.priceMin != null) req.priceMin = state.priceMin
  if (state.priceMax != null) req.priceMax = state.priceMax
  if (state.kmMin != null) req.kmMin = state.kmMin
  if (state.kmMax != null) req.kmMax = state.kmMax
  if (state.yearFrom != null) req.yearFrom = state.yearFrom
  if (state.yearTo != null) req.yearTo = state.yearTo
  return req
}

// GET /api/v1/listings — search current listings.
// The Axios response interceptor normalizes network/backend errors to ApiError.
export async function searchListings(state: SearchUrlState): Promise<SearchListingsResponseDto> {
  const client = getApiClient()
  const { data } = await client.get<unknown>("/listings", { params: buildRequest(state) })
  return searchListingsResponseSchema.parse(data)
}
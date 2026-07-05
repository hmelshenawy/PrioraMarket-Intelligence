import { mapListingCard } from "@/features/listings"
import type { SearchListingsResponseDto, SearchResultsModel } from "../types"

// Map the full search response to the UI model used by ResultsGrid/Pagination.
// Per-card mapping is owned by the listings feature; search composes the result set.
export function mapSearchResults(dto: SearchListingsResponseDto): SearchResultsModel {
  return {
    items: dto.data.map(mapListingCard),
    page: dto.meta.page,
    limit: dto.meta.limit,
    total: dto.meta.total,
    totalPages: dto.meta.totalPages,
    isEmpty: dto.data.length === 0 || dto.meta.total === 0,
  }
}
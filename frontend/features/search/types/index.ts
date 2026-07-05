// Search feature types. DTOs that are listing entities are sourced from the
// listings feature; search owns the search-response and request contract.

import type { SortOption } from "@/lib/validation/searchStateSchema"
import type { ListingCardModel, ListingSearchResultDto } from "@/features/listings/types"

// Re-export the listing entities consumed by search for caller convenience.
export type { ListingCardModel, ListingSearchResultDto }

export interface PaginationMetaDto {
  page: number
  limit: number
  total: number
  totalPages: number
}

export interface SearchListingsResponseDto {
  data: ListingSearchResultDto[]
  meta: PaginationMetaDto
}

// ListingSearchRequest mirrors the normalized URL state sent to GET /api/v1/listings.
export interface ListingSearchRequestDto {
  q?: string
  condition?: "used" | "new"
  make?: string
  model?: string
  yearFrom?: number
  yearTo?: number
  priceMin?: number
  priceMax?: number
  kmMin?: number
  kmMax?: number
  location?: string
  sellerType?: string
  page: number
  limit: number
  sort: SortOption
}

// UI model for the search results set; items are listing card models.
export interface SearchResultsModel {
  items: ListingCardModel[]
  page: number
  limit: number
  total: number
  totalPages: number
  isEmpty: boolean
}
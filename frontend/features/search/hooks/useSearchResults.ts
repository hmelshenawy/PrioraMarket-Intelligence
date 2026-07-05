"use client"

import { useQuery } from "@tanstack/react-query"
import { searchListings } from "../api/search.api"
import { mapSearchResults } from "../mappers/searchResultMapper"
import { queryKeys } from "@/lib/query/keys"
import type { ApiError } from "@/lib/api/types"
import type { SearchUrlState } from "@/lib/routing/searchState"
import type { SearchResultsModel } from "../types"

export interface UseSearchResultsResult {
  data: SearchResultsModel | undefined
  isLoading: boolean
  isFetching: boolean
  error: ApiError | null
  refetch: () => void
}

// useSearchResults — read-only search query keyed by normalized URL state.
// The URL is the source of truth; this hook refetches whenever URL state changes.
export function useSearchResults(state: SearchUrlState): UseSearchResultsResult {
  const query = useQuery({
    queryKey: queryKeys.listings.search(state),
    queryFn: async () => {
      const dto = await searchListings(state)
      return mapSearchResults(dto)
    },
    // Keep previous data visible while fetching the next page/filter set.
    placeholderData: (prev) => prev,
  })

  return {
    data: query.data,
    isLoading: query.isLoading,
    isFetching: query.isFetching,
    error: (query.error as ApiError | null) ?? null,
    refetch: () => {
      void query.refetch()
    },
  }
}
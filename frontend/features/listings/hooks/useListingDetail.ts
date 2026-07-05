"use client"

import { useQuery } from "@tanstack/react-query"
import { fetchListingDetail } from "../api/listings.api"
import { mapListingDetail } from "../mappers/listingDetailMapper"
import { queryKeys } from "@/lib/query/keys"
import type { ApiError } from "@/lib/api/types"
import type { ListingDetailModel } from "../types"

export interface UseListingDetailResult {
  data: ListingDetailModel | undefined
  isLoading: boolean
  error: ApiError | null
  isNotFound: boolean
  refetch: () => void
}

// useListingDetail — read-only listing detail keyed by normalized id.
// 404 responses surface as a not-found state the page renders inline.
export function useListingDetail(id: string): UseListingDetailResult {
  const query = useQuery({
    queryKey: queryKeys.listing.detail(id),
    queryFn: async () => {
      const dto = await fetchListingDetail(id)
      return mapListingDetail(dto)
    },
    // Retry behavior is governed by QueryClient defaults (no retry for
    // badRequest/notFound; short retry for transient failures).
  })

  const error = (query.error as ApiError | null) ?? null

  return {
    data: query.data,
    isLoading: query.isLoading,
    error,
    isNotFound: error?.category === "notFound",
    refetch: () => {
      void query.refetch()
    },
  }
}
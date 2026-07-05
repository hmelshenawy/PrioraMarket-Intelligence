"use client"

import { useQuery } from "@tanstack/react-query"
import { fetchFilterOptions } from "../api/market-api.client"
import { marketQueryKeys } from "../constants/market"
import type { ApiError } from "@/lib/api/types"
import type { FilterOptionsDto, MarketSnapshotRequest } from "../types"

export interface UseFilterOptionsResult {
  data: FilterOptionsDto | undefined
  isLoading: boolean
  isFetching: boolean
  error: ApiError | null
}

// TanStack Query hook for cascading filter options. The query key includes only the
// higher-level canonical filters (make/model/trim/year) so options re-fetch when the
// selection changes and cache entries do not collide across scopes. Runs in parallel
// with the snapshot query. No client-side analytics. Read-only.
export function useFilterOptions(request: MarketSnapshotRequest = {}): UseFilterOptionsResult {
  const query = useQuery({
    queryKey: marketQueryKeys.filterOptions({
      make: request.make,
      model: request.model,
      trim: request.trim,
      year: request.year
    }),
    queryFn: () => fetchFilterOptions(request),
    placeholderData: (prev) => prev
  })

  return {
    data: query.data,
    isLoading: query.isLoading,
    isFetching: query.isFetching,
    error: (query.error as ApiError | null) ?? null
  }
}
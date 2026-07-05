"use client"

import { useQuery } from "@tanstack/react-query"
import { fetchMarketStats } from "../api/stats.api"
import { mapMarketStats } from "../mappers/statsMapper"
import { queryKeys } from "@/lib/query/keys"
import { STALE_TIME } from "@/lib/constants/query"
import type { ApiError } from "@/lib/api/types"
import type { MarketStatsModel } from "../types"

export interface UseMarketStatsResult {
  data: MarketStatsModel | undefined
  isLoading: boolean
  error: ApiError | null
  refetch: () => void
}

// useMarketStats — read-only Market Overview metrics with a stable key.
// Scoped: a stats failure is reported to MarketOverview but never blocks search.
export function useMarketStats(): UseMarketStatsResult {
  const query = useQuery({
    queryKey: queryKeys.stats.overview(),
    queryFn: async () => {
      const dto = await fetchMarketStats()
      return mapMarketStats(dto)
    },
    staleTime: STALE_TIME,
  })

  return {
    data: query.data,
    isLoading: query.isLoading,
    error: (query.error as ApiError | null) ?? null,
    refetch: () => {
      void query.refetch()
    },
  }
}
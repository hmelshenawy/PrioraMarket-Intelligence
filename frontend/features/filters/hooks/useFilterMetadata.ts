"use client"

import { useQuery } from "@tanstack/react-query"
import { fetchFilterMetadata } from "../api/filters.api"
import { mapFilterMetadata } from "../mappers/filterMetadataMapper"
import { queryKeys } from "@/lib/query/keys"
import { STALE_TIME } from "@/lib/constants/query"
import type { ApiError } from "@/lib/api/types"
import type { FilterMetadataModel } from "../types"

export interface UseFilterMetadataResult {
  data: FilterMetadataModel | undefined
  isLoading: boolean
  error: ApiError | null
  refetch: () => void
}

// useFilterMetadata — read-only filter metadata query with a stable key.
// Scoped: a metadata failure is reported to the sidebar but never blocks search.
export function useFilterMetadata(): UseFilterMetadataResult {
  const query = useQuery({
    queryKey: queryKeys.filters.metadata(),
    queryFn: async () => {
      const dto = await fetchFilterMetadata()
      return mapFilterMetadata(dto)
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
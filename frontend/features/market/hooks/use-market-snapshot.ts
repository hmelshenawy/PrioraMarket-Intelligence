"use client"

import { useCallback } from "react"
import { useQuery } from "@tanstack/react-query"
import { usePathname, useRouter, useSearchParams } from "next/navigation"
import { fetchMarketSnapshot } from "../api/market-api.client"
import { mapMarketSnapshot } from "../mappers/market-snapshot-mapper"
import { marketQueryKeys, DEFAULT_PERIOD_DAYS } from "../constants/market"
import type { ApiError } from "@/lib/api/types"
import type { MarketSnapshotRequest, MarketSnapshotViewModel } from "../types"

export interface UseMarketSnapshotResult {
  data: MarketSnapshotViewModel | undefined
  isLoading: boolean
  isFetching: boolean
  error: ApiError | null
  refetch: () => void
}

// TanStack Query hook for the overall / filtered market snapshot. Keyed by the canonical
// filters + period so cache entries do not collide across scopes. No client-side
// analytics: all aggregation is performed by the backend, the frontend only maps and
// formats. Read-only — never mutates listing, raw_listing, catalog, lifecycle, or
// price-history data.
export function useMarketSnapshot(request: MarketSnapshotRequest = {}): UseMarketSnapshotResult {
  const query = useQuery({
    queryKey: marketQueryKeys.snapshot(request),
    queryFn: async () => {
      const dto = await fetchMarketSnapshot(request)
      return mapMarketSnapshot(dto)
    },
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

export interface MarketFiltersUrlState {
  request: MarketSnapshotRequest
  /** Replace URL query params with the next filter selection (no full page reload). */
  setFilters: (next: MarketSnapshotRequest) => void
}

/**
 * Read/write market filter selection from the URL query string. Filters live in the URL
 * so the dashboard is shareable and back/forward works; TanStack Query re-fetches when the
 * canonical key changes. `router.replace` updates the URL client-side — no full reload.
 * `periodDays` defaults to the backend default when absent from the URL.
 */
export function useMarketFiltersFromUrl(): MarketFiltersUrlState {
  const searchParams = useSearchParams()
  const router = useRouter()
  const pathname = usePathname()

  const request: MarketSnapshotRequest = {
    make: searchParams.get("make") ?? undefined,
    model: searchParams.get("model") ?? undefined,
    trim: searchParams.get("trim") ?? undefined,
    year: searchParams.get("year") ? Number(searchParams.get("year")) : undefined,
    periodDays: searchParams.get("periodDays") ? Number(searchParams.get("periodDays")) : DEFAULT_PERIOD_DAYS
  }

  const setFilters = useCallback(
    (next: MarketSnapshotRequest) => {
      const params = new URLSearchParams()
      if (next.make) params.set("make", next.make)
      if (next.model) params.set("model", next.model)
      if (next.trim) params.set("trim", next.trim)
      if (next.year != null) params.set("year", String(next.year))
      if (next.periodDays != null && next.periodDays !== DEFAULT_PERIOD_DAYS) {
        params.set("periodDays", String(next.periodDays))
      }
      const qs = params.toString()
      router.replace(qs ? `${pathname}?${qs}` : pathname, { scroll: false })
    },
    [router, pathname]
  )

  return { request, setFilters }
}
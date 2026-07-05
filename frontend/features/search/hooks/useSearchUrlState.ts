"use client"

import { useCallback, useEffect, useMemo, useRef } from "react"
import { usePathname, useRouter, useSearchParams } from "next/navigation"
import {
  buildSearchString,
  defaultSearchState,
  parseSearchState,
  updateSearchState,
  type SearchUrlState,
} from "@/lib/routing/searchState"
import type { SortOption } from "@/lib/validation/searchStateSchema"
import { SEARCH_DEBOUNCE_MS } from "@/lib/constants/debounce"
import { restoreScroll } from "@/lib/routing/scrollRestore"

export interface UseSearchUrlStateResult {
  state: SearchUrlState
  setQ: (value: string) => void
  setFilter: (patch: Partial<SearchUrlState>) => void
  setSort: (sort: SortOption) => void
  setPage: (page: number) => void
  setLimit: (limit: number) => void
  clearFilters: () => void
  hasActiveFilters: boolean
}

// useSearchUrlState — the URL is the single source of truth for search state.
// Reads derive from useSearchParams (reactive to Back/Forward); writes push new
// URLs through next/navigation. Text input is debounced; filter/sort/page/limit
// changes update immediately. Clear filters resets to defaults.
export function useSearchUrlState(): UseSearchUrlStateResult {
  const router = useRouter()
  const pathname = usePathname()
  const searchParams = useSearchParams()

  // Reactive state derived from the URL (updates on navigation, including Back/Forward).
  const state = useMemo(() => parseSearchState(searchParams), [searchParams])
  const stateRef = useRef(state)
  useEffect(() => {
    stateRef.current = state
  }, [state])

  // Push a new search state into the URL without a scroll reset (results handle their own scroll).
  const pushUrl = useCallback(
    (next: SearchUrlState) => {
      const url = `${pathname}${buildSearchString(next)}`
      router.push(url, { scroll: false })
    },
    [pathname, router],
  )

  // Debounced text search: keep the latest value and fire once after the debounce window.
  const debounceTimer = useRef<ReturnType<typeof setTimeout> | null>(null)
  const setQ = useCallback(
    (value: string) => {
      if (debounceTimer.current) clearTimeout(debounceTimer.current)
      debounceTimer.current = setTimeout(() => {
        const next = updateSearchState(stateRef.current, { q: value.trim() || undefined })
        pushUrl(next)
      }, SEARCH_DEBOUNCE_MS)
    },
    [pushUrl],
  )

  useEffect(() => {
    return () => {
      if (debounceTimer.current) clearTimeout(debounceTimer.current)
    }
  }, [])

  const setFilter = useCallback(
    (patch: Partial<SearchUrlState>) => {
      pushUrl(updateSearchState(stateRef.current, patch))
    },
    [pushUrl],
  )

  const setSort = useCallback(
    (sort: SortOption) => {
      pushUrl(updateSearchState(stateRef.current, { sort }, { resetPage: true }))
    },
    [pushUrl],
  )

  const setPage = useCallback(
    (page: number) => {
      pushUrl(updateSearchState(stateRef.current, { page }, { resetPage: false }))
    },
    [pushUrl],
  )

  const setLimit = useCallback(
    (limit: number) => {
      pushUrl(updateSearchState(stateRef.current, { limit }, { resetPage: true }))
    },
    [pushUrl],
  )

  const clearFilters = useCallback(() => {
    pushUrl(defaultSearchState)
  }, [pushUrl])

  // Restore scroll position when returning from listing detail (mount-only).
  useEffect(() => {
    restoreScroll()
  }, [])

  const hasActiveFilters = useMemo(() => {
    const s = state
    return Boolean(
      s.q ||
        s.condition ||
        s.make ||
        s.model ||
        s.sellerType ||
        s.location ||
        s.priceMin != null ||
        s.priceMax != null ||
        s.kmMin != null ||
        s.kmMax != null ||
        s.yearFrom != null ||
        s.yearTo != null ||
        s.sort !== defaultSearchState.sort,
    )
  }, [state])

  return { state, setQ, setFilter, setSort, setPage, setLimit, clearFilters, hasActiveFilters }
}
"use client"

import { useSearchUrlState } from "../hooks/useSearchUrlState"
import { useSearchResults } from "../hooks/useSearchResults"
import { useFilterMetadata } from "@/features/filters"
import { SearchToolbar } from "./SearchToolbar"
import { FilterSidebar } from "./FilterSidebar"
import { MobileFilters } from "./MobileFilters"
import { ResultsGrid } from "./ResultsGrid"
import { SearchPagination } from "./SearchPagination"
import { Spinner } from "@/components/ui/Spinner"

// SearchExperience — client composition of the home search page.
// Holds the URL-driven state hook, the search query, and filter metadata;
// composes toolbar, filters (desktop + mobile drawer), results, pagination.
export function SearchExperience() {
  const { state, setQ, setFilter, setSort, setPage, clearFilters, hasActiveFilters } = useSearchUrlState()
  const { data, isLoading, isFetching, error, refetch } = useSearchResults(state)
  const { data: metadata, isLoading: metadataLoading, error: metadataError, refetch: refetchMetadata } = useFilterMetadata()

  const resultsCount = data?.total
  const filterProps = {
    state,
    onFilterChange: setFilter,
    onClear: clearFilters,
    hasActiveFilters,
    metadata,
    metadataLoading,
    metadataError,
    onRetryMetadata: refetchMetadata,
  }

  return (
    <div className="flex flex-col gap-6">
      <SearchToolbar
        state={state}
        onQChange={setQ}
        onSortChange={setSort}
        onClear={clearFilters}
        hasActiveFilters={hasActiveFilters}
        resultsCount={resultsCount}
      />
      <div className="grid gap-6 lg:grid-cols-[260px_1fr]">
        <aside aria-label="Filters" className="hidden lg:sticky lg:top-4 lg:block lg:self-start">
          <FilterSidebar {...filterProps} />
        </aside>
        <section aria-label="Search results" aria-busy={isFetching} className="relative min-w-0">
          <div className="mb-4">
            <MobileFilters {...filterProps} />
          </div>
          {isFetching && data && (
            <div className="absolute right-0 top-0 z-10" aria-hidden>
              <Spinner size="sm" />
            </div>
          )}
          <ResultsGrid data={data} isLoading={isLoading} error={error} onRetry={refetch} />
          <SearchPagination
            page={data?.page ?? state.page}
            totalPages={data?.totalPages ?? 0}
            onPageChange={setPage}
          />
        </section>
      </div>
    </div>
  )
}
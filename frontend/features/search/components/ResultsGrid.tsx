"use client"

import { EmptyState } from "@/components/ui/EmptyState"
import { ErrorState } from "@/components/ui/ErrorState"
import { ListingCard, ListingCardSkeleton } from "@/features/listings"
import type { ApiError } from "@/lib/api/types"
import type { SearchResultsModel } from "../types"

export interface ResultsGridProps {
  data: SearchResultsModel | undefined
  isLoading: boolean
  error: ApiError | null
  onRetry?: () => void
}

const SKELETON_COUNT = 6

// ResultsGrid — renders skeleton/empty/error/data states for search results.
// Cards and skeletons are owned by the listings feature.
export function ResultsGrid({ data, isLoading, error, onRetry }: ResultsGridProps) {
  if (error) {
    return (
      <ErrorState
        title="Couldn't load listings"
        message={error.message}
        retryLabel="Try again"
        onRetry={onRetry}
      />
    )
  }

  if (isLoading && !data) {
    return (
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {Array.from({ length: SKELETON_COUNT }, (_, i) => (
          <ListingCardSkeleton key={i} />
        ))}
      </div>
    )
  }

  if (data?.isEmpty) {
    return (
      <EmptyState
        title="No listings found"
        description="Try adjusting your search or clearing some filters to see more results."
      />
    )
  }

  if (!data) return null

  return (
    <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
      {data.items.map((item) => (
        <ListingCard key={item.id} item={item} />
      ))}
    </div>
  )
}
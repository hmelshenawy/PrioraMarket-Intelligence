"use client"

import { EmptyState } from "@/components/ui/EmptyState"
import { ErrorState } from "@/components/ui/ErrorState"
import { Skeleton } from "@/components/ui/Skeleton"
import { Card } from "@/components/ui/Card"
import { useListingDetail } from "../hooks/useListingDetail"
import { ImageGallery } from "./ImageGallery"
import { VehicleSummary } from "./VehicleSummary"
import { VehicleSpecifications } from "./VehicleSpecifications"
import { MarketplaceAction } from "./MarketplaceAction"

export interface ListingDetailViewProps {
  id: string
}

// ListingDetailView — client composition of the listing detail page.
// Loading → skeleton; 404 → not-found state with path back to search;
// other errors → recoverable error with retry; data → full detail layout.
export function ListingDetailView({ id }: ListingDetailViewProps) {
  const { data, isLoading, error, isNotFound, refetch } = useListingDetail(id)

  if (isLoading) return <DetailSkeleton />

  if (isNotFound) {
    return (
      <EmptyState
        title="Listing not found"
        description="This listing may have been removed or is no longer available."
        actionLabel="Back to search"
        actionHref="/"
      />
    )
  }

  if (error || !data) {
    return (
      <ErrorState
        title="Couldn't load this listing"
        message={error?.message ?? "We couldn't load this listing. Please try again."}
        retryLabel="Try again"
        onRetry={refetch}
      />
    )
  }

  return (
    <div className="flex flex-col gap-6">
      {/* <ImageGallery title={data.title} photosCount={data.gallery.photosCount} /> */}
      <div className="grid gap-6 lg:grid-cols-[1fr_320px]">
        <div className="flex flex-col gap-6">
          <VehicleSummary model={data} />
          <VehicleSpecifications model={data} />
        </div>
        <aside className="lg:sticky lg:top-4 lg:self-start">
          <Card className="flex flex-col gap-3 p-4">
            <h2 className="text-sm font-semibold text-text">Original listing</h2>
            <MarketplaceAction url={data.marketplaceAction.url} />
          </Card>
        </aside>
      </div>
    </div>
  )
}

function DetailSkeleton() {
  return (
    <div className="flex flex-col gap-6">
      <Skeleton className="aspect-video w-full rounded-card" />
      <div className="grid gap-6 lg:grid-cols-[1fr_320px]">
        <div className="flex flex-col gap-4">
          <Skeleton className="h-8 w-2/3" />
          <Skeleton className="h-5 w-1/2" />
          <Skeleton className="h-40 w-full" />
        </div>
        <Skeleton className="h-32 w-full" />
      </div>
    </div>
  )
}

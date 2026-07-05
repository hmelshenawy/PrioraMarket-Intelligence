import { Suspense } from "react"
import type { Metadata } from "next"
import { ListingDetailView } from "@/features/listings/components/ListingDetailView"
import { listingMetadata } from "@/lib/seo/metadata"

// Listing detail route. `params` is a Promise in Next 16; await before use.
export async function generateMetadata({
  params,
}: {
  params: Promise<{ id: string }>
}): Promise<Metadata> {
  const { id } = await params
  return listingMetadata({ id })
}

export default async function ListingDetailPage({
  params,
}: {
  params: Promise<{ id: string }>
}) {
  const { id } = await params
  return (
    <Suspense fallback={<DetailFallback />}>
      <ListingDetailView id={id} />
    </Suspense>
  )
}

function DetailFallback() {
  return (
    <div className="flex flex-col gap-6">
      <div className="aspect-video w-full animate-pulse rounded-card bg-skeleton" aria-hidden />
      <div className="h-8 w-2/3 animate-pulse rounded bg-skeleton" aria-hidden />
      <div className="h-40 w-full animate-pulse rounded bg-skeleton" aria-hidden />
    </div>
  )
}
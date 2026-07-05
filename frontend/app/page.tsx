import { Suspense } from "react"
import { SearchExperience } from "@/features/search/components/SearchExperience"
import { MarketOverview } from "@/features/stats"
import { Skeleton } from "@/components/ui/Skeleton"
import { homeMetadata } from "@/lib/seo/metadata"

export const metadata = homeMetadata

// Home page (Server Component). Composes Market Overview and the search
// experience as independent sections; no direct Axios. useSearchParams requires
// a Suspense boundary for static prerendering in Next 16. MarketOverview manages
// its own loading/error state so a stats failure never blocks search.
export default function Home() {
  return (
    <div className="flex flex-col gap-8">
      <MarketOverview />
      <Suspense fallback={<HomeSearchFallback />}>
        <SearchExperience />
      </Suspense>
    </div>
  )
}

function HomeSearchFallback() {
  return (
    <div className="flex flex-col gap-6">
      <Skeleton className="h-10 w-full max-w-xl" />
      <div className="grid gap-6 lg:grid-cols-[260px_1fr]">
        <Skeleton className="h-64 w-full" />
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {Array.from({ length: 6 }, (_, i) => (
            <ResultsGridSkeleton key={i} />
          ))}
        </div>
      </div>
    </div>
  )
}

function ResultsGridSkeleton() {
  return (
    <div className="overflow-hidden rounded-card border border-border bg-elevated">
      <Skeleton className="aspect-video w-full rounded-none" />
      <div className="flex flex-col gap-2 p-3">
        <Skeleton className="h-5 w-24" />
        <Skeleton className="h-4 w-full" />
        <Skeleton className="h-3 w-1/2" />
      </div>
    </div>
  )
}
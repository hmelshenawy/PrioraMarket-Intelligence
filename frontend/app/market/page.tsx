import { Suspense } from "react"
import type { Metadata } from "next"
import { DashboardShell } from "@/features/market/components/DashboardShell"
import { Skeleton } from "@/components/ui/Skeleton"

// Market Snapshot page (Server Component). US1 renders the overall scope dashboard; US2
// adds cascading make/model/trim/year filters (URL-driven, no full page reload). DashboardShell
// is a client component (TanStack Query); the Suspense boundary provides a streaming fallback
// and mirrors the Next 16 pattern used by the home page.
export const metadata: Metadata = {
  title: "Market Snapshot",
  description:
    "Generated UAE used car market snapshot: active listings, median price, typical price range, inventory change, and price drops.",
  alternates: { canonical: "/market" },
}

export default function MarketPage() {
  return (
    <Suspense fallback={<MarketFallback />}>
      <DashboardShell />
    </Suspense>
  )
}

function MarketFallback() {
  return (
    <div className="flex flex-col gap-6">
      <Skeleton className="h-8 w-64" />
      <Skeleton className="h-4 w-40" />
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {Array.from({ length: 5 }, (_, i) => (
          <Skeleton key={i} className="h-32 w-full" />
        ))}
      </div>
    </div>
  )
}
"use client"

import { useEffect } from "react"
import { ErrorState } from "@/components/ui/ErrorState"

// Scoped error boundary for the listing detail route. Client Component.
// Receives `unstable_retry` (Next.js 16) for recovery. Never exposes stack traces.
export default function ListingDetailError({
  error,
  unstable_retry,
}: {
  error: Error & { digest?: string }
  unstable_retry: () => void
}) {
  useEffect(() => {
    if (process.env.NODE_ENV !== "production") {
      console.error("[PrioraMarket] listing detail error:", error)
    }
  }, [error])

  return (
    <div className="py-12">
      <ErrorState
        title="Couldn't load this listing"
        message="An error occurred while loading this listing. You can try again."
        retryLabel="Try again"
        onRetry={() => unstable_retry()}
      />
    </div>
  )
}
"use client"

import { useEffect } from "react"
import { ErrorState } from "@/components/ui/ErrorState"

// Global route-level error boundary. Must be a Client Component.
// Receives `unstable_retry` (Next.js 16) to attempt recovery. Never exposes stack traces.
export default function GlobalError({
  error,
  unstable_retry,
}: {
  error: Error & { digest?: string }
  unstable_retry: () => void
}) {
  useEffect(() => {
    // Architectural guidance: structured logging only in development.
    if (process.env.NODE_ENV !== "production") {
      console.error("[PrioraMarket] route error:", error)
    }
  }, [error])

  return (
    <div className="py-12">
      <ErrorState
        title="Something went wrong"
        message="An unexpected error occurred. You can try again without losing your search state."
        onRetry={() => unstable_retry()}
      />
    </div>
  )
}
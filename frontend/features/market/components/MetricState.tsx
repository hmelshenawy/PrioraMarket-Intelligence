import { Skeleton } from "@/components/ui/Skeleton"
import type { MetricSupportStatusDto } from "../types"

export interface MetricStateProps {
  status: MetricSupportStatusDto
  /** Optional override; defaults to the metric's own reason. */
  reason?: string | null
  isLoading?: boolean
  children?: React.ReactNode
}

// Renders a metric's non-ready states (loading / unsupported / unavailable) or passes
// children through for supported / partial metrics. Distinguishes unsupported (no
// platform tracking → reason text, no value) from a true calculated zero (supported →
// children render "0"). Never fabricates values.
export function MetricState({ status, reason, isLoading, children }: MetricStateProps) {
  if (isLoading) {
    return (
      <div className="flex flex-col gap-2" aria-hidden>
        <Skeleton className="h-8 w-24" />
        <Skeleton className="h-3 w-16" />
      </div>
    )
  }

  if (status.status === "supported") return <>{children}</>

  if (status.status === "partial") {
    return (
      <div className="flex flex-col gap-1">
        {children}
        {(reason ?? status.reason) && (
          <p className="text-xs text-muted">{reason ?? status.reason}</p>
        )}
      </div>
    )
  }

  // unsupported | unavailable → explanatory text, no value (never fabricate zero).
  const fallback = status.status === "unavailable" ? "No usable data for this scope" : "Not available"
  return (
    <p className="text-sm text-muted" role="note">
      {reason ?? status.reason ?? fallback}
    </p>
  )
}
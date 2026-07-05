import { Card } from "@/components/ui/Card"
import { MetricState } from "./MetricState"
import { formatAed } from "../utils/market-format"
import type { TypicalPriceRangeMetricDto } from "../types"

export function TypicalPriceRangeCard({ metric }: { metric: TypicalPriceRangeMetricDto }) {
  // In the supported branch, exactly one pair is populated: lower/upper (typical range)
  // or min/max (fallback for insufficient sample). Unavailable is handled by MetricState.
  const range =
    metric.lowerAmount != null && metric.upperAmount != null
      ? `${formatAed(metric.lowerAmount)} – ${formatAed(metric.upperAmount)}`
      : `${formatAed(metric.minAmount)} – ${formatAed(metric.maxAmount)}`

  return (
    <Card className="flex flex-col gap-2 p-5">
      <h3 className="text-sm text-muted">{metric.title}</h3>
      <MetricState status={metric.status} reason={metric.status.reason}>
        <div className="flex flex-col gap-1">
          <p className="text-2xl font-semibold text-text">{range}</p>
          <p className="text-xs text-muted">
            Median {formatAed(metric.medianAmount)} · Based on {metric.sampleSize} listings
          </p>
        </div>
      </MetricState>
    </Card>
  )
}
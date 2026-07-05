import { Card } from "@/components/ui/Card"
import { MetricState } from "./MetricState"
import { formatAed } from "../utils/market-format"
import type { MedianPriceMetricDto } from "../types"

export function MedianPriceCard({ metric }: { metric: MedianPriceMetricDto }) {
  return (
    <Card className="flex flex-col gap-2 p-5">
      <h3 className="text-sm text-muted">{metric.title}</h3>
      <MetricState status={metric.status} reason={metric.status.reason}>
        <div className="flex flex-col gap-1">
          <p className="text-2xl font-semibold text-text">{formatAed(metric.amount)}</p>
          <p className="text-xs text-muted">Based on {metric.sampleSize} listings</p>
        </div>
      </MetricState>
    </Card>
  )
}
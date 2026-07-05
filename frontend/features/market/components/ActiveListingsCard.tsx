import { Card } from "@/components/ui/Card"
import { MetricState } from "./MetricState"
import { formatCount } from "../utils/market-format"
import type { ActiveListingsMetricDto } from "../types"

export function ActiveListingsCard({ metric }: { metric: ActiveListingsMetricDto }) {
  return (
    <Card className="flex flex-col gap-2 p-5">
      <h3 className="text-sm text-muted">{metric.title}</h3>
      <MetricState status={metric.status} reason={metric.status.reason}>
        <div className="flex flex-col gap-1">
          <p className="text-2xl font-semibold text-text">{formatCount(metric.count)}</p>
          <p className="text-xs text-muted">{metric.scopeLabel}</p>
        </div>
      </MetricState>
    </Card>
  )
}
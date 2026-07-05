import { Card } from "@/components/ui/Card"
import { MetricState } from "./MetricState"
import { formatCount } from "../utils/market-format"
import type { InventoryChangeMetricDto } from "../types"

export function InventoryChangeCard({ metric }: { metric: InventoryChangeMetricDto }) {
  return (
    <Card className="flex flex-col gap-2 p-5">
      <h3 className="text-sm text-muted">{metric.title}</h3>
      <MetricState status={metric.status} reason={metric.status.reason}>
        <div className="flex flex-col gap-1">
          <p className="text-2xl font-semibold text-text">{formatCount(metric.activeInventory)}</p>
          <p className="text-xs text-muted">Active inventory</p>
          <dl className="mt-1 grid grid-cols-3 gap-2 text-xs">
            <div>
              <dt className="text-muted">New</dt>
              <dd className="text-text">{formatCount(metric.newListings)}</dd>
            </div>
            <div>
              <dt className="text-muted">Removed</dt>
              <dd className="text-text">{formatCount(metric.removedListings)}</dd>
            </div>
            <div>
              <dt className="text-muted">Net</dt>
              <dd className="text-text">{formatCount(metric.netChange)}</dd>
            </div>
          </dl>
        </div>
      </MetricState>
    </Card>
  )
}
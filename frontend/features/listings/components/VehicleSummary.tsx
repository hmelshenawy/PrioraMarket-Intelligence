import { Badge } from "@/components/ui/Badge"
import { Tag } from "@/components/ui/Tag"
import { Divider } from "@/components/ui/Divider"
import type { ListingDetailModel } from "../types"

export interface VehicleSummaryProps {
  model: ListingDetailModel
}

// VehicleSummary — headline listing identity and key facts.
// All values are display-ready (mapper-centralized); no null handling here.
export function VehicleSummary({ model }: VehicleSummaryProps) {
  const s = model.summary
  return (
    <div className="flex flex-col gap-3">
      <div className="flex flex-wrap items-start justify-between gap-2">
        <h1 className="text-2xl font-semibold text-text">{model.title}</h1>
        <span className="text-2xl font-semibold text-text">{s.priceLabel}</span>
      </div>
      <div className="flex flex-wrap items-center gap-2">
        {s.conditionLabel !== "—" && (
          <Badge variant="neutral" className="capitalize">
            {s.conditionLabel}
          </Badge>
        )}
        <Tag>{s.yearLabel}</Tag>
        <Tag>{s.kmLabel}</Tag>
        {s.sellerTypeLabel !== "—" && <Tag className="capitalize">{s.sellerTypeLabel}</Tag>}
      </div>
      <p className="text-sm text-muted">{s.locationLabel}</p>
      <Divider />
      <dl className="grid grid-cols-2 gap-x-4 gap-y-2 text-sm sm:grid-cols-3">
        <div>
          <dt className="text-xs text-muted">First seen</dt>
          <dd className="text-text">{s.firstSeenLabel}</dd>
        </div>
        <div>
          <dt className="text-xs text-muted">Last updated</dt>
          <dd className="text-text">{s.lastSeenLabel}</dd>
        </div>
      </dl>
    </div>
  )
}
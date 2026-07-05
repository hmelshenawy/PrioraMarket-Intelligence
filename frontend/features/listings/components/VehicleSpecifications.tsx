import { Card } from "@/components/ui/Card"
import type { ListingDetailModel, SpecRow } from "../types"

export interface VehicleSpecificationsProps {
  model: ListingDetailModel
}

// VehicleSpecifications — grouped display of all available specification fields,
// including unknown specs keys surfaced as additional specifications.
export function VehicleSpecifications({ model }: VehicleSpecificationsProps) {
  const groups: { title: string; rows: SpecRow[] }[] = [
    { title: "Vehicle specifications", rows: model.specifications },
    { title: "Additional specifications", rows: model.additionalSpecs },
    { title: "Seller & source", rows: sellerSourceRows(model) },
  ].filter((g) => g.rows.length > 0)

  if (groups.length === 0) {
    return <p className="text-sm text-muted">No additional specifications available.</p>
  }

  return (
    <div className="flex flex-col gap-4">
      {groups.map((group) => (
        <Card key={group.title} className="p-4">
          <h2 className="mb-3 text-sm font-semibold text-text">{group.title}</h2>
          <dl className="grid grid-cols-1 gap-x-6 gap-y-2 sm:grid-cols-2">
            {group.rows.map((r) => (
              <div key={r.label} className="flex justify-between gap-4 border-b border-border py-1 text-sm last:border-b-0">
                <dt className="text-muted">{r.label}</dt>
                <dd className="text-right text-text">{r.value}</dd>
              </div>
            ))}
          </dl>
        </Card>
      ))}
    </div>
  )
}

function sellerSourceRows(model: ListingDetailModel): SpecRow[] {
  const s = model.sellerSource
  const rows: SpecRow[] = []
  if (s.sellerLabel !== "—") rows.push({ label: "Seller", value: s.sellerLabel })
  if (s.marketplaceLabel !== "—") rows.push({ label: "Marketplace", value: s.marketplaceLabel })
  if (s.neighbourhoodLabel !== "—") rows.push({ label: "Neighbourhood", value: s.neighbourhoodLabel })
  if (s.isVerified != null) rows.push({ label: "Verified", value: s.isVerified ? "Yes" : "No" })
  if (s.isAgent != null) rows.push({ label: "Agent", value: s.isAgent ? "Yes" : "No" })
  return rows
}
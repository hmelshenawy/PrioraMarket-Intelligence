import type { FilterMetadataDto, FilterMetadataModel, FilterOption } from "../types"

const toOption = (value: string): FilterOption => ({ value, label: value })

// Humanize a raw categorical value for display (e.g., "dealer" → "Dealer").
const humanize = (v: string): string =>
  v
    .replace(/([a-z0-9])([A-Z])/g, "$1 $2")
    .replace(/\b\w/g, (c) => c.toUpperCase())

const toLabeledOption = (value: string): FilterOption => ({ value, label: humanize(value) })

// Map the filter metadata DTO to the display-ready model. Categorical values are
// converted to labeled options; ranges are passed through (null bounds are kept so
// the UI can soften/disable that side of the range control).
export function mapFilterMetadata(dto: FilterMetadataDto): FilterMetadataModel {
  const modelsByMake: Record<string, FilterOption[]> = {}
  const fallback: FilterOption[] = []
  for (const [make, models] of Object.entries(dto.models)) {
    const opts = models.map(toOption)
    modelsByMake[make] = opts
    fallback.push(...opts)
  }
  // Deduplicate the fallback list while preserving order.
  const seen = new Set<string>()
  const modelFallback = fallback.filter((o) => (seen.has(o.value) ? false : (seen.add(o.value), true)))

  return {
    makes: dto.makes.map(toOption),
    modelsByMake,
    modelFallback,
    price: dto.price,
    year: dto.year,
    km: dto.km,
    conditions: dto.conditions.map(toLabeledOption),
    sellerTypes: dto.sellerTypes.map(toLabeledOption),
  }
}
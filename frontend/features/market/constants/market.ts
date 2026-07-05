// Market feature constants. Metric order is the canonical card order required by the
// contract; period default matches the backend DTO default.

export const METRIC_ORDER = [
  "activeListings",
  "medianPrice",
  "typicalPriceRange",
  "inventoryChange",
  "priceDrops",
] as const

export type MetricType = (typeof METRIC_ORDER)[number]

export const DEFAULT_PERIOD_DAYS = 7
export const CURRENCY = "AED"

// Query key factory for TanStack Query. Keys include the canonical filters + period so
// cache entries do not collide across scopes.
export const marketQueryKeys = {
  all: ["market"] as const,
  snapshot: (request: { make?: string; model?: string; trim?: string; year?: number; periodDays?: number }) =>
    ["market", "snapshot", request] as const,
  filterOptions: (request: { make?: string; model?: string; trim?: string; year?: number }) =>
    ["market", "filter-options", request] as const,
} as const
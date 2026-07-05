import type { SearchUrlState } from "@/lib/routing/searchState"

// Centralized query key factories to prevent cache fragmentation.
// Listings/search keys are derived from normalized URL state, not raw param order.
export const queryKeys = {
  listings: {
    all: ["listings"] as const,
    search: (state: SearchUrlState) => ["listings", "search", state] as const,
  },
  listing: {
    all: ["listing"] as const,
    detail: (id: string) => ["listing", "detail", id] as const,
  },
  filters: {
    all: ["filters"] as const,
    metadata: () => ["filters", "metadata"] as const,
  },
  stats: {
    all: ["stats"] as const,
    overview: () => ["stats", "overview"] as const,
  },
  health: {
    all: ["health"] as const,
    status: () => ["health", "status"] as const,
  },
} as const
// Listings feature types. Listing entities (DTOs + UI models) live here; the
// search feature consumes them via the listings public API.

export interface ListingSearchResultDto {
  id: string
  externalId: string | null
  title: string | null
  make: string | null
  model: string | null
  trim: string | null
  year: number | null
  priceAed: number | null
  km: number | null
  condition: string | null
  location: string | null
  sellerType: string | null
  url: string | null
  photosCount: number | null
  firstSeenAt: string | null
  lastSeenAt: string | null
}

// Full detail payload (GET /api/v1/listings/:id); used by US3.
export interface ListingDetailDto extends ListingSearchResultDto {
  marketplace: string | null
  bodyType: string | null
  fuel: string | null
  transmission: string | null
  color: string | null
  specs: Record<string, unknown> | null
  seller: string | null
  isVerified: boolean | null
  isAgent: boolean | null
  neighbourhood: string | null
  firstSeenRunId: string | null
  lastSeenRunId: string | null
  canonicalHash: string | null
}

// Display-ready card model produced by the mapper; components never handle nulls.
export interface ListingCardModel {
  id: string
  title: string
  subtitle: string
  priceLabel: string
  kmLabel: string
  yearLabel: string
  conditionLabel: string
  locationLabel: string
  sellerTypeLabel: string
  href: string
  externalUrl: string | null
  photosCount: number | null
  firstSeenLabel: string
  lastSeenLabel: string
}

// --- Listing detail UI model (post-mapper; safe to render) -------------------

export interface SpecRow {
  label: string
  value: string
}

export interface ListingDetailModel {
  id: string
  title: string
  href: string
  gallery: {
    photosCount: number | null
  }
  summary: {
    priceLabel: string
    yearLabel: string
    kmLabel: string
    conditionLabel: string
    locationLabel: string
    sellerTypeLabel: string
    firstSeenLabel: string
    lastSeenLabel: string
  }
  sellerSource: {
    sellerLabel: string
    marketplaceLabel: string
    neighbourhoodLabel: string
    isVerified: boolean | null
    isAgent: boolean | null
  }
  specifications: SpecRow[]
  additionalSpecs: SpecRow[]
  marketplaceAction: {
    url: string | null
  }
}

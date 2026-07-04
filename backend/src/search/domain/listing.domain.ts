export interface ListingDomain {
  id: string;
  externalId: string | null;
  title: string | null;
  make: string | null;
  model: string | null;
  trim: string | null;
  year: number | null;
  priceAed: number | null;
  km: number | null;
  condition: string | null;
  location: string | null;
  sellerType: string | null;
  url: string | null;
  photosCount: number | null;
  firstSeenAt: string | null;
  lastSeenAt: string | null;
}

export interface ListingDetailDomain extends ListingDomain {
  marketplace: string | null;
  bodyType: string | null;
  fuel: string | null;
  transmission: string | null;
  color: string | null;
  specs: Record<string, unknown> | null;
  seller: string | null;
  isVerified: boolean | null;
  isAgent: boolean | null;
  neighbourhood: string | null;
  firstSeenRunId: string | null;
  lastSeenRunId: string | null;
  canonicalHash: string | null;
}

export interface SearchListingsResultDomain {
  rows: ListingDomain[];
  total: number;
}

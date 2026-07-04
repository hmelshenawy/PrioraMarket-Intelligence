export type ListingSort =
  | 'relevance'
  | 'newest'
  | 'price_asc'
  | 'price_desc'
  | 'year_asc'
  | 'year_desc'
  | 'km_asc'
  | 'km_desc';

export interface ListingSearchCriteria {
  q?: string;
  condition?: 'used' | 'new';
  make?: string;
  model?: string;
  yearFrom?: number;
  yearTo?: number;
  priceMin?: number;
  priceMax?: number;
  kmMin?: number;
  kmMax?: number;
  location?: string;
  sellerType?: string;
  page: number;
  limit: number;
  sort: ListingSort;
}

export interface BuiltListingSearchMeta {
  sortType: ListingSort;
  freeTextUsed: boolean;
}

export interface BuiltListingSearchQuery {
  where: Record<string, unknown>;
  orderBy: Record<string, unknown> | Array<Record<string, unknown>>;
  skip: number;
  take: number;
  select?: Record<string, unknown>;
  include?: Record<string, unknown>;
  requiresRawRead?: boolean;
  parameters?: unknown[];
  meta: BuiltListingSearchMeta;
}

export interface BuiltListingDetailQuery {
  where: Record<string, unknown>;
  select?: Record<string, unknown>;
  include?: Record<string, unknown>;
}

export interface BuiltFilterMetadataQuery {
  where: Record<string, unknown>;
  select?: Record<string, unknown>;
}

export interface BuiltInventoryStatsQuery {
  where: Record<string, unknown>;
  select?: Record<string, unknown>;
}

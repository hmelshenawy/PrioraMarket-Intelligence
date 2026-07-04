export class ListingSearchResultResponseDto {
  id!: string;
  externalId!: string | null;
  title!: string | null;
  make!: string | null;
  model!: string | null;
  trim!: string | null;
  year!: number | null;
  priceAed!: number | null;
  km!: number | null;
  condition!: string | null;
  location!: string | null;
  sellerType!: string | null;
  url!: string | null;
  photosCount!: number | null;
  firstSeenAt!: string | null;
  lastSeenAt!: string | null;
}

export class SearchListingsResponseDto {
  data!: ListingSearchResultResponseDto[];
  meta!: import('./pagination-meta-response.dto').PaginationMetaResponseDto;
}

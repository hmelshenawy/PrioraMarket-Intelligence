import { ListingSearchResultResponseDto } from './listing-search-result-response.dto';

export class ListingDetailResponseDto extends ListingSearchResultResponseDto {
  marketplace!: string | null;
  bodyType!: string | null;
  fuel!: string | null;
  transmission!: string | null;
  color!: string | null;
  specs!: Record<string, unknown> | null;
  seller!: string | null;
  isVerified!: boolean | null;
  isAgent!: boolean | null;
  neighbourhood!: string | null;
  firstSeenRunId!: string | null;
  lastSeenRunId!: string | null;
  canonicalHash!: string | null;
}

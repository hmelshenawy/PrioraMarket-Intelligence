import { FilterMetadataDomain } from './domain/listing-filters.domain';
import { InventoryStatsDomain } from './domain/listing-stats.domain';
import { ListingDetailDomain, SearchListingsResultDomain } from './domain/listing.domain';
import {
  BuiltFilterMetadataQuery,
  BuiltInventoryStatsQuery,
  BuiltListingDetailQuery,
  BuiltListingSearchQuery
} from './domain/search-query.domain';

export interface ListingReadRepositoryInterface {
  search(query: BuiltListingSearchQuery): Promise<SearchListingsResultDomain>;
  findDetail(query: BuiltListingDetailQuery): Promise<ListingDetailDomain | null>;
  getFilterMetadata(query: BuiltFilterMetadataQuery): Promise<FilterMetadataDomain>;
  getInventoryStats(query: BuiltInventoryStatsQuery): Promise<InventoryStatsDomain>;
}

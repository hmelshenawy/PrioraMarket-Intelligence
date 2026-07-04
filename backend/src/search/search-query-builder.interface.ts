import {
  BuiltFilterMetadataQuery,
  BuiltInventoryStatsQuery,
  BuiltListingDetailQuery,
  BuiltListingSearchQuery,
  ListingSearchCriteria
} from './domain/search-query.domain';

export interface ISearchQueryBuilder {
  buildListingSearchQuery(criteria: ListingSearchCriteria): BuiltListingSearchQuery;
  buildListingDetailQuery(id: string): BuiltListingDetailQuery;
  buildFilterMetadataQuery(): BuiltFilterMetadataQuery;
  buildInventoryStatsQuery(): BuiltInventoryStatsQuery;
}

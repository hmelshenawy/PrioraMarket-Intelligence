import { Injectable } from '@nestjs/common';
import { FilterMetadataDomain } from './domain/listing-filters.domain';
import { InventoryStatsDomain } from './domain/listing-stats.domain';
import { ListingDetailDomain, SearchListingsResultDomain } from './domain/listing.domain';
import {
  BuiltFilterMetadataQuery,
  BuiltInventoryStatsQuery,
  BuiltListingDetailQuery,
  BuiltListingSearchQuery
} from './domain/search-query.domain';
import { ListingReadRepositoryInterface } from './listing-read.repository.interface';

@Injectable()
export class PrismaListingReadRepository implements ListingReadRepositoryInterface {
  async search(_query: BuiltListingSearchQuery): Promise<SearchListingsResultDomain> {
    return { rows: [], total: 0 };
  }

  async findDetail(_query: BuiltListingDetailQuery): Promise<ListingDetailDomain | null> {
    return null;
  }

  async getFilterMetadata(_query: BuiltFilterMetadataQuery): Promise<FilterMetadataDomain> {
    return {
      makes: [],
      models: {},
      price: { min: null, max: null },
      year: { min: null, max: null },
      km: { min: null, max: null },
      conditions: [],
      sellerTypes: []
    };
  }

  async getInventoryStats(_query: BuiltInventoryStatsQuery): Promise<InventoryStatsDomain> {
    return {
      totalListings: 0,
      usedListings: 0,
      newListings: 0,
      totalMakes: 0,
      totalModels: 0,
      averagePriceAed: null,
      minPriceAed: null,
      maxPriceAed: null,
      lastUpdatedAt: null
    };
  }
}

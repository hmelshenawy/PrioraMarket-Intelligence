import { Injectable } from '@nestjs/common';
import {
  BuiltFilterMetadataQuery,
  BuiltInventoryStatsQuery,
  BuiltListingDetailQuery,
  BuiltListingSearchQuery,
  ListingSearchCriteria
} from './domain/search-query.domain';
import { ISearchQueryBuilder } from './search-query-builder.interface';

@Injectable()
export class SearchQueryBuilder implements ISearchQueryBuilder {
  buildListingSearchQuery(criteria: ListingSearchCriteria): BuiltListingSearchQuery {
    return {
      where: { status: 'ACTIVE' },
      orderBy: { lastSeenAt: 'desc' },
      skip: (criteria.page - 1) * criteria.limit,
      take: criteria.limit,
      select: this.listingSearchSelect()
    };
  }

  buildListingDetailQuery(id: string): BuiltListingDetailQuery {
    return {
      where: { id },
      include: { marketplaceSource: true, latestSnapshot: true }
    };
  }

  buildFilterMetadataQuery(): BuiltFilterMetadataQuery {
    return { where: { status: 'ACTIVE' }, select: this.filterMetadataSelect() };
  }

  buildInventoryStatsQuery(): BuiltInventoryStatsQuery {
    return { where: { status: 'ACTIVE' }, select: this.statsSelect() };
  }

  private listingSearchSelect(): Record<string, boolean> {
    return {
      id: true,
      uuid: true,
      title: true,
      make: true,
      model: true,
      trim: true,
      year: true,
      price: true,
      mileage: true,
      condition: true,
      location: true,
      sellerType: true,
      url: true,
      firstSeenAt: true,
      lastSeenAt: true
    };
  }

  private filterMetadataSelect(): Record<string, boolean> {
    return { make: true, model: true, price: true, year: true, mileage: true, condition: true, sellerType: true };
  }

  private statsSelect(): Record<string, boolean> {
    return { id: true, condition: true, make: true, model: true, price: true, lastSeenAt: true };
  }
}

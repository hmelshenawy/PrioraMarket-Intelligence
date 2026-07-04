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
    const where: Record<string, unknown> = { status: 'ACTIVE' };

    if (criteria.condition) {
      where.condition = criteria.condition;
    }

    if (criteria.make) {
      where.make = { equals: criteria.make, mode: 'insensitive' };
    }

    if (criteria.model) {
      where.model = { equals: criteria.model, mode: 'insensitive' };
    }

    if (criteria.yearFrom !== undefined || criteria.yearTo !== undefined) {
      where.year = this.range(criteria.yearFrom, criteria.yearTo);
    }

    if (criteria.priceMin !== undefined || criteria.priceMax !== undefined) {
      where.price = this.range(criteria.priceMin, criteria.priceMax);
    }

    if (criteria.kmMin !== undefined || criteria.kmMax !== undefined) {
      where.mileage = this.range(criteria.kmMin, criteria.kmMax);
    }

    if (criteria.location) {
      where.location = { contains: criteria.location, mode: 'insensitive' };
    }

    if (criteria.sellerType) {
      where.sellerType = { equals: criteria.sellerType, mode: 'insensitive' };
    }

    if (criteria.q) {
      where.OR = ['title', 'make', 'model', 'trim'].map((field) => ({ [field]: { contains: criteria.q, mode: 'insensitive' } }));
    }

    return {
      where,
      orderBy: this.orderBy(criteria),
      skip: (criteria.page - 1) * criteria.limit,
      take: criteria.limit,
      select: this.listingSearchSelect(),
      meta: { sortType: criteria.sort, freeTextUsed: Boolean(criteria.q) }
    };
  }

  buildListingDetailQuery(id: string): BuiltListingDetailQuery {
    return {
      where: { id: /^\d+$/.test(id) ? BigInt(id) : id },
      select: this.listingDetailSelect()
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

  private listingDetailSelect(): Record<string, boolean> {
    return {
      ...this.listingSearchSelect(),
      marketplaceSourceId: true,
      firstSeenRunId: true,
      lastSeenRunId: true,
      canonicalHash: true
    };
  }

  private statsSelect(): Record<string, boolean> {
    return { id: true, condition: true, make: true, model: true, price: true, lastSeenAt: true };
  }

  private range(min?: number, max?: number): Record<string, number> {
    return {
      ...(min !== undefined ? { gte: min } : {}),
      ...(max !== undefined ? { lte: max } : {})
    };
  }

  private orderBy(criteria: ListingSearchCriteria): Array<Record<string, unknown>> {
    if (criteria.sort === 'relevance' && criteria.q) {
      return [
        { _relevance: { fields: ['title', 'make', 'model', 'trim'], search: criteria.q, sort: 'desc' } },
        { lastSeenAt: 'desc' },
        { id: 'desc' }
      ];
    }

    const sortMap: Record<string, Array<Record<string, string>>> = {
      newest: [{ lastSeenAt: 'desc' }, { id: 'desc' }],
      price_asc: [{ price: 'asc' }, { id: 'desc' }],
      price_desc: [{ price: 'desc' }, { id: 'desc' }],
      year_asc: [{ year: 'asc' }, { id: 'desc' }],
      year_desc: [{ year: 'desc' }, { id: 'desc' }],
      km_asc: [{ mileage: 'asc' }, { id: 'desc' }],
      km_desc: [{ mileage: 'desc' }, { id: 'desc' }],
      relevance: [{ lastSeenAt: 'desc' }, { id: 'desc' }]
    };

    return sortMap[criteria.sort];
  }
}

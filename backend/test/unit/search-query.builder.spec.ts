import { SearchQueryBuilder } from '../../src/search/search-query.builder';

describe('SearchQueryBuilder', () => {
  const builder = new SearchQueryBuilder();

  it('builds filters, sorting, pagination, and projections for listing search', () => {
    const query = builder.buildListingSearchQuery({
      q: 'camry',
      condition: 'used',
      make: 'Toyota',
      model: 'Camry',
      yearFrom: 2018,
      yearTo: 2023,
      priceMin: 10000,
      priceMax: 120000,
      kmMin: 0,
      kmMax: 90000,
      location: 'Dubai',
      sellerType: 'dealer',
      page: 2,
      limit: 25,
      sort: 'relevance'
    });

    expect(query.skip).toBe(25);
    expect(query.take).toBe(25);
    expect(query.select).toMatchObject({ id: true, uuid: true, title: true, lastSeenAt: true });
    expect(query.where).toMatchObject({
      status: 'ACTIVE',
      condition: 'used',
      make: { equals: 'Toyota', mode: 'insensitive' },
      model: { equals: 'Camry', mode: 'insensitive' },
      year: { gte: 2018, lte: 2023 },
      price: { gte: 10000, lte: 120000 },
      mileage: { gte: 0, lte: 90000 },
      location: { contains: 'Dubai', mode: 'insensitive' },
      sellerType: { equals: 'dealer', mode: 'insensitive' }
    });
    expect(query.where.OR).toHaveLength(4);
    expect(query.orderBy).toEqual([{ _relevance: { fields: ['title', 'make', 'model', 'trim'], search: 'camry', sort: 'desc' } }, { lastSeenAt: 'desc' }, { id: 'desc' }]);
    expect(query.meta).toEqual({ sortType: 'relevance', freeTextUsed: true });
  });

  it('builds newest ordering by default shape', () => {
    const query = builder.buildListingSearchQuery({ page: 1, limit: 20, sort: 'newest' });

    expect(query.where).toEqual({ status: 'ACTIVE' });
    expect(query.orderBy).toEqual([{ lastSeenAt: 'desc' }, { id: 'desc' }]);
    expect(query.meta).toEqual({ sortType: 'newest', freeTextUsed: false });
  });
});

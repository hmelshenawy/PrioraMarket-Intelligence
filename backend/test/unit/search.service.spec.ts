import { ConfigService } from '@nestjs/config';
import { FilterMetadataResponseMapper } from '../../src/search/mappers/filter-metadata-response.mapper';
import { ListingResponseMapper } from '../../src/search/mappers/listing-response.mapper';
import { SearchService } from '../../src/search/search.service';

describe('SearchService', () => {
  const repository = {
    search: jest.fn(),
    findDetail: jest.fn(),
    getFilterMetadata: jest.fn(),
    getInventoryStats: jest.fn()
  };
  const queryBuilder = {
    buildListingSearchQuery: jest.fn(),
    buildListingDetailQuery: jest.fn(),
    buildFilterMetadataQuery: jest.fn(),
    buildInventoryStatsQuery: jest.fn()
  };
  const cache = { get: jest.fn(), set: jest.fn(), clear: jest.fn() };
  const service = new SearchService(
    repository,
    queryBuilder,
    cache,
    {} as ConfigService,
    new ListingResponseMapper(),
    new FilterMetadataResponseMapper()
  );

  beforeEach(() => jest.clearAllMocks());

  it('uses defaults to calculate pagination metadata', async () => {
    queryBuilder.buildListingSearchQuery.mockReturnValue({ where: {}, orderBy: [], skip: 0, take: 20, meta: { sortType: 'newest', freeTextUsed: false } });
    repository.search.mockResolvedValue({ rows: [], total: 0 });

    await expect(service.search({ page: 1, limit: 20, sort: 'newest' })).resolves.toEqual({ data: [], meta: { page: 1, limit: 20, total: 0, totalPages: 0 } });
  });

  it('falls back relevance sort to newest when no free text exists', async () => {
    queryBuilder.buildListingSearchQuery.mockReturnValue({ where: {}, orderBy: [], skip: 0, take: 20, meta: { sortType: 'newest', freeTextUsed: false } });
    repository.search.mockResolvedValue({ rows: [], total: 0 });

    await service.search({ page: 1, limit: 20, sort: 'relevance' });

    expect(queryBuilder.buildListingSearchQuery).toHaveBeenCalledWith({ page: 1, limit: 20, sort: 'newest' });
  });

  it('uses ListingReadRepositoryInterface through the injected abstraction', async () => {
    queryBuilder.buildListingSearchQuery.mockReturnValue({ where: { status: 'ACTIVE' }, orderBy: [], skip: 0, take: 20, meta: { sortType: 'newest', freeTextUsed: false } });
    repository.search.mockResolvedValue({ rows: [], total: 0 });

    await service.search({ page: 1, limit: 20, sort: 'newest' });

    expect(repository.search).toHaveBeenCalledWith(expect.objectContaining({ where: { status: 'ACTIVE' } }));
  });
});

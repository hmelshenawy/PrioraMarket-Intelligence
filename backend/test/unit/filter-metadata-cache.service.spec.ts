import { ConfigService } from '@nestjs/config';
import { FilterMetadataResponseMapper } from '../../src/search/mappers/filter-metadata-response.mapper';
import { ListingResponseMapper } from '../../src/search/mappers/listing-response.mapper';
import { SearchService } from '../../src/search/search.service';

describe('SearchService filter metadata cache', () => {
  const repository = { search: jest.fn(), findDetail: jest.fn(), getFilterMetadata: jest.fn(), getInventoryStats: jest.fn() };
  const queryBuilder = { buildListingSearchQuery: jest.fn(), buildListingDetailQuery: jest.fn(), buildFilterMetadataQuery: jest.fn(), buildInventoryStatsQuery: jest.fn() };
  const cache = { get: jest.fn(), set: jest.fn(), clear: jest.fn() };
  const service = new SearchService(repository, queryBuilder, cache, {} as ConfigService, new ListingResponseMapper(), new FilterMetadataResponseMapper());
  const metadata = { makes: ['Toyota'], models: { Toyota: ['Camry'] }, price: { min: 1, max: 2 }, year: { min: 2020, max: 2022 }, km: { min: 0, max: 10 }, conditions: ['used'], sellerTypes: ['dealer'] };

  beforeEach(() => jest.clearAllMocks());

  it('returns cached metadata without repository call', async () => {
    cache.get.mockReturnValue(metadata);
    await expect(service.getFilterMetadata()).resolves.toEqual(metadata);
    expect(repository.getFilterMetadata).not.toHaveBeenCalled();
  });

  it('loads and caches metadata on cache miss', async () => {
    cache.get.mockReturnValue(null);
    queryBuilder.buildFilterMetadataQuery.mockReturnValue({ where: { status: 'ACTIVE' } });
    repository.getFilterMetadata.mockResolvedValue(metadata);
    await expect(service.getFilterMetadata()).resolves.toEqual(metadata);
    expect(cache.set).toHaveBeenCalledWith(metadata);
  });
});

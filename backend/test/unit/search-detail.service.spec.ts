import { ConfigService } from '@nestjs/config';
import { NotFoundException } from '@nestjs/common';
import { FilterMetadataResponseMapper } from '../../src/search/mappers/filter-metadata-response.mapper';
import { ListingResponseMapper } from '../../src/search/mappers/listing-response.mapper';
import { SearchService } from '../../src/search/search.service';

describe('SearchService detail', () => {
  const repository = { search: jest.fn(), findDetail: jest.fn(), getFilterMetadata: jest.fn(), getInventoryStats: jest.fn() };
  const queryBuilder = { buildListingSearchQuery: jest.fn(), buildListingDetailQuery: jest.fn(), buildFilterMetadataQuery: jest.fn(), buildInventoryStatsQuery: jest.fn() };
  const cache = { get: jest.fn(), set: jest.fn(), clear: jest.fn() };
  const service = new SearchService(repository, queryBuilder, cache, {} as ConfigService, new ListingResponseMapper(), new FilterMetadataResponseMapper());

  beforeEach(() => jest.clearAllMocks());

  it('uses repository abstraction and mapper for detail', async () => {
    const detail = {
      id: '1', externalId: null, marketplace: null, title: null, make: null, model: null, trim: null, year: null, priceAed: null, km: null,
      condition: null, bodyType: null, fuel: null, transmission: null, color: null, specs: null, sellerType: null, seller: null,
      isVerified: null, isAgent: null, neighbourhood: null, location: null, url: null, photosCount: null, firstSeenRunId: null,
      lastSeenRunId: null, firstSeenAt: null, lastSeenAt: null, canonicalHash: null
    };
    queryBuilder.buildListingDetailQuery.mockReturnValue({ where: { id: 1 } });
    repository.findDetail.mockResolvedValue(detail);

    await expect(service.findDetail('1')).resolves.toEqual(detail);
    expect(repository.findDetail).toHaveBeenCalledWith({ where: { id: 1 } });
  });

  it('throws NotFoundException when repository returns null', async () => {
    queryBuilder.buildListingDetailQuery.mockReturnValue({ where: { id: 999 } });
    repository.findDetail.mockResolvedValue(null);

    await expect(service.findDetail('999')).rejects.toBeInstanceOf(NotFoundException);
  });
});

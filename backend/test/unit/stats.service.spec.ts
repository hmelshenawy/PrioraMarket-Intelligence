import { InventoryStatsResponseMapper } from '../../src/search/mappers/inventory-stats-response.mapper';
import { StatsService } from '../../src/search/stats.service';

describe('StatsService', () => {
  const repository = { search: jest.fn(), findDetail: jest.fn(), getFilterMetadata: jest.fn(), getInventoryStats: jest.fn() };
  const queryBuilder = { buildListingSearchQuery: jest.fn(), buildListingDetailQuery: jest.fn(), buildFilterMetadataQuery: jest.fn(), buildInventoryStatsQuery: jest.fn() };
  const service = new StatsService(repository, queryBuilder, new InventoryStatsResponseMapper());

  beforeEach(() => jest.clearAllMocks());

  it('uses LISTING_READ_REPOSITORY abstraction and mapper for stats', async () => {
    const stats = {
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
    queryBuilder.buildInventoryStatsQuery.mockReturnValue({ where: { status: 'ACTIVE' } });
    repository.getInventoryStats.mockResolvedValue(stats);

    await expect(service.getInventoryStats()).resolves.toEqual(stats);
    expect(repository.getInventoryStats).toHaveBeenCalledWith({ where: { status: 'ACTIVE' } });
  });
});

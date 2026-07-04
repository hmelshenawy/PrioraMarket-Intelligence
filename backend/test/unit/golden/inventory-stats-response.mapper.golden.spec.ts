import { InventoryStatsResponseMapper } from '../../../src/search/mappers/inventory-stats-response.mapper';

describe('InventoryStatsResponseMapper golden responses', () => {
  it('maps inventory stats domain data to stable DTO output', () => {
    const stats = {
      totalListings: 10,
      usedListings: 7,
      newListings: 3,
      totalMakes: 4,
      totalModels: 8,
      averagePriceAed: 85000,
      minPriceAed: 10000,
      maxPriceAed: 250000,
      lastUpdatedAt: '2026-07-04T00:00:00.000Z'
    };

    expect(new InventoryStatsResponseMapper().toResponse(stats)).toEqual(stats);
  });
});

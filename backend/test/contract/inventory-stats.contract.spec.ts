import { Test } from '@nestjs/testing';
import { StatsController } from '../../src/search/stats.controller';
import { StatsService } from '../../src/search/stats.service';

describe('GET /api/v1/stats contract', () => {
  it('returns stable inventory stats shape through StatsController', async () => {
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
    const moduleRef = await Test.createTestingModule({
      controllers: [StatsController],
      providers: [{ provide: StatsService, useValue: { getInventoryStats: jest.fn().mockResolvedValue(stats) } }]
    }).compile();

    await expect(moduleRef.get(StatsController).getStats()).resolves.toEqual(stats);
  });
});

import { Test } from '@nestjs/testing';
import { SearchController } from '../../src/search/search.controller';
import { SearchService } from '../../src/search/search.service';

describe('GET /api/v1/listings/filters contract', () => {
  it('returns stable filter metadata shape through SearchController', async () => {
    const metadata = { makes: [], models: {}, price: { min: null, max: null }, year: { min: null, max: null }, km: { min: null, max: null }, conditions: [], sellerTypes: [] };
    const moduleRef = await Test.createTestingModule({
      controllers: [SearchController],
      providers: [{ provide: SearchService, useValue: { search: jest.fn(), findDetail: jest.fn(), getFilterMetadata: jest.fn().mockResolvedValue(metadata) } }]
    }).compile();

    await expect(moduleRef.get(SearchController).filters()).resolves.toEqual(metadata);
  });
});

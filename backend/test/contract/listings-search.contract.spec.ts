import { Test } from '@nestjs/testing';
import { SearchController } from '../../src/search/search.controller';
import { SearchService } from '../../src/search/search.service';

describe('GET /api/v1/listings contract', () => {
  it('returns paginated listing response shape through SearchController', async () => {
    const search = jest.fn().mockResolvedValue({ data: [], meta: { page: 1, limit: 20, total: 0, totalPages: 0 } });
    const moduleRef = await Test.createTestingModule({
      controllers: [SearchController],
      providers: [{ provide: SearchService, useValue: { search, getFilterMetadata: jest.fn(), findDetail: jest.fn() } }]
    }).compile();

    const controller = moduleRef.get(SearchController);

    await expect(controller.search({ page: 1, limit: 20, sort: 'newest' })).resolves.toEqual({
      data: [],
      meta: { page: 1, limit: 20, total: 0, totalPages: 0 }
    });
  });
});

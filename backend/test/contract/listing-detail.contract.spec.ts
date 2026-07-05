import { NotFoundException } from '@nestjs/common';
import { Test } from '@nestjs/testing';
import { SearchController } from '../../src/search/search.controller';
import { SearchService } from '../../src/search/search.service';

describe('GET /api/v1/listings/:id contract', () => {
  it('returns listing detail response shape through SearchController', async () => {
    const detail = {
      id: '1',
      externalId: 'external-1',
      marketplace: 'Dubizzle UAE',
      title: 'Toyota Camry',
      make: 'Toyota',
      model: 'Camry',
      trim: null,
      year: 2022,
      priceAed: 85000,
      km: 45000,
      condition: 'used',
      bodyType: null,
      fuel: null,
      transmission: null,
      color: null,
      specs: {},
      sellerType: 'dealer',
      seller: null,
      isVerified: null,
      isAgent: null,
      neighbourhood: null,
      location: 'Dubai',
      url: 'https://dubai.dubizzle.com/motors/used-cars/toyota/camry/1234567/',
      photosCount: null,
      firstSeenRunId: '10',
      lastSeenRunId: '11',
      firstSeenAt: '2026-07-01T00:00:00.000Z',
      lastSeenAt: '2026-07-04T00:00:00.000Z',
      canonicalHash: 'hash'
    };
    const moduleRef = await Test.createTestingModule({
      controllers: [SearchController],
      providers: [{ provide: SearchService, useValue: { search: jest.fn(), getFilterMetadata: jest.fn(), findDetail: jest.fn().mockResolvedValue(detail) } }]
    }).compile();

    await expect(moduleRef.get(SearchController).detail('1')).resolves.toEqual(detail);
  });

  it('propagates not found responses', async () => {
    const moduleRef = await Test.createTestingModule({
      controllers: [SearchController],
      providers: [{ provide: SearchService, useValue: { search: jest.fn(), getFilterMetadata: jest.fn(), findDetail: jest.fn().mockRejectedValue(new NotFoundException('Listing not found')) } }]
    }).compile();

    await expect(moduleRef.get(SearchController).detail('missing')).rejects.toBeInstanceOf(NotFoundException);
  });
});

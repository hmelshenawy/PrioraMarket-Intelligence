import { ListingResponseMapper } from '../../../src/search/mappers/listing-response.mapper';

describe('ListingResponseMapper golden search responses', () => {
  const mapper = new ListingResponseMapper();

  it('maps listing search domain data to stable DTO output', () => {
    const response = mapper.toSearchResponse(
      [
        {
          id: '1',
          externalId: 'dubizzle-1',
          title: 'Toyota Camry',
          make: 'Toyota',
          model: 'Camry',
          trim: null,
          year: 2022,
          priceAed: 85000,
          km: 45000,
          condition: 'used',
          location: 'Dubai',
          sellerType: 'dealer',
          url: 'https://example.test/listing/1',
          photosCount: null,
          firstSeenAt: '2026-07-01T00:00:00.000Z',
          lastSeenAt: '2026-07-04T00:00:00.000Z'
        }
      ],
      1,
      20,
      1
    );

    expect(response).toEqual({
      data: [
        {
          id: '1',
          externalId: 'dubizzle-1',
          title: 'Toyota Camry',
          make: 'Toyota',
          model: 'Camry',
          trim: null,
          year: 2022,
          priceAed: 85000,
          km: 45000,
          condition: 'used',
          location: 'Dubai',
          sellerType: 'dealer',
          url: 'https://example.test/listing/1',
          photosCount: null,
          firstSeenAt: '2026-07-01T00:00:00.000Z',
          lastSeenAt: '2026-07-04T00:00:00.000Z'
        }
      ],
      meta: { page: 1, limit: 20, total: 1, totalPages: 1 }
    });
  });
});

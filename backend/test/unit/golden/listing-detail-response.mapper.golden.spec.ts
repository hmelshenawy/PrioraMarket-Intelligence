import { ListingResponseMapper } from '../../../src/search/mappers/listing-response.mapper';

describe('ListingResponseMapper golden detail responses', () => {
  it('maps listing detail domain data to stable DTO output', () => {
    const detail = {
      id: '1', externalId: 'external-1', marketplace: 'Dubizzle UAE', title: 'Toyota Camry', make: 'Toyota', model: 'Camry', trim: 'SE',
      year: 2022, priceAed: 85000, km: 45000, condition: 'used', bodyType: 'sedan', fuel: 'petrol', transmission: 'automatic',
      color: 'white', specs: { doors: 4 }, sellerType: 'dealer', seller: 'Dealer LLC', isVerified: true, isAgent: false,
      neighbourhood: 'Marina', location: 'Dubai', url: 'https://dubai.dubizzle.com/motors/used-cars/toyota/camry/1234567/', photosCount: 12, firstSeenRunId: '10',
      lastSeenRunId: '11', firstSeenAt: '2026-07-01T00:00:00.000Z', lastSeenAt: '2026-07-04T00:00:00.000Z', canonicalHash: 'hash'
    };

    expect(new ListingResponseMapper().toDetail(detail)).toEqual(detail);
  });
});

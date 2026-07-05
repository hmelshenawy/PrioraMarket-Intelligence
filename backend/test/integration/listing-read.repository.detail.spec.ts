import { PrismaListingReadRepository } from '../../src/search/listing-read.repository';

describe('PrismaListingReadRepository detail', () => {
  it('reads listing, marketplace, and latest snapshot without writes', async () => {
    const prisma = {
      listing: { findFirst: jest.fn().mockResolvedValue({
        id: 1, uuid: 'external-1', marketplaceSourceId: 2, title: 'Toyota Camry', make: 'Toyota', model: 'Camry', trim: 'SE', year: 2022,
        price: '85000.00', mileage: 45000, condition: 'used', location: 'Dubai', sellerType: 'dealer', url: 'https://dubai.dubizzle.com/motors/used-cars/toyota/camry/1234567/',
        firstSeenAt: new Date('2026-07-01T00:00:00.000Z'), lastSeenAt: new Date('2026-07-04T00:00:00.000Z'), firstSeenRunId: 10,
        lastSeenRunId: 11, canonicalHash: 'hash'
      }) },
      marketplaceSource: { findUnique: jest.fn().mockResolvedValue({ name: 'Dubizzle UAE' }) },
      listingSnapshot: { findFirst: jest.fn().mockResolvedValue({ canonicalPayload: { bodyType: 'sedan', fuel: 'petrol', photosCount: 12 } }) }
    };
    const repository = new PrismaListingReadRepository(prisma as never);

    await expect(repository.findDetail({ where: { id: BigInt(1) } })).resolves.toMatchObject({
      id: '1', externalId: 'external-1', marketplace: 'Dubizzle UAE', trim: 'SE', url: 'https://dubai.dubizzle.com/motors/used-cars/toyota/camry/1234567/', bodyType: 'sedan', fuel: 'petrol', photosCount: 12
    });
    expect('create' in repository).toBe(false);
    expect('update' in repository).toBe(false);
    expect('delete' in repository).toBe(false);
  });
});

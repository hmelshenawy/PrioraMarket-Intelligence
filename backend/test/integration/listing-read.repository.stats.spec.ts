import { PrismaListingReadRepository } from '../../src/search/listing-read.repository';

describe('PrismaListingReadRepository stats', () => {
  it('reads aggregate stats without writes', async () => {
    const prisma = {
      listing: {
        findMany: jest.fn().mockResolvedValue([
          { condition: 'used', make: 'Toyota', model: 'Camry', price: '10000.00', lastSeenAt: new Date('2026-07-01T00:00:00.000Z') },
          { condition: 'new', make: 'Nissan', model: 'Patrol', price: '20000.00', lastSeenAt: new Date('2026-07-04T00:00:00.000Z') }
        ])
      }
    };
    const repository = new PrismaListingReadRepository(prisma as never);

    await expect(repository.getInventoryStats({ where: { status: 'ACTIVE' } })).resolves.toEqual({
      totalListings: 2,
      usedListings: 1,
      newListings: 1,
      totalMakes: 2,
      totalModels: 2,
      averagePriceAed: 15000,
      minPriceAed: 10000,
      maxPriceAed: 20000,
      lastUpdatedAt: '2026-07-04T00:00:00.000Z'
    });
    expect('create' in repository).toBe(false);
  });
});

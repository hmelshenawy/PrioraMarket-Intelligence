import { PrismaListingReadRepository } from '../../src/search/listing-read.repository';

describe('PrismaListingReadRepository search', () => {
  it('exposes read-only search method without mutation methods', () => {
    const repository = new PrismaListingReadRepository({ listing: { findMany: jest.fn(), count: jest.fn() } } as never);

    expect(repository.search).toBeInstanceOf(Function);
    expect('create' in repository).toBe(false);
    expect('update' in repository).toBe(false);
    expect('delete' in repository).toBe(false);
  });

  it('executes read queries and maps rows to domain objects', async () => {
    const prisma = {
      listing: {
        findMany: jest.fn().mockResolvedValue([
          {
            id: 1,
            uuid: 'external-1',
            title: 'Toyota Camry',
            make: 'Toyota',
            model: 'Camry',
            trim: null,
            year: 2022,
            price: '85000.00',
            mileage: 45000,
            condition: 'used',
            location: 'Dubai',
            sellerType: 'dealer',
            url: 'https://example.test/1',
            firstSeenAt: new Date('2026-07-01T00:00:00.000Z'),
            lastSeenAt: new Date('2026-07-04T00:00:00.000Z')
          }
        ]),
        count: jest.fn().mockResolvedValue(1)
      }
    };
    const repository = new PrismaListingReadRepository(prisma as never);

    await expect(
      repository.search({ where: { status: 'ACTIVE' }, orderBy: [], skip: 0, take: 20, select: { id: true }, meta: { sortType: 'newest', freeTextUsed: false } })
    ).resolves.toEqual({
      rows: [
        {
          id: '1',
          externalId: 'external-1',
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
          url: 'https://example.test/1',
          photosCount: null,
          firstSeenAt: '2026-07-01T00:00:00.000Z',
          lastSeenAt: '2026-07-04T00:00:00.000Z'
        }
      ],
      total: 1
    });
    expect(prisma.listing.findMany).toHaveBeenCalled();
    expect(prisma.listing.count).toHaveBeenCalled();
  });
});

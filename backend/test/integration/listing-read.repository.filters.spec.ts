import { PrismaListingReadRepository } from '../../src/search/listing-read.repository';

describe('PrismaListingReadRepository filters', () => {
  it('reads distinct metadata and ranges without writes', async () => {
    const prisma = { listing: { findMany: jest.fn().mockResolvedValue([
      { make: 'Toyota', model: 'Camry', price: '10000.00', year: 2020, mileage: 1000, condition: 'used', sellerType: 'dealer' },
      { make: 'Toyota', model: 'Corolla', price: '20000.00', year: 2022, mileage: 2000, condition: 'new', sellerType: 'owner' }
    ]) } };
    const repository = new PrismaListingReadRepository(prisma as never);
    await expect(repository.getFilterMetadata({ where: { status: 'ACTIVE' } })).resolves.toEqual({
      makes: ['Toyota'], models: { Toyota: ['Camry', 'Corolla'] }, price: { min: 10000, max: 20000 }, year: { min: 2020, max: 2022 }, km: { min: 1000, max: 2000 }, conditions: ['new', 'used'], sellerTypes: ['dealer', 'owner']
    });
    expect('create' in repository).toBe(false);
  });
});

import { PrismaListingReadRepository } from '../../src/search/listing-read.repository';
import { SearchQueryBuilder } from '../../src/search/search-query.builder';

describe('read-only safety', () => {
  it('keeps listing and ingestion counts unchanged around read API repository calls', async () => {
    const prisma = {
      listing: {
        count: jest.fn().mockResolvedValue(2),
        findMany: jest.fn().mockResolvedValue([]),
        findFirst: jest.fn().mockResolvedValue(null),
        create: jest.fn(),
        update: jest.fn(),
        upsert: jest.fn(),
        delete: jest.fn()
      },
      ingestionRun: { count: jest.fn().mockResolvedValue(3), create: jest.fn(), update: jest.fn(), delete: jest.fn() },
      rawListing: { count: jest.fn().mockResolvedValue(5), create: jest.fn(), update: jest.fn(), delete: jest.fn() },
      marketplaceSource: { findUnique: jest.fn() },
      listingSnapshot: { findFirst: jest.fn() }
    };
    const repository = new PrismaListingReadRepository(prisma as never);
    const queryBuilder = new SearchQueryBuilder();
    const before = await counts(prisma);

    await repository.search(queryBuilder.buildListingSearchQuery({ page: 1, limit: 20, sort: 'newest' }));
    await repository.findDetail(queryBuilder.buildListingDetailQuery('999'));
    await repository.getFilterMetadata(queryBuilder.buildFilterMetadataQuery());
    await repository.getInventoryStats(queryBuilder.buildInventoryStatsQuery());

    await expect(counts(prisma)).resolves.toEqual(before);
    for (const table of [prisma.listing, prisma.ingestionRun, prisma.rawListing]) {
      expect(table.create).not.toHaveBeenCalled();
      expect(table.update).not.toHaveBeenCalled();
      expect(table.delete).not.toHaveBeenCalled();
    }
    expect(prisma.listing.upsert).not.toHaveBeenCalled();
  });
});

async function counts(prisma: { listing: Countable; ingestionRun: Countable; rawListing: Countable }) {
  return {
    listings: await prisma.listing.count(),
    ingestionRuns: await prisma.ingestionRun.count(),
    rawListings: await prisma.rawListing.count()
  };
}

interface Countable {
  count(): Promise<number>;
}

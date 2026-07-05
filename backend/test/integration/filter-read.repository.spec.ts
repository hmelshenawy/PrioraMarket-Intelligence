import { PrismaFilterReadRepository } from '../../src/analytics/filter-read.repository';
import type { CatalogReadRepositoryInterface } from '../../src/analytics/catalog-read.repository.interface';

type GroupByArgs = { by: string[]; where: Record<string, unknown>; _count: unknown; orderBy: unknown };

/**
 * Fake CatalogReadRepositoryInterface: returns pre-seeded make/model display
 * maps. Defaults to empty maps (all null) → canonical fallback, which preserves
 * the US2/T057 assertions. US3/T062 tests seed display names to assert catalog
 * resolution.
 */
function buildCatalog(
  makeDisplays: Map<string, string | null> = new Map(),
  modelDisplays: Map<string, string | null> = new Map()
): CatalogReadRepositoryInterface {
  return {
    findMakeDisplay: jest.fn(async (make: string) => makeDisplays.get(make.toLowerCase()) ?? null),
    findModelDisplay: jest.fn(async (_make: string, model: string) => modelDisplays.get(model.toLowerCase()) ?? null),
    findMakeDisplays: jest.fn(async (makes: string[]) => {
      const m = new Map<string, string | null>();
      for (const mk of makes) m.set(mk.toLowerCase(), makeDisplays.get(mk.toLowerCase()) ?? null);
      return m;
    }),
    findModelDisplays: jest.fn(async (_make: string, models: string[]) => {
      const m = new Map<string, string | null>();
      for (const mo of models) m.set(mo.toLowerCase(), modelDisplays.get(mo.toLowerCase()) ?? null);
      return m;
    })
  };
}

describe('PrismaFilterReadRepository cascading (US2 / T057 + US3 / T062)', () => {
  function buildPrisma() {
    const groupBy = jest.fn(async (args: GroupByArgs) => {
      const field = args.by[0];
      if (field === 'make') {
        return [
          { make: 'toyota', _count: { _all: 4381 } },
          { make: 'bmw', _count: { _all: 2981 } }
        ];
      }
      if (field === 'model') {
        return [
          { model: 'corolla', _count: { _all: 842 } },
          { model: 'camry', _count: { _all: 612 } }
        ];
      }
      if (field === 'trim') {
        return [
          { trim: 'xli', _count: { _all: 214 } },
          { trim: 'gli', _count: { _all: 120 } }
        ];
      }
      if (field === 'year') {
        return [
          { year: 2023, _count: { _all: 57 } },
          { year: 2022, _count: { _all: 31 } }
        ];
      }
      return [];
    });
    const findFirst = jest.fn().mockResolvedValue({
      lastSeenAt: new Date('2026-07-05T08:00:00.000Z'),
      lastSeenRunId: 1042n,
      normalizationVersion: 'canonical-2024.05'
    });
    return { listing: { groupBy, findFirst } };
  }

  it('lists makes with canonical-fallback display names and active listing counts', async () => {
    // Empty catalog → canonical fallback (US2 behavior preserved).
    const repo = new PrismaFilterReadRepository(buildPrisma() as never, buildCatalog());
    const makes = await repo.listMakes();
    expect(makes).toEqual([
      { value: 'toyota', displayName: 'toyota', activeListingCount: 4381 },
      { value: 'bmw', displayName: 'bmw', activeListingCount: 2981 }
    ]);
  });

  it('scopes model options to the selected canonical make', async () => {
    const prisma = buildPrisma();
    const repo = new PrismaFilterReadRepository(prisma as never, buildCatalog());
    const models = await repo.listModels('toyota');
    expect(models.map((m) => m.value)).toEqual(['corolla', 'camry']);
    const call = (prisma.listing.groupBy as jest.Mock).mock.calls[0][0] as GroupByArgs;
    expect(call.where.make).toEqual({ equals: 'toyota', mode: 'insensitive' });
    // Models are NOT constrained by sibling makes — only the selected make applies.
    expect(call.where.model).toEqual({ not: null });
  });

  it('scopes trims to make+model and years to make+model+trim', async () => {
    const prisma = buildPrisma();
    const catalog = buildCatalog();
    const repo = new PrismaFilterReadRepository(prisma as never, catalog);

    const trims = await repo.listTrims('toyota', 'corolla');
    expect(trims.map((t) => t.value)).toEqual(['xli', 'gli']);
    const trimCall = (prisma.listing.groupBy as jest.Mock).mock.calls[0][0] as GroupByArgs;
    expect(trimCall.where.make).toEqual({ equals: 'toyota', mode: 'insensitive' });
    expect(trimCall.where.model).toEqual({ equals: 'corolla', mode: 'insensitive' });

    const years = await repo.listYears('toyota', 'corolla', 'xli');
    expect(years.map((y) => y.value)).toEqual([2023, 2022]);
    const yearCall = (prisma.listing.groupBy as jest.Mock).mock.calls[1][0] as GroupByArgs;
    expect(yearCall.where.trim).toEqual({ equals: 'xli', mode: 'insensitive' });
    // Year options are integer values with canonical-fallback display names.
    expect(years[0]).toEqual({ value: 2023, displayName: '2023', activeListingCount: 57 });
    // Trims and years never consult the catalog (no trim/year display column).
    expect(catalog.findMakeDisplays).not.toHaveBeenCalled();
    expect(catalog.findModelDisplays).not.toHaveBeenCalled();
  });

  it('derives scoped freshness from the latest listing observation', async () => {
    const prisma = buildPrisma();
    const repo = new PrismaFilterReadRepository(prisma as never, buildCatalog());
    const freshness = await repo.getFreshness({ make: 'toyota' });
    expect(freshness).toEqual({
      lastUpdated: '2026-07-05T08:00:00.000Z',
      datasetVersion: 'canonical-2024.05',
      scrapeRunId: 1042
    });
    const call = (prisma.listing.findFirst as jest.Mock).mock.calls[0][0];
    expect(call.where.make).toEqual({ equals: 'toyota', mode: 'insensitive' });
    expect(call.where.status).toBe('ACTIVE');
    expect(call.orderBy).toEqual({ lastSeenAt: 'desc' });
  });

  it('returns all-null freshness when no scoped listings exist', async () => {
    const prisma = {
      listing: { groupBy: jest.fn().mockResolvedValue([]), findFirst: jest.fn().mockResolvedValue(null) }
    };
    const repo = new PrismaFilterReadRepository(prisma as never, buildCatalog());
    const freshness = await repo.getFreshness({ make: 'unknown' });
    expect(freshness).toEqual({ lastUpdated: null, datasetVersion: null, scrapeRunId: null });
  });

  it('exposes read-only repository methods without mutation methods', () => {
    const repo = new PrismaFilterReadRepository(buildPrisma() as never, buildCatalog());
    expect(repo.listMakes).toBeInstanceOf(Function);
    expect(repo.listModels).toBeInstanceOf(Function);
    expect(repo.listTrims).toBeInstanceOf(Function);
    expect(repo.listYears).toBeInstanceOf(Function);
    expect(repo.getFreshness).toBeInstanceOf(Function);
    expect('create' in repo).toBe(false);
    expect('update' in repo).toBe(false);
    expect('delete' in repo).toBe(false);
  });

  // US3 / T062 — catalog display-name resolution with canonical fallback.
  describe('catalog display-name resolution (US3 / T062)', () => {
    const makeDisplays = new Map<string, string | null>([
      ['toyota', 'Toyota'],
      ['bmw', 'BMW']
    ]);
    const modelDisplays = new Map<string, string | null>([
      ['corolla', 'Corolla'],
      ['camry', 'Camry']
    ]);

    it('resolves make option display names from the catalog with a single batch call', async () => {
      const prisma = buildPrisma();
      const catalog = buildCatalog(makeDisplays, modelDisplays);
      const repo = new PrismaFilterReadRepository(prisma as never, catalog);
      const makes = await repo.listMakes();
      expect(makes).toEqual([
        { value: 'toyota', displayName: 'Toyota', activeListingCount: 4381 },
        { value: 'bmw', displayName: 'BMW', activeListingCount: 2981 }
      ]);
      // One batched catalog lookup for all makes — no per-make fan-out.
      expect(catalog.findMakeDisplays).toHaveBeenCalledTimes(1);
      expect(catalog.findMakeDisplays).toHaveBeenCalledWith(['toyota', 'bmw']);
    });

    it('falls back to the canonical make value when the catalog has no row', async () => {
      const prisma = buildPrisma();
      // Catalog knows toyota but not bmw.
      const catalog = buildCatalog(new Map([['toyota', 'Toyota']]), new Map());
      const repo = new PrismaFilterReadRepository(prisma as never, catalog);
      const makes = await repo.listMakes();
      expect(makes[0]).toEqual({ value: 'toyota', displayName: 'Toyota', activeListingCount: 4381 });
      // bmw has no catalog row → canonical fallback, unchanged (no title-casing).
      expect(makes[1]).toEqual({ value: 'bmw', displayName: 'bmw', activeListingCount: 2981 });
    });

    it('resolves model option display names from the catalog scoped by the selected make', async () => {
      const prisma = buildPrisma();
      const catalog = buildCatalog(makeDisplays, modelDisplays);
      const repo = new PrismaFilterReadRepository(prisma as never, catalog);
      const models = await repo.listModels('toyota');
      expect(models).toEqual([
        { value: 'corolla', displayName: 'Corolla', activeListingCount: 842 },
        { value: 'camry', displayName: 'Camry', activeListingCount: 612 }
      ]);
      // Model display lookup is scoped by the selected canonical make.
      expect(catalog.findModelDisplays).toHaveBeenCalledWith('toyota', ['corolla', 'camry']);
    });

    it('uses canonical fallback for trim and year options (no catalog consultation)', async () => {
      const prisma = buildPrisma();
      const catalog = buildCatalog(makeDisplays, modelDisplays);
      const repo = new PrismaFilterReadRepository(prisma as never, catalog);

      const trims = await repo.listTrims('toyota', 'corolla');
      // Trim display = canonical fallback (catalog has no trim column).
      expect(trims).toEqual([
        { value: 'xli', displayName: 'xli', activeListingCount: 214 },
        { value: 'gli', displayName: 'gli', activeListingCount: 120 }
      ]);

      const years = await repo.listYears('toyota', 'corolla', 'xli');
      // Year display = canonical fallback (the integer stringified).
      expect(years).toEqual([
        { value: 2023, displayName: '2023', activeListingCount: 57 },
        { value: 2022, displayName: '2022', activeListingCount: 31 }
      ]);

      // Trims and years never call the catalog.
      expect(catalog.findMakeDisplays).not.toHaveBeenCalled();
      expect(catalog.findModelDisplays).not.toHaveBeenCalled();
    });
  });
});
import { PrismaSnapshotReadRepository } from '../../src/analytics/snapshot-read.repository';
import { MarketSnapshotService } from '../../src/analytics/market-snapshot.service';
import { SnapshotAggregationService } from '../../src/analytics/aggregation/market-snapshot.aggregator';
import type {
  ActiveListingsMetric,
  MedianPriceMetric,
  TypicalPriceRangeMetric
} from '../../src/analytics/domain/market-metric.domain';
import { MarketSnapshotResponseMapper } from '../../src/analytics/mappers/market-snapshot-response.mapper';
import type { CatalogReadRepositoryInterface } from '../../src/analytics/catalog-read.repository.interface';

describe('MarketSnapshotService + PrismaSnapshotReadRepository integration', () => {
  const PRICES = [100000, 120000, 140000, 160000, 180000, 200000, 220000, 240000];

  function buildPrisma() {
    return {
      listing: {
        count: jest.fn().mockResolvedValue(8),
        findMany: jest.fn().mockResolvedValue(PRICES.map((price) => ({ price: `${price}.00` }))),
        findFirst: jest.fn().mockResolvedValue({
          lastSeenAt: new Date('2026-07-05T08:00:00.000Z'),
          lastSeenRunId: 1042n,
          normalizationVersion: 'canonical-2024.05'
        })
      }
    };
  }

  /**
   * Fake CatalogReadRepositoryInterface. Defaults to null lookups (canonical
   * fallback), preserving US2 scope-label assertions. US3 tests seed display
   * names to assert catalog resolution.
   */
  function buildCatalog(
    makeDisplay: string | null = null,
    modelDisplay: string | null = null
  ): CatalogReadRepositoryInterface {
    return {
      findMakeDisplay: jest.fn().mockResolvedValue(makeDisplay),
      findModelDisplay: jest.fn().mockResolvedValue(modelDisplay),
      findMakeDisplays: jest.fn().mockResolvedValue(new Map<string, string | null>()),
      findModelDisplays: jest.fn().mockResolvedValue(new Map<string, string | null>())
    };
  }

  it('exposes read-only repository methods without mutation methods', () => {
    const repository = new PrismaSnapshotReadRepository(buildPrisma() as never);
    expect(repository.countActiveListings).toBeInstanceOf(Function);
    expect('create' in repository).toBe(false);
    expect('update' in repository).toBe(false);
    expect('delete' in repository).toBe(false);
  });

  it('assembles an overall snapshot with freshness populated from seeded listing timestamps', async () => {
    const prisma = buildPrisma();
    const repository = new PrismaSnapshotReadRepository(prisma as never);
    const service = new MarketSnapshotService(
      repository,
      new SnapshotAggregationService(),
      new MarketSnapshotResponseMapper(),
      buildCatalog()
    );

    const result = await service.getSnapshot({ periodDays: 7 } as never);

    // Read-only fan-out: count + prices + freshness.
    expect(prisma.listing.count).toHaveBeenCalledTimes(1);
    expect(prisma.listing.findMany).toHaveBeenCalledTimes(1);
    expect(prisma.listing.findFirst).toHaveBeenCalledTimes(1);

    expect(result.scope).toEqual({ level: 'overall', label: 'Overall UAE Used Cars', canonical: {} });
    expect(result.period).toEqual({ days: 7, label: 'Last 7 days' });

    // Freshness derived from the seeded latest listing observation.
    expect(result.freshness.lastUpdated).toBe('2026-07-05T08:00:00.000Z');
    expect(result.freshness.datasetVersion).toBe('canonical-2024.05');
    expect(result.freshness.scrapeRunId).toBe(1042);

    // Metric order + raw values.
    expect(result.metrics.map((m: { type: string }) => m.type)).toEqual([
      'activeListings',
      'medianPrice',
      'typicalPriceRange',
      'inventoryChange',
      'priceDrops'
    ]);
    expect((result.metrics[0] as ActiveListingsMetric).count).toBe(8);
    expect((result.metrics[1] as MedianPriceMetric).amount).toBe(170000);
    expect((result.metrics[1] as MedianPriceMetric).sampleSize).toBe(8);
    expect((result.metrics[2] as TypicalPriceRangeMetric).lowerAmount).toBe(135000);
    expect((result.metrics[2] as TypicalPriceRangeMetric).upperAmount).toBe(205000);

    // History-dependent metrics default to unsupported/partial in US1.
    expect(result.supportStatuses.inventoryChange.status).toBe('partial');
    expect(result.supportStatuses.priceDrops.status).toBe('unsupported');

    // generatedAt is an ISO-8601 string set at generation time.
    expect(typeof result.generatedAt).toBe('string');
    expect(() => new Date(result.generatedAt).toISOString()).not.toThrow();
  });

  it('returns all-null freshness when no scoped listings exist', async () => {
    const prisma = {
      listing: {
        count: jest.fn().mockResolvedValue(0),
        findMany: jest.fn().mockResolvedValue([]),
        findFirst: jest.fn().mockResolvedValue(null)
      }
    };
    const repository = new PrismaSnapshotReadRepository(prisma as never);
    const service = new MarketSnapshotService(
      repository,
      new SnapshotAggregationService(),
      new MarketSnapshotResponseMapper(),
      buildCatalog()
    );

    const result = await service.getSnapshot({ periodDays: 7 } as never);

    expect(result.freshness).toEqual({ lastUpdated: null, datasetVersion: null, scrapeRunId: null });
    expect((result.metrics[0] as ActiveListingsMetric).count).toBe(0);
    expect(result.supportStatuses.medianPrice.status).toBe('unavailable');
  });

  // US2 (T049/T050/T051): filtered scope — all reads scoped by canonical filters,
  // aggregator produces scope-relative metrics, and the scope label is the canonical fallback.
  it('scopes all reads by canonical filters and builds a filtered scope label', async () => {
    const prisma = buildPrisma();
    const repository = new PrismaSnapshotReadRepository(prisma as never);
    const service = new MarketSnapshotService(
      repository,
      new SnapshotAggregationService(),
      new MarketSnapshotResponseMapper(),
      buildCatalog()
    );

    const result = await service.getSnapshot({
      make: 'toyota',
      model: 'corolla',
      trim: 'xli',
      year: 2023,
      periodDays: 7
    } as never);

    // The count query is scoped by all canonical filters (exact match, no normalization).
    const countWhere = (prisma.listing.count as jest.Mock).mock.calls[0][0].where;
    expect(countWhere).toMatchObject({
      status: 'ACTIVE',
      make: { equals: 'toyota', mode: 'insensitive' },
      model: { equals: 'corolla', mode: 'insensitive' },
      trim: { equals: 'xli', mode: 'insensitive' },
      year: 2023
    });
    // Freshness is scoped by the same filters.
    const freshnessWhere = (prisma.listing.findFirst as jest.Mock).mock.calls[0][0].where;
    expect(freshnessWhere).toMatchObject({ make: { equals: 'toyota', mode: 'insensitive' }, year: 2023 });

    // Scope label = canonical fallback (raw values joined, no transformation/normalization).
    expect(result.scope).toEqual({
      level: 'year',
      label: 'toyota corolla xli 2023',
      canonical: { make: 'toyota', model: 'corolla', trim: 'xli', year: 2023 }
    });
    // Aggregator reuses the US1 calculation paths with the scope-relative label.
    expect((result.metrics[0] as ActiveListingsMetric).scopeLabel).toBe('toyota corolla xli 2023');
    expect(result.metrics.map((m: { type: string }) => m.type)).toEqual([
      'activeListings',
      'medianPrice',
      'typicalPriceRange',
      'inventoryChange',
      'priceDrops'
    ]);
  });

  it('builds a make-only scope label and level', async () => {
    const prisma = buildPrisma();
    const repository = new PrismaSnapshotReadRepository(prisma as never);
    const service = new MarketSnapshotService(
      repository,
      new SnapshotAggregationService(),
      new MarketSnapshotResponseMapper(),
      buildCatalog()
    );

    const result = await service.getSnapshot({ make: 'toyota', periodDays: 7 } as never);
    expect(result.scope).toEqual({
      level: 'make',
      label: 'toyota',
      canonical: { make: 'toyota' }
    });
  });

  // US3 (T065): scope label uses catalog display names for make/model when
  // available, with canonical fallback for trim/year (catalog has no trim/year
  // display column). Canonical filters echoed in the response stay raw.
  it('builds the scope label from catalog display names when available', async () => {
    const prisma = buildPrisma();
    const repository = new PrismaSnapshotReadRepository(prisma as never);
    const catalog = buildCatalog('Toyota', 'Corolla');
    const service = new MarketSnapshotService(
      repository,
      new SnapshotAggregationService(),
      new MarketSnapshotResponseMapper(),
      catalog
    );

    const result = await service.getSnapshot({
      make: 'toyota',
      model: 'corolla',
      trim: 'xli',
      year: 2023,
      periodDays: 7
    } as never);

    // Catalog display names for make+model; canonical fallback for trim+year
    // (no transformation — "xli" stays "xli", year stringified).
    expect(result.scope.label).toBe('Toyota Corolla xli 2023');
    // Canonical filters remain the raw canonical values.
    expect(result.scope.canonical).toEqual({ make: 'toyota', model: 'corolla', trim: 'xli', year: 2023 });
    expect((result.metrics[0] as ActiveListingsMetric).scopeLabel).toBe('Toyota Corolla xli 2023');
    // Catalog looked up the single make and (make, model) once each.
    expect(catalog.findMakeDisplay).toHaveBeenCalledWith('toyota');
    expect(catalog.findModelDisplay).toHaveBeenCalledWith('toyota', 'corolla');
  });

  it('falls back to canonical values in the scope label when the catalog has no row', async () => {
    const prisma = buildPrisma();
    const repository = new PrismaSnapshotReadRepository(prisma as never);
    // Catalog returns null → canonical fallback, unchanged (no title-casing).
    const service = new MarketSnapshotService(
      repository,
      new SnapshotAggregationService(),
      new MarketSnapshotResponseMapper(),
      buildCatalog(null, null)
    );

    const result = await service.getSnapshot({ make: 'toyota', periodDays: 7 } as never);
    expect(result.scope).toEqual({
      level: 'make',
      label: 'toyota',
      canonical: { make: 'toyota' }
    });
  });
});
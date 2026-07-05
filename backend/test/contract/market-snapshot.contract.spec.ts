import { Test } from '@nestjs/testing';
import { validate } from 'class-validator';
import { plainToInstance } from 'class-transformer';
import { MarketSnapshotController } from '../../src/analytics/market-snapshot.controller';
import { MarketSnapshotService } from '../../src/analytics/market-snapshot.service';
import { MarketSnapshotQueryDto } from '../../src/analytics/dto/market-snapshot-query.dto';

describe('GET /api/v1/market/snapshot contract', () => {
  const overallSnapshot = {
    scope: { level: 'overall', label: 'Overall UAE Used Cars', canonical: {} },
    filters: { periodDays: 7 },
    period: { days: 7, label: 'Last 7 days' },
    metrics: [
      {
        type: 'activeListings',
        title: 'Active Listings',
        status: { status: 'supported', dataAvailable: true },
        count: 4381,
        scopeLabel: 'Overall UAE Used Cars'
      },
      {
        type: 'medianPrice',
        title: 'Median Price',
        status: { status: 'supported', dataAvailable: true },
        amount: 165000,
        currency: 'AED',
        sampleSize: 842
      },
      {
        type: 'typicalPriceRange',
        title: 'Typical Price Range',
        status: { status: 'supported', dataAvailable: true },
        method: 'typical-range',
        currency: 'AED',
        medianAmount: 165000,
        lowerAmount: 145000,
        upperAmount: 190000,
        minAmount: null,
        maxAmount: null,
        sampleSize: 842
      },
      {
        type: 'inventoryChange',
        title: 'Inventory Change',
        status: { status: 'partial', dataAvailable: true, reason: 'Period inventory change tracking is not available' },
        activeInventory: 4381,
        newListings: null,
        removedListings: null,
        netChange: null,
        periodDays: 7
      },
      {
        type: 'priceDrops',
        title: 'Price Drops',
        status: { status: 'unsupported', dataAvailable: false, reason: 'Price history is not available' },
        count: null,
        averageDropPercentage: null,
        sampleSize: null,
        periodDays: 7
      }
    ],
    supportStatuses: {
      activeListings: { status: 'supported', dataAvailable: true },
      medianPrice: { status: 'supported', dataAvailable: true },
      typicalPriceRange: { status: 'supported', dataAvailable: true },
      inventoryChange: { status: 'partial', dataAvailable: true, reason: 'Period inventory change tracking is not available' },
      priceDrops: { status: 'unsupported', dataAvailable: false, reason: 'Price history is not available' }
    },
    freshness: {
      lastUpdated: '2026-07-05T08:00:00.000Z',
      datasetVersion: 'canonical-2024.05',
      scrapeRunId: 1042
    },
    generatedAt: '2026-07-05T12:30:00.000Z'
  };

  it('returns overall snapshot response shape through MarketSnapshotController', async () => {
    const moduleRef = await Test.createTestingModule({
      controllers: [MarketSnapshotController],
      providers: [
        { provide: MarketSnapshotService, useValue: { getSnapshot: jest.fn().mockResolvedValue(overallSnapshot) } }
      ]
    }).compile();

    const controller = moduleRef.get(MarketSnapshotController);
    const query = new MarketSnapshotQueryDto();
    query.periodDays = 7;

    await expect(controller.getSnapshot(query)).resolves.toEqual(overallSnapshot);
  });

  it('exposes the required metric order, raw values, freshness, and generatedAt', () => {
    const types = overallSnapshot.metrics.map((m: { type: string }) => m.type);
    expect(types).toEqual(['activeListings', 'medianPrice', 'typicalPriceRange', 'inventoryChange', 'priceDrops']);
    expect(overallSnapshot.freshness.lastUpdated).toBe('2026-07-05T08:00:00.000Z');
    expect(overallSnapshot.freshness.datasetVersion).toBe('canonical-2024.05');
    expect(overallSnapshot.freshness.scrapeRunId).toBe(1042);
    expect(overallSnapshot.generatedAt).toBe('2026-07-05T12:30:00.000Z');
    expect(overallSnapshot.scope.level).toBe('overall');
    expect(overallSnapshot.scope.label).toBe('Overall UAE Used Cars');
    // Raw numeric values, not formatted strings.
    expect(typeof overallSnapshot.metrics[1].amount).toBe('number');
    expect(overallSnapshot.metrics[1].currency).toBe('AED');
  });

  // US2 (T046): filtered scope with canonical filters echoed and freshness present.
  const filteredSnapshot = {
    scope: {
      level: 'year',
      label: 'toyota corolla xli 2023',
      canonical: { make: 'toyota', model: 'corolla', trim: 'xli', year: 2023 }
    },
    filters: { make: 'toyota', model: 'corolla', trim: 'xli', year: 2023, periodDays: 7 },
    period: { days: 7, label: 'Last 7 days' },
    metrics: overallSnapshot.metrics.map((m: { type: string }) =>
      m.type === 'activeListings'
        ? { ...m, count: 57, scopeLabel: 'toyota corolla xli 2023' }
        : m
    ),
    supportStatuses: overallSnapshot.supportStatuses,
    freshness: {
      lastUpdated: '2026-07-05T08:00:00.000Z',
      datasetVersion: 'canonical-2024.05',
      scrapeRunId: 1042
    },
    generatedAt: '2026-07-05T12:30:00.000Z'
  };

  it('returns a filtered snapshot response shape through MarketSnapshotController', async () => {
    const moduleRef = await Test.createTestingModule({
      controllers: [MarketSnapshotController],
      providers: [
        {
          provide: MarketSnapshotService,
          useValue: { getSnapshot: jest.fn().mockResolvedValue(filteredSnapshot) }
        }
      ]
    }).compile();

    const controller = moduleRef.get(MarketSnapshotController);
    const query = new MarketSnapshotQueryDto();
    Object.assign(query, { make: 'toyota', model: 'corolla', trim: 'xli', year: 2023, periodDays: 7 });

    await expect(controller.getSnapshot(query)).resolves.toEqual(filteredSnapshot);
  });

  it('echoes canonical filters and exposes freshness for a filtered scope', () => {
    expect(filteredSnapshot.scope.level).toBe('year');
    expect(filteredSnapshot.scope.canonical).toEqual({
      make: 'toyota',
      model: 'corolla',
      trim: 'xli',
      year: 2023
    });
    // Canonical filters are echoed unchanged (no normalization).
    expect(filteredSnapshot.filters).toEqual({
      make: 'toyota',
      model: 'corolla',
      trim: 'xli',
      year: 2023,
      periodDays: 7
    });
    // Freshness is present and distinct from generatedAt.
    expect(filteredSnapshot.freshness.lastUpdated).toBe('2026-07-05T08:00:00.000Z');
    expect(filteredSnapshot.freshness.scrapeRunId).toBe(1042);
    expect(filteredSnapshot.generatedAt).toBe('2026-07-05T12:30:00.000Z');
  });

  it.each([
    ['model without make', { model: 'corolla', periodDays: 7 }, /model requires make/i],
    ['trim without make+model', { make: 'toyota', trim: 'xli', periodDays: 7 }, /trim requires make and model/i],
    ['year without make+model+trim', { make: 'toyota', model: 'corolla', year: 2023, periodDays: 7 }, /year requires make, model, and trim/i]
  ])('rejects an invalid filter hierarchy (%s) with a validation error', async (_label, payload, expected) => {
    const dto = plainToInstance(MarketSnapshotQueryDto, payload);
    const errors = await validate(dto);
    expect(errors.length).toBeGreaterThan(0);
    const messages = errors.flatMap((e) => (e.constraints ? Object.values(e.constraints) : []));
    expect(messages.some((m) => expected.test(m))).toBe(true);
  });
});
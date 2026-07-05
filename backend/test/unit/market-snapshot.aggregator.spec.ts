import { SnapshotAggregationService } from '../../src/analytics/aggregation/market-snapshot.aggregator';
import type {
  ActiveListingsMetric,
  InventoryChangeMetric,
  MedianPriceMetric,
  PriceDropsMetric,
  TypicalPriceRangeMetric
} from '../../src/analytics/domain/market-metric.domain';

describe('SnapshotAggregationService', () => {
  const aggregator = new SnapshotAggregationService();

  it('computes active listings, median, and P25/P75 typical range for a sufficient sample', () => {
    const prices = [100000, 120000, 140000, 160000, 180000, 200000, 220000, 240000];
    const { metrics, supportStatuses } = aggregator.aggregate({
      activeListingsCount: 8,
      prices,
      scopeLabel: 'Overall UAE Used Cars',
      periodDays: 7
    });

    const active = metrics[0] as ActiveListingsMetric;
    expect(active.type).toBe('activeListings');
    expect(active.count).toBe(8);
    expect(active.scopeLabel).toBe('Overall UAE Used Cars');
    expect(active.status.status).toBe('supported');

    const median = metrics[1] as MedianPriceMetric;
    expect(median.type).toBe('medianPrice');
    expect(median.amount).toBe(170000); // 160000 + 0.5*(180000-160000)
    expect(median.currency).toBe('AED');
    expect(median.sampleSize).toBe(8);

    const range = metrics[2] as TypicalPriceRangeMetric;
    expect(range.type).toBe('typicalPriceRange');
    expect(range.method).toBe('typical-range');
    expect(range.medianAmount).toBe(170000);
    expect(range.lowerAmount).toBe(135000); // 120000 + 0.75*(140000-120000)
    expect(range.upperAmount).toBe(205000); // 200000 + 0.25*(220000-200000)
    expect(range.minAmount).toBeNull();
    expect(range.maxAmount).toBeNull();
    expect(range.sampleSize).toBe(8);

    expect(supportStatuses.activeListings.status).toBe('supported');
    expect(supportStatuses.medianPrice.status).toBe('supported');
    expect(supportStatuses.typicalPriceRange.status).toBe('supported');
  });

  it('falls back to min/max when the priced sample is insufficient', () => {
    const { metrics } = aggregator.aggregate({
      activeListingsCount: 2,
      prices: [100000, 150000],
      scopeLabel: 'Overall UAE Used Cars',
      periodDays: 7
    });

    const range = metrics[2] as TypicalPriceRangeMetric;
    expect(range.lowerAmount).toBeNull();
    expect(range.upperAmount).toBeNull();
    expect(range.minAmount).toBe(100000);
    expect(range.maxAmount).toBe(150000);
    expect(range.medianAmount).toBe(125000); // 100000 + 0.5*(150000-100000)
    expect(range.sampleSize).toBe(2);
  });

  it('reports unsupported-by-default for new/removed/net and priceDrops', () => {
    const { metrics, supportStatuses } = aggregator.aggregate({
      activeListingsCount: 4381,
      prices: [165000],
      scopeLabel: 'Overall UAE Used Cars',
      periodDays: 7
    });

    const inventory = metrics[3] as InventoryChangeMetric;
    expect(inventory.activeInventory).toBe(4381);
    expect(inventory.newListings).toBeNull();
    expect(inventory.removedListings).toBeNull();
    expect(inventory.netChange).toBeNull();
    expect(inventory.periodDays).toBe(7);
    expect(inventory.status.status).toBe('partial');
    expect(inventory.status.dataAvailable).toBe(true);
    expect(inventory.status.reason).toBeDefined();

    const drops = metrics[4] as PriceDropsMetric;
    expect(drops.count).toBeNull();
    expect(drops.averageDropPercentage).toBeNull();
    expect(drops.sampleSize).toBeNull();
    expect(drops.status.status).toBe('unsupported');
    expect(drops.status.dataAvailable).toBe(false);

    expect(supportStatuses.inventoryChange.status).toBe('partial');
    expect(supportStatuses.priceDrops.status).toBe('unsupported');
  });

  it('reports unavailable price metrics with sample size zero when no usable prices exist', () => {
    const { metrics, supportStatuses } = aggregator.aggregate({
      activeListingsCount: 0,
      prices: [],
      scopeLabel: 'Overall UAE Used Cars',
      periodDays: 7
    });

    const active = metrics[0] as ActiveListingsMetric;
    expect(active.count).toBe(0);
    expect(active.status.status).toBe('supported'); // true calculated zero

    const median = metrics[1] as MedianPriceMetric;
    expect(median.amount).toBeNull();
    expect(median.sampleSize).toBe(0);
    expect(median.status.status).toBe('unavailable');
    expect(median.status.dataAvailable).toBe(false);

    const range = metrics[2] as TypicalPriceRangeMetric;
    expect(range.medianAmount).toBeNull();
    expect(range.lowerAmount).toBeNull();
    expect(range.upperAmount).toBeNull();
    expect(range.minAmount).toBeNull();
    expect(range.maxAmount).toBeNull();
    expect(range.sampleSize).toBe(0);
    expect(range.status.status).toBe('unavailable');

    expect(supportStatuses.medianPrice.status).toBe('unavailable');
    expect(supportStatuses.typicalPriceRange.status).toBe('unavailable');
  });

  it('emits metrics in the required order', () => {
    const { metrics } = aggregator.aggregate({
      activeListingsCount: 1,
      prices: [100000],
      scopeLabel: 'Overall UAE Used Cars',
      periodDays: 7
    });
    expect(metrics.map((m) => m.type)).toEqual([
      'activeListings',
      'medianPrice',
      'typicalPriceRange',
      'inventoryChange',
      'priceDrops'
    ]);
  });
});
import { SnapshotAggregationService } from '../../../src/analytics/aggregation/market-snapshot.aggregator';
import { toAppliedMarketFilters } from '../../../src/analytics/domain/applied-market-filters.domain';
import { UNKNOWN_FRESHNESS } from '../../../src/analytics/domain/freshness.domain';
import type { ActiveListingsMetric, MedianPriceMetric } from '../../../src/analytics/domain/market-metric.domain';
import { MarketSnapshotResponseMapper } from '../../../src/analytics/mappers/market-snapshot-response.mapper';

// Canonical listing fixture rows (read-only inputs). Only the fields used by the
// snapshot pipeline are modeled here.
interface FixtureListing {
  price: string | null;
  status: string;
  lastSeenAt: Date | null;
  lastSeenRunId: bigint | null;
  normalizationVersion: string | null;
}

const PRICES = [100000, 120000, 140000, 160000, 180000, 200000, 220000, 240000];

const fixtureListings: FixtureListing[] = PRICES.map((price, index) => ({
  price: `${price}.00`,
  status: 'ACTIVE',
  // Index 7 carries the latest observation / run / version.
  lastSeenAt: new Date(`2026-07-0${index + 1}T08:00:00.000Z`),
  lastSeenRunId: BigInt(1000 + index),
  normalizationVersion: 'canonical-2024.05'
}));

// Mirrors PrismaSnapshotReadRepository.getFreshness: latest observation by lastSeenAt.
function deriveFreshness(listings: FixtureListing[]) {
  if (listings.length === 0) return { ...UNKNOWN_FRESHNESS };
  const latest = [...listings]
    .filter((l) => l.lastSeenAt)
    .sort((a, b) => (b.lastSeenAt as Date).getTime() - (a.lastSeenAt as Date).getTime())[0];
  if (!latest) return { ...UNKNOWN_FRESHNESS };
  return {
    lastUpdated: (latest.lastSeenAt as Date).toISOString(),
    datasetVersion: latest.normalizationVersion,
    scrapeRunId: latest.lastSeenRunId === null ? null : Number(latest.lastSeenRunId)
  };
}

function derivePrices(listings: FixtureListing[]): number[] {
  return listings
    .map((l) => (l.price === null ? null : Number(l.price)))
    .filter((p): p is number => p !== null && Number.isFinite(p))
    .sort((a, b) => a - b);
}

const aggregator = new SnapshotAggregationService();
const mapper = new MarketSnapshotResponseMapper();

describe('Market Snapshot golden aggregation', () => {
  it('produces the expected overall snapshot JSON for a priced fixture', () => {
    const prices = derivePrices(fixtureListings);
    const freshness = deriveFreshness(fixtureListings);
    const filters = toAppliedMarketFilters({}, 7);

    const { metrics, supportStatuses } = aggregator.aggregate({
      activeListingsCount: fixtureListings.length,
      prices,
      scopeLabel: 'Overall UAE Used Cars',
      periodDays: 7
    });

    const response = mapper.toResponse({
      scope: { level: 'overall', label: 'Overall UAE Used Cars', canonical: {} },
      filters,
      metrics,
      supportStatuses,
      period: { days: 7, label: 'Last 7 days' },
      freshness,
      generatedAt: '2026-07-05T12:30:00.000Z'
    });

    expect(response).toEqual({
      scope: { level: 'overall', label: 'Overall UAE Used Cars', canonical: {} },
      filters: { periodDays: 7 },
      period: { days: 7, label: 'Last 7 days' },
      metrics: [
        {
          type: 'activeListings',
          title: 'Active Listings',
          status: { status: 'supported', dataAvailable: true },
          count: 8,
          scopeLabel: 'Overall UAE Used Cars'
        },
        {
          type: 'medianPrice',
          title: 'Median Price',
          status: { status: 'supported', dataAvailable: true },
          amount: 170000,
          currency: 'AED',
          sampleSize: 8
        },
        {
          type: 'typicalPriceRange',
          title: 'Typical Price Range',
          status: { status: 'supported', dataAvailable: true },
          method: 'typical-range',
          currency: 'AED',
          medianAmount: 170000,
          lowerAmount: 135000,
          upperAmount: 205000,
          minAmount: null,
          maxAmount: null,
          sampleSize: 8
        },
        {
          type: 'inventoryChange',
          title: 'Inventory Change',
          status: { status: 'partial', dataAvailable: true, reason: 'Period inventory change tracking is not available' },
          activeInventory: 8,
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
        lastUpdated: '2026-07-08T08:00:00.000Z',
        datasetVersion: 'canonical-2024.05',
        scrapeRunId: 1007
      },
      generatedAt: '2026-07-05T12:30:00.000Z'
    });
  });

  it('produces an empty/unsupported snapshot when the fixture has no listings', () => {
    const prices = derivePrices([]);
    const freshness = deriveFreshness([]);
    const filters = toAppliedMarketFilters({}, 7);

    const { metrics, supportStatuses } = aggregator.aggregate({
      activeListingsCount: 0,
      prices,
      scopeLabel: 'Overall UAE Used Cars',
      periodDays: 7
    });

    const response = mapper.toResponse({
      scope: { level: 'overall', label: 'Overall UAE Used Cars', canonical: {} },
      filters,
      metrics,
      supportStatuses,
      period: { days: 7, label: 'Last 7 days' },
      freshness,
      generatedAt: '2026-07-05T12:30:00.000Z'
    });

    expect((response.metrics[0] as ActiveListingsMetric).count).toBe(0);
    expect((response.metrics[1] as MedianPriceMetric).amount).toBeNull();
    expect((response.metrics[1] as MedianPriceMetric).sampleSize).toBe(0);
    expect(response.supportStatuses.medianPrice.status).toBe('unavailable');
    expect(response.supportStatuses.typicalPriceRange.status).toBe('unavailable');
    // Freshness block is always present, all null — never appears real-time.
    expect(response.freshness).toEqual({ lastUpdated: null, datasetVersion: null, scrapeRunId: null });
  });
});
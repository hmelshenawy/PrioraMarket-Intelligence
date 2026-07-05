import { Injectable } from '@nestjs/common';
import {
  ActiveListingsMetric,
  InventoryChangeMetric,
  MarketMetric,
  MarketMetricType,
  MedianPriceMetric,
  PriceDropsMetric,
  TypicalPriceRangeMetric
} from '../domain/market-metric.domain';
import {
  MetricSupportStatus,
  SUPPORTED,
  partial,
  unavailable,
  unsupported
} from '../domain/metric-support-status.domain';

export interface AggregationInputs {
  activeListingsCount: number;
  /** Usable prices (Decimal-safe numbers) for the selected scope. */
  prices: number[];
  scopeLabel: string;
  periodDays: number;
}

export interface AggregationResult {
  metrics: MarketMetric[];
  supportStatuses: Record<MarketMetricType, MetricSupportStatus>;
}

export const CURRENCY = 'AED';

/** Minimum priced-listing sample to expose a P25/P75 typical range; below this, min/max is used. */
export const TYPICAL_RANGE_MIN_SAMPLE = 8;

/**
 * SnapshotAggregationService — pure metric computation, no DB access and no formatting.
 * Receives raw scoped data from the repository and produces the ordered metric list
 * plus per-metric support statuses. History-dependent metrics (new/removed/net/priceDrops)
 * default to unsupported in US1; period tracking is implemented in US3.
 */
@Injectable()
export class SnapshotAggregationService {
  aggregate(inputs: AggregationInputs): AggregationResult {
    const { activeListingsCount, prices, scopeLabel, periodDays } = inputs;
    const sorted = [...prices].sort((a, b) => a - b);
    const sampleSize = sorted.length;
    const priceAvailable = sampleSize > 0;

    const activeListings: ActiveListingsMetric = {
      type: 'activeListings',
      title: 'Active Listings',
      status: SUPPORTED,
      count: activeListingsCount,
      scopeLabel
    };

    const medianPrice: MedianPriceMetric = {
      type: 'medianPrice',
      title: 'Median Price',
      status: priceAvailable ? SUPPORTED : unavailable('No usable prices for the selected scope'),
      amount: priceAvailable ? this.percentile(sorted, 0.5) : null,
      currency: CURRENCY,
      sampleSize
    };

    const typicalPriceRange: TypicalPriceRangeMetric = priceAvailable
      ? this.buildTypicalPriceRange(sorted, sampleSize)
      : {
          type: 'typicalPriceRange',
          title: 'Typical Price Range',
          status: unavailable('No usable prices for the selected scope'),
          method: 'typical-range',
          currency: CURRENCY,
          medianAmount: null,
          lowerAmount: null,
          upperAmount: null,
          minAmount: null,
          maxAmount: null,
          sampleSize
        };

    const inventoryChange: InventoryChangeMetric = {
      type: 'inventoryChange',
      title: 'Inventory Change',
      status: partial('Period inventory change tracking is not available'),
      activeInventory: activeListingsCount,
      newListings: null,
      removedListings: null,
      netChange: null,
      periodDays
    };

    const priceDrops: PriceDropsMetric = {
      type: 'priceDrops',
      title: 'Price Drops',
      status: unsupported('Price history is not available'),
      count: null,
      averageDropPercentage: null,
      sampleSize: null,
      periodDays
    };

    const metrics: MarketMetric[] = [
      activeListings,
      medianPrice,
      typicalPriceRange,
      inventoryChange,
      priceDrops
    ];

    const supportStatuses: Record<MarketMetricType, MetricSupportStatus> = {
      activeListings: activeListings.status,
      medianPrice: medianPrice.status,
      typicalPriceRange: typicalPriceRange.status,
      inventoryChange: inventoryChange.status,
      priceDrops: priceDrops.status
    };

    return { metrics, supportStatuses };
  }

  private buildTypicalPriceRange(sorted: number[], sampleSize: number): TypicalPriceRangeMetric {
    const median = this.percentile(sorted, 0.5);
    const base = {
      type: 'typicalPriceRange' as const,
      title: 'Typical Price Range',
      status: SUPPORTED,
      method: 'typical-range',
      currency: CURRENCY,
      medianAmount: median,
      sampleSize
    };

    if (sampleSize >= TYPICAL_RANGE_MIN_SAMPLE) {
      return {
        ...base,
        lowerAmount: this.percentile(sorted, 0.25),
        upperAmount: this.percentile(sorted, 0.75),
        minAmount: null,
        maxAmount: null
      };
    }

    // Insufficient sample for a stable typical range — fall back to observed min/max.
    return {
      ...base,
      lowerAmount: null,
      upperAmount: null,
      minAmount: sorted[0],
      maxAmount: sorted[sorted.length - 1]
    };
  }

  /** Linear-interpolation percentile on a sorted ascending array, rounded to whole AED. */
  private percentile(sorted: number[], p: number): number {
    if (sorted.length === 0) return 0;
    if (sorted.length === 1) return Math.round(sorted[0]);
    const rank = p * (sorted.length - 1);
    const lower = Math.floor(rank);
    const upper = Math.ceil(rank);
    if (lower === upper) return Math.round(sorted[lower]);
    const frac = rank - lower;
    return Math.round(sorted[lower] + frac * (sorted[upper] - sorted[lower]));
  }
}
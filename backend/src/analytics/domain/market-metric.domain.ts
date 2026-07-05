import { MetricSupportStatus } from './metric-support-status.domain';

export type MarketMetricType =
  | 'activeListings'
  | 'medianPrice'
  | 'typicalPriceRange'
  | 'inventoryChange'
  | 'priceDrops';

export const MARKET_METRIC_TYPES: readonly MarketMetricType[] = [
  'activeListings',
  'medianPrice',
  'typicalPriceRange',
  'inventoryChange',
  'priceDrops'
];

export interface MarketMetricBase {
  type: MarketMetricType;
  title: string;
  status: MetricSupportStatus;
}

export interface ActiveListingsMetric extends MarketMetricBase {
  type: 'activeListings';
  count: number;
  scopeLabel: string;
}

export interface MedianPriceMetric extends MarketMetricBase {
  type: 'medianPrice';
  amount: number | null;
  currency: string;
  sampleSize: number;
}

export interface TypicalPriceRangeMetric extends MarketMetricBase {
  type: 'typicalPriceRange';
  method: string;
  currency: string;
  medianAmount: number | null;
  lowerAmount: number | null;
  upperAmount: number | null;
  minAmount: number | null;
  maxAmount: number | null;
  sampleSize: number;
}

export interface InventoryChangeMetric extends MarketMetricBase {
  type: 'inventoryChange';
  activeInventory: number;
  newListings: number | null;
  removedListings: number | null;
  netChange: number | null;
  periodDays: number;
}

export interface PriceDropsMetric extends MarketMetricBase {
  type: 'priceDrops';
  count: number | null;
  averageDropPercentage: number | null;
  sampleSize: number | null;
  periodDays: number;
}

export type MarketMetric =
  | ActiveListingsMetric
  | MedianPriceMetric
  | TypicalPriceRangeMetric
  | InventoryChangeMetric
  | PriceDropsMetric;
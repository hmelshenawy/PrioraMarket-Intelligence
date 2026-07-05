import { AppliedMarketFilters } from './domain/applied-market-filters.domain';
import { Freshness } from './domain/freshness.domain';

/** Raw usable prices (Decimal-safe numbers) and the count usable for stats. */
export interface PriceStatsData {
  prices: number[];
  usableCount: number;
}

/** Result of a period-bounded change count (new listings, removed listings). */
export interface PeriodChangeData {
  count: number | null;
  /** false when the underlying signal cannot be derived from available data. */
  supported: boolean;
}

/** Result of a price-drop query over the period. */
export interface PriceDropsData {
  count: number | null;
  averageDropPercentage: number | null;
  sampleSize: number | null;
  supported: boolean;
}

/**
 * Read-only data access for the Market Snapshot aggregate. Implementations MUST
 * perform data access only — no metric aggregation, no formatting, no normalization
 * of filter values. All calculations are owned by the aggregation service.
 *
 * Scoped by AppliedMarketFilters; the repository treats filter values as canonical
 * and never mutates them.
 */
export interface SnapshotReadRepositoryInterface {
  countActiveListings(filters: AppliedMarketFilters): Promise<number>;
  fetchPricesForStats(filters: AppliedMarketFilters): Promise<PriceStatsData>;
  fetchFirstSeenInPeriod(filters: AppliedMarketFilters, periodDays: number): Promise<PeriodChangeData>;
  fetchRemovedInPeriod(filters: AppliedMarketFilters, periodDays: number): Promise<PeriodChangeData>;
  fetchPriceDrops(filters: AppliedMarketFilters, periodDays: number): Promise<PriceDropsData>;
  getFreshness(filters: AppliedMarketFilters): Promise<Freshness>;
}
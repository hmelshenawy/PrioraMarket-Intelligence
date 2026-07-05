import { AppliedMarketFilters } from '../domain/applied-market-filters.domain';
import { Freshness } from '../domain/freshness.domain';
import { MarketMetric, MarketMetricType } from '../domain/market-metric.domain';
import { MetricSupportStatus } from '../domain/metric-support-status.domain';
import { MarketScope } from '../domain/market-scope.domain';
import { SnapshotPeriod } from '../domain/snapshot-period.domain';

/**
 * Response payload for GET /market/snapshot. Raw values only — the frontend owns
 * all formatting (currency, dates, percentages, labels).
 */
export class MarketSnapshotResponseDto {
  scope!: MarketScope;
  filters!: AppliedMarketFilters;
  period!: SnapshotPeriod;
  metrics!: MarketMetric[];
  supportStatuses!: Record<MarketMetricType, MetricSupportStatus>;
  freshness!: Freshness;
  generatedAt!: string;
}
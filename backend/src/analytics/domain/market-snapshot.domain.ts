import { AppliedMarketFilters } from './applied-market-filters.domain';
import { Freshness } from './freshness.domain';
import { MarketMetric, MarketMetricType } from './market-metric.domain';
import { MetricSupportStatus } from './metric-support-status.domain';
import { MarketScope } from './market-scope.domain';
import { SnapshotPeriod } from './snapshot-period.domain';

export interface MarketSnapshot {
  scope: MarketScope;
  filters: AppliedMarketFilters;
  metrics: MarketMetric[];
  supportStatuses: Record<MarketMetricType, MetricSupportStatus>;
  period: SnapshotPeriod;
  freshness: Freshness;
  generatedAt: string;
}
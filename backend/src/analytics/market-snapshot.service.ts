import { Inject, Injectable } from '@nestjs/common';
import {
  MarketFilterSelection,
  toAppliedMarketFilters
} from './domain/applied-market-filters.domain';
import { MarketSnapshot } from './domain/market-snapshot.domain';
import { buildMarketScope } from './domain/market-scope.domain';
import { buildScopeDisplayLabel, ScopeDisplayNames, displayOrCanonical } from './domain/display-name.domain';
import { buildSnapshotPeriod } from './domain/snapshot-period.domain';
import { MarketSnapshotResponseMapper } from './mappers/market-snapshot-response.mapper';
import { SnapshotAggregationService } from './aggregation/market-snapshot.aggregator';
import { SnapshotReadRepositoryInterface } from './snapshot-read.repository.interface';
import { CatalogReadRepositoryInterface } from './catalog-read.repository.interface';
import { SNAPSHOT_READ_REPOSITORY, CATALOG_READ_REPOSITORY } from './analytics.tokens';
import { MarketSnapshotQueryDto } from './dto/market-snapshot-query.dto';

/**
 * MarketSnapshotService — application orchestration. Builds canonical filters and
 * scope, fans out read-only repository calls (metrics + freshness + catalog
 * display-name lookup), delegates metric computation to the aggregation service,
 * resolves the catalog-backed scope label, assembles the domain snapshot, and
 * maps it to the response DTO. No business calculations live here; no DB access;
 * no formatting.
 *
 * US3 (T065): the scope label is rebuilt from catalog display names when
 * available (make, model) with canonical fallback for trim and year (the catalog
 * exposes no trim/year display column). The canonical filters echoed in the
 * response remain the raw canonical values — only the label is display-enhanced.
 */
@Injectable()
export class MarketSnapshotService {
  constructor(
    @Inject(SNAPSHOT_READ_REPOSITORY) private readonly repository: SnapshotReadRepositoryInterface,
    private readonly aggregator: SnapshotAggregationService,
    private readonly mapper: MarketSnapshotResponseMapper,
    @Inject(CATALOG_READ_REPOSITORY) private readonly catalog: CatalogReadRepositoryInterface
  ) {}

  async getSnapshot(query: MarketSnapshotQueryDto) {
    const selection: MarketFilterSelection = {
      make: query.make,
      model: query.model,
      trim: query.trim,
      year: query.year
    };
    const filters = toAppliedMarketFilters(selection, query.periodDays);
    const scope = buildMarketScope(selection);

    const [activeListingsCount, priceStats, freshness, displayNames] = await Promise.all([
      this.repository.countActiveListings(filters),
      this.repository.fetchPricesForStats(filters),
      this.repository.getFreshness(filters),
      this.resolveScopeDisplayNames(selection)
    ]);

    // Replace the canonical-fallback label with the catalog-backed display label.
    scope.label = buildScopeDisplayLabel(scope.level, displayNames);

    const { metrics, supportStatuses } = this.aggregator.aggregate({
      activeListingsCount,
      prices: priceStats.prices,
      scopeLabel: scope.label,
      periodDays: filters.periodDays
    });

    const snapshot: MarketSnapshot = {
      scope,
      filters,
      metrics,
      supportStatuses,
      period: buildSnapshotPeriod(filters.periodDays),
      freshness,
      generatedAt: new Date().toISOString()
    };

    return this.mapper.toResponse(snapshot);
  }

  /**
   * Resolve display names for the selected scope. Make/model come from the
   * catalog when a row exists, with canonical fallback otherwise. Trim and year
   * always use canonical fallback (no catalog display column). Gated by the
   * filter hierarchy (model requires make; trim requires make+model; year
   * requires make+model+trim) to mirror buildMarketScope.
   */
  private async resolveScopeDisplayNames(selection: MarketFilterSelection): Promise<ScopeDisplayNames> {
    const names: ScopeDisplayNames = {};
    const { make, model, trim, year } = selection;
    if (make) {
      const makeDisplay = await this.catalog.findMakeDisplay(make);
      names.make = displayOrCanonical(makeDisplay, make);
    }
    if (make && model) {
      const modelDisplay = await this.catalog.findModelDisplay(make, model);
      names.model = displayOrCanonical(modelDisplay, model);
    }
    if (make && model && trim) {
      // No catalog trim display — canonical fallback, unchanged.
      names.trim = displayOrCanonical(null, trim);
    }
    if (make && model && trim && year !== undefined) {
      // No catalog year display — canonical fallback (stringified integer).
      names.year = displayOrCanonical(null, year);
    }
    return names;
  }
}
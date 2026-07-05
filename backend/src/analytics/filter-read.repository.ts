import { Inject, Injectable } from '@nestjs/common';
import { PrismaService } from '../db/prisma.service';
import { MarketFilterSelection } from './domain/applied-market-filters.domain';
import { FilterOption } from './domain/filter-option.domain';
import { displayOrCanonical } from './domain/display-name.domain';
import { Freshness, UNKNOWN_FRESHNESS } from './domain/freshness.domain';
import { FilterReadRepositoryInterface } from './filter-read.repository.interface';
import { CatalogReadRepositoryInterface } from './catalog-read.repository.interface';
import { CATALOG_READ_REPOSITORY } from './analytics.tokens';

/**
 * PrismaFilterReadRepository — read-only data access for the filter-options
 * endpoint. Returns canonical option values with active-listing counts and
 * catalog-backed display names. Data access only — no hierarchy resolution,
 * no formatting, no value normalization. `mode: 'insensitive'` is a query-time
 * comparison only and does not mutate the supplied canonical values.
 *
 * US3 (T064): make/model display names are resolved from
 * `vehicle_reference_catalog` via CatalogReadRepository (one batched lookup per
 * level) with canonical fallback when no catalog row exists. Trim and year use
 * canonical fallback — the catalog exposes no trim/year display column.
 */
@Injectable()
export class PrismaFilterReadRepository implements FilterReadRepositoryInterface {
  constructor(
    private readonly prisma: PrismaService,
    @Inject(CATALOG_READ_REPOSITORY) private readonly catalog: CatalogReadRepositoryInterface
  ) {}

  async listMakes(): Promise<FilterOption[]> {
    const groups = await this.prisma.listing.groupBy({
      by: ['make'],
      where: { status: 'ACTIVE', make: { not: null } },
      _count: { _all: true },
      orderBy: { make: 'asc' }
    });
    if (groups.length === 0) return [];
    const canonicalMakes = groups.map((g) => g.make as string);
    const displayMap = await this.catalog.findMakeDisplays(canonicalMakes);
    return groups.map((g) => {
      const canonical = g.make as string;
      const catalogDisplay = displayMap.get(canonical.toLowerCase()) ?? null;
      return this.toOption(canonical, g._count._all, catalogDisplay);
    });
  }

  async listModels(make: string): Promise<FilterOption[]> {
    const groups = await this.prisma.listing.groupBy({
      by: ['model'],
      where: { status: 'ACTIVE', make: { equals: make, mode: 'insensitive' }, model: { not: null } },
      _count: { _all: true },
      orderBy: { model: 'asc' }
    });
    if (groups.length === 0) return [];
    const canonicalModels = groups.map((g) => g.model as string);
    const displayMap = await this.catalog.findModelDisplays(make, canonicalModels);
    return groups.map((g) => {
      const canonical = g.model as string;
      const catalogDisplay = displayMap.get(canonical.toLowerCase()) ?? null;
      return this.toOption(canonical, g._count._all, catalogDisplay);
    });
  }

  async listTrims(make: string, model: string): Promise<FilterOption[]> {
    const groups = await this.prisma.listing.groupBy({
      by: ['trim'],
      where: {
        status: 'ACTIVE',
        make: { equals: make, mode: 'insensitive' },
        model: { equals: model, mode: 'insensitive' },
        trim: { not: null }
      },
      _count: { _all: true },
      orderBy: { trim: 'asc' }
    });
    // Trim display = canonical fallback (catalog has no trim display column).
    return groups.map((g) => this.toOption(g.trim as string, g._count._all, null));
  }

  async listYears(make: string, model: string, trim: string): Promise<FilterOption[]> {
    const groups = await this.prisma.listing.groupBy({
      by: ['year'],
      where: {
        status: 'ACTIVE',
        make: { equals: make, mode: 'insensitive' },
        model: { equals: model, mode: 'insensitive' },
        trim: { equals: trim, mode: 'insensitive' },
        year: { not: null }
      },
      _count: { _all: true },
      orderBy: { year: 'desc' }
    });
    // Year display = canonical fallback (the integer stringified).
    return groups.map((g) => this.toOption(g.year as number, g._count._all, null));
  }

  async getFreshness(filters: MarketFilterSelection): Promise<Freshness> {
    const row = await this.prisma.listing.findFirst({
      where: this.buildWhere(filters),
      select: { lastSeenAt: true, lastSeenRunId: true, normalizationVersion: true },
      orderBy: { lastSeenAt: 'desc' }
    });
    if (!row) return { ...UNKNOWN_FRESHNESS };
    return {
      lastUpdated: this.toIso(row.lastSeenAt),
      datasetVersion: row.normalizationVersion ?? null,
      scrapeRunId: this.toNumber(row.lastSeenRunId)
    };
  }

  /**
   * Builds a FilterOption. `catalogDisplay` is the raw catalog display name or
   * null; the displayOrCanonical policy applies the canonical fallback without
   * transforming or normalizing the canonical value.
   */
  private toOption(value: string | number, count: number, catalogDisplay: string | null): FilterOption {
    return { value, displayName: displayOrCanonical(catalogDisplay, value), activeListingCount: count };
  }

  private buildWhere(filters: MarketFilterSelection): Record<string, unknown> {
    const where: Record<string, unknown> = { status: 'ACTIVE' };
    if (filters.make) where.make = { equals: filters.make, mode: 'insensitive' };
    if (filters.model) where.model = { equals: filters.model, mode: 'insensitive' };
    if (filters.trim) where.trim = { equals: filters.trim, mode: 'insensitive' };
    if (filters.year !== undefined) where.year = filters.year;
    return where;
  }

  private toNumber(value: unknown): number | null {
    if (value === null || value === undefined) return null;
    const n = Number(value);
    return Number.isFinite(n) ? n : null;
  }

  private toIso(value: unknown): string | null {
    if (!value) return null;
    const d = value instanceof Date ? value : new Date(String(value));
    return Number.isFinite(d.getTime()) ? d.toISOString() : null;
  }
}
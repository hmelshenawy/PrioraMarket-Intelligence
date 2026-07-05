import { Injectable } from '@nestjs/common';
import { PrismaService } from '../db/prisma.service';
import { AppliedMarketFilters } from './domain/applied-market-filters.domain';
import { Freshness, UNKNOWN_FRESHNESS } from './domain/freshness.domain';
import {
  PeriodChangeData,
  PriceDropsData,
  PriceStatsData,
  SnapshotReadRepositoryInterface
} from './snapshot-read.repository.interface';

/**
 * PrismaSnapshotReadRepository — read-only data access for the Market Snapshot.
 * Data access only: no metric calculations, no formatting, no value normalization.
 * Filter values are treated as canonical; `mode: 'insensitive'` is a query-time
 * comparison only and does not mutate the supplied canonical values.
 */
@Injectable()
export class PrismaSnapshotReadRepository implements SnapshotReadRepositoryInterface {
  constructor(private readonly prisma: PrismaService) {}

  async countActiveListings(filters: AppliedMarketFilters): Promise<number> {
    return this.prisma.listing.count({ where: this.buildWhere(filters) });
  }

  async fetchPricesForStats(filters: AppliedMarketFilters): Promise<PriceStatsData> {
    const rows = await this.prisma.listing.findMany({
      where: this.buildWhere(filters),
      select: { price: true }
    });
    const prices = rows
      .map((row: { price: unknown }) => this.toNumber(row.price))
      .filter((price): price is number => price !== null && Number.isFinite(price));
    return { prices, usableCount: prices.length };
  }

  async fetchFirstSeenInPeriod(_filters: AppliedMarketFilters, _periodDays: number): Promise<PeriodChangeData> {
    // US1: period inventory change is not exposed. US3 implements first-seen-in-period counting.
    return { count: null, supported: false };
  }

  async fetchRemovedInPeriod(_filters: AppliedMarketFilters, _periodDays: number): Promise<PeriodChangeData> {
    // Removed-listing tracking is not available in scope (no lifecycle/removal table).
    return { count: null, supported: false };
  }

  async fetchPriceDrops(_filters: AppliedMarketFilters, _periodDays: number): Promise<PriceDropsData> {
    // Price history is not available in scope.
    return { count: null, averageDropPercentage: null, sampleSize: null, supported: false };
  }

  async getFreshness(filters: AppliedMarketFilters): Promise<Freshness> {
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

  private buildWhere(filters: AppliedMarketFilters): Record<string, unknown> {
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
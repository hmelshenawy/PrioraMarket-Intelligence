import { Injectable } from '@nestjs/common';
import { PrismaService } from '../db/prisma.service';
import { FilterMetadataDomain } from './domain/listing-filters.domain';
import { InventoryStatsDomain } from './domain/listing-stats.domain';
import { ListingDetailDomain, SearchListingsResultDomain } from './domain/listing.domain';
import {
  BuiltFilterMetadataQuery,
  BuiltInventoryStatsQuery,
  BuiltListingDetailQuery,
  BuiltListingSearchQuery
} from './domain/search-query.domain';
import { ListingReadRepositoryInterface } from './listing-read.repository.interface';

@Injectable()
export class PrismaListingReadRepository implements ListingReadRepositoryInterface {
  constructor(private readonly prisma: PrismaService) {}

  async search(query: BuiltListingSearchQuery): Promise<SearchListingsResultDomain> {
    const [rows, total] = await Promise.all([
      this.prisma.listing.findMany({
        where: query.where,
        orderBy: query.orderBy,
        skip: query.skip,
        take: query.take,
        select: query.select
      }),
      this.prisma.listing.count({ where: query.where })
    ]);
    const listingRows = rows as ListingRow[];

    return {
      rows: listingRows.map((row: ListingRow) => this.toListingDomain(row)),
      total
    };
  }

  async findDetail(_query: BuiltListingDetailQuery): Promise<ListingDetailDomain | null> {
    const listing = (await this.prisma.listing.findFirst({
      where: _query.where,
      select: _query.select
    })) as ListingDetailRow | null;

    if (!listing) {
      return null;
    }

    const [marketplace, latestSnapshot] = await Promise.all([
      this.prisma.marketplaceSource.findUnique({ where: { id: listing.marketplaceSourceId } }),
      this.prisma.listingSnapshot.findFirst({
        where: { listingId: this.toBigIntId(listing.id) },
        orderBy: { capturedAt: 'desc' },
        select: { canonicalPayload: true }
      })
    ]);

    return this.toListingDetailDomain(listing, marketplace as MarketplaceSourceRow | null, latestSnapshot as ListingSnapshotRow | null);
  }

  async getFilterMetadata(query: BuiltFilterMetadataQuery): Promise<FilterMetadataDomain> {
    const rows = (await this.prisma.listing.findMany({
      where: query.where,
      select: query.select
    })) as FilterMetadataRow[];

    const makes = this.sortedUnique(rows.map((row) => row.make));
    const models = rows.reduce<Record<string, string[]>>((acc, row) => {
      if (!row.make || !row.model) {
        return acc;
      }
      acc[row.make] = acc[row.make] ?? [];
      if (!acc[row.make].includes(row.model)) {
        acc[row.make].push(row.model);
      }
      return acc;
    }, {});

    for (const make of Object.keys(models)) {
      models[make].sort();
    }

    return {
      makes,
      models,
      price: this.range(rows.map((row) => this.toNumber(row.price))),
      year: this.range(rows.map((row) => row.year ?? null)),
      km: this.range(rows.map((row) => row.mileage ?? null)),
      conditions: this.sortedUnique(rows.map((row) => row.condition)),
      sellerTypes: this.sortedUnique(rows.map((row) => row.sellerType))
    };
  }

  async getInventoryStats(query: BuiltInventoryStatsQuery): Promise<InventoryStatsDomain> {
    const rows = (await this.prisma.listing.findMany({
      where: query.where,
      select: query.select
    })) as InventoryStatsRow[];
    const prices = rows.map((row) => this.toNumber(row.price)).filter((price): price is number => price !== null);
    const lastUpdatedAt = rows
      .map((row) => row.lastSeenAt)
      .filter((value): value is Date | string => value !== null && value !== undefined)
      .map((value) => (value instanceof Date ? value : new Date(value)))
      .filter((value) => Number.isFinite(value.getTime()))
      .sort((a, b) => b.getTime() - a.getTime())[0];

    return {
      totalListings: rows.length,
      usedListings: rows.filter((row) => row.condition === 'used').length,
      newListings: rows.filter((row) => row.condition === 'new').length,
      totalMakes: this.sortedUnique(rows.map((row) => row.make)).length,
      totalModels: this.sortedUnique(rows.map((row) => row.model)).length,
      averagePriceAed: prices.length === 0 ? null : Math.round(prices.reduce((sum, price) => sum + price, 0) / prices.length),
      minPriceAed: prices.length === 0 ? null : Math.min(...prices),
      maxPriceAed: prices.length === 0 ? null : Math.max(...prices),
      lastUpdatedAt: lastUpdatedAt ? lastUpdatedAt.toISOString() : null
    };
  }

  private toListingDomain(row: ListingRow) {
    return {
      id: String(row.id),
      externalId: row.uuid ?? null,
      title: row.title ?? null,
      make: row.make ?? null,
      model: row.model ?? null,
      trim: row.trim ?? null,
      year: row.year ?? null,
      priceAed: row.price === null || row.price === undefined ? null : Number(row.price),
      km: row.mileage ?? null,
      condition: row.condition ?? null,
      location: row.location ?? null,
      sellerType: row.sellerType ?? null,
      url: row.url ?? null,
      photosCount: null,
      firstSeenAt: row.firstSeenAt instanceof Date ? row.firstSeenAt.toISOString() : (row.firstSeenAt ?? null),
      lastSeenAt: row.lastSeenAt instanceof Date ? row.lastSeenAt.toISOString() : (row.lastSeenAt ?? null)
    };
  }

  private toListingDetailDomain(row: ListingDetailRow, marketplace: MarketplaceSourceRow | null, snapshot: ListingSnapshotRow | null): ListingDetailDomain {
    const canonical = this.canonicalPayload(snapshot);
    return {
      ...this.toListingDomain(row),
      marketplace: marketplace?.name ?? row.source ?? null,
      bodyType: this.stringValue(canonical.bodyType),
      fuel: this.stringValue(canonical.fuel),
      transmission: this.stringValue(canonical.transmission),
      color: this.stringValue(canonical.color),
      specs: this.objectValue(canonical.specs),
      seller: this.stringValue(canonical.seller),
      isVerified: this.booleanValue(canonical.isVerified),
      isAgent: this.booleanValue(canonical.isAgent),
      neighbourhood: this.stringValue(canonical.neighbourhood),
      photosCount: this.numberValue(canonical.photosCount),
      firstSeenRunId: row.firstSeenRunId === undefined || row.firstSeenRunId === null ? null : String(row.firstSeenRunId),
      lastSeenRunId: row.lastSeenRunId === undefined || row.lastSeenRunId === null ? null : String(row.lastSeenRunId),
      canonicalHash: row.canonicalHash ?? null
    };
  }

  private canonicalPayload(snapshot: ListingSnapshotRow | null): Record<string, unknown> {
    return this.objectValue(snapshot?.canonicalPayload) ?? {};
  }

  private sortedUnique(values: Array<string | null | undefined>): string[] {
    return [...new Set(values.filter((value): value is string => Boolean(value)))].sort();
  }

  private range(values: Array<number | null>): { min: number | null; max: number | null } {
    const numeric = values.filter((value): value is number => value !== null && Number.isFinite(value));
    return numeric.length === 0 ? { min: null, max: null } : { min: Math.min(...numeric), max: Math.max(...numeric) };
  }

  private toNumber(value: unknown): number | null {
    if (value === null || value === undefined) {
      return null;
    }
    const parsed = Number(value);
    return Number.isFinite(parsed) ? parsed : null;
  }

  private toBigIntId(value: bigint | number | string): bigint {
    return typeof value === 'bigint' ? value : BigInt(value);
  }

  private stringValue(value: unknown): string | null {
    return typeof value === 'string' && value.length > 0 ? value : null;
  }

  private numberValue(value: unknown): number | null {
    return typeof value === 'number' && Number.isFinite(value) ? value : null;
  }

  private booleanValue(value: unknown): boolean | null {
    return typeof value === 'boolean' ? value : null;
  }

  private objectValue(value: unknown): Record<string, unknown> | null {
    return value !== null && typeof value === 'object' && !Array.isArray(value) ? (value as Record<string, unknown>) : null;
  }
}

interface ListingRow {
  id: bigint | number | string;
  uuid?: string | null;
  title?: string | null;
  make?: string | null;
  model?: string | null;
  trim?: string | null;
  year?: number | null;
  price?: unknown | null;
  mileage?: number | null;
  condition?: string | null;
  location?: string | null;
  sellerType?: string | null;
  url?: string | null;
  firstSeenAt?: Date | string | null;
  lastSeenAt?: Date | string | null;
}

interface ListingDetailRow extends ListingRow {
  marketplaceSourceId: bigint | number;
  source?: string | null;
  firstSeenRunId?: bigint | number | string | null;
  lastSeenRunId?: bigint | number | string | null;
  canonicalHash?: string | null;
}

interface MarketplaceSourceRow {
  name?: string | null;
}

interface ListingSnapshotRow {
  canonicalPayload?: unknown;
}

interface FilterMetadataRow {
  make?: string | null;
  model?: string | null;
  price?: unknown | null;
  year?: number | null;
  mileage?: number | null;
  condition?: string | null;
  sellerType?: string | null;
}

interface InventoryStatsRow {
  condition?: string | null;
  make?: string | null;
  model?: string | null;
  price?: unknown | null;
  lastSeenAt?: Date | string | null;
}

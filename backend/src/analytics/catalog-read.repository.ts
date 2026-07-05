import { Injectable } from '@nestjs/common';
import { PrismaService } from '../db/prisma.service';
import { CatalogReadRepositoryInterface } from './catalog-read.repository.interface';

/**
 * PrismaCatalogReadRepository — read-only access to `vehicle_reference_catalog`.
 * Resolves catalog display names (make_display, model_display) for canonical
 * make/model keys. Data access only: no fallback policy, no formatting, no
 * normalization. Returns the raw catalog display string or `null` when no row
 * matches; the caller applies the canonical-fallback rule.
 *
 * `mode: 'insensitive'` is a query-time comparison only and does not mutate the
 * supplied canonical values. Map keys are lowercased for case-insensitive lookup
 * — this is internal bookkeeping, not normalization of the displayed value.
 */
@Injectable()
export class PrismaCatalogReadRepository implements CatalogReadRepositoryInterface {
  constructor(private readonly prisma: PrismaService) {}

  async findMakeDisplay(make: string): Promise<string | null> {
    const row = await this.prisma.vehicleReferenceCatalog.findFirst({
      where: { makeKey: { equals: make, mode: 'insensitive' } },
      select: { makeDisplay: true }
    });
    return row?.makeDisplay ?? null;
  }

  async findModelDisplay(make: string, model: string): Promise<string | null> {
    const row = await this.prisma.vehicleReferenceCatalog.findFirst({
      where: {
        makeKey: { equals: make, mode: 'insensitive' },
        modelKey: { equals: model, mode: 'insensitive' }
      },
      select: { modelDisplay: true }
    });
    return row?.modelDisplay ?? null;
  }

  async findMakeDisplays(makes: string[]): Promise<Map<string, string | null>> {
    const map = new Map<string, string | null>();
    if (makes.length === 0) return map;
    const rows = await this.prisma.vehicleReferenceCatalog.findMany({
      where: { makeKey: { in: makes, mode: 'insensitive' } },
      select: { makeKey: true, makeDisplay: true }
    });
    for (const row of rows) {
      const key = row.makeKey.toLowerCase();
      if (!map.has(key)) map.set(key, row.makeDisplay);
    }
    return map;
  }

  async findModelDisplays(make: string, models: string[]): Promise<Map<string, string | null>> {
    const map = new Map<string, string | null>();
    if (models.length === 0) return map;
    const rows = await this.prisma.vehicleReferenceCatalog.findMany({
      where: {
        makeKey: { equals: make, mode: 'insensitive' },
        modelKey: { in: models, mode: 'insensitive' }
      },
      select: { modelKey: true, modelDisplay: true }
    });
    for (const row of rows) {
      const key = row.modelKey.toLowerCase();
      if (!map.has(key)) map.set(key, row.modelDisplay);
    }
    return map;
  }
}
import { z } from "zod"

// Trust boundary: validate the Market Snapshot payload from the backend before it
// enters feature code. Mirrors contracts/market-snapshot-api.md exactly (raw values).

const nullableString = z.string().nullable()
const nullableNumber = z.number().nullable()

export const metricSupportStatusSchema = z.object({
  status: z.enum(["supported", "unsupported", "unavailable", "partial"]),
  dataAvailable: z.boolean(),
  reason: z.string().optional(),
})

export const marketScopeSchema = z.object({
  level: z.enum(["overall", "make", "model", "trim", "year"]),
  label: z.string(),
  canonical: z.object({
    make: z.string().optional(),
    model: z.string().optional(),
    trim: z.string().optional(),
    year: z.number().nullable().optional(),
  }),
})

// Selection-only filters (filter-options response): make/model/trim/year, no period.
export const marketFilterSelectionSchema = z.object({
  make: z.string().optional(),
  model: z.string().optional(),
  trim: z.string().optional(),
  year: z.number().optional(),
})

// Applied filters (snapshot response): selection + periodDays.
export const appliedMarketFiltersSchema = marketFilterSelectionSchema.extend({
  periodDays: z.number(),
})

export const snapshotPeriodSchema = z.object({
  days: z.number(),
  label: z.string(),
})

export const freshnessSchema = z.object({
  lastUpdated: nullableString,
  datasetVersion: nullableString,
  scrapeRunId: nullableNumber,
})

const activeListingsMetricSchema = z.object({
  type: z.literal("activeListings"),
  title: z.string(),
  status: metricSupportStatusSchema,
  count: z.number(),
  scopeLabel: z.string(),
})

const medianPriceMetricSchema = z.object({
  type: z.literal("medianPrice"),
  title: z.string(),
  status: metricSupportStatusSchema,
  amount: nullableNumber,
  currency: z.string(),
  sampleSize: z.number(),
})

const typicalPriceRangeMetricSchema = z.object({
  type: z.literal("typicalPriceRange"),
  title: z.string(),
  status: metricSupportStatusSchema,
  method: z.string(),
  currency: z.string(),
  medianAmount: nullableNumber,
  lowerAmount: nullableNumber,
  upperAmount: nullableNumber,
  minAmount: nullableNumber,
  maxAmount: nullableNumber,
  sampleSize: z.number(),
})

const inventoryChangeMetricSchema = z.object({
  type: z.literal("inventoryChange"),
  title: z.string(),
  status: metricSupportStatusSchema,
  activeInventory: z.number(),
  newListings: nullableNumber,
  removedListings: nullableNumber,
  netChange: nullableNumber,
  periodDays: z.number(),
})

const priceDropsMetricSchema = z.object({
  type: z.literal("priceDrops"),
  title: z.string(),
  status: metricSupportStatusSchema,
  count: nullableNumber,
  averageDropPercentage: nullableNumber,
  sampleSize: nullableNumber,
  periodDays: z.number(),
})

export const marketMetricSchema = z.discriminatedUnion("type", [
  activeListingsMetricSchema,
  medianPriceMetricSchema,
  typicalPriceRangeMetricSchema,
  inventoryChangeMetricSchema,
  priceDropsMetricSchema,
])

export const supportStatusesSchema = z.object({
  activeListings: metricSupportStatusSchema,
  medianPrice: metricSupportStatusSchema,
  typicalPriceRange: metricSupportStatusSchema,
  inventoryChange: metricSupportStatusSchema,
  priceDrops: metricSupportStatusSchema,
})

export const marketSnapshotSchema = z.object({
  scope: marketScopeSchema,
  filters: appliedMarketFiltersSchema,
  period: snapshotPeriodSchema,
  metrics: z.array(marketMetricSchema),
  supportStatuses: supportStatusesSchema,
  freshness: freshnessSchema,
  generatedAt: z.string(),
})

export type MarketSnapshotParsed = z.infer<typeof marketSnapshotSchema>
export type MarketMetricParsed = z.infer<typeof marketMetricSchema>
export type ActiveListingsMetricParsed = z.infer<typeof activeListingsMetricSchema>
export type MedianPriceMetricParsed = z.infer<typeof medianPriceMetricSchema>
export type TypicalPriceRangeMetricParsed = z.infer<typeof typicalPriceRangeMetricSchema>
export type InventoryChangeMetricParsed = z.infer<typeof inventoryChangeMetricSchema>
export type PriceDropsMetricParsed = z.infer<typeof priceDropsMetricSchema>
export type MetricSupportStatusParsed = z.infer<typeof metricSupportStatusSchema>
export type FreshnessParsed = z.infer<typeof freshnessSchema>
export type MarketFilterSelectionParsed = z.infer<typeof marketFilterSelectionSchema>
import { z } from "zod"
import { freshnessSchema, marketFilterSelectionSchema } from "./market-snapshot.schema"

// Trust boundary: validate the Filter Options payload before it enters feature code.
// Mirrors contracts/filter-options-api.md.

const filterOptionSchema = z.object({
  value: z.union([z.string(), z.number()]),
  displayName: z.string(),
  activeListingCount: z.number().nullable().optional(),
})

export const filterOptionsSchema = z.object({
  filters: marketFilterSelectionSchema,
  options: z.object({
    makes: z.array(filterOptionSchema),
    models: z.array(filterOptionSchema),
    trims: z.array(filterOptionSchema),
    years: z.array(filterOptionSchema),
  }),
  freshness: freshnessSchema,
  generatedAt: z.string(),
})

export type FilterOptionsParsed = z.infer<typeof filterOptionsSchema>
export type FilterOptionParsed = z.infer<typeof filterOptionSchema>
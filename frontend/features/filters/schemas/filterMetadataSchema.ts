import { z } from "zod"

// Trust boundary: validate the FilterMetadataResponse payload from Feature 003
// before it enters feature code. Unknown future fields are ignored (passthrough).

const numericRangeSchema = z.object({
  min: z.number().nullable(),
  max: z.number().nullable(),
})

export const filterMetadataSchema = z.object({
  makes: z.array(z.string()),
  models: z.record(z.string(), z.array(z.string())),
  price: numericRangeSchema,
  year: numericRangeSchema,
  km: numericRangeSchema,
  conditions: z.array(z.string()),
  sellerTypes: z.array(z.string()),
})

export type FilterMetadataParsed = z.infer<typeof filterMetadataSchema>
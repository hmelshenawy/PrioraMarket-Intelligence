import { z } from "zod"

// Trust boundary: validate the SearchListingsResponse payload from Feature 003
// before it enters feature code. After this parse, the typed DTO flows through
// features without re-validation per the Zod Validation Boundary policy.

const nullableString = z.string().nullable()
const nullableNumber = z.number().nullable()

export const listingSearchResultSchema = z.object({
  id: z.string(),
  externalId: nullableString,
  title: nullableString,
  make: nullableString,
  model: nullableString,
  trim: nullableString,
  year: nullableNumber,
  priceAed: nullableNumber,
  km: nullableNumber,
  condition: nullableString,
  location: nullableString,
  sellerType: nullableString,
  url: nullableString,
  photosCount: nullableNumber,
  firstSeenAt: nullableString,
  lastSeenAt: nullableString,
})

export const paginationMetaSchema = z.object({
  page: z.number(),
  limit: z.number(),
  total: z.number(),
  totalPages: z.number(),
})

export const searchListingsResponseSchema = z.object({
  data: z.array(listingSearchResultSchema),
  meta: paginationMetaSchema,
})

export type SearchListingsResponseParsed = z.infer<typeof searchListingsResponseSchema>
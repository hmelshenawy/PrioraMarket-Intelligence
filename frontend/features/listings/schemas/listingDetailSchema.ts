import { z } from "zod"
import { listingSearchResultSchema } from "@/features/search/schemas/searchResponseSchema"

// Trust boundary: validate the ListingDetailResponse payload from Feature 003
// before it enters feature code. Extends the search-result shape with detail-only
// fields, and treats unknown `specs` keys as a free-form object (displayed safely).

const nullableString = z.string().nullable()
const nullableBoolean = z.boolean().nullable()

export const listingDetailSchema = listingSearchResultSchema.extend({
  marketplace: nullableString,
  bodyType: nullableString,
  fuel: nullableString,
  transmission: nullableString,
  color: nullableString,
  // Unknown specifications are displayed as additional specifications; we do not
  // impose a shape beyond a record of primitives.
  specs: z.record(z.string(), z.unknown()).nullable(),
  seller: nullableString,
  isVerified: nullableBoolean,
  isAgent: nullableBoolean,
  neighbourhood: nullableString,
  firstSeenRunId: nullableString,
  lastSeenRunId: nullableString,
  canonicalHash: nullableString,
})

export type ListingDetailParsed = z.infer<typeof listingDetailSchema>
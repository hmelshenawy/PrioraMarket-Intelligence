import { z } from "zod"

// Backend sort enum aligned to Feature 003 contracts.
export const sortOptions = [
  "relevance",
  "newest",
  "price_asc",
  "price_desc",
  "year_asc",
  "year_desc",
  "km_asc",
  "km_desc",
] as const
export type SortOption = (typeof sortOptions)[number]

export const defaultSort: SortOption = "relevance"
export const defaultPage = 1
export const defaultLimit = 20

// Trust boundary: parse raw URL query string values into normalized SearchUrlState.
// Invalid/empty values are omitted; ranges validate min<=max; page>=1; unsupported
// sort values normalize to the default sort (per data-model.md).
const numString = z
  .string()
  .optional()
  .transform((v) => {
    if (v == null || v === "") return undefined
    const n = Number(v)
    return Number.isFinite(n) ? n : undefined
  })

const nonEmptyString = z
  .string()
  .optional()
  .transform((v) => (v == null || v.trim() === "" ? undefined : v.trim()))

// Lenient condition: drop anything that is not exactly "used" or "new".
const conditionField = z
  .string()
  .optional()
  .transform((v): "used" | "new" | undefined => (v === "used" || v === "new" ? v : undefined))

// Lenient sort: unsupported values fall back to the default sort.
const sortField = z
  .string()
  .optional()
  .transform((v) =>
    v && (sortOptions as readonly string[]).includes(v) ? (v as SortOption) : defaultSort,
  )

export const searchStateSchema = z
  .object({
    q: nonEmptyString,
    condition: conditionField,
    make: nonEmptyString,
    model: nonEmptyString,
    sellerType: nonEmptyString,
    location: nonEmptyString,
    priceMin: numString,
    priceMax: numString,
    kmMin: numString,
    kmMax: numString,
    yearFrom: numString,
    yearTo: numString,
    sort: sortField,
    page: numString,
    limit: numString,
  })
  .transform((s) => {
    // Range validation: if min > max, drop both to avoid invalid API requests.
    const clampRange = (min: number | undefined, max: number | undefined) => {
      if (min != null && max != null && min > max) return { min: undefined, max: undefined }
      return { min, max }
    }
    const price = clampRange(s.priceMin, s.priceMax)
    const km = clampRange(s.kmMin, s.kmMax)
    const year = clampRange(s.yearFrom, s.yearTo)

    const page = s.page == null || !Number.isFinite(s.page) || s.page < 1 ? defaultPage : Math.floor(s.page)
    const limit = s.limit == null || !Number.isFinite(s.limit) || s.limit < 1 ? defaultLimit : Math.floor(s.limit)

    return {
      q: s.q,
      condition: s.condition,
      make: s.make,
      model: s.model,
      sellerType: s.sellerType,
      location: s.location,
      priceMin: price.min,
      priceMax: price.max,
      kmMin: km.min,
      kmMax: km.max,
      yearFrom: year.min,
      yearTo: year.max,
      sort: s.sort ?? defaultSort,
      page,
      limit,
    }
  })

export type SearchUrlState = z.infer<typeof searchStateSchema>
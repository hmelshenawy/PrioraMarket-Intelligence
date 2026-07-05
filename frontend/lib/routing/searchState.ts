import { searchStateSchema, type SearchUrlState, defaultPage, defaultLimit, defaultSort } from "@/lib/validation/searchStateSchema"

export type { SearchUrlState }
export { defaultPage, defaultLimit, defaultSort }

// Parse a URLSearchParams (or record) into normalized SearchUrlState.
// Invalid/empty values are omitted; ranges validated; page/limit defaulted.
export function parseSearchState(input: URLSearchParams | Record<string, string | string[] | undefined>): SearchUrlState {
  const record: Record<string, string | undefined> = {}
  if (input instanceof URLSearchParams) {
    input.forEach((value, key) => {
      record[key] = value
    })
  } else {
    for (const [key, value] of Object.entries(input)) {
      record[key] = Array.isArray(value) ? value[0] : value
    }
  }
  return searchStateSchema.parse(record)
}

// Serialize SearchUrlState back into URLSearchParams, omitting empty/default values.
export function serializeSearchState(state: SearchUrlState): URLSearchParams {
  const params = new URLSearchParams()
  const set = (key: string, value: string | number | undefined) => {
    if (value == null || value === "") return
    const str = String(value)
    params.set(key, str)
  }
  set("q", state.q)
  set("condition", state.condition)
  set("make", state.make)
  set("model", state.model)
  set("sellerType", state.sellerType)
  set("location", state.location)
  set("priceMin", state.priceMin)
  set("priceMax", state.priceMax)
  set("kmMin", state.kmMin)
  set("kmMax", state.kmMax)
  set("yearFrom", state.yearFrom)
  set("yearTo", state.yearTo)
  // Omit default sort/page/limit to keep URLs clean.
  if (state.sort !== defaultSort) set("sort", state.sort)
  if (state.page !== defaultPage) set("page", state.page)
  if (state.limit !== defaultLimit) set("limit", state.limit)
  return params
}

// Build the query string for navigation; returns "" or "?key=value&...".
export function buildSearchString(state: SearchUrlState): string {
  const params = serializeSearchState(state)
  const qs = params.toString()
  return qs ? `?${qs}` : ""
}

// Default cleared search state (used by Clear Filters).
export const defaultSearchState: SearchUrlState = {
  q: undefined,
  condition: undefined,
  make: undefined,
  model: undefined,
  sellerType: undefined,
  location: undefined,
  priceMin: undefined,
  priceMax: undefined,
  kmMin: undefined,
  kmMax: undefined,
  yearFrom: undefined,
  yearTo: undefined,
  sort: defaultSort,
  page: defaultPage,
  limit: defaultLimit,
}

// Produce a new state with one or more partial updates applied, resetting page to 1
// when a non-pagination field changes.
export function updateSearchState(
  current: SearchUrlState,
  patch: Partial<SearchUrlState>,
  opts: { resetPage?: boolean } = { resetPage: true },
): SearchUrlState {
  const next: SearchUrlState = { ...current, ...patch }
  if (opts.resetPage && patch.page == null) next.page = defaultPage
  return next
}
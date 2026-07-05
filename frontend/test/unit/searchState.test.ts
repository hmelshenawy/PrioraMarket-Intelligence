import { describe, expect, it } from "vitest"
import {
  buildSearchString,
  defaultSearchState,
  parseSearchState,
  serializeSearchState,
  updateSearchState,
} from "@/lib/routing/searchState"
import { defaultLimit, defaultPage, defaultSort } from "@/lib/validation/searchStateSchema"

describe("parseSearchState", () => {
  it("parses valid params into normalized state with defaults applied", () => {
    const state = parseSearchState(new URLSearchParams("q=toyota&sort=newest&page=3"))
    expect(state.q).toBe("toyota")
    expect(state.sort).toBe("newest")
    expect(state.page).toBe(3)
    expect(state.limit).toBe(defaultLimit)
  })

  it("trims whitespace and drops empty strings", () => {
    const state = parseSearchState(new URLSearchParams("q=   &make=  Toyota "))
    expect(state.q).toBeUndefined()
    expect(state.make).toBe("Toyota")
  })

  it("clamps page to >= 1 and floors fractional pages", () => {
    expect(parseSearchState(new URLSearchParams("page=0")).page).toBe(1)
    expect(parseSearchState(new URLSearchParams("page=-2")).page).toBe(1)
    expect(parseSearchState(new URLSearchParams("page=2.9")).page).toBe(2)
  })

  it("drops both sides of an inverted range", () => {
    const state = parseSearchState(new URLSearchParams("priceMin=100&priceMax=50"))
    expect(state.priceMin).toBeUndefined()
    expect(state.priceMax).toBeUndefined()
  })

  it("normalizes unsupported sort to the default", () => {
    const state = parseSearchState(new URLSearchParams("sort=bogus"))
    expect(state.sort).toBe(defaultSort)
  })
})

describe("serializeSearchState", () => {
  it("omits empty values and default sort/page/limit", () => {
    const params = serializeSearchState({ ...defaultSearchState, q: "camry" })
    expect(params.get("q")).toBe("camry")
    expect(params.get("sort")).toBeNull()
    expect(params.get("page")).toBeNull()
    expect(params.get("limit")).toBeNull()
  })

  it("keeps non-default sort/page/limit", () => {
    const params = serializeSearchState({
      ...defaultSearchState,
      sort: "price_asc",
      page: 4,
      limit: 40,
    })
    expect(params.get("sort")).toBe("price_asc")
    expect(params.get("page")).toBe("4")
    expect(params.get("limit")).toBe("40")
  })
})

describe("buildSearchString", () => {
  it("returns empty string for default state", () => {
    expect(buildSearchString(defaultSearchState)).toBe("")
  })

  it("returns a query string with leading '?' for non-default state", () => {
    const qs = buildSearchString({ ...defaultSearchState, q: "honda" })
    expect(qs.startsWith("?")).toBe(true)
    expect(qs).toContain("q=honda")
  })
})

describe("updateSearchState", () => {
  it("resets page to 1 when a non-pagination field changes", () => {
    const next = updateSearchState({ ...defaultSearchState, page: 5 }, { make: "Tesla" })
    expect(next.make).toBe("Tesla")
    expect(next.page).toBe(1)
  })

  it("preserves page when the patch is a page change", () => {
    const next = updateSearchState({ ...defaultSearchState, page: 2 }, { page: 7 })
    expect(next.page).toBe(7)
  })

  it("preserves page when resetPage is false", () => {
    const next = updateSearchState(
      { ...defaultSearchState, page: 3 },
      { make: "Tesla" },
      { resetPage: false },
    )
    expect(next.page).toBe(3)
  })
})

describe("defaultSearchState", () => {
  it("has default sort/page/limit and undefined filters", () => {
    expect(defaultSearchState.sort).toBe(defaultSort)
    expect(defaultSearchState.page).toBe(defaultPage)
    expect(defaultSearchState.limit).toBe(defaultLimit)
    expect(defaultSearchState.q).toBeUndefined()
  })
})
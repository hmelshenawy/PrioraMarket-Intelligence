import { describe, expect, it } from "vitest"
import { searchStateSchema, defaultLimit, defaultPage, defaultSort, sortOptions } from "@/lib/validation/searchStateSchema"

describe("searchStateSchema", () => {
  it("accepts an empty record and applies all defaults", () => {
    const parsed = searchStateSchema.parse({})
    expect(parsed.sort).toBe(defaultSort)
    expect(parsed.page).toBe(defaultPage)
    expect(parsed.limit).toBe(defaultLimit)
  })

  it("accepts the documented condition enum values", () => {
    expect(searchStateSchema.parse({ condition: "used" }).condition).toBe("used")
    expect(searchStateSchema.parse({ condition: "new" }).condition).toBe("new")
  })

  it("drops unsupported condition values (lenient trust boundary)", () => {
    expect(searchStateSchema.parse({ condition: "broken" }).condition).toBeUndefined()
  })

  it("normalizes unsupported sort to the default", () => {
    expect(searchStateSchema.parse({ sort: "bogus" }).sort).toBe(defaultSort)
    expect(searchStateSchema.parse({ sort: "" }).sort).toBe(defaultSort)
    // Valid values pass through.
    sortOptions.forEach((opt) => {
      expect(searchStateSchema.parse({ sort: opt }).sort).toBe(opt)
    })
  })

  it("drops inverted price ranges", () => {
    const parsed = searchStateSchema.parse({ priceMin: "200", priceMax: "100" })
    expect(parsed.priceMin).toBeUndefined()
    expect(parsed.priceMax).toBeUndefined()
  })

  it("keeps valid ranges", () => {
    const parsed = searchStateSchema.parse({ yearFrom: "2015", yearTo: "2022" })
    expect(parsed.yearFrom).toBe(2015)
    expect(parsed.yearTo).toBe(2022)
  })

  it("treats non-numeric strings as undefined for numeric fields", () => {
    const parsed = searchStateSchema.parse({ page: "abc", kmMin: "lots" })
    expect(parsed.page).toBe(defaultPage)
    expect(parsed.kmMin).toBeUndefined()
  })
})
import { describe, expect, it } from "vitest"
import { searchListings } from "@/features/search/api/search.api"
import { searchSuccessFixture, searchEmptyFixture } from "@/test/mocks/fixtures"
import { defaultSearchState } from "@/lib/routing/searchState"
import { ApiErrorImpl } from "@/lib/api/errors"

describe("search.api", () => {
  it("returns parsed results for a normal search", async () => {
    const dto = await searchListings({ ...defaultSearchState, q: "toyota" })
    expect(dto.data).toHaveLength(searchSuccessFixture.data.length)
    expect(dto.meta.total).toBe(searchSuccessFixture.meta.total)
  })

  it("returns an empty result set when q=empty", async () => {
    const dto = await searchListings({ ...defaultSearchState, q: "empty" })
    expect(dto.data).toHaveLength(0)
    expect(dto.meta.total).toBe(0)
    expect(dto.meta.totalPages).toBe(0)
  })

  it("normalizes a 400 backend error into a badRequest ApiError", async () => {
    try {
      await searchListings({ ...defaultSearchState, q: "fail" })
      throw new Error("expected searchListings to reject")
    } catch (e) {
      expect(e).toBeInstanceOf(ApiErrorImpl)
      const err = e as ApiErrorImpl
      expect(err.category).toBe("badRequest")
      expect(err.status).toBe(400)
    }
  })

  it("validates the response shape at the trust boundary", async () => {
    const dto = await searchListings(defaultSearchState)
    expect(dto).toMatchObject({
      data: expect.any(Array),
      meta: expect.objectContaining({
        page: expect.any(Number),
        limit: expect.any(Number),
        total: expect.any(Number),
        totalPages: expect.any(Number),
      }),
    })
    expect(searchEmptyFixture.data).toEqual([])
  })
})
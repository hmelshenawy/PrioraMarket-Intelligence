import { describe, expect, it } from "vitest"
import { fetchListingDetail } from "@/features/listings/api/listings.api"
import { ApiErrorImpl } from "@/lib/api/errors"
import { listingDetailFixture } from "@/test/mocks/fixtures"

describe("listings.api", () => {
  it("returns the parsed detail payload for an existing listing", async () => {
    const dto = await fetchListingDetail("abc")
    expect(dto.id).toBe("abc")
    expect(dto.make).toBe(listingDetailFixture.make)
    expect(dto.specs).toEqual(listingDetailFixture.specs)
  })

  it("normalizes a 404 into a notFound ApiError", async () => {
    try {
      await fetchListingDetail("missing")
      throw new Error("expected fetchListingDetail to reject")
    } catch (e) {
      expect(e).toBeInstanceOf(ApiErrorImpl)
      expect((e as ApiErrorImpl).category).toBe("notFound")
      expect((e as ApiErrorImpl).status).toBe(404)
    }
  })

  it("normalizes a 500 into a serverError ApiError", async () => {
    try {
      await fetchListingDetail("fail")
      throw new Error("expected fetchListingDetail to reject")
    } catch (e) {
      expect(e).toBeInstanceOf(ApiErrorImpl)
      expect((e as ApiErrorImpl).category).toBe("serverError")
      expect((e as ApiErrorImpl).status).toBe(500)
    }
  })
})
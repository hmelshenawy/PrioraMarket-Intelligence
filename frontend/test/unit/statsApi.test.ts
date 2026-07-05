import { describe, expect, it } from "vitest"
import { http, HttpResponse } from "msw"
import { fetchMarketStats } from "@/features/stats/api/stats.api"
import { ApiErrorImpl } from "@/lib/api/errors"
import { server } from "@/test/mocks/server"
import { statsFixture } from "@/test/mocks/fixtures"

const BASE = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:3000"

describe("stats.api", () => {
  it("returns the parsed inventory stats payload", async () => {
    const dto = await fetchMarketStats()
    expect(dto.totalListings).toBe(statsFixture.totalListings)
    expect(dto.averagePriceAed).toBe(statsFixture.averagePriceAed)
    expect(dto.lastUpdatedAt).toBe(statsFixture.lastUpdatedAt)
  })

  it("normalizes a 500 into a serverError ApiError", async () => {
    server.use(
      http.get(`${BASE}/api/v1/stats`, () =>
        HttpResponse.json({ statusCode: 500, error: "Server Error", message: "down" }, { status: 500 }),
      ),
    )
    try {
      await fetchMarketStats()
      throw new Error("expected fetchMarketStats to reject")
    } catch (e) {
      expect(e).toBeInstanceOf(ApiErrorImpl)
      expect((e as ApiErrorImpl).category).toBe("serverError")
      expect((e as ApiErrorImpl).status).toBe(500)
    }
  })
})
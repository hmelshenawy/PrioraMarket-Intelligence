import { describe, expect, it } from "vitest"
import { http, HttpResponse } from "msw"
import { fetchFilterMetadata } from "@/features/filters/api/filters.api"
import { ApiErrorImpl } from "@/lib/api/errors"
import { server } from "@/test/mocks/server"
import { filterMetadataFixture } from "@/test/mocks/fixtures"

const BASE = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:3000"

describe("filters.api", () => {
  it("returns the parsed filter metadata", async () => {
    const dto = await fetchFilterMetadata()
    expect(dto.makes).toEqual(filterMetadataFixture.makes)
    expect(dto.models.Toyota).toEqual(["Camry", "Corolla"])
    expect(dto.conditions).toEqual(["used", "new"])
  })

  it("normalizes a 500 into a serverError ApiError", async () => {
    server.use(
      http.get(`${BASE}/api/v1/listings/filters`, () =>
        HttpResponse.json({ statusCode: 500, error: "Server Error", message: "down" }, { status: 500 }),
      ),
    )
    try {
      await fetchFilterMetadata()
      throw new Error("expected fetchFilterMetadata to reject")
    } catch (e) {
      expect(e).toBeInstanceOf(ApiErrorImpl)
      expect((e as ApiErrorImpl).category).toBe("serverError")
    }
  })
})
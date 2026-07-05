import { describe, expect, it } from "vitest"
import { normalizeApiError } from "@/lib/api/errors"
import type { ApiErrorResponseDto } from "@/lib/api/types"

describe("normalizeApiError", () => {
  it("maps a no-response ERR_NETWORK error to the offline category", () => {
    const err = normalizeApiError({ isAxiosError: true, code: "ERR_NETWORK", message: "Network Error" })
    expect(err.category).toBe("offline")
  })

  it("maps a no-response timeout to the network category", () => {
    const err = normalizeApiError({ isAxiosError: true, code: "ECONNABORTED", message: "timeout" })
    expect(err.category).toBe("offline")
  })

  it("maps a 400 response with an ApiErrorResponse body to badRequest and joins messages", () => {
    const body: ApiErrorResponseDto = { statusCode: 400, error: "Bad Request", message: ["q invalid", "limit invalid"], requestId: "r-1" }
    const err = normalizeApiError({ isAxiosError: true, response: { status: 400, data: body } })
    expect(err.category).toBe("badRequest")
    expect(err.status).toBe(400)
    expect(err.message).toBe("q invalid, limit invalid")
    expect(err.requestId).toBe("r-1")
  })

  it("maps a 404 response to notFound", () => {
    const err = normalizeApiError({ isAxiosError: true, response: { status: 404, data: { statusCode: 404, error: "Not Found", message: "nope" } } })
    expect(err.category).toBe("notFound")
  })

  it("maps a 500 response to serverError with a safe message", () => {
    const err = normalizeApiError({ isAxiosError: true, response: { status: 500, data: {} } })
    expect(err.category).toBe("serverError")
    expect(err.message).toMatch(/backend reported an error/i)
  })

  it("passes through an already-normalized ApiError", () => {
    const normalized = { category: "offline" as const, message: "x" }
    expect(normalizeApiError(normalized)).toBe(normalized)
  })
})
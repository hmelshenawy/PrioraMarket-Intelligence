import { http, HttpResponse } from "msw"
import {
  searchSuccessFixture,
  searchEmptyFixture,
  listingDetailFixture,
  filterMetadataFixture,
  statsFixture,
  healthOkFixture,
  apiErrorFixture,
} from "./fixtures"

const BASE = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:3000"

// Default handlers for the five allowed Feature 003 endpoints.
// `/listings/filters` is registered before `/listings/:id` so the static path is
// matched first (otherwise `:id` would capture "filters" as an id).
// Tests can override per-test using server.use(...).
export const handlers = [
  http.get(`${BASE}/api/v1/listings`, ({ request }) => {
    const url = new URL(request.url)
    const q = url.searchParams.get("q")
    if (q === "empty") return HttpResponse.json(searchEmptyFixture)
    if (q === "fail") return HttpResponse.json(apiErrorFixture(400, "Bad search"), { status: 400 })
    return HttpResponse.json(searchSuccessFixture)
  }),

  http.get(`${BASE}/api/v1/listings/filters`, () => HttpResponse.json(filterMetadataFixture)),

  http.get(`${BASE}/api/v1/listings/:id`, ({ params }) => {
    const id = params.id as string
    if (id === "missing") return HttpResponse.json(apiErrorFixture(404, "Listing not found"), { status: 404 })
    if (id === "fail") return HttpResponse.json(apiErrorFixture(500, "Server error"), { status: 500 })
    return HttpResponse.json({ ...listingDetailFixture, id })
  }),

  http.get(`${BASE}/api/v1/stats`, () => {
    if (process.env.MSW_STATS_FAIL === "1") {
      return HttpResponse.json(apiErrorFixture(500, "stats down"), { status: 500 })
    }
    return HttpResponse.json(statsFixture)
  }),

  http.get(`${BASE}/api/v1/health`, () => {
    if (process.env.MSW_HEALTH_FAIL === "1") {
      return new HttpResponse(null, { status: 503 })
    }
    return HttpResponse.json(healthOkFixture)
  }),
]
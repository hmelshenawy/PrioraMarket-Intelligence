import { describe, expect, it, afterEach } from "vitest"
import { render, screen, waitFor } from "@testing-library/react"
import { http, HttpResponse } from "msw"
import { QueryClient, QueryClientProvider } from "@tanstack/react-query"
import { MarketOverview } from "@/features/stats/components/MarketOverview"
import { server } from "@/test/mocks/server"
import { statsFixture } from "@/test/mocks/fixtures"
import { formatAed, formatDate, formatNumber } from "@/lib/formatting"
import { EMPTY_VALUE } from "@/lib/formatting/emptyValue"

const BASE = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:3000"

function renderOverview() {
  const client = new QueryClient({
    defaultOptions: { queries: { retry: false, gcTime: 0, staleTime: 0 } },
  })
  return render(
    <QueryClientProvider client={client}>
      <MarketOverview />
    </QueryClientProvider>,
  )
}

describe("MarketOverview", () => {
  afterEach(() => {
    server.resetHandlers()
  })

  it("shows the summary skeleton while stats load", () => {
    // Never-resolving handler keeps the query pending so the loading state persists.
    server.use(http.get(`${BASE}/api/v1/stats`, () => new Promise<never>(() => {})))
    renderOverview()
    expect(document.querySelector('section[aria-busy="true"]')).not.toBeNull()
  })

  it("renders formatted metrics once stats are available", async () => {
    renderOverview()
    await waitFor(() => expect(screen.getByText(formatNumber(statsFixture.totalListings))).toBeInTheDocument())
    expect(screen.getByText(formatNumber(statsFixture.usedListings))).toBeInTheDocument()
    expect(screen.getByText(formatNumber(statsFixture.newListings))).toBeInTheDocument()
    expect(screen.getByText(formatNumber(statsFixture.totalMakes))).toBeInTheDocument()
    expect(screen.getByText(formatNumber(statsFixture.totalModels))).toBeInTheDocument()
    expect(screen.getByText(formatAed(statsFixture.averagePriceAed!, { compact: true }))).toBeInTheDocument()
    expect(screen.getByText(formatDate(statsFixture.lastUpdatedAt))).toBeInTheDocument()
  })

  it("softens a null average price and missing last updated to the empty placeholder", async () => {
    server.use(
      http.get(`${BASE}/api/v1/stats`, () =>
        HttpResponse.json({ ...statsFixture, averagePriceAed: null, lastUpdatedAt: null }),
      ),
    )
    renderOverview()
    await waitFor(() => expect(screen.getAllByText(EMPTY_VALUE).length).toBeGreaterThanOrEqual(2))
  })

  it("shows a scoped error state with retry when stats fail", async () => {
    server.use(
      http.get(`${BASE}/api/v1/stats`, () =>
        HttpResponse.json({ statusCode: 500, error: "Server Error", message: "down" }, { status: 500 }),
      ),
    )
    renderOverview()
    await waitFor(() => expect(screen.getByRole("alert").textContent).toMatch(/Market overview unavailable/i))
    expect(screen.getByRole("button", { name: /try again/i })).toBeInTheDocument()
  })
})
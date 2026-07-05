import { describe, expect, it, vi, beforeEach, afterEach } from "vitest"
import { render, screen, waitFor } from "@testing-library/react"
import { http, HttpResponse } from "msw"
import { QueryClient, QueryClientProvider } from "@tanstack/react-query"
import { MarketFilterBar } from "@/features/market/components/MarketFilterBar"
import { ScopeLabel } from "@/features/market/components/ScopeLabel"
import { server } from "@/test/mocks/server"
import type { MarketFilterSelectionDto } from "@/features/market/types"

const BASE = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:3000"

function makeOptions(name: string): string[] {
  const sel = document.querySelector(`select[name="${name}"]`) as HTMLSelectElement
  return Array.from(sel.options).map((o) => o.textContent ?? "")
}

function renderFilterBar(selection: MarketFilterSelectionDto = {}) {
  const client = new QueryClient({
    defaultOptions: { queries: { retry: false, gcTime: 0, staleTime: 0 } }
  })
  return render(
    <QueryClientProvider client={client}>
      <MarketFilterBar selection={selection} onSelectionChange={vi.fn()} />
    </QueryClientProvider>
  )
}

describe("MarketFilterBar display-name rendering (US3 / T063)", () => {
  afterEach(() => server.resetHandlers())

  beforeEach(() => {
    server.use(
      http.get(`${BASE}/api/v1/market/filter-options`, ({ request }) => {
        const url = new URL(request.url)
        const make = url.searchParams.get("make")
        // Distinctive display names prove the component renders the API value, not a
        // hardcoded name. Year display is the integer stringified (canonical fallback).
        const makes = [
          { value: "toyota", displayName: "Toyota Motor Co", activeListingCount: 4381 },
          { value: "bmw", displayName: "BMW Group", activeListingCount: 2981 }
        ]
        const models =
          make === "toyota"
            ? [{ value: "corolla", displayName: "Corolla Sedan", activeListingCount: 842 }]
            : []
        return HttpResponse.json({
          filters: { make: make ?? undefined, model: undefined, trim: undefined, year: undefined },
          options: { makes, models, trims: [], years: [] },
          freshness: { lastUpdated: "2026-07-05T08:00:00.000Z", datasetVersion: "canonical-2024.05", scrapeRunId: 1042 },
          generatedAt: "2026-07-05T12:30:00.000Z"
        })
      })
    )
  })

  it("renders make option labels from the API displayName with active listing counts", async () => {
    renderFilterBar()
    await waitFor(() =>
      expect(makeOptions("make")).toEqual([
        "All makes",
        "Toyota Motor Co (4,381)",
        "BMW Group (2,981)"
      ])
    )
  })

  it("does not hardcode vehicle names — only the API displayName is shown", async () => {
    renderFilterBar()
    // The distinctive API display names appear verbatim; a hardcoded "Toyota" / "BMW"
    // (without the suffix) would NOT match these option labels.
    await waitFor(() => expect(makeOptions("make")).toContain("Toyota Motor Co (4,381)"))
    await waitFor(() => expect(makeOptions("make")).toContain("BMW Group (2,981)"))
    // The raw canonical value is NOT displayed as the label when a display name exists.
    expect(makeOptions("make")).not.toContain("toyota (4,381)")
  })

  it("renders model option display names scoped by the selected make", async () => {
    renderFilterBar({ make: "toyota" })
    await waitFor(() => expect(makeOptions("model")).toEqual(["All models", "Corolla Sedan (842)"]))
    // Model select is enabled once a make is selected.
    expect((document.querySelector('select[name="model"]') as HTMLSelectElement).disabled).toBe(false)
    // Trim/year remain disabled (no model+trim selected).
    expect((document.querySelector('select[name="trim"]') as HTMLSelectElement).disabled).toBe(true)
    expect((document.querySelector('select[name="year"]') as HTMLSelectElement).disabled).toBe(true)
  })

  it("renders the canonical value unchanged when the API returns no display name (no title-casing)", async () => {
    server.resetHandlers()
    server.use(
      http.get(`${BASE}/api/v1/market/filter-options`, () =>
        HttpResponse.json({
          filters: { make: undefined, model: undefined, trim: undefined, year: undefined },
          options: {
            makes: [{ value: "toyota", displayName: "toyota", activeListingCount: 4381 }],
            models: [],
            trims: [],
            years: []
          },
          freshness: { lastUpdated: "2026-07-05T08:00:00.000Z", datasetVersion: "canonical-2024.05", scrapeRunId: 1042 },
          generatedAt: "2026-07-05T12:30:00.000Z"
        })
      )
    )
    renderFilterBar()
    // Canonical fallback is shown verbatim — not transformed to "Toyota".
    await waitFor(() => expect(makeOptions("make")).toEqual(["All makes", "toyota (4,381)"]))
  })
})

describe("ScopeLabel renders the API-provided scope label (US3 / T068)", () => {
  it("renders the API scope label verbatim with no hardcoded names", () => {
    render(<ScopeLabel label="Toyota Corolla xli 2023" level="year" />)
    const heading = screen.getByRole("heading", { level: 1 })
    expect(heading).toHaveTextContent("Toyota Corolla xli 2023")
    expect(heading).toHaveAttribute("data-scope-level", "year")
  })

  it("renders the overall label when the API provides it", () => {
    render(<ScopeLabel label="Overall UAE Used Cars" level="overall" />)
    expect(screen.getByRole("heading", { level: 1 })).toHaveTextContent("Overall UAE Used Cars")
  })
})
import { describe, expect, it, vi, beforeEach } from "vitest"
import { useSyncExternalStore } from "react"
import { render, screen, waitFor, fireEvent } from "@testing-library/react"
import { QueryClient, QueryClientProvider } from "@tanstack/react-query"
import { http, HttpResponse } from "msw"
import { DashboardShell } from "@/features/market/components/DashboardShell"
import { server } from "@/test/mocks/server"

const BASE = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:3000"

// URL-as-source-of-truth simulation: router.replace updates a store backed by
// useSyncExternalStore so components re-render when the URL changes (the real
// next/navigation useSearchParams re-renders on navigation). No full page reload.
let cachedParams = new URLSearchParams("")
const subscribers = new Set<() => void>()
const replaceCalls: string[] = []

function subscribe(cb: () => void) {
  subscribers.add(cb)
  return () => subscribers.delete(cb)
}
function getSnapshot() {
  return cachedParams
}
function setSearch(search: string) {
  cachedParams = new URLSearchParams(search)
  subscribers.forEach((cb) => cb())
}
function resetSearch(search: string) {
  cachedParams = new URLSearchParams(search)
  subscribers.clear()
  replaceCalls.length = 0
}

vi.mock("next/navigation", () => ({
  usePathname: () => "/market",
  useRouter: () => ({
    replace: (url: string) => {
      replaceCalls.push(url)
      const idx = url.indexOf("?")
      setSearch(idx >= 0 ? url.slice(idx + 1) : "")
    },
    push: (url: string) => {
      replaceCalls.push(url)
      const idx = url.indexOf("?")
      setSearch(idx >= 0 ? url.slice(idx + 1) : "")
    }
  }),
  useSearchParams: () => useSyncExternalStore(subscribe, getSnapshot)
}))

function makeOptions(name: string): string[] {
  const sel = document.querySelector(`select[name="${name}"]`) as HTMLSelectElement
  return Array.from(sel.options).map((o) => o.textContent ?? "")
}

function selectOption(name: string, value: string) {
  const sel = document.querySelector(`select[name="${name}"]`) as HTMLSelectElement
  fireEvent.change(sel, { target: { value } })
}

// Dynamic MSW handlers: snapshot echoes the selected scope; filter-options cascade by
// higher-level filters. Unselected filter fields are omitted (undefined → omitted in JSON),
// matching the backend serialization the frontend zod schema expects.
function marketHandlers() {
  return [
    http.get(`${BASE}/api/v1/market/snapshot`, ({ request }) => {
      const url = new URL(request.url)
      const make = url.searchParams.get("make")
      const model = url.searchParams.get("model")
      const trim = url.searchParams.get("trim")
      const year = url.searchParams.get("year")
      const level = year ? "year" : trim ? "trim" : model ? "model" : make ? "make" : "overall"
      const parts = [make, model, trim, year].filter(Boolean)
      const label = parts.length ? parts.join(" ") : "Overall UAE Used Cars"
      const count = year ? 57 : trim ? 214 : model ? 842 : make ? 4381 : 8421
      return HttpResponse.json({
        scope: { level, label, canonical: { make: make ?? undefined, model: model ?? undefined, trim: trim ?? undefined, year: year ? Number(year) : null } },
        filters: { make: make ?? undefined, model: model ?? undefined, trim: trim ?? undefined, year: year ? Number(year) : undefined, periodDays: 7 },
        period: { days: 7, label: "Last 7 days" },
        metrics: [
          { type: "activeListings", title: "Active Listings", status: { status: "supported", dataAvailable: true }, count, scopeLabel: label },
          { type: "medianPrice", title: "Median Price", status: { status: "supported", dataAvailable: true }, amount: 170000, currency: "AED", sampleSize: 8 },
          { type: "typicalPriceRange", title: "Typical Price Range", status: { status: "supported", dataAvailable: true }, method: "typical-range", currency: "AED", medianAmount: 170000, lowerAmount: 135000, upperAmount: 205000, minAmount: null, maxAmount: null, sampleSize: 8 },
          { type: "inventoryChange", title: "Inventory Change", status: { status: "partial", dataAvailable: true, reason: "Period inventory change tracking is not available" }, activeInventory: count, newListings: null, removedListings: null, netChange: null, periodDays: 7 },
          { type: "priceDrops", title: "Price Drops", status: { status: "unsupported", dataAvailable: false, reason: "Price history is not available" }, count: null, averageDropPercentage: null, sampleSize: null, periodDays: 7 }
        ],
        supportStatuses: {
          activeListings: { status: "supported", dataAvailable: true },
          medianPrice: { status: "supported", dataAvailable: true },
          typicalPriceRange: { status: "supported", dataAvailable: true },
          inventoryChange: { status: "partial", dataAvailable: true, reason: "Period inventory change tracking is not available" },
          priceDrops: { status: "unsupported", dataAvailable: false, reason: "Price history is not available" }
        },
        freshness: { lastUpdated: "2026-07-05T08:00:00.000Z", datasetVersion: "canonical-2024.05", scrapeRunId: 1042 },
        generatedAt: "2026-07-05T12:30:00.000Z"
      })
    }),
    http.get(`${BASE}/api/v1/market/filter-options`, ({ request }) => {
      const url = new URL(request.url)
      const make = url.searchParams.get("make")
      const model = url.searchParams.get("model")
      const trim = url.searchParams.get("trim")
      const makes = [
        { value: "toyota", displayName: "toyota", activeListingCount: 4381 },
        { value: "bmw", displayName: "bmw", activeListingCount: 2981 }
      ]
      const models = make === "toyota"
        ? [
            { value: "corolla", displayName: "corolla", activeListingCount: 842 },
            { value: "camry", displayName: "camry", activeListingCount: 612 }
          ]
        : []
      const trims = make === "toyota" && model === "corolla"
        ? [{ value: "xli", displayName: "xli", activeListingCount: 214 }]
        : []
      const years = make === "toyota" && model === "corolla" && trim === "xli"
        ? [{ value: 2023, displayName: "2023", activeListingCount: 57 }]
        : []
      return HttpResponse.json({
        filters: { make: make ?? undefined, model: model ?? undefined, trim: trim ?? undefined, year: undefined },
        options: { makes, models, trims, years },
        freshness: { lastUpdated: "2026-07-05T08:00:00.000Z", datasetVersion: "canonical-2024.05", scrapeRunId: 1042 },
        generatedAt: "2026-07-05T12:30:00.000Z"
      })
    })
  ]
}

function renderDashboard() {
  const client = new QueryClient({
    defaultOptions: { queries: { retry: false, gcTime: 0, staleTime: 0 } }
  })
  return render(
    <QueryClientProvider client={client}>
      <DashboardShell />
    </QueryClientProvider>
  )
}

beforeEach(() => {
  resetSearch("")
  server.use(...marketHandlers())
})

describe("Market dashboard cascading filters (US2 / T048)", () => {
  it("renders the overall snapshot and populates the make filter from filter-options", async () => {
    renderDashboard()
    await waitFor(() =>
      expect(screen.getByRole("heading", { level: 1 })).toHaveTextContent("Overall UAE Used Cars")
    )
    await waitFor(() => expect(makeOptions("make")).toEqual(expect.arrayContaining(["toyota (4,381)", "bmw (2,981)"])))
    // Lower-level selects start disabled (no higher-level selection).
    expect((document.querySelector('select[name="model"]') as HTMLSelectElement).disabled).toBe(true)
    expect((document.querySelector('select[name="trim"]') as HTMLSelectElement).disabled).toBe(true)
    expect((document.querySelector('select[name="year"]') as HTMLSelectElement).disabled).toBe(true)
  })

  it("limits model options to the selected make and keeps deeper selects disabled", async () => {
    resetSearch("make=toyota")
    renderDashboard()
    await waitFor(() => expect(makeOptions("model")).toEqual(expect.arrayContaining(["corolla (842)", "camry (612)"])))
    // No sibling-make model leaks into the model select.
    expect(makeOptions("model")).not.toContain(expect.stringContaining("altima"))
    // Trim and year stay disabled until model (and trim) are selected.
    expect((document.querySelector('select[name="trim"]') as HTMLSelectElement).disabled).toBe(true)
    expect((document.querySelector('select[name="year"]') as HTMLSelectElement).disabled).toBe(true)
    // Snapshot updated for the make scope without a full page reload.
    await waitFor(() =>
      expect(screen.getByRole("heading", { level: 1 })).toHaveTextContent("toyota")
    )
  })

  it("clears lower-level selections and refetches the snapshot when the make changes", async () => {
    resetSearch("make=toyota&model=corolla")
    renderDashboard()
    await waitFor(() => expect(screen.getByRole("heading", { level: 1 })).toHaveTextContent("toyota corolla"))
    // Wait for the make select to be populated, then change it to bmw.
    await waitFor(() => expect(makeOptions("make")).toContain("bmw (2,981)"))
    selectOption("make", "bmw")

    // URL updated client-side with make=bmw and model removed (no full reload).
    await waitFor(() => expect(replaceCalls.some((u) => u.includes("make=bmw"))).toBe(true))
    expect(replaceCalls.at(-1)).not.toMatch(/model=/)
    // Snapshot refetches for the bmw scope in place (same heading element updates).
    await waitFor(() => expect(screen.getByRole("heading", { level: 1 })).toHaveTextContent("bmw"))
    // Model select value reset to "All models".
    expect((document.querySelector('select[name="model"]') as HTMLSelectElement).value).toBe("")
  })

  it("cascades through trim and year and updates the scope label", async () => {
    resetSearch("make=toyota&model=corolla&trim=xli")
    renderDashboard()
    await waitFor(() => expect(makeOptions("year")).toEqual(["All years", "2023 (57)"]))
    // Year select is enabled now that make+model+trim are selected.
    expect((document.querySelector('select[name="year"]') as HTMLSelectElement).disabled).toBe(false)

    selectOption("year", "2023")
    await waitFor(() =>
      expect(screen.getByRole("heading", { level: 1 })).toHaveTextContent("toyota corolla xli 2023")
    )
    expect(replaceCalls.some((u) => u.includes("year=2023"))).toBe(true)
  })

  it("updates filters via client-side router.replace without a full page reload", async () => {
    renderDashboard()
    await waitFor(() => expect(screen.getByRole("heading", { level: 1 })).toHaveTextContent("Overall UAE Used Cars"))
    await waitFor(() => expect(makeOptions("make")).toContain("toyota (4,381)"))
    selectOption("make", "toyota")
    // router.replace was used (not window.location), so the SPA stays mounted and the
    // heading element is reused for the new scope label.
    await waitFor(() => expect(replaceCalls.some((u) => /\/market\?make=toyota/.test(u))).toBe(true))
    await waitFor(() => expect(screen.getByRole("heading", { level: 1 })).toHaveTextContent("toyota"))
  })
})
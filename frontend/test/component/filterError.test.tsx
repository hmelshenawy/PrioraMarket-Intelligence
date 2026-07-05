import { describe, expect, it, vi, beforeEach, afterEach } from "vitest"
import { render, screen, waitFor } from "@testing-library/react"
import { http, HttpResponse } from "msw"
import { QueryClient, QueryClientProvider } from "@tanstack/react-query"
import { SearchExperience } from "@/features/search/components/SearchExperience"
import { server } from "@/test/mocks/server"

const BASE = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:3000"

let currentSearch = ""

vi.mock("next/navigation", () => ({
  usePathname: () => "/",
  useRouter: () => ({
    push: (url: string) => {
      const idx = url.indexOf("?")
      currentSearch = idx >= 0 ? url.slice(idx + 1) : ""
    },
    replace: (url: string) => {
      const idx = url.indexOf("?")
      currentSearch = idx >= 0 ? url.slice(idx + 1) : ""
    },
  }),
  useSearchParams: () => new URLSearchParams(currentSearch),
}))

function renderSearch() {
  const client = new QueryClient({
    defaultOptions: { queries: { retry: false, gcTime: 0, staleTime: 0 } },
  })
  return render(
    <QueryClientProvider client={client}>
      <SearchExperience />
    </QueryClientProvider>,
  )
}

describe("Filter scoped error state", () => {
  beforeEach(() => {
    currentSearch = ""
    server.use(
      http.get(`${BASE}/api/v1/listings/filters`, () =>
        HttpResponse.json({ statusCode: 500, error: "Server Error", message: "down" }, { status: 500 }),
      ),
    )
  })
  afterEach(() => server.resetHandlers())

  it("shows the scoped filter error while keeping search usable", async () => {
    renderSearch()
    // Filter metadata failed → scoped error alert appears.
    await waitFor(() => expect(screen.getByText(/Filters unavailable/i)).toBeInTheDocument())
    // Search results still load and render a listing.
    await waitFor(() => expect(screen.getByText("2021 Toyota Camry SE")).toBeInTheDocument())
  })
})
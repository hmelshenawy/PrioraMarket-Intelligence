import { describe, expect, it, vi, beforeEach } from "vitest"
import { render, screen, waitFor, fireEvent } from "@testing-library/react"
import { QueryClient, QueryClientProvider } from "@tanstack/react-query"
import { SearchExperience } from "@/features/search/components/SearchExperience"

// In-memory URL state for the next/navigation mock. Tests set `currentSearch`
// before rendering to seed the initial URL state.
let currentSearch = ""
const pushCalls: string[] = []

vi.mock("next/navigation", () => ({
  usePathname: () => "/",
  useRouter: () => ({
    push: (url: string) => {
      pushCalls.push(url)
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

beforeEach(() => {
  currentSearch = ""
  pushCalls.length = 0
})

describe("SearchExperience integration", () => {
  it("renders listings from the search endpoint on initial load", async () => {
    renderSearch()
    await waitFor(() => expect(screen.getByText(/2 results/i)).toBeInTheDocument())
    // At least one listing title from the fixture renders.
    expect(screen.getByText("2021 Toyota Camry SE")).toBeInTheDocument()
  })

  it("renders the empty state when the backend returns no results", async () => {
    currentSearch = "q=empty"
    renderSearch()
    await waitFor(() => expect(screen.getByText(/No listings found/i)).toBeInTheDocument())
  })

  it("renders the error state when the backend returns a 400", async () => {
    currentSearch = "q=fail"
    renderSearch()
    await waitFor(() => expect(screen.getByRole("alert")).toBeInTheDocument())
    expect(screen.getByText(/Couldn't load listings/i)).toBeInTheDocument()
  })

  it("pushes a URL update when the sort control changes", async () => {
    const { container } = renderSearch()
    await waitFor(() => expect(screen.getByText(/2 results/i)).toBeInTheDocument())
    const sortSelect = container.querySelector('select[name="sort"]') as HTMLSelectElement
    expect(sortSelect).toBeTruthy()
    fireEvent.change(sortSelect, { target: { value: "price_asc" } })
    await waitFor(() => expect(pushCalls.some((u) => u.includes("sort=price_asc"))).toBe(true))
  })
})
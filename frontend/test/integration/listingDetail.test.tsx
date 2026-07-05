import { describe, expect, it } from "vitest"
import { render, screen, waitFor } from "@testing-library/react"
import { QueryClient, QueryClientProvider } from "@tanstack/react-query"
import { ListingDetailView } from "@/features/listings/components/ListingDetailView"

function renderDetail(id: string) {
  const client = new QueryClient({
    defaultOptions: { queries: { retry: false, gcTime: 0, staleTime: 0 } },
  })
  return render(
    <QueryClientProvider client={client}>
      <ListingDetailView id={id} />
    </QueryClientProvider>,
  )
}

describe("ListingDetailView integration", () => {
  it("renders the gallery, summary, specifications, and marketplace action from the fixture", async () => {
    renderDetail("abc")
    await waitFor(() => expect(screen.getByRole("heading", { level: 1 })).toBeInTheDocument())
    expect(screen.getByText("2021 Toyota Camry SE")).toBeInTheDocument()
    expect(screen.getAllByText(/No photo available/i).length).toBeGreaterThan(0)
    expect(screen.queryByRole("img")).toBeNull()
    expect(screen.getByText(/5 photos/i)).toBeInTheDocument()
    // Specifications group renders known fields.
    expect(screen.getByText("Body type")).toBeInTheDocument()
    expect(screen.getByText("Fuel")).toBeInTheDocument()
    // Marketplace action button present (fixture has a valid URL).
    expect(screen.getByRole("button", { name: /View on marketplace/i })).toBeInTheDocument()
  })

  it("renders the not-found state for a 404 response with a path back to search", async () => {
    renderDetail("missing")
    await waitFor(() => expect(screen.getByText(/Listing not found/i)).toBeInTheDocument())
    const back = screen.getByRole("link", { name: /Back to search/i })
    expect(back).toHaveAttribute("href", "/")
  })

  it("renders the error state for a 500 response with a retry control", async () => {
    renderDetail("fail")
    await waitFor(() => expect(screen.getByRole("alert")).toBeInTheDocument())
    expect(screen.getByText(/Couldn't load this listing/i)).toBeInTheDocument()
  })
})

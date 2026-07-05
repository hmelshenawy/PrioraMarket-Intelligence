import { describe, expect, it, vi } from "vitest"
import { render, screen } from "@testing-library/react"
import { ResultsGrid } from "@/features/search/components/ResultsGrid"
import { mapListingCard } from "@/features/listings/mappers/listingCardMapper"
import { listingResultFactory } from "@/test/mocks/fixtures"
import type { ApiError } from "@/lib/api/types"

const sampleItems = () => [mapListingCard(listingResultFactory({ id: "1" }))]

describe("ResultsGrid states", () => {
  it("renders skeletons while loading with no data", () => {
    render(<ResultsGrid data={undefined} isLoading={true} error={null} />)
    // ListingCardSkeleton renders an aria-hidden skeleton block; grid has 6.
    const skeletons = document.querySelectorAll(".animate-pulse")
    expect(skeletons.length).toBeGreaterThan(0)
  })

  it("renders the empty state when data is empty", () => {
    render(
      <ResultsGrid
        data={{ items: [], page: 1, limit: 20, total: 0, totalPages: 0, isEmpty: true }}
        isLoading={false}
        error={null}
      />,
    )
    expect(screen.getByText(/No listings found/i)).toBeInTheDocument()
  })

  it("renders the error state with retry when an error is present", () => {
    const error: ApiError = { category: "serverError", status: 500, message: "Boom." }
    const onRetry = vi.fn()
    render(<ResultsGrid data={undefined} isLoading={false} error={error} onRetry={onRetry} />)
    expect(screen.getByRole("alert")).toBeInTheDocument()
    expect(screen.getByText(/Couldn't load listings/i)).toBeInTheDocument()
    expect(screen.getByText("Boom.")).toBeInTheDocument()
  })

  it("renders listing cards when data is present", () => {
    render(
      <ResultsGrid
        data={{
          items: sampleItems(),
          page: 1,
          limit: 20,
          total: 1,
          totalPages: 1,
          isEmpty: false,
        }}
        isLoading={false}
        error={null}
      />,
    )
    expect(screen.getByRole("link", { name: /View details for/i })).toBeInTheDocument()
  })
})
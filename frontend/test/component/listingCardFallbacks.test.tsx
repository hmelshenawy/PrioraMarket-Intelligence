import { describe, expect, it } from "vitest"
import { render, screen } from "@testing-library/react"
import { ListingCard } from "@/features/listings/components/ListingCard"
import { mapListingCard } from "@/features/listings/mappers/listingCardMapper"
import { listingResultFactory } from "@/test/mocks/fixtures"

describe("ListingCard fallbacks", () => {
  it("does not render the marketplace link when no valid external URL exists", () => {
    const item = mapListingCard(listingResultFactory({ url: null }))
    render(<ListingCard item={item} />)
    expect(screen.queryByText(/View on marketplace/i)).toBeNull()
  })

  it("does not render a photos badge when photosCount is null or zero", () => {
    const item = mapListingCard(listingResultFactory({ photosCount: null }))
    render(<ListingCard item={item} />)
    expect(screen.queryByText(/^\d+ photos?$/i)).toBeNull()
  })

  it("uses placeholder labels instead of misleading data for missing optional fields", () => {
    const item = mapListingCard(
      listingResultFactory({
        title: null,
        make: null,
        model: null,
        trim: null,
        year: null,
        priceAed: null,
        km: null,
        condition: null,
        location: null,
        sellerType: null,
        url: null,
        photosCount: null,
      }),
    )
    render(<ListingCard item={item} />)
    expect(screen.getByText("Untitled listing")).toBeInTheDocument()
    // Price fallback must not show a fabricated number.
    expect(screen.getByText(/Price not available/i)).toBeInTheDocument()
    // No condition badge renders when condition is the placeholder.
    expect(screen.queryByText(/^used$/i)).toBeNull()
  })

  it("renders an accessible no-photo message when no image is available", () => {
    const item = mapListingCard(listingResultFactory())
    render(<ListingCard item={item} />)
    expect(screen.getByText(/No photo available/i)).toBeInTheDocument()
    expect(screen.queryByRole("img")).toBeNull()
  })
})

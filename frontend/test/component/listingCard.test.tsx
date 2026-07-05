import { describe, expect, it } from "vitest"
import { render, screen } from "@testing-library/react"
import { ListingCard } from "@/features/listings/components/ListingCard"
import { mapListingCard } from "@/features/listings/mappers/listingCardMapper"
import { listingResultFactory } from "@/test/mocks/fixtures"

describe("ListingCard", () => {
  it("renders title, price, mileage, year, location, and a detail link when all fields are present", () => {
    const item = mapListingCard(listingResultFactory())
    render(<ListingCard item={item} />)
    const link = screen.getByRole("link", { name: /View details for/i })
    expect(link).toHaveAttribute("href", item.href)
    expect(screen.getByText(item.title)).toBeInTheDocument()
    expect(screen.getByText(item.priceLabel)).toBeInTheDocument()
    expect(screen.getByText(item.locationLabel)).toBeInTheDocument()
    expect(screen.getByText("2021")).toBeInTheDocument()
    expect(screen.queryByRole("img")).toBeNull()
    expect(screen.getByText(/No photo available/i)).toBeInTheDocument()
  })

  it("shows the marketplace link when a valid external URL exists", () => {
    const item = mapListingCard(listingResultFactory())
    const { container } = render(<ListingCard item={item} />)
    const marketplace = screen.getByRole("link", { name: /View on marketplace/i })
    expect(marketplace).toHaveAttribute("href", item.externalUrl!)
    expect(marketplace).toHaveAttribute("target", "_blank")
    expect(marketplace).toHaveAttribute("rel", "noopener noreferrer")
    expect(screen.getByRole("link", { name: /View details for/i })).toHaveAttribute("href", item.href)
    expect(container.querySelectorAll("a a")).toHaveLength(0)
  })

  it("surfaces photosCount as metadata when greater than zero", () => {
    const item = mapListingCard(listingResultFactory({ photosCount: 3 }))
    render(<ListingCard item={item} />)
    expect(screen.getByText(/3 photos/i)).toBeInTheDocument()
    expect(screen.queryByRole("img")).toBeNull()
  })
})

import { describe, expect, it } from "vitest"
import { mapListingCard } from "@/features/listings/mappers/listingCardMapper"
import type { ListingSearchResultDto } from "@/features/listings/types"

const fullDto: ListingSearchResultDto = {
  id: "abc",
  externalId: "ext-1",
  title: "  2021 Toyota Camry SE  ",
  make: "Toyota",
  model: "Camry",
  trim: "SE",
  year: 2021,
  priceAed: 95000,
  km: 42000,
  condition: "used",
  location: "Dubai",
  sellerType: "dealer",
  url: "https://market.example/listing/abc",
  photosCount: 5,
  firstSeenAt: "2024-01-10T08:00:00.000Z",
  lastSeenAt: "2024-07-01T08:00:00.000Z",
}

describe("mapListingCard", () => {
  it("formats currency, mileage, and year from a full DTO", () => {
    const card = mapListingCard(fullDto)
    expect(card.title).toBe("2021 Toyota Camry SE")
    expect(card.priceLabel).toContain("95,000")
    expect(card.kmLabel).toContain("42,000")
    expect(card.yearLabel).toBe("2021")
    expect(card.locationLabel).toBe("Dubai")
  })

  it("builds a subtitle from make/model/trim", () => {
    expect(mapListingCard(fullDto).subtitle).toBe("Toyota Camry SE")
  })

  it("validates external URL and drops non-http(s) links", () => {
    expect(mapListingCard(fullDto).externalUrl).toBe("https://market.example/listing/abc")
    expect(mapListingCard({ ...fullDto, url: "javascript:alert(1)" }).externalUrl).toBeNull()
    expect(mapListingCard({ ...fullDto, url: "not-a-url" }).externalUrl).toBeNull()
    expect(mapListingCard({ ...fullDto, url: null }).externalUrl).toBeNull()
  })

  it("derives a title from year/make/model when title is missing", () => {
    const card = mapListingCard({ ...fullDto, title: null })
    expect(card.title).toBe("2021 Toyota Camry")
  })

  it("falls back to placeholder labels for missing optional fields", () => {
    const sparse = mapListingCard({
      ...fullDto,
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
      firstSeenAt: null,
      lastSeenAt: null,
    })
    expect(sparse.title).toBe("Untitled listing")
    expect(sparse.subtitle).toBe("")
    expect(sparse.priceLabel).toMatch(/not available/i)
    expect(sparse.kmLabel).toMatch(/not available/i)
    expect(sparse.yearLabel).toBe("—")
    expect(sparse.conditionLabel).toBe("—")
    expect(sparse.locationLabel).toMatch(/not available/i)
    expect(sparse.externalUrl).toBeNull()
  })

  it("encodes the id into the detail href", () => {
    expect(mapListingCard({ ...fullDto, id: "a b/c" }).href).toBe("/listings/a%20b%2Fc")
  })
})
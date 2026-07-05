import { describe, expect, it } from "vitest"
import { mapListingDetail } from "@/features/listings/mappers/listingDetailMapper"
import type { ListingDetailDto } from "@/features/listings/types"
import { listingDetailFixture } from "@/test/mocks/fixtures"

describe("mapListingDetail", () => {
  it("groups known fields into specifications and formats summary values", () => {
    const model = mapListingDetail(listingDetailFixture as ListingDetailDto)
    expect(model.title).toBe("2021 Toyota Camry SE")
    expect(model.summary.priceLabel).toContain("95,000")
    expect(model.summary.yearLabel).toBe("2021")
    expect(model.summary.kmLabel).toContain("42,000")
    expect(model.gallery).toEqual({ photosCount: 5 })
    const labels = model.specifications.map((r) => r.label)
    expect(labels).toEqual(["Body type", "Fuel", "Transmission", "Color"])
  })

  it("surfaces unknown specs keys as additional specifications", () => {
    const model = mapListingDetail({
      ...listingDetailFixture,
      specs: { doors: 4, cylinders: 4, roofType: "sunroof" },
    } as ListingDetailDto)
    const additional = model.additionalSpecs.map((r) => r.label)
    expect(additional).toEqual(["Doors", "Cylinders", "Roof Type"])
  })

  it("omits empty specs entries from additional specifications", () => {
    const model = mapListingDetail({
      ...listingDetailFixture,
      specs: { doors: 4, empty: null, blank: "" },
    } as ListingDetailDto)
    const additional = model.additionalSpecs.map((r) => r.label)
    expect(additional).toEqual(["Doors"])
  })

  it("uses fallbacks for missing identity and optional fields", () => {
    const sparse = mapListingDetail({
      ...listingDetailFixture,
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
      bodyType: null,
      fuel: null,
      transmission: null,
      color: null,
      specs: null,
      url: null,
    } as unknown as ListingDetailDto)
    expect(sparse.title).toBe("Untitled listing")
    expect(sparse.specifications).toEqual([])
    expect(sparse.additionalSpecs).toEqual([])
    expect(sparse.summary.priceLabel).toMatch(/not available/i)
    expect(sparse.marketplaceAction.url).toBeNull()
  })

  it("validates the marketplace URL and drops non-http(s) links", () => {
    expect(
      mapListingDetail({ ...listingDetailFixture, url: "https://m.example/x" } as ListingDetailDto)
        .marketplaceAction.url,
    ).toBe("https://m.example/x")
    expect(
      mapListingDetail({ ...listingDetailFixture, url: "javascript:alert(1)" } as ListingDetailDto)
        .marketplaceAction.url,
    ).toBeNull()
  })

  it("encodes the id into the href", () => {
    expect(
      mapListingDetail({ ...listingDetailFixture, id: "a b/c" } as ListingDetailDto).href,
    ).toBe("/listings/a%20b%2Fc")
  })
})

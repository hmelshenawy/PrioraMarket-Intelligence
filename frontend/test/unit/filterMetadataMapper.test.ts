import { describe, expect, it } from "vitest"
import { mapFilterMetadata } from "@/features/filters/mappers/filterMetadataMapper"
import type { FilterMetadataDto } from "@/features/filters/types"

const dto: FilterMetadataDto = {
  makes: ["Toyota", "Nissan"],
  models: { Toyota: ["Camry", "Corolla"], Nissan: ["Altima", "Patrol"] },
  price: { min: 30000, max: 250000 },
  year: { min: 2010, max: 2024 },
  km: { min: 0, max: 200000 },
  conditions: ["used", "new"],
  sellerTypes: ["dealer", "private"],
}

describe("mapFilterMetadata", () => {
  it("converts makes and models into labeled options grouped by make", () => {
    const model = mapFilterMetadata(dto)
    expect(model.makes.map((m) => m.value)).toEqual(["Toyota", "Nissan"])
    expect(model.modelsByMake["Toyota"].map((m) => m.value)).toEqual(["Camry", "Corolla"])
  })

  it("humanizes condition and sellerType values for display", () => {
    const model = mapFilterMetadata(dto)
    expect(model.conditions).toEqual([
      { value: "used", label: "Used" },
      { value: "new", label: "New" },
    ])
    expect(model.sellerTypes.map((s) => s.label)).toEqual(["Dealer", "Private"])
  })

  it("passes numeric ranges through unchanged (null bounds kept)", () => {
    const model = mapFilterMetadata({ ...dto, price: { min: null, max: null } })
    expect(model.price).toEqual({ min: null, max: null })
    expect(model.year).toEqual(dto.year)
  })

  it("builds a deduplicated model fallback list across makes", () => {
    const model = mapFilterMetadata({
      ...dto,
      models: { Toyota: ["Camry"], Nissan: ["Camry", "Altima"] },
    })
    expect(model.modelFallback.map((m) => m.value)).toEqual(["Camry", "Altima"])
  })
})
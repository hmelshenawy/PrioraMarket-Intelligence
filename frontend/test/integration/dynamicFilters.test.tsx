import { describe, expect, it, vi } from "vitest"
import { render, fireEvent } from "@testing-library/react"
import { FilterSidebar } from "@/features/search/components/FilterSidebar"
import { mapFilterMetadata } from "@/features/filters/mappers/filterMetadataMapper"
import { filterMetadataFixture } from "@/test/mocks/fixtures"
import { defaultSearchState } from "@/lib/routing/searchState"
import type { SearchUrlState } from "@/lib/routing/searchState"

const metadata = mapFilterMetadata(filterMetadataFixture)

function optionsOf(name: string): string[] {
  const sel = document.querySelector(`select[name="${name}"]`) as HTMLSelectElement
  return Array.from(sel.options).map((o) => o.value)
}

describe("FilterSidebar dynamic metadata", () => {
  it("populates the make select from dynamic metadata", () => {
    render(
      <FilterSidebar
        state={defaultSearchState}
        onFilterChange={vi.fn()}
        onClear={vi.fn()}
        hasActiveFilters={false}
        metadata={metadata}
      />,
    )
    const makes = optionsOf("make")
    expect(makes).toContain("Toyota")
    expect(makes).toContain("Nissan")
  })

  it("limits model options to the selected make", () => {
    render(
      <FilterSidebar
        state={{ ...defaultSearchState, make: "Toyota" }}
        onFilterChange={vi.fn()}
        onClear={vi.fn()}
        hasActiveFilters={false}
        metadata={metadata}
      />,
    )
    const models = optionsOf("model")
    expect(models).toContain("Camry")
    expect(models).toContain("Corolla")
    expect(models).not.toContain("Altima")
  })

  it("emits a make change and clears the model via onFilterChange", () => {
    const onFilterChange = vi.fn()
    render(
      <FilterSidebar
        state={defaultSearchState}
        onFilterChange={onFilterChange}
        onClear={vi.fn()}
        hasActiveFilters={false}
        metadata={metadata}
      />,
    )
    const makeSelect = document.querySelector('select[name="make"]') as HTMLSelectElement
    fireEvent.change(makeSelect, { target: { value: "Nissan" } })
    // The make change pushes a single combined patch: set make and clear model.
    expect(onFilterChange).toHaveBeenCalledWith({ make: "Nissan", model: undefined })
  })

  it("clears the inverted bound when a range min exceeds its max", () => {
    const onFilterChange = vi.fn()
    render(
      <FilterSidebar
        state={{ ...defaultSearchState, priceMax: 100 }}
        onFilterChange={onFilterChange}
        onClear={vi.fn()}
        hasActiveFilters={true}
        metadata={metadata}
      />,
    )
    const priceMinInput = document.querySelector('input[name="priceMin"]') as HTMLInputElement
    fireEvent.change(priceMinInput, { target: { value: "500" } })
    const last = onFilterChange.mock.calls.at(-1)?.[0] as Partial<SearchUrlState>
    // The patch clears priceMax because 500 > 100.
    expect(last.priceMin).toBe(500)
    expect(last.priceMax).toBeUndefined()
  })
})
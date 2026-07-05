"use client"

import { useForm, useWatch } from "react-hook-form"
import { FilterX } from "lucide-react"
import { SearchInput } from "@/components/ui/SearchInput"
import { Select, type SelectOption } from "@/components/ui/Select"
import { Button } from "@/components/ui/Button"
import { sortOptions, type SortOption } from "@/lib/validation/searchStateSchema"
import { sortLabels } from "@/lib/constants/sort"
import type { SearchUrlState } from "@/lib/routing/searchState"

interface SortFormValues {
  sort: SortOption
}

export interface SearchToolbarProps {
  state: SearchUrlState
  onQChange: (value: string) => void
  onSortChange: (sort: SortOption) => void
  onClear: () => void
  hasActiveFilters: boolean
  resultsCount?: number
}

// SearchToolbar — top-of-page search controls.
// Text search uses the debounced design-system SearchInput; sort is a temporary
// form value managed by React Hook Form that syncs to the URL on change.
// Clear Filters resets the whole search state.
export function SearchToolbar({
  state,
  onQChange,
  onSortChange,
  onClear,
  hasActiveFilters,
  resultsCount,
}: SearchToolbarProps) {
  const { control, setValue } = useForm<SortFormValues>({
    defaultValues: { sort: state.sort },
  })

  // Re-seed sort from URL on Back/Forward navigation. RHF holds the temporary
  // form value; the URL remains the source of truth.
  const currentSort = useWatch({ control, name: "sort" })
  if (currentSort !== state.sort) {
    setValue("sort", state.sort, { shouldDirty: false })
  }

  const sortOptionsList: SelectOption[] = sortOptions.map((value) => ({
    value,
    label: sortLabels[value],
  }))

  return (
    <div className="flex flex-col gap-3">
      <div className="flex flex-col gap-3 sm:flex-row sm:items-end sm:justify-between">
        <div className="w-full max-w-xl">
          <SearchInput
            initialValue={state.q ?? ""}
            ariaLabel="Search listings by make, model, or keyword"
            onDebouncedChange={onQChange}
          />
        </div>
        <div className="flex items-end gap-2">
          <div className="w-44">
            <Select
              label="Sort by"
              name="sort"
              options={sortOptionsList}
              value={state.sort}
              onValueChange={(value) => {
                setValue("sort", value as SortOption)
                onSortChange(value as SortOption)
              }}
            />
          </div>
          {hasActiveFilters && (
            <Button type="button" variant="ghost" onClick={onClear} className="whitespace-nowrap">
              <FilterX aria-hidden className="h-4 w-4" />
              Clear filters
            </Button>
          )}
        </div>
      </div>
      {resultsCount != null && <p className="text-sm text-muted">{resultsCount} results</p>}
    </div>
  )
}
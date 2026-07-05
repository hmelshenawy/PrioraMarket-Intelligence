"use client"

import { useEffect } from "react"
import { useForm, useWatch } from "react-hook-form"
import { Select, type SelectOption } from "@/components/ui/Select"
import { RangeInput } from "@/components/ui/RangeInput"
import { Button } from "@/components/ui/Button"
import { Divider } from "@/components/ui/Divider"
import { Alert } from "@/components/ui/Alert"
import type { FilterMetadataModel, FilterOption } from "@/features/filters"
import type { ApiError } from "@/lib/api/types"
import type { SearchUrlState } from "@/lib/routing/searchState"
import { FilterSkeleton } from "./FilterSkeleton"

// Static fallback options used before metadata loads or when metadata fails
// (keeps search usable per the scoped-error policy).
const STATIC_MAKES: SelectOption[] = [
  { value: "Toyota", label: "Toyota" },
  { value: "Nissan", label: "Nissan" },
  { value: "Honda", label: "Honda" },
  { value: "Mercedes-Benz", label: "Mercedes-Benz" },
]
const STATIC_MODELS: SelectOption[] = [
  { value: "Camry", label: "Camry" },
  { value: "Corolla", label: "Corolla" },
  { value: "Altima", label: "Altima" },
  { value: "Patrol", label: "Patrol" },
]
const STATIC_CONDITIONS: SelectOption[] = [
  { value: "used", label: "Used" },
  { value: "new", label: "New" },
]
const STATIC_SELLER_TYPES: SelectOption[] = [
  { value: "dealer", label: "Dealer" },
  { value: "private", label: "Private seller" },
]

interface FilterFormValues {
  make: string
  model: string
  condition: string
  sellerType: string
  priceMin: string
  priceMax: string
  kmMin: string
  kmMax: string
  yearFrom: string
  yearTo: string
}

const toStr = (v: number | string | undefined | null): string => (v == null ? "" : String(v))
const toNum = (v: string): number | undefined => (v.trim() === "" || !Number.isFinite(Number(v)) ? undefined : Number(v))
const opts = (list: FilterOption[] | undefined, fallback: SelectOption[]): SelectOption[] =>
  list && list.length > 0 ? list.map((o) => ({ value: o.value, label: o.label })) : fallback

const formValuesFromState = (s: SearchUrlState): FilterFormValues => ({
  make: toStr(s.make),
  model: toStr(s.model),
  condition: toStr(s.condition),
  sellerType: toStr(s.sellerType),
  priceMin: toStr(s.priceMin),
  priceMax: toStr(s.priceMax),
  kmMin: toStr(s.kmMin),
  kmMax: toStr(s.kmMax),
  yearFrom: toStr(s.yearFrom),
  yearTo: toStr(s.yearTo),
})

export interface FilterSidebarProps {
  state: SearchUrlState
  onFilterChange: (patch: Partial<SearchUrlState>) => void
  onClear: () => void
  hasActiveFilters: boolean
  metadata?: FilterMetadataModel
  metadataLoading?: boolean
  metadataError?: ApiError | null
  onRetryMetadata?: () => void
}

// FilterSidebar — filter controls wired to URL state via React Hook Form.
// Populated from dynamic metadata when available; falls back to static options
// while loading or when metadata fails so search stays usable.
export function FilterSidebar({
  state,
  onFilterChange,
  onClear,
  hasActiveFilters,
  metadata,
  metadataLoading,
  metadataError,
  onRetryMetadata,
}: FilterSidebarProps) {
  const { control, reset, setValue } = useForm<FilterFormValues>({
    defaultValues: formValuesFromState(state),
  })

  useEffect(() => {
    reset(formValuesFromState(state))
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [state])

  const values = useWatch({ control }) ?? formValuesFromState(state)

  // Dependent model options: limited by selected make when metadata provides them.
  const modelOptions: SelectOption[] = (() => {
    if (metadata && state.make) {
      const byMake = metadata.modelsByMake[state.make]
      if (byMake && byMake.length > 0) return byMake.map((o) => ({ value: o.value, label: o.label }))
    }
    return opts(metadata?.modelFallback, STATIC_MODELS)
  })()

  const makeOptions = opts(metadata?.makes, STATIC_MAKES)
  const conditionOptions = opts(metadata?.conditions, STATIC_CONDITIONS)
  const sellerTypeOptions = opts(metadata?.sellerTypes, STATIC_SELLER_TYPES)

  const patch = (field: keyof SearchUrlState, stringValue: string, numeric?: boolean) => {
    onFilterChange({ [field]: numeric ? toNum(stringValue) : stringValue || undefined } as Partial<SearchUrlState>)
  }

  // Range helpers: enforce min<=max before the URL update. If the new value would
  // invert the pair, clear the other bound so the user can re-enter it.
  const patchRangeMin = (
    field: keyof SearchUrlState,
    other: keyof SearchUrlState,
    otherValue: string | undefined,
    v: string,
  ) => {
    const p: Partial<SearchUrlState> = { [field]: toNum(v) } as Partial<SearchUrlState>
    if (otherValue && Number(v) > Number(otherValue)) p[other] = undefined
    onFilterChange(p)
  }
  const patchRangeMax = (
    field: keyof SearchUrlState,
    other: keyof SearchUrlState,
    otherValue: string | undefined,
    v: string,
  ) => {
    const p: Partial<SearchUrlState> = { [field]: toNum(v) } as Partial<SearchUrlState>
    if (otherValue && Number(v) < Number(otherValue)) p[other] = undefined
    onFilterChange(p)
  }

  const showSkeleton = metadataLoading && !metadata
  const showScopedError = metadataError && !metadata

  return (
    <form aria-label="Filter listings" className="flex flex-col gap-4" onSubmit={(e) => e.preventDefault()}>
      {showScopedError && (
        <Alert variant="warning" title="Filters unavailable">
          <p className="text-sm text-text">
            Filter options couldn’t load. You can still search; try reloading filters.
          </p>
          {onRetryMetadata && (
            <Button type="button" variant="ghost" size="sm" onClick={onRetryMetadata} className="mt-2">
              Reload filters
            </Button>
          )}
        </Alert>
      )}
      {showSkeleton ? (
        <FilterSkeleton />
      ) : (
        <>
          <Select
            label="Make"
            name="make"
            placeholder="Any make"
            options={makeOptions}
            value={values.make}
            onValueChange={(v) => {
              setValue("make", v)
              setValue("model", "")
              // Single combined patch: set the make and clear the model in one URL
              // push. Two separate pushes would race — the second push reads stale
              // state (stateRef not yet updated) and overwrite the make change.
              onFilterChange({ make: v || undefined, model: undefined })
            }}
          />
          <Select
            label="Model"
            name="model"
            placeholder="Any model"
            options={modelOptions}
            value={values.model}
            onValueChange={(v) => {
              setValue("model", v)
              patch("model", v)
            }}
          />
          <Select
            label="Condition"
            name="condition"
            placeholder="Any condition"
            options={conditionOptions}
            value={values.condition}
            onValueChange={(v) => {
              setValue("condition", v)
              patch("condition", v)
            }}
          />
          <Select
            label="Seller type"
            name="sellerType"
            placeholder="Any seller"
            options={sellerTypeOptions}
            value={values.sellerType}
            onValueChange={(v) => {
              setValue("sellerType", v)
              patch("sellerType", v)
            }}
          />
          <Divider />
          <RangeInput
            label="Price (AED)"
            name="price"
            min={values.priceMin}
            max={values.priceMax}
            onMinChange={(v) => {
              setValue("priceMin", v)
              patchRangeMin("priceMin", "priceMax", values.priceMax, v)
            }}
            onMaxChange={(v) => {
              setValue("priceMax", v)
              patchRangeMax("priceMax", "priceMin", values.priceMin, v)
            }}
          />
          <RangeInput
            label="Year"
            name="year"
            min={values.yearFrom}
            max={values.yearTo}
            onMinChange={(v) => {
              setValue("yearFrom", v)
              patchRangeMin("yearFrom", "yearTo", values.yearTo, v)
            }}
            onMaxChange={(v) => {
              setValue("yearTo", v)
              patchRangeMax("yearTo", "yearFrom", values.yearFrom, v)
            }}
          />
          <RangeInput
            label="Mileage (km)"
            name="km"
            min={values.kmMin}
            max={values.kmMax}
            onMinChange={(v) => {
              setValue("kmMin", v)
              patchRangeMin("kmMin", "kmMax", values.kmMax, v)
            }}
            onMaxChange={(v) => {
              setValue("kmMax", v)
              patchRangeMax("kmMax", "kmMin", values.kmMin, v)
            }}
          />
          {hasActiveFilters && (
            <Button type="button" variant="ghost" onClick={onClear} className="w-full">
              Clear all filters
            </Button>
          )}
        </>
      )}
    </form>
  )
}
"use client"

import { useFilterOptions } from "../hooks/use-filter-options"
import { formatCount } from "../utils/market-format"
import type { FilterOptionDto, MarketFilterSelectionDto } from "../types"

export interface MarketFilterBarProps {
  selection: MarketFilterSelectionDto
  /** Called with the next selection; deeper levels are cleared on higher-level change. */
  onSelectionChange: (next: MarketFilterSelectionDto) => void
}

const ALL = ""

/**
 * MarketFilterBar — cascading make/model/trim/year selects. Options come from the
 * filter-options endpoint via useFilterOptions; each option label shows the API
 * displayName plus its active-listing count ("Toyota (4,381)"). Lower-level selects are
 * disabled until their higher-level filters are chosen, and changing a higher-level
 * filter clears the deeper selections so the active scope stays valid. Presentation
 * only — no analytics, no hardcoded vehicle names, no canonical-value transformation.
 */
export function MarketFilterBar({ selection, onSelectionChange }: MarketFilterBarProps) {
  const { data, isLoading, isFetching } = useFilterOptions(selection)
  const options = data?.options
  const loadingMakes = isLoading && !options

  const canModel = Boolean(selection.make)
  const canTrim = Boolean(selection.make && selection.model)
  const canYear = Boolean(selection.make && selection.model && selection.trim)

  return (
    <div
      className="flex flex-col gap-3 sm:flex-row sm:flex-wrap"
      role="group"
      aria-label="Market filters"
    >
      <FilterSelect
        name="make"
        label="Make"
        value={selection.make ?? ALL}
        disabled={loadingMakes}
        placeholder="All makes"
        loading={loadingMakes}
        options={options?.makes ?? []}
        onChange={(v) => onSelectionChange({ make: v || undefined, model: undefined, trim: undefined, year: undefined })}
      />
      <FilterSelect
        name="model"
        label="Model"
        value={selection.model ?? ALL}
        disabled={!canModel || loadingMakes}
        placeholder="All models"
        loading={canModel && !options}
        options={options?.models ?? []}
        onChange={(v) => onSelectionChange({ ...selection, model: v || undefined, trim: undefined, year: undefined })}
      />
      <FilterSelect
        name="trim"
        label="Trim"
        value={selection.trim ?? ALL}
        disabled={!canTrim || loadingMakes}
        placeholder="All trims"
        loading={canTrim && !options}
        options={options?.trims ?? []}
        onChange={(v) => onSelectionChange({ ...selection, trim: v || undefined, year: undefined })}
      />
      <FilterSelect
        name="year"
        label="Year"
        value={selection.year != null ? String(selection.year) : ALL}
        disabled={!canYear || loadingMakes}
        placeholder="All years"
        loading={canYear && !options}
        options={options?.years ?? []}
        onChange={(v) => onSelectionChange({ ...selection, year: v ? Number(v) : undefined })}
      />
      {isFetching && options && (
        <span className="self-center text-xs text-muted" aria-live="polite">
          Refreshing…
        </span>
      )}
    </div>
  )
}

interface FilterSelectProps {
  name: string
  label: string
  value: string
  disabled: boolean
  placeholder: string
  loading: boolean
  options: FilterOptionDto[]
  onChange: (value: string) => void
}

function FilterSelect({ name, label, value, disabled, placeholder, loading, options, onChange }: FilterSelectProps) {
  return (
    <label className="flex flex-col gap-1 text-sm">
      <span className="text-muted">{label}</span>
      <select
        name={name}
        value={value}
        disabled={disabled}
        aria-label={label}
        onChange={(e) => onChange(e.target.value)}
        className="min-w-36 rounded-control border border-border bg-elevated px-3 py-2 text-text disabled:opacity-50"
      >
        <option value={ALL}>{loading ? "Loading…" : placeholder}</option>
        {options.map((o) => (
          <option key={String(o.value)} value={String(o.value)}>
            {optionLabel(o.displayName, o.activeListingCount)}
          </option>
        ))}
      </select>
    </label>
  )
}

function optionLabel(displayName: string, count: number | null | undefined): string {
  return count != null ? `${displayName} (${formatCount(count)})` : displayName
}
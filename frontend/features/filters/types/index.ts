// Filters feature types. DTOs mirror Feature 003 data-model.md.

export interface NumericRangeDto {
  min: number | null
  max: number | null
}

export interface FilterMetadataDto {
  makes: string[]
  models: Record<string, string[]>
  price: NumericRangeDto
  year: NumericRangeDto
  km: NumericRangeDto
  conditions: string[]
  sellerTypes: string[]
}

// UI option for categorical selects.
export interface FilterOption {
  value: string
  label: string
}

// Display-ready filter metadata model produced by the mapper.
export interface FilterMetadataModel {
  makes: FilterOption[]
  // Models grouped by make; a flat fallback list is provided for the no-make case.
  modelsByMake: Record<string, FilterOption[]>
  modelFallback: FilterOption[]
  price: NumericRangeDto
  year: NumericRangeDto
  km: NumericRangeDto
  conditions: FilterOption[]
  sellerTypes: FilterOption[]
}
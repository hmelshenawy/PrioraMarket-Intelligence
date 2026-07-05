export interface VehicleCatalogDisplayValues {
  makeKey: string
  makeDisplay: string
  modelKey: string
  modelDisplay: string
}

export interface ListingCatalogDisplayContract {
  make: string | null
  model: string | null
  makeDisplay?: string | null
  modelDisplay?: string | null
}

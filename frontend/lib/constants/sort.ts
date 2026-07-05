import { sortOptions, type SortOption } from "@/lib/validation/searchStateSchema"

export { sortOptions, type SortOption }

// UI labels for sort options; backend enum values stay aligned with Feature 003.
export const sortLabels: Record<SortOption, string> = {
  relevance: "Relevance",
  newest: "Newest",
  price_asc: "Price: Low to High",
  price_desc: "Price: High to Low",
  year_asc: "Year: Oldest",
  year_desc: "Year: Newest",
  km_asc: "Mileage: Low to High",
  km_desc: "Mileage: High to Low",
}
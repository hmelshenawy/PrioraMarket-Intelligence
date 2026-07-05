// Shared E2E mock helpers. Playwright `page.route` fulfills the five allowed
// Feature 003 endpoints with deterministic payloads so the E2E suites do not
// depend on a live backend. Shapes match data-model.md DTOs.
//
// The route pattern is a RegExp (not a glob) so it matches multi-segment API
// paths such as /api/v1/listings/filters and /api/v1/listings/:id — the glob
// `**/api/v1/*` would only match a single segment after /api/v1/.

import type { Page, Route } from "@playwright/test"

export const API = /\/api\/v1\//

export const listingFixture = (overrides: Record<string, unknown> = {}) => ({
  id: "listing-1",
  externalId: "ext-1",
  title: "2021 Toyota Camry SE",
  make: "Toyota",
  model: "Camry",
  trim: "SE",
  year: 2021,
  priceAed: 95000,
  km: 42000,
  condition: "used",
  location: "Dubai",
  sellerType: "dealer",
  url: "https://example-marketplace.example/listing/1",
  photosCount: 5,
  firstSeenAt: "2024-01-10T08:00:00.000Z",
  lastSeenAt: "2024-07-01T08:00:00.000Z",
  ...overrides,
})

export const searchFixture = {
  data: [
    listingFixture({ id: "1" }),
    listingFixture({ id: "2", title: "2020 Nissan Altima S", make: "Nissan", model: "Altima", priceAed: 70000 }),
  ],
  meta: { page: 1, limit: 20, total: 2, totalPages: 1 },
}

export const emptySearchFixture = { data: [], meta: { page: 1, limit: 20, total: 0, totalPages: 0 } }

export const filterMetadataFixture = {
  makes: ["Toyota", "Nissan"],
  models: { Toyota: ["Camry", "Corolla"], Nissan: ["Altima", "Patrol"] },
  price: { min: 30000, max: 250000 },
  year: { min: 2010, max: 2024 },
  km: { min: 0, max: 200000 },
  conditions: ["used", "new"],
  sellerTypes: ["dealer", "private"],
}

export const statsFixture = {
  totalListings: 1200,
  usedListings: 1000,
  newListings: 200,
  totalMakes: 12,
  totalModels: 40,
  averagePriceAed: 85000,
  minPriceAed: 30000,
  maxPriceAed: 250000,
  lastUpdatedAt: "2024-07-04T08:00:00.000Z",
}

export const detailFixture = {
  ...listingFixture(),
  marketplace: "example",
  bodyType: "Sedan",
  fuel: "Petrol",
  transmission: "Automatic",
  color: "White",
  specs: { doors: 4, cylinders: 4 },
  seller: "Example Motors",
  isVerified: true,
  isAgent: false,
  neighbourhood: "Al Quoz",
  firstSeenRunId: "run-1",
  lastSeenRunId: "run-2",
  canonicalHash: "hash-1",
}

interface Overrides {
  search?: { status?: number; json?: unknown }
  detail?: { status?: number; json?: unknown }
  filters?: { status?: number; json?: unknown }
  stats?: { status?: number; json?: unknown }
  health?: { status?: number; json?: unknown }
}

function isDetail(url: string): boolean {
  return /\/listings\/[^/]+$/.test(url) && !url.includes("/listings/filters")
}

function fulfill(route: Route, override: { status?: number; json?: unknown } | undefined, fallback: () => unknown) {
  if (override) {
    return route.fulfill({
      status: override.status ?? 200,
      json: override.json ?? fallback(),
    })
  }
  return route.fulfill({ json: fallback() })
}

// Install a single route handler covering all five endpoints, with optional
// per-endpoint overrides (status/json). A single handler avoids Playwright
// route-ordering ambiguity between overlapping patterns.
export async function mockApi(page: Page, overrides: Overrides = {}) {
  await page.route(API, async (route) => {
    const url = route.request().url()
    if (url.includes("/listings/filters")) return fulfill(route, overrides.filters, () => filterMetadataFixture)
    if (isDetail(url)) {
      if (overrides.detail) return fulfill(route, overrides.detail, () => detailFixture)
      const id = url.split("/listings/")[1]?.split("?")[0] ?? "listing-1"
      if (id === "missing") return route.fulfill({ status: 404, json: { statusCode: 404, error: "Not Found", message: "Listing not found", requestId: "r" } })
      return route.fulfill({ json: { ...detailFixture, id } })
    }
    if (url.includes("/listings")) return fulfill(route, overrides.search, () => searchFixture)
    if (url.includes("/stats")) return fulfill(route, overrides.stats, () => statsFixture)
    if (url.includes("/health")) return fulfill(route, overrides.health, () => ({ status: "ok" }))
    return route.fulfill({ status: 404 })
  })
}

// Default happy-path mocks (no overrides).
export const mockAll = (page: Page) => mockApi(page)
// Fixtures for the five allowed Feature 003 backend endpoints.
// Shapes match data-model.md DTOs. Used by MSW handlers and component tests.

export const listingResultFactory = (overrides: Partial<Record<string, unknown>> = {}) => ({
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
  url: "https://dubai.dubizzle.com/motors/used-cars/toyota/camry/1234567/",
  photosCount: 5,
  firstSeenAt: "2024-01-10T08:00:00.000Z",
  lastSeenAt: "2024-07-01T08:00:00.000Z",
  ...overrides,
})

export const searchSuccessFixture = {
  data: [
    listingResultFactory({ id: "1" }),
    listingResultFactory({ id: "2", title: "2020 Nissan Altima S", make: "Nissan", model: "Altima", priceAed: 70000 }),
  ],
  meta: { page: 1, limit: 20, total: 2, totalPages: 1 },
}

export const searchEmptyFixture = {
  data: [],
  meta: { page: 1, limit: 20, total: 0, totalPages: 0 },
}

export const listingDetailFixture = {
  ...listingResultFactory(),
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

export const healthOkFixture = { status: "ok" as const }

export const apiErrorFixture = (statusCode: number, message: string | string[]) => ({
  statusCode,
  error: statusCode === 404 ? "Not Found" : "Bad Request",
  message,
  requestId: "req-1",
})

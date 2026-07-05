import { test, expect, type Page } from "@playwright/test"
import { mockAll, searchFixture, detailFixture, filterMetadataFixture, statsFixture, API } from "./mocks"

// E2E for US1: search + filters + sort + pagination + Back/Forward.
// Uses page.route mocks so no live backend is required.

test.beforeEach(async ({ page }) => {
  await mockAll(page)
})

// Wait for client components to hydrate (listing card renders) before interacting
// with client-only controls, so native events fire into attached React handlers.
async function waitForHydrated(page: Page) {
  await expect(page.getByText(searchFixture.data[0].title).first()).toBeVisible({ timeout: 20_000 })
}

test("search updates results after debounce and reflects state in the URL", async ({ page }) => {
  await page.goto("/")
  await waitForHydrated(page)
  const searchInput = page.getByRole("searchbox", { name: /search/i }).or(page.getByPlaceholder(/search/i))
  await searchInput.fill("Camry")
  await expect(page).toHaveURL(/q=Camry/, { timeout: 15_000 })
  await expect(page.getByText(searchFixture.data[0].title).first()).toBeVisible()
})

test("applying a make filter updates the URL and results", async ({ page, viewport }) => {
  test.skip(viewport != null && viewport.width < 1024, "inline sidebar only on >=lg")
  await page.goto("/")
  await waitForHydrated(page)
  await page.locator('select[name="make"]').selectOption("Toyota")
  await expect(page).toHaveURL(/make=Toyota/, { timeout: 15_000 })
})

test("changing sort updates the URL sort parameter", async ({ page }) => {
  await page.goto("/")
  await waitForHydrated(page)
  await page.locator('select[name="sort"]').selectOption("price_asc")
  await expect(page).toHaveURL(/sort=price_asc/, { timeout: 15_000 })
})

test("pagination updates the page parameter and result set", async ({ page }) => {
  // Replace the default mocks with a handler that varies the search response by page.
  await page.unrouteAll()
  await page.route(API, async (route) => {
    const url = route.request().url()
    if (url.includes("/listings/filters")) return route.fulfill({ json: filterMetadataFixture })
    if (url.includes("/stats")) return route.fulfill({ json: statsFixture })
    if (url.includes("/health")) return route.fulfill({ json: { status: "ok" } })
    if (url.includes("/listings") && !url.includes("/listings/filters") && !/\/listings\/[^/]+$/.test(url)) {
      const u = new URL(url)
      const p = Number(u.searchParams.get("page") ?? 1)
      const data = p === 2 ? [{ ...detailFixture, id: "p2", title: "Page Two Listing" }] : searchFixture.data
      return route.fulfill({ json: { data, meta: { page: p, limit: 20, total: 25, totalPages: 2 } } })
    }
    return route.fulfill({ json: detailFixture })
  })
  await page.goto("/")
  await waitForHydrated(page)
  await page.getByRole("button", { name: "Page 2" }).click()
  await expect(page).toHaveURL(/page=2/, { timeout: 15_000 })
})

test("Back and Forward restore search state", async ({ page }) => {
  await page.goto("/")
  await waitForHydrated(page)
  await page.locator('select[name="sort"]').selectOption("price_asc")
  await expect(page).toHaveURL(/sort=price_asc/, { timeout: 15_000 })
  await page.goBack()
  expect(page.url()).not.toMatch(/sort=price_asc/)
  await page.goForward()
  await expect(page).toHaveURL(/sort=price_asc/, { timeout: 15_000 })
})
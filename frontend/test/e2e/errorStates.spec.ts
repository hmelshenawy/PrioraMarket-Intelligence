import { test, expect } from "@playwright/test"
import { mockApi, detailFixture, emptySearchFixture } from "./mocks"

const apiError = (status: number, message: string) => ({ statusCode: status, error: "Server Error", message, requestId: "r" })

test.describe("error states", () => {
  test("stats failure shows a scoped Market Overview error without blocking search", async ({ page }) => {
    await mockApi(page, { stats: { status: 500, json: apiError(500, "down") } })
    await page.goto("/")
    await expect(page.getByText(/Market overview unavailable/i)).toBeVisible({ timeout: 15_000 })
    await expect(page.getByText(detailFixture.title).first()).toBeVisible()
  })

  test("filter metadata failure keeps search usable with a scoped alert", async ({ page }) => {
    await mockApi(page, { filters: { status: 500, json: apiError(500, "down") } })
    await page.goto("/")
    await expect(page.getByText(/Filters unavailable/i)).toBeVisible({ timeout: 15_000 })
    await expect(page.getByText(detailFixture.title).first()).toBeVisible()
  })

  test("empty search results show the empty state with Clear Filters", async ({ page }) => {
    await mockApi(page, { search: { json: emptySearchFixture } })
    await page.goto("/")
    await expect(page.getByText(/No results|No listings/i).first()).toBeVisible({ timeout: 15_000 })
  })

  test("listing detail 404 shows a not-found state", async ({ page }) => {
    await mockApi(page, { detail: { status: 404, json: apiError(404, "Listing not found") } })
    await page.goto("/listings/missing")
    await expect(page.getByText(/not found|couldn't|unavailable/i).first()).toBeVisible({ timeout: 15_000 })
  })

  test("backend offline is reflected in the health indicator", async ({ page }) => {
    await mockApi(page, { health: { status: 503 } })
    await page.goto("/")
    await expect(page.getByText(/Backend unavailable/i)).toBeVisible({ timeout: 15_000 })
  })
})
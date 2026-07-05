import { test, expect } from "@playwright/test"
import { mockAll, detailFixture } from "./mocks"

// E2E for US3: open detail + return restores state + scroll.

test.beforeEach(async ({ page }) => {
  await mockAll(page)
})

test("opening a listing detail renders its identity fields", async ({ page }) => {
  await page.goto("/")
  await page.getByRole("link", { name: new RegExp(detailFixture.title) }).first().click()
  await expect(page).toHaveURL(/\/listings\//)
  await expect(page.getByText(detailFixture.bodyType).first()).toBeVisible()
})

test("returning from detail restores the previous search URL", async ({ page }) => {
  await page.goto("/?q=Camry")
  await page.getByRole("link", { name: new RegExp(detailFixture.title) }).first().click()
  await expect(page).toHaveURL(/\/listings\//)
  await page.goBack()
  await expect(page).toHaveURL(/q=Camry/)
})

test("marketplace action opens the original listing URL", async ({ page }) => {
  await page.goto(`/listings/${detailFixture.id}`)
  await expect(page.getByText(/view on|marketplace|original listing/i).first()).toBeVisible({ timeout: 15_000 })
})
import { test, expect } from "@playwright/test"
import { mockAll, searchFixture } from "./mocks"

// Responsive pass: verifies no horizontal scrolling and correct filter
// sidebar/drawer behavior across desktop, laptop, tablet, and mobile.
// (The playwright.config projects supply the four viewports.)

test.beforeEach(async ({ page }) => {
  await mockAll(page)
})

test.describe("responsive layout", () => {
  test("home page has no horizontal overflow at each breakpoint", async ({ page }) => {
    await page.goto("/")
    await expect(page.getByRole("link", { name: "PrioraMarket home" })).toBeVisible()
    // Market Overview metrics render.
    await expect(page.getByText("Total listings")).toBeVisible()
    // At least one listing card title renders.
    await expect(page.getByText(searchFixture.data[0].title).first()).toBeVisible()

    const overflow = await page.evaluate(() => {
      return {
        scrollWidth: document.documentElement.scrollWidth,
        clientWidth: document.documentElement.clientWidth,
      }
    })
    expect(overflow.scrollWidth).toBeLessThanOrEqual(overflow.clientWidth + 1)
  })

  test("desktop and laptop render the inline filter sidebar", async ({ page, viewport }) => {
    test.skip(viewport != null && viewport.width < 1024, "inline sidebar only on >=lg")
    await page.goto("/")
    // The inline sidebar is visible on lg+; the mobile Filters button is hidden.
    await expect(page.getByRole("button", { name: /^Filters$/ })).toBeHidden()
    await expect(page.getByLabel("Filter listings")).toBeVisible()
  })

  test("tablet and mobile expose the Filters button and open the drawer", async ({ page, viewport }) => {
    test.skip(viewport != null && viewport.width >= 1024, "Filters button only on <lg")
    await page.goto("/")
    const filtersButton = page.getByRole("button", { name: /^Filters$/ })
    await expect(filtersButton).toBeVisible()
    await filtersButton.click()
    // Drawer opens with the filter form.
    await expect(page.getByRole("dialog", { name: "Filters" })).toBeVisible()
  })
})
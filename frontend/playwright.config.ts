import { defineConfig, devices } from "@playwright/test"

// Playwright config: desktop/laptop/tablet/mobile viewports, E2E + responsive + error-state suites.
// Tests assume the Next dev server; CI can override with PLAYWRIGHT_BASE_URL.
export default defineConfig({
  testDir: "./test/e2e",
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: process.env.CI ? "github" : "list",
  timeout: 30_000,
  use: {
    baseURL: process.env.PLAYWRIGHT_BASE_URL ?? "http://localhost:3000",
    trace: "on-first-retry",
  },
  projects: [
    { name: "desktop", use: { ...devices["Desktop Chrome"], viewport: { width: 1280, height: 800 } } },
    { name: "laptop", use: { ...devices["Desktop Chrome"], viewport: { width: 1100, height: 700 } } },
    { name: "tablet", use: { ...devices["iPad Pro"], viewport: { width: 900, height: 1200 } } },
    { name: "mobile", use: { ...devices["iPhone 15"], viewport: { width: 390, height: 844 } } },
  ],
  webServer: process.env.CI
    ? undefined
    : {
        command: "npm run dev",
        url: "http://localhost:3000",
        reuseExistingServer: true,
        timeout: 120_000,
      },
})
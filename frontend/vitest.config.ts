import { defineConfig } from "vitest/config"
import react from "@vitejs/plugin-react"
import path from "node:path"

// Vitest configuration for unit/component/integration tests.
// Tests run in jsdom and resolve "@/..." to the frontend root.
export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      "@": path.resolve(__dirname),
    },
  },
  test: {
    environment: "jsdom",
    globals: true,
    setupFiles: ["./test/setup.ts"],
    include: ["test/unit/**/*.test.{ts,tsx}", "test/component/**/*.test.tsx", "test/integration/**/*.test.tsx"],
    exclude: ["test/e2e/**", "node_modules/**", ".next/**"],
    coverage: {
      reporter: ["text", "html"],
      exclude: ["test/**", "**/*.config.*", ".next/**", "playwright.config.ts"],
    },
  },
})
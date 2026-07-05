import "@testing-library/jest-dom/vitest"
import { afterEach, afterAll, beforeAll } from "vitest"
import { server } from "./mocks/server"

// MSW: start interception before tests and reset handlers between tests.
beforeAll(() => server.listen({ onUnhandledRequest: "warn" }))
afterEach(() => server.resetHandlers())
afterAll(() => server.close())

// jsdom does not implement matchMedia; ThemeProvider relies on it for system theme.
if (!window.matchMedia) {
  Object.defineProperty(window, "matchMedia", {
    writable: true,
    value: (query: string) => ({
      matches: false,
      media: query,
      onchange: null,
      addEventListener: () => {},
      removeEventListener: () => {},
      addListener: () => {},
      removeListener: () => {},
      dispatchEvent: () => false,
    }),
  })
}

// jsdom does not implement scrollTo.
if (!window.scrollTo) {
  Object.defineProperty(window, "scrollTo", {
    writable: true,
    value: () => {},
  })
}
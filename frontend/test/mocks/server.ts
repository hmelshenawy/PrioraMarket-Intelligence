import { setupServer } from "msw/node"
import { handlers } from "./handlers"

// MSW server for Vitest (node). Started/reset/closed in test/setup.ts.
export const server = setupServer(...handlers)
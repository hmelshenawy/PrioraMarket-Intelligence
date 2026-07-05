"use client"

import { useState } from "react"
import { QueryClient, QueryClientProvider } from "@tanstack/react-query"

// Read-only server-state defaults for Feature 004. No mutations.
function createQueryClient() {
  return new QueryClient({
    defaultOptions: {
      queries: {
        // Short retry for transient network failures only.
        retry: (failureCount, error) => {
          const category = (error as { category?: string })?.category
          if (category === "badRequest" || category === "notFound") return false
          return failureCount < 2
        },
        retryDelay: (attempt) => Math.min(1000 * 2 ** attempt, 8000),
        staleTime: 30_000,
        refetchOnWindowFocus: false,
      },
    },
  })
}

export function QueryProvider({ children }: { children: React.ReactNode }) {
  // Stable client for the session; created once on the client.
  const [client] = useState(() => createQueryClient())
  return <QueryClientProvider client={client}>{children}</QueryClientProvider>
}
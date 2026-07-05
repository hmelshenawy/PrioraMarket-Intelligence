"use client"

import { ThemeProvider } from "@/features/theme"
import { QueryProvider } from "@/lib/query/QueryProvider"

// Composed once near the app root. Generic, reusable, free of search-specific logic.
export function Providers({ children }: { children: React.ReactNode }) {
  return (
    <ThemeProvider>
      <QueryProvider>{children}</QueryProvider>
    </ThemeProvider>
  )
}
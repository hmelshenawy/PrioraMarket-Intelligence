"use client"

import Link from "next/link"
import { ThemeSwitcher } from "@/features/theme"
import { Container } from "./Container"
import { useBackendHealth } from "@/features/health"
import { StatusIndicator } from "@/components/ui/StatusIndicator"

// TopNav — reusable top navigation with logo, home link, theme switcher, health indicator,
// and reserved space for future navigation items. No feature-specific data fetching beyond
// reusable health/theme behavior.
export function TopNav() {
  const { state, label } = useBackendHealth()
  return (
    <header className="sticky top-0 z-nav border-b border-border bg-elevated/95 backdrop-blur">
      <Container>
        <nav className="flex h-16 items-center justify-between gap-4" aria-label="Main">
          <Link href="/" className="flex items-center gap-2 text-text hover:opacity-80" aria-label="PrioraMarket home">
            <span className="text-xl font-bold text-accent">PrioraMarket</span>
          </Link>
          <div className="flex items-center gap-3">
            <StatusIndicator state={state} label={label} />
            <ThemeSwitcher />
            {/* Reserved space for future navigation items */}
          </div>
        </nav>
      </Container>
    </header>
  )
}
"use client"

import { useState } from "react"
import dynamic from "next/dynamic"
import { SlidersHorizontal } from "lucide-react"
import { Button } from "@/components/ui/Button"
import { FilterSidebar } from "./FilterSidebar"
import type { FilterMetadataModel } from "@/features/filters"
import type { ApiError } from "@/lib/api/types"
import type { SearchUrlState } from "@/lib/routing/searchState"

// Lazy-load the Drawer (and its portal/focus-trap code) so it stays out of the
// initial bundle until the user opens mobile filters.
const Drawer = dynamic(() => import("@/components/ui/Drawer").then((m) => m.Drawer), {
  ssr: false,
})

export interface MobileFiltersProps {
  state: SearchUrlState
  onFilterChange: (patch: Partial<SearchUrlState>) => void
  onClear: () => void
  hasActiveFilters: boolean
  metadata?: FilterMetadataModel
  metadataLoading?: boolean
  metadataError?: ApiError | null
  onRetryMetadata?: () => void
}

// MobileFilters — a "Filters" trigger (mobile only) that opens a Drawer
// containing the FilterSidebar. Desktop renders the sidebar inline instead.
export function MobileFilters(props: MobileFiltersProps) {
  const [open, setOpen] = useState(false)
  return (
    <div className="lg:hidden">
      <Button type="button" variant="secondary" onClick={() => setOpen(true)}>
        <SlidersHorizontal aria-hidden className="h-4 w-4" />
        Filters
      </Button>
      <Drawer open={open} onClose={() => setOpen(false)} title="Filters">
        <FilterSidebar {...props} />
      </Drawer>
    </div>
  )
}
"use client"

import { Pagination } from "@/components/ui/Pagination"
import { scrollToTop } from "@/lib/routing/scrollRestore"

export interface SearchPaginationProps {
  page: number
  totalPages: number
  onPageChange: (page: number) => void
}

// SearchPagination — wraps the design-system Pagination with scroll-to-top on
// page change and suppression when there are fewer than two pages.
export function SearchPagination({ page, totalPages, onPageChange }: SearchPaginationProps) {
  const handle = (next: number) => {
    onPageChange(next)
    scrollToTop("main")
  }
  if (totalPages <= 1) return null
  return (
    <div className="flex justify-center py-4">
      <Pagination page={page} totalPages={totalPages} onPageChange={handle} />
    </div>
  )
}
"use client"

// Scroll restoration for returning from listing detail to search results.
// Captures scroll position into history state before navigating away and restores on return.
const SCROLL_KEY = "prioramarket.scrollY"

export function captureScroll(): void {
  if (typeof window === "undefined") return
  try {
    window.history.replaceState(
      { ...window.history.state, [SCROLL_KEY]: window.scrollY },
      "",
    )
  } catch {
    // Some browsers reject custom history state; degrade safely.
  }
}

export function restoreScroll(): void {
  if (typeof window === "undefined") return
  try {
    const state = window.history.state as Record<string, unknown> | null
    const y = state?.[SCROLL_KEY]
    if (typeof y === "number") window.scrollTo(0, y)
  } catch {
    // Degrade safely if the browser cannot restore.
  }
}

// Scroll to top of the results area or page content on pagination change.
export function scrollToTop(selector = "main"): void {
  if (typeof window === "undefined") return
  const el = document.querySelector(selector)
  if (el) el.scrollIntoView({ behavior: "smooth", block: "start" })
  else window.scrollTo({ top: 0, behavior: "smooth" })
}
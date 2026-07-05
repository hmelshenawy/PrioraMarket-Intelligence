"use client"

import { createContext, useCallback, useContext, useEffect, useMemo, useSyncExternalStore } from "react"
import type { ThemeContextValue, ThemeMode, ResolvedTheme } from "./types"
import { DEFAULT_THEME_MODE, THEME_STORAGE_KEY } from "./constants"

// --- External store for the persisted theme mode -----------------------------------------------
// useSyncExternalStore is the idiomatic way to read an external store (localStorage)
// without setState-in-effect, with SSR via getServerSnapshot.
type ModeListener = () => void
const modeListeners = new Set<ModeListener>()

function readMode(): ThemeMode {
  try {
    const stored = window.localStorage.getItem(THEME_STORAGE_KEY) as ThemeMode | null
    if (stored === "light" || stored === "dark" || stored === "system") return stored
  } catch {
    // Storage unavailable.
  }
  return DEFAULT_THEME_MODE
}

function subscribeMode(listener: ModeListener): () => void {
  modeListeners.add(listener)
  const onStorage = (e: StorageEvent) => {
    if (e.key === THEME_STORAGE_KEY) listener()
  }
  window.addEventListener("storage", onStorage)
  return () => {
    modeListeners.delete(listener)
    window.removeEventListener("storage", onStorage)
  }
}

function writeMode(mode: ThemeMode): void {
  try {
    window.localStorage.setItem(THEME_STORAGE_KEY, mode)
  } catch {
    // Persistence failure falls back silently to in-memory mode.
  }
  modeListeners.forEach((l) => l())
}

// --- External store for the OS color-scheme preference ------------------------------------------
type SystemListener = () => void

function getSystemMql(): MediaQueryList | null {
  if (typeof window === "undefined") return null
  return window.matchMedia("(prefers-color-scheme: dark)")
}

function readSystemTheme(): ResolvedTheme {
  const mql = getSystemMql()
  return mql?.matches ? "dark" : "light"
}

function subscribeSystem(listener: SystemListener): () => void {
  const mql = getSystemMql()
  if (!mql) return () => {}
  const update = () => listener()
  mql.addEventListener("change", update)
  return () => mql.removeEventListener("change", update)
}

// --- Provider ----------------------------------------------------------------------------------
export function ThemeProvider({ children }: { children: React.ReactNode }) {
  const mode = useSyncExternalStore(subscribeMode, readMode, () => DEFAULT_THEME_MODE)
  const systemTheme = useSyncExternalStore(
    subscribeSystem,
    readSystemTheme,
    (): ResolvedTheme => "light",
  )

  const resolvedTheme: ResolvedTheme = useMemo(
    () => (mode === "system" ? systemTheme : mode),
    [mode, systemTheme],
  )

  // Apply resolved theme to <html> (external DOM update, no React state).
  useEffect(() => {
    const root = document.documentElement
    root.classList.toggle("dark", resolvedTheme === "dark")
    root.style.colorScheme = resolvedTheme
  }, [resolvedTheme])

  const setMode = useCallback((next: ThemeMode) => {
    writeMode(next)
  }, [])

  const value: ThemeContextValue = useMemo(
    () => ({ mode, resolvedTheme, setMode }),
    [mode, resolvedTheme, setMode],
  )

  return <ThemeContext.Provider value={value}>{children}</ThemeContext.Provider>
}

const ThemeContext = createContext<ThemeContextValue | null>(null)

export function useTheme(): ThemeContextValue {
  const ctx = useContext(ThemeContext)
  if (!ctx) throw new Error("useTheme must be used within ThemeProvider")
  return ctx
}
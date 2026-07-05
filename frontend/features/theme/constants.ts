import type { ThemeMode } from "./types"

// Only the selected mode is persisted. Search state belongs in the URL, never here.
export const THEME_STORAGE_KEY = "prioramarket.theme"
export const DEFAULT_THEME_MODE: ThemeMode = "system"
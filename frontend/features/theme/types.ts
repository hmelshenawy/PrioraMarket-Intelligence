export type ThemeMode = "light" | "dark" | "system"
export type ResolvedTheme = "light" | "dark"

export interface ThemeContextValue {
  mode: ThemeMode
  resolvedTheme: ResolvedTheme
  setMode: (mode: ThemeMode) => void
}
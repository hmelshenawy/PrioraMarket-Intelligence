"use client"

import { Moon, Sun, Monitor } from "lucide-react"
import { useTheme } from "../ThemeProvider"
import { IconButton } from "@/components/ui/IconButton"
import type { ThemeMode } from "../types"

const modes: { value: ThemeMode; label: string; icon: React.ReactNode }[] = [
  { value: "light", label: "Light theme", icon: <Sun aria-hidden className="h-4 w-4" /> },
  { value: "dark", label: "Dark theme", icon: <Moon aria-hidden className="h-4 w-4" /> },
  { value: "system", label: "System theme", icon: <Monitor aria-hidden className="h-4 w-4" /> },
]

// ThemeSwitcher — light/dark/system toggle group in the top nav.
export function ThemeSwitcher() {
  const { mode, setMode } = useTheme()
  return (
    <div role="group" aria-label="Theme" className="inline-flex items-center gap-1 rounded-control border border-border p-1">
      {modes.map((m) => (
        <IconButton
          key={m.value}
          aria-label={m.label}
          aria-pressed={mode === m.value}
          variant={mode === m.value ? "secondary" : "ghost"}
          size="sm"
          onClick={() => setMode(m.value)}
        >
          {m.icon}
        </IconButton>
      ))}
    </div>
  )
}
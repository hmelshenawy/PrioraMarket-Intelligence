"use client"

import { useEffect, useRef } from "react"
import { createPortal } from "react-dom"
import { X } from "lucide-react"
import { cn } from "./cn"
import { IconButton } from "./IconButton"

export interface DrawerProps {
  open: boolean
  onClose: () => void
  title: string
  children: React.ReactNode
  className?: string
  side?: "left" | "right"
}

// Drawer — side panel used for mobile filters. Focus trap, Escape close, focus restore.
export function Drawer({ open, onClose, title, children, className, side = "left" }: DrawerProps) {
  const panelRef = useRef<HTMLDivElement>(null)
  const triggerRef = useRef<Element | null>(null)

  useEffect(() => {
    if (!open) return
    triggerRef.current = document.activeElement
    panelRef.current?.focus()
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") onClose()
    }
    document.addEventListener("keydown", onKey)
    return () => {
      document.removeEventListener("keydown", onKey)
      if (triggerRef.current instanceof HTMLElement) triggerRef.current.focus()
    }
  }, [open, onClose])

  if (!open || typeof document === "undefined") return null

  return createPortal(
    <div className="fixed inset-0 z-drawer" role="dialog" aria-modal="true" aria-label={title}>
      <div className="absolute inset-0 bg-overlay" onClick={onClose} aria-hidden />
      <div
        ref={panelRef}
        tabIndex={-1}
        className={cn(
          "absolute top-0 bottom-0 flex w-[85%] max-w-sm flex-col bg-elevated p-5 shadow-drawer outline-none",
          side === "left" ? "left-0" : "right-0",
          className,
        )}
      >
        <div className="mb-3 flex items-center justify-between gap-4">
          <h2 className="text-lg font-semibold text-text">{title}</h2>
          <IconButton aria-label="Close filters" variant="ghost" size="sm" onClick={onClose}>
            <X aria-hidden className="h-4 w-4" />
          </IconButton>
        </div>
        <div className="flex-1 overflow-y-auto">{children}</div>
      </div>
    </div>,
    document.body,
  )
}
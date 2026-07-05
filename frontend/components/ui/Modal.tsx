"use client"

import { useEffect, useRef } from "react"
import { createPortal } from "react-dom"
import { X } from "lucide-react"
import { cn } from "./cn"
import { IconButton } from "./IconButton"

export interface ModalProps {
  open: boolean
  onClose: () => void
  title: string
  children: React.ReactNode
  className?: string
}

// Modal — accessible dialog: focus trap, Escape to close, focus restore, portal.
export function Modal({ open, onClose, title, children, className }: ModalProps) {
  const dialogRef = useRef<HTMLDivElement>(null)
  const triggerRef = useRef<Element | null>(null)

  useEffect(() => {
    if (!open) return
    triggerRef.current = document.activeElement
    dialogRef.current?.focus()
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") onClose()
    }
    document.addEventListener("keydown", onKey)
    return () => {
      document.removeEventListener("keydown", onKey)
      // Restore focus to the opener.
      if (triggerRef.current instanceof HTMLElement) triggerRef.current.focus()
    }
  }, [open, onClose])

  useEffect(() => {
    if (!open) return
    const node = dialogRef.current
    if (!node) return
    const focusables = node.querySelectorAll<HTMLElement>(
      'a[href], button:not([disabled]), textarea, input, select, [tabindex]:not([tabindex="-1"])',
    )
    const first = focusables[0]
    const handleTab = (e: KeyboardEvent) => {
      if (e.key !== "Tab") return
      if (e.shiftKey && document.activeElement === node) {
        e.preventDefault()
        first?.focus()
      }
    }
    node.addEventListener("keydown", handleTab)
    return () => node.removeEventListener("keydown", handleTab)
  }, [open])

  if (!open || typeof document === "undefined") return null

  return createPortal(
    <div
      className="fixed inset-0 z-modal flex items-center justify-center p-4"
      role="dialog"
      aria-modal="true"
      aria-label={title}
    >
      <div className="absolute inset-0 bg-overlay" onClick={onClose} aria-hidden />
      <div
        ref={dialogRef}
        tabIndex={-1}
        className={cn("relative z-modal w-full max-w-lg rounded-modal bg-elevated p-6 shadow-modal outline-none", className)}
      >
        <div className="mb-3 flex items-center justify-between gap-4">
          <h2 className="text-lg font-semibold text-text">{title}</h2>
          <IconButton aria-label="Close dialog" variant="ghost" size="sm" onClick={onClose}>
            <X aria-hidden className="h-4 w-4" />
          </IconButton>
        </div>
        {children}
      </div>
    </div>,
    document.body,
  )
}
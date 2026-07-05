import { forwardRef } from "react"
import { cn } from "./cn"

export type ButtonVariant = "primary" | "secondary" | "ghost" | "destructive" | "link"
export type ButtonSize = "sm" | "md" | "lg"

export interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: ButtonVariant
  size?: ButtonSize
}

const variants: Record<ButtonVariant, string> = {
  primary: "bg-accent text-accent-foreground hover:opacity-90",
  secondary: "bg-surface text-text border border-border hover:bg-elevated",
  ghost: "bg-transparent text-text hover:bg-surface",
  destructive: "bg-danger text-white hover:opacity-90",
  link: "bg-transparent text-accent underline-offset-4 hover:underline",
}

const sizes: Record<ButtonSize, string> = {
  sm: "h-8 px-3 text-sm",
  md: "h-10 px-4 text-sm",
  lg: "h-12 px-6 text-base",
}

// Button — server-compatible presentational component.
export const Button = forwardRef<HTMLButtonElement, ButtonProps>(function Button(
  { variant = "primary", size = "md", className, type = "button", ...props },
  ref,
) {
  return (
    <button
      ref={ref}
      type={type}
      className={cn(
        "inline-flex items-center justify-center gap-2 rounded-control font-medium transition-colors",
        "focus-visible:outline focus-visible:outline-2 focus-visible:outline-focus",
        "disabled:cursor-not-allowed disabled:opacity-50",
        variants[variant],
        sizes[size],
        className,
      )}
      {...props}
    />
  )
})
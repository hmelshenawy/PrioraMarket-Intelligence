import { forwardRef } from "react"
import { cn } from "./cn"
import { Button, type ButtonProps } from "./Button"

export interface IconButtonProps extends ButtonProps {
  "aria-label": string
}

// IconButton — square icon-only button. Requires an accessible name via aria-label.
export const IconButton = forwardRef<HTMLButtonElement, IconButtonProps>(function IconButton(
  { className, size = "md", ...props },
  ref,
) {
  const sizeClass = size === "sm" ? "h-8 w-8" : size === "lg" ? "h-12 w-12" : "h-10 w-10"
  return (
    <Button
      ref={ref}
      size={size}
      className={cn("p-0", sizeClass, className)}
      {...props}
    />
  )
})
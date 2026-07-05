import { cn } from "./cn"

export type DividerProps = React.HTMLAttributes<HTMLHRElement>

// Divider — semantic separator using border token.
export function Divider({ className, ...props }: DividerProps) {
  return <hr className={cn("border-0 border-t border-border", className)} {...props} />
}
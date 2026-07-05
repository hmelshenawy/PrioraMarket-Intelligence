import { cn } from "./cn"

export interface CardProps extends React.HTMLAttributes<HTMLDivElement> {
  as?: React.ElementType
}

// Card — presentational surface with semantic tokens and shadow.
export function Card({ as: Tag = "div", className, ...props }: CardProps) {
  return (
    <Tag
      className={cn("rounded-card border border-border bg-elevated shadow-card", className)}
      {...props}
    />
  )
}
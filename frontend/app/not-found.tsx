import { EmptyState } from "@/components/ui/EmptyState"

// Handles unknown application routes and missing listing detail flows.
export default function NotFound() {
  return (
    <div className="py-12">
      <EmptyState
        title="Page not found"
        description="The page you're looking for doesn't exist or may have moved."
        actionLabel="Back to search"
        actionHref="/"
      />
    </div>
  )
}
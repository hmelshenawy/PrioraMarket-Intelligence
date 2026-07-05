// SkipToContent — keyboard/screen-reader bypass to main content.
export function SkipToContent({ targetId = "main-content" }: { targetId?: string }) {
  return (
    <a
      href={`#${targetId}`}
      className="sr-only focus:not-sr-only focus:fixed focus:left-4 focus:top-4 focus:z-toast focus:rounded-control focus:bg-accent focus:px-4 focus:py-2 focus:text-accent-foreground"
    >
      Skip to content
    </a>
  )
}
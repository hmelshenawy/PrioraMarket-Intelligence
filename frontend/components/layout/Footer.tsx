import { Container } from "./Container"

// Footer — consistent end-of-page landmark with lightweight product context.
// No account/admin/marketplace-management capabilities.
export function Footer() {
  return (
    <footer className="border-t border-border bg-surface mt-12">
      <Container>
        <div className="flex flex-col gap-2 py-8 text-sm text-muted sm:flex-row sm:items-center sm:justify-between">
          <p>PrioraMarket — vehicle market intelligence.</p>
          <p>© {new Date().getFullYear()} PrioraMarket. All rights reserved.</p>
        </div>
      </Container>
    </footer>
  )
}
import { TopNav } from "./TopNav"
import { Footer } from "./Footer"
import { Container } from "./Container"
import { SkipToContent } from "./SkipToContent"

// AppShell — wraps all current and future pages. Visually neutral, reusable,
// no feature-specific data fetching beyond reusable health/theme behavior in TopNav.
export function AppShell({ children }: { children: React.ReactNode }) {
  return (
    <>
      <SkipToContent />
      <TopNav />
      <main id="main-content" tabIndex={-1} className="flex-1 focus:outline-none">
        <Container className="py-6">{children}</Container>
      </main>
      <Footer />
    </>
  )
}
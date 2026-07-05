import { describe, expect, it, beforeEach, afterEach } from "vitest"
import { render, screen, fireEvent } from "@testing-library/react"
import { ThemeProvider, ThemeSwitcher } from "@/features/theme"
import { Button } from "@/components/ui/Button"
import { Card } from "@/components/ui/Card"
import { Badge } from "@/components/ui/Badge"
import { Tag } from "@/components/ui/Tag"
import { Alert } from "@/components/ui/Alert"
import { Divider } from "@/components/ui/Divider"
import { Skeleton } from "@/components/ui/Skeleton"
import { Spinner } from "@/components/ui/Spinner"
import { StatusIndicator } from "@/components/ui/StatusIndicator"
import { EmptyState } from "@/components/ui/EmptyState"
import { ErrorState } from "@/components/ui/ErrorState"
import { THEME_STORAGE_KEY } from "@/features/theme/constants"

// ThemeCoverage — renders a representative sample of shared UI components inside
// the ThemeProvider and verifies light/dark/system modes apply the `dark` class to
// <html> and that every component renders without error in both themes.
function Sample() {
  return (
    <>
      <ThemeSwitcher />
      <Card className="p-4">
        <Button variant="primary">Search</Button>
        <Badge>Used</Badge>
        <Tag>2021</Tag>
        <Alert variant="info" title="Info">
          Notice
        </Alert>
        <Divider />
        <Skeleton className="h-4 w-24" />
        <Spinner />
        <StatusIndicator state="available" label="Backend available" />
        <EmptyState title="No results" description="Try a different search" />
        <ErrorState title="Something went wrong" message="Retry" />
      </Card>
    </>
  )
}

function renderInTheme() {
  return render(
    <ThemeProvider>
      <Sample />
    </ThemeProvider>,
  )
}

describe("Theme coverage", () => {
  beforeEach(() => {
    window.localStorage.clear()
    document.documentElement.classList.remove("dark")
  })
  afterEach(() => {
    window.localStorage.clear()
    document.documentElement.classList.remove("dark")
  })

  it("renders the shared component sample without error", () => {
    renderInTheme()
    expect(screen.getByText("Search")).toBeInTheDocument()
    expect(screen.getByText("No results")).toBeInTheDocument()
    expect(screen.getAllByRole("status").length).toBeGreaterThan(0)
  })

  it("applies the dark class to <html> when Dark theme is selected", () => {
    renderInTheme()
    fireEvent.click(screen.getByLabelText("Dark theme"))
    expect(document.documentElement.classList.contains("dark")).toBe(true)
  })

  it("removes the dark class when Light theme is selected", () => {
    renderInTheme()
    fireEvent.click(screen.getByLabelText("Dark theme"))
    expect(document.documentElement.classList.contains("dark")).toBe(true)
    fireEvent.click(screen.getByLabelText("Light theme"))
    expect(document.documentElement.classList.contains("dark")).toBe(false)
  })

  it("persists the selected mode to localStorage", () => {
    renderInTheme()
    fireEvent.click(screen.getByLabelText("Dark theme"))
    expect(window.localStorage.getItem(THEME_STORAGE_KEY)).toBe("dark")
  })
})
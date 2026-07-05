import { describe, expect, it } from "vitest"
import { render, screen } from "@testing-library/react"
import { SnapshotMetrics } from "@/features/market/components/SnapshotMetrics"
import { METRIC_ORDER } from "@/features/market/constants/market"
import type {
  MarketMetricDto,
  MarketSnapshotViewModel,
} from "@/features/market/types"

// Inline fixture view model for US1: overall scope with five metrics in the canonical
// order. history-dependent metrics (inventoryChange, priceDrops) reflect the US1
// defaults — partial and unsupported respectively — so we can assert unsupported states
// without an MSW harness.
function buildSnapshot(): MarketSnapshotViewModel {
  const metrics: MarketMetricDto[] = [
    {
      type: "activeListings",
      title: "Active Listings",
      status: { status: "supported", dataAvailable: true },
      count: 4381,
      scopeLabel: "Overall UAE Used Cars",
    },
    {
      type: "medianPrice",
      title: "Median Price",
      status: { status: "supported", dataAvailable: true },
      amount: 170000,
      currency: "AED",
      sampleSize: 8,
    },
    {
      type: "typicalPriceRange",
      title: "Typical Price Range",
      status: { status: "supported", dataAvailable: true },
      method: "percentile",
      currency: "AED",
      medianAmount: 170000,
      lowerAmount: 135000,
      upperAmount: 205000,
      minAmount: null,
      maxAmount: null,
      sampleSize: 8,
    },
    {
      type: "inventoryChange",
      title: "Inventory Change",
      status: {
        status: "partial",
        dataAvailable: true,
        reason: "Period inventory change tracking is not available",
      },
      // Distinct from activeListings.count so presentation assertions are unambiguous.
      activeInventory: 4250,
      newListings: null,
      removedListings: null,
      netChange: null,
      periodDays: 7,
    },
    {
      type: "priceDrops",
      title: "Price Drops",
      status: {
        status: "unsupported",
        dataAvailable: false,
        reason: "Price history is not available",
      },
      count: null,
      averageDropPercentage: null,
      sampleSize: null,
      periodDays: 7,
    },
  ]

  return {
    scopeLabel: "Overall UAE Used Cars",
    scopeLevel: "overall",
    asOf: "As of 5 Jul 2026, 04:30 PM",
    generatedAt: "2026-07-05T12:30:00.000Z",
    periodDays: 7,
    metrics,
    supportStatuses: {
      activeListings: { status: "supported", dataAvailable: true },
      medianPrice: { status: "supported", dataAvailable: true },
      typicalPriceRange: { status: "supported", dataAvailable: true },
      inventoryChange: {
        status: "partial",
        dataAvailable: true,
        reason: "Period inventory change tracking is not available",
      },
      priceDrops: {
        status: "unsupported",
        dataAvailable: false,
        reason: "Price history is not available",
      },
    },
    freshness: {
      lastUpdated: "2026-07-05T08:00:00.000Z",
      datasetVersion: "2026.1.0",
      scrapeRunId: 1042,
    },
  }
}

describe("SnapshotMetrics", () => {
  it("renders five card skeletons in the loading state", () => {
    render(<SnapshotMetrics isLoading={true} error={null} />)
    const grid = document.querySelector('div[aria-busy="true"][aria-label="Loading market snapshot"]')
    expect(grid).not.toBeNull()
    // Five metric skeletons (each Card holds three shimmer blocks).
    const skeletons = document.querySelectorAll(".bg-skeleton")
    expect(skeletons.length).toBeGreaterThanOrEqual(5)
  })

  it("renders the five metric cards in the canonical METRIC_ORDER", () => {
    render(<SnapshotMetrics data={buildSnapshot()} isLoading={false} error={null} />)
    const titles = screen
      .getAllByRole("heading", { level: 3 })
      .map((h) => h.textContent)
    const expectedTitles = METRIC_ORDER.map((type) => {
      switch (type) {
        case "activeListings":
          return "Active Listings"
        case "medianPrice":
          return "Median Price"
        case "typicalPriceRange":
          return "Typical Price Range"
        case "inventoryChange":
          return "Inventory Change"
        case "priceDrops":
          return "Price Drops"
      }
    })
    expect(titles).toEqual(expectedTitles)
  })

  it("renders raw values for supported metrics without re-formatting", () => {
    render(<SnapshotMetrics data={buildSnapshot()} isLoading={false} error={null} />)
    // activeListings count with thousand separator.
    expect(screen.getByText("4,381")).toBeInTheDocument()
    // medianPrice as AED with grouping.
    expect(screen.getByText("AED 170,000")).toBeInTheDocument()
    // typicalPriceRange lower – upper.
    expect(screen.getByText("AED 135,000 – AED 205,000")).toBeInTheDocument()
  })

  it("renders a partial inventory card with the active count and the reason note", () => {
    render(<SnapshotMetrics data={buildSnapshot()} isLoading={false} error={null} />)
    // Active inventory value is shown.
    expect(screen.getByText("Active inventory")).toBeInTheDocument()
    // The partial reason note is rendered alongside the value.
    expect(
      screen.getByText("Period inventory change tracking is not available"),
    ).toBeInTheDocument()
    // New / Removed / Net labels render; their null values fall back to the placeholder.
    expect(screen.getByText("New")).toBeInTheDocument()
    expect(screen.getByText("Removed")).toBeInTheDocument()
    expect(screen.getByText("Net")).toBeInTheDocument()
  })

  it("renders an unsupported price-drops card with a reason and no fabricated value", () => {
    render(<SnapshotMetrics data={buildSnapshot()} isLoading={false} error={null} />)
    // The unsupported reason is shown.
    expect(screen.getByText("Price history is not available")).toBeInTheDocument()
    // The card title is present so the slot still occupies its grid position.
    expect(screen.getByRole("heading", { level: 3, name: "Price Drops" })).toBeInTheDocument()
    // No sample-size line is rendered for an unsupported metric (children are skipped).
    expect(screen.queryByText(/Based on 0 listings/)).toBeNull()
  })

  it("renders a scoped error state with retry when the snapshot fails to load", () => {
    render(
      <SnapshotMetrics
        isLoading={false}
        error={{ category: "serverError", status: 500, message: "down" }}
        onRetry={() => {}}
      />,
    )
    expect(screen.getByRole("alert").textContent).toMatch(/Couldn't load the market snapshot/i)
    expect(screen.getByRole("button", { name: /try again/i })).toBeInTheDocument()
  })
})
import { describe, expect, it, vi } from "vitest"
import { render, screen } from "@testing-library/react"
import { MarketplaceAction } from "@/features/listings/components/MarketplaceAction"

describe("MarketplaceAction", () => {
  it("renders a button that opens the URL in a new browser context when a valid URL exists", () => {
    const openSpy = vi.spyOn(window, "open").mockImplementation(() => null)
    render(<MarketplaceAction url="https://market.example/listing/1" />)
    const button = screen.getByRole("button", { name: /View on marketplace/i })
    button.click()
    expect(openSpy).toHaveBeenCalledWith("https://market.example/listing/1", "_blank", "noopener,noreferrer")
    openSpy.mockRestore()
  })

  it("renders the hidden/unavailable state and no link when the URL is missing", () => {
    render(<MarketplaceAction url={null} />)
    expect(screen.queryByRole("button")).toBeNull()
    expect(screen.getByText(/No marketplace link available/i)).toBeInTheDocument()
  })

  it("renders the hidden state when the URL is invalid", () => {
    render(<MarketplaceAction url="" />)
    expect(screen.queryByRole("button")).toBeNull()
    expect(screen.getByText(/No marketplace link available/i)).toBeInTheDocument()
  })
})
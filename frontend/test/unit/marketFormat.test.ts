import { describe, expect, it } from "vitest"
import { formatAed, formatNumber, formatPercent, formatAsOf, formatCount } from "@/features/market/utils/market-format"
import { EMPTY_VALUE } from "@/lib/formatting/emptyValue"

// Market presentation formatting. These tests pin the user-facing labels (AED prefix,
// thousand separators, percent suffix, and the "As of <generatedAt>" recency cue) so
// downstream cards can render raw backend values without re-formatting.
describe("market-format", () => {
  describe("formatAed (re-exported)", () => {
    it("prefixes AED and groups thousands", () => {
      expect(formatAed(85000)).toBe("AED 85,000")
    })

    it("formats larger prices with thousand separators", () => {
      expect(formatAed(1_250_000)).toBe("AED 1,250,000")
    })

    it("returns the empty placeholder for null/undefined (never fabricates)", () => {
      expect(formatAed(null)).toBe(EMPTY_VALUE)
      expect(formatAed(undefined)).toBe(EMPTY_VALUE)
      expect(formatAed(Number.NaN)).toBe(EMPTY_VALUE)
    })
  })

  describe("formatNumber / formatCount", () => {
    it("groups counts with thousand separators", () => {
      expect(formatNumber(4381)).toBe("4,381")
      expect(formatCount(1200)).toBe("1,200")
    })

    it("returns the empty placeholder for null/undefined counts", () => {
      expect(formatCount(null)).toBe(EMPTY_VALUE)
      expect(formatCount(undefined)).toBe(EMPTY_VALUE)
    })

    it("renders a true zero count distinctly from unsupported", () => {
      // A supported metric with zero listings must render "0", not the placeholder.
      expect(formatCount(0)).toBe("0")
    })
  })

  describe("formatPercent", () => {
    it("appends a percent sign with one fractional digit by default", () => {
      expect(formatPercent(12.5)).toBe("12.5%")
    })

    it("pads to the requested fractional precision", () => {
      expect(formatPercent(8, 1)).toBe("8.0%")
    })

    it("returns the empty placeholder for null/undefined", () => {
      expect(formatPercent(null)).toBe(EMPTY_VALUE)
      expect(formatPercent(undefined)).toBe(EMPTY_VALUE)
    })
  })

  describe("formatAsOf", () => {
    it("prefixes the formatted generatedAt with 'As of'", () => {
      const result = formatAsOf("2026-07-05T12:30:00.000Z")
      expect(result.startsWith("As of ")).toBe(true)
      // Date portion is timezone-stable for a noon-UTC timestamp.
      expect(result).toMatch(/2026/)
      expect(result).toMatch(/Jul/)
    })

    it("returns the empty placeholder when generatedAt is missing", () => {
      expect(formatAsOf(null)).toBe(EMPTY_VALUE)
      expect(formatAsOf(undefined)).toBe(EMPTY_VALUE)
    })

    it("returns the empty placeholder for an invalid timestamp", () => {
      expect(formatAsOf("not-a-date")).toBe(EMPTY_VALUE)
    })
  })
})
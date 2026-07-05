// AsOfTimestamp — the user-facing recency cue ("As of <generatedAt>"). Sourced from the
// snapshot's generatedAt, NEVER from freshness.lastUpdated: freshness is raw metadata and
// MUST NOT be presented as a real-time market reading.
export function AsOfTimestamp({ asOf }: { asOf: string }) {
  return (
    <p className="text-sm text-muted" data-testid="as-of-timestamp">
      {asOf}
    </p>
  )
}
// ScopeLabel — the dashboard heading naming the market scope (e.g. "Overall UAE Used
// Cars"). Presentation only.
export function ScopeLabel({ label, level }: { label: string; level: string }) {
  return (
    <h1 className="text-2xl font-semibold text-text" data-scope-level={level}>
      {label}
    </h1>
  )
}
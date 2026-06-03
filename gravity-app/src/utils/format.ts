/**
 * format.ts — Shared number formatting helpers
 *
 * Previously duplicated as `shortNum` in Dashboard.tsx and `fmt` in llm.ts.
 * Single source of truth for human-readable numeric output.
 */

/**
 * Compact human-readable number (e.g. 1234567 → "1.2M").
 * Used in chart labels, stat cards, and AI prompt context.
 */
export function formatNum(n: number | undefined): string {
  if (n === undefined || isNaN(n)) return 'N/A'
  const abs = Math.abs(n)
  if (abs >= 1e9) return `${(n / 1e9).toFixed(1)}B`
  if (abs >= 1e6) return `${(n / 1e6).toFixed(1)}M`
  if (abs >= 1e3) return `${(n / 1e3).toFixed(1)}K`
  return n % 1 === 0 ? n.toLocaleString() : n.toFixed(2)
}

/**
 * Higher-precision variant used in LLM prompt context strings
 * (keeps 3 decimal places instead of 2 for floats < 1K).
 */
export function formatNumPrecise(n: number | undefined): string {
  if (n === undefined || isNaN(n)) return 'N/A'
  const abs = Math.abs(n)
  if (abs >= 1e9) return `${(n / 1e9).toFixed(2)}B`
  if (abs >= 1e6) return `${(n / 1e6).toFixed(2)}M`
  if (abs >= 1e3) return `${(n / 1e3).toFixed(1)}K`
  return n % 1 === 0 ? n.toLocaleString() : n.toFixed(3)
}

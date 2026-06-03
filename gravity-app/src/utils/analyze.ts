/**
 * analyze.ts
 * Auto-analyzes DataRecord[] and returns typed insights, field stats,
 * chart data, and auto-generated natural-language sentences.
 */

import type { DataRecord } from '../types/data'

// ─── Types ────────────────────────────────────────────────────────────────────

export type FieldType = 'numeric' | 'categorical' | 'text'

export interface FieldStat {
  key: string
  type: FieldType
  // numeric
  min?: number
  max?: number
  avg?: number
  sum?: number
  minLabel?: string   // record label for min
  maxLabel?: string   // record label for max
  // categorical
  topValues?: { value: string; count: number; pct: number }[]
  // bar chart data (top 10, normalised 0–100)
  chartBars?: { label: string; value: number; pct: number }[]
}

export interface DataInsights {
  recordCount: number
  fieldCount: number
  fieldStats: FieldStat[]
  sentences: string[]
  labelField: string  // best field to use as card title/label
}

// ─── Main analyzer ────────────────────────────────────────────────────────────

export function analyzeRecords(records: DataRecord[]): DataInsights {
  if (records.length === 0) {
    return { recordCount: 0, fieldCount: 0, fieldStats: [], sentences: [], labelField: '' }
  }

  const allKeys = Array.from(
    new Set(records.flatMap((r) => Object.keys(r.fields)))
  )

  const fieldStats: FieldStat[] = allKeys.map((key) =>
    analyzeField(key, records)
  )

  const labelField = chooseLabelField(fieldStats)
  const sentences = generateSentences(fieldStats, records, labelField)

  return {
    recordCount: records.length,
    fieldCount: allKeys.length,
    fieldStats,
    sentences,
    labelField,
  }
}

// ─── Field analysis ───────────────────────────────────────────────────────────

function analyzeField(key: string, records: DataRecord[]): FieldStat {
  const rawValues = records
    .map((r) => r.fields[key])
    .filter((v) => v !== undefined && v !== '')

  const cleaned = rawValues.map((v) => v.trim())

  // Detect date/time columns — skip numeric parsing for these
  const DATE_PATTERN = /date|time|created_at|updated_at|timestamp|_date|_dt|datetime/i
  const isDateColumn = DATE_PATTERN.test(key)

  // Detect numeric: strip $ % , and see if the result is a valid number
  const numericValues = isDateColumn ? [] : cleaned
    .map((v) => parseFloat(v.replace(/[$%,\s]/g, '').replace(/B$/, 'e9').replace(/M$/, 'e6').replace(/K$/, 'e3')))
    .filter((n) => !isNaN(n) && isFinite(n))

  if (numericValues.length >= Math.max(2, records.length * 0.6)) {
    // Numeric field
    const sorted = [...numericValues].sort((a, b) => a - b)
    const min = sorted[0]
    const max = sorted[sorted.length - 1]
    const sum = sorted.reduce((a, b) => a + b, 0)
    const avg = sum / sorted.length

    // Build chart bars — top values by raw number, max 8
    const paired = records
      .map((r) => ({
        label: r.fields[key] ?? '',
        rawVal: parseFloat((r.fields[key] ?? '').replace(/[$%,\s]/g, '').replace(/B$/, 'e9').replace(/M$/, 'e6').replace(/K$/, 'e3')),
        recordLabel: getLabel(r),
      }))
      .filter((p) => !isNaN(p.rawVal))
      .sort((a, b) => b.rawVal - a.rawVal)
      .slice(0, 8)

    const chartMax = paired[0]?.rawVal ?? 1
    const chartBars = paired.map((p) => ({
      label: p.recordLabel.length > 12 ? p.recordLabel.slice(0, 11) + '…' : p.recordLabel,
      value: p.rawVal,
      pct: Math.max(4, Math.round((p.rawVal / chartMax) * 100)),
    }))

    const maxRecord = records.find(
      (r) => parseFloat((r.fields[key] ?? '').replace(/[$%,\s]/g, '').replace(/B$/, 'e9').replace(/M$/, 'e6').replace(/K$/, 'e3')) === max
    )
    const minRecord = records.find(
      (r) => parseFloat((r.fields[key] ?? '').replace(/[$%,\s]/g, '').replace(/B$/, 'e9').replace(/M$/, 'e6').replace(/K$/, 'e3')) === min
    )

    return {
      key,
      type: 'numeric',
      min,
      max,
      avg,
      sum,
      minLabel: minRecord ? getLabel(minRecord) : undefined,
      maxLabel: maxRecord ? getLabel(maxRecord) : undefined,
      chartBars,
    }
  }

  // Categorical field
  const freq: Record<string, number> = {}
  cleaned.forEach((v) => { freq[v] = (freq[v] ?? 0) + 1 })
  const sorted = Object.entries(freq).sort((a, b) => b[1] - a[1])
  const total = cleaned.length
  const topValues = sorted.slice(0, 6).map(([value, count]) => ({
    value,
    count,
    pct: Math.round((count / total) * 100),
  }))

  // Categorical with very long values → treat as text
  const isText = topValues.some((v) => v.value.length > 40)

  return { key, type: isText ? 'text' : 'categorical', topValues }
}

// ─── Label chooser ────────────────────────────────────────────────────────────

function chooseLabelField(stats: FieldStat[]): string {
  // Prefer: short categorical with mostly unique values
  const nameKeys = ['name', 'country', 'title', 'city', 'product', 'user', 'item', 'label', 'coin']
  for (const key of nameKeys) {
    const found = stats.find((s) => s.key.toLowerCase().includes(key) && s.type === 'categorical')
    if (found) return found.key
  }
  // Fallback: first categorical field with mostly unique values
  const cat = stats.find((s) => s.type === 'categorical')
  return cat?.key ?? stats[0]?.key ?? ''
}

function getLabel(record: DataRecord): string {
  const nameKeys = ['name', 'country', 'title', 'city', 'product', 'user', 'coin', 'mission', 'label']
  for (const key of nameKeys) {
    const found = Object.entries(record.fields).find(([k]) => k.toLowerCase().includes(key))
    if (found) return found[1]
  }
  return Object.values(record.fields)[0] ?? ''
}

// ─── Insight sentences ────────────────────────────────────────────────────────

function generateSentences(
  stats: FieldStat[],
  records: DataRecord[],
  labelField: string
): string[] {
  const sentences: string[] = []

  for (const stat of stats) {
    if (sentences.length >= 5) break

    if (stat.type === 'numeric') {
      if (stat.maxLabel && stat.max !== undefined) {
        sentences.push(
          `${stat.maxLabel} has the highest ${stat.key.toLowerCase()} at ${formatNum(stat.max, stat.key)}.`
        )
      }
      if (stat.minLabel && stat.min !== undefined && stat.minLabel !== stat.maxLabel) {
        sentences.push(
          `${stat.minLabel} has the lowest ${stat.key.toLowerCase()} at ${formatNum(stat.min, stat.key)}.`
        )
      }
      if (stat.avg !== undefined && stat.max !== undefined) {
        sentences.push(
          `Average ${stat.key.toLowerCase()}: ${formatNum(stat.avg, stat.key)}.`
        )
      }
    } else if (stat.type === 'categorical' && stat.topValues && stat.topValues.length > 1 && stat.key !== labelField) {
      const top = stat.topValues[0]
      if (top.pct < 90) {
        sentences.push(
          `Most common ${stat.key.toLowerCase()}: "${top.value}" (${top.count} of ${records.length} records, ${top.pct}%).`
        )
      }
    }
  }

  if (sentences.length === 0) {
    sentences.push(`${records.length} records loaded with ${stats.length} fields each.`)
  }

  return sentences
}

function formatNum(n: number, key: string): string {
  const k = key.toLowerCase()
  if (k.includes('%') || k.includes('change') || k.includes('pct') || k.includes('percent')) {
    return `${n.toFixed(1)}%`
  }
  if (k.includes('price') || k.includes('cap') || k.includes('cost') || k.includes('revenue')) {
    if (Math.abs(n) >= 1e9) return `$${(n / 1e9).toFixed(1)}B`
    if (Math.abs(n) >= 1e6) return `$${(n / 1e6).toFixed(1)}M`
    if (Math.abs(n) >= 1e3) return `$${(n / 1e3).toFixed(1)}K`
    return `$${n.toLocaleString()}`
  }
  if (Math.abs(n) >= 1e9) return `${(n / 1e9).toFixed(1)}B`
  if (Math.abs(n) >= 1e6) return `${(n / 1e6).toFixed(1)}M`
  if (Math.abs(n) >= 1e3) return `${(n / 1e3).toFixed(1)}K`
  return n % 1 === 0 ? n.toLocaleString() : n.toFixed(2)
}

/**
 * Data Parsers
 *
 * Utilities for parsing CSV and JSON text into DataRecord arrays.
 * Both functions cap output at MAX_RECORDS for performance.
 */

import type { DataRecord } from '../types/data'
import { nanoid } from '../utils/nanoid'

export const MAX_RECORDS = 10_000

/**
 * Parse a CSV string into DataRecord[].
 * Handles quoted fields, Windows line endings, empty rows.
 */
export function parseCSV(text: string, source = 'CSV Upload'): DataRecord[] {
  const normalized = text.replace(/^\uFEFF/, '')
  const rows = parseCsvRows(normalized, detectDelimiter(normalized))
    .filter((row) => row.some((value) => value.trim().length > 0))
  if (rows.length < 2) throw new Error('CSV must have a header row and at least one data row')

  // Parse header
  const headers = makeUniqueHeaders(rows[0])
  if (headers.length === 0) throw new Error('Could not parse CSV headers')

  const records: DataRecord[] = []
  for (let i = 1; i < Math.min(rows.length, MAX_RECORDS + 1); i++) {
    const values = rows[i]
    if (values.length === 0) continue

    const fields: Record<string, string> = {}
    headers.forEach((h, idx) => {
      const key = h.trim() || `col${idx + 1}`
      const val = (values[idx] ?? '').trim()
      if (key && val !== undefined) {
        fields[key] = val
      }
    })

    records.push({ id: nanoid(), source, fields })
  }

  if (records.length === 0) throw new Error('No valid data rows found in CSV')
  return records
}

/**
 * Parse CSV rows while respecting escaped quotes and quoted newlines.
 */
function detectDelimiter(text: string): string {
  const counts = new Map([[',', 0], [';', 0], ['\t', 0]])
  let inQuotes = false
  for (let index = 0; index < text.length; index++) {
    const character = text[index]
    if (character === '"') {
      if (inQuotes && text[index + 1] === '"') index++
      else inQuotes = !inQuotes
    } else if (!inQuotes && (character === '\n' || character === '\r')) {
      break
    } else if (!inQuotes && counts.has(character)) {
      counts.set(character, (counts.get(character) ?? 0) + 1)
    }
  }
  return [...counts.entries()].sort((a, b) => b[1] - a[1])[0][0]
}

function parseCsvRows(text: string, delimiter: string): string[][] {
  const rows: string[][] = []
  let fields: string[] = []
  let current = ''
  let inQuotes = false

  for (let i = 0; i < text.length; i++) {
    const ch = text[i]
    if (ch === '"') {
      if (inQuotes && text[i + 1] === '"') {
        current += '"'
        i++
      } else {
        inQuotes = !inQuotes
      }
    } else if (ch === delimiter && !inQuotes) {
      fields.push(current)
      current = ''
    } else if ((ch === '\n' || ch === '\r') && !inQuotes) {
      fields.push(current)
      rows.push(fields)
      fields = []
      current = ''
      if (ch === '\r' && text[i + 1] === '\n') i++
    } else {
      current += ch
    }
  }
  if (inQuotes) throw new Error('CSV contains an unterminated quoted field')
  fields.push(current)
  rows.push(fields)
  return rows
}

function makeUniqueHeaders(rawHeaders: string[]): string[] {
  const seen = new Map<string, number>()
  return rawHeaders.map((header, index) => {
    const base = header.trim() || `col${index + 1}`
    const count = seen.get(base) ?? 0
    seen.set(base, count + 1)
    return count === 0 ? base : `${base}_${count + 1}`
  })
}

/**
 * Parse a JSON string into DataRecord[].
 * Accepts: array of objects, { data: [...] }, { results: [...] },
 * or a single object (wraps it in an array).
 */
export function parseJSON(text: string, source = 'JSON Upload'): DataRecord[] {
  let parsed: unknown
  try {
    parsed = JSON.parse(text)
  } catch {
    throw new Error('Invalid JSON — could not parse the file')
  }

  let items = extractArray(parsed)
  if (items.length === 0) throw new Error('No array of records found in JSON')
  items = items.slice(0, MAX_RECORDS)

  return items.map((item) => {
    const fields = flattenObject(item)
    return { id: nanoid(), source, fields }
  })
}

/**
 * Try to extract an array from various JSON shapes.
 */
function extractArray(data: unknown): Record<string, unknown>[] {
  if (Array.isArray(data)) {
    return data.filter((d) => typeof d === 'object' && d !== null) as Record<string, unknown>[]
  }
  if (typeof data === 'object' && data !== null) {
    const obj = data as Record<string, unknown>
    // Common API response wrappers
    for (const key of ['data', 'results', 'items', 'records', 'entries', 'list', 'rows', 'docs']) {
      if (Array.isArray(obj[key])) {
        return (obj[key] as unknown[]).filter(
          (d) => typeof d === 'object' && d !== null
        ) as Record<string, unknown>[]
      }
    }
    // Single object — wrap it
    return [obj]
  }
  return []
}

/**
 * Flatten a nested object into key: value string pairs.
 * Nested keys use dot notation. Fields and values are preserved for analysis.
 */
function flattenObject(
  obj: Record<string, unknown>,
  prefix = '',
  maxDepth = 2,
  currentDepth = 0
): Record<string, string> {
  const result: Record<string, string> = {}

  for (const [key, value] of Object.entries(obj)) {
    const fullKey = prefix ? `${prefix}.${key}` : key

    if (
      currentDepth < maxDepth &&
      typeof value === 'object' &&
      value !== null &&
      !Array.isArray(value)
    ) {
      const nested = flattenObject(
        value as Record<string, unknown>,
        fullKey,
        maxDepth,
        currentDepth + 1
      )
      Object.assign(result, nested)
    } else if (Array.isArray(value)) {
      const str = value.slice(0, 3).join(', ')
      result[fullKey] = str
    } else if (value !== null && value !== undefined) {
      const str = String(value)
      result[fullKey] = str
    }
  }

  return result
}

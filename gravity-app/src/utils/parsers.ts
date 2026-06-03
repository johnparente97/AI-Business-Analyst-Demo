/**
 * Data Parsers
 *
 * Utilities for parsing CSV and JSON text into DataRecord arrays.
 * Both functions cap output at MAX_RECORDS for performance.
 */

import type { DataRecord } from '../types/data'
import { nanoid } from '../utils/nanoid'

const MAX_RECORDS = 500

/**
 * Parse a CSV string into DataRecord[].
 * Handles quoted fields, Windows line endings, empty rows.
 */
export function parseCSV(text: string, source = 'CSV Upload'): DataRecord[] {
  const lines = text.replace(/\r\n/g, '\n').replace(/\r/g, '\n').split('\n')
  const nonEmpty = lines.filter((l) => l.trim().length > 0)
  if (nonEmpty.length < 2) throw new Error('CSV must have a header row and at least one data row')

  // Parse header
  const headers = parseCsvRow(nonEmpty[0])
  if (headers.length === 0) throw new Error('Could not parse CSV headers')

  const records: DataRecord[] = []
  for (let i = 1; i < Math.min(nonEmpty.length, MAX_RECORDS + 1); i++) {
    const values = parseCsvRow(nonEmpty[i])
    if (values.length === 0) continue

    const fields: Record<string, string> = {}
    headers.forEach((h, idx) => {
      const key = h.trim() || `col${idx + 1}`
      const val = (values[idx] ?? '').trim()
      if (key && val !== undefined) {
        fields[key] = val.length > 60 ? val.slice(0, 57) + '…' : val
      }
    })

    records.push({ id: nanoid(), source, fields })
  }

  if (records.length === 0) throw new Error('No valid data rows found in CSV')
  return records
}

/**
 * Parse a single CSV row, respecting quoted fields.
 */
function parseCsvRow(row: string): string[] {
  const fields: string[] = []
  let current = ''
  let inQuotes = false

  for (let i = 0; i < row.length; i++) {
    const ch = row[i]
    if (ch === '"') {
      if (inQuotes && row[i + 1] === '"') {
        current += '"'
        i++
      } else {
        inQuotes = !inQuotes
      }
    } else if (ch === ',' && !inQuotes) {
      fields.push(current)
      current = ''
    } else {
      current += ch
    }
  }
  fields.push(current)
  return fields
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
 * Nested keys use dot notation. Max 8 fields, max 60 char values.
 */
function flattenObject(
  obj: Record<string, unknown>,
  prefix = '',
  maxDepth = 2,
  currentDepth = 0
): Record<string, string> {
  const result: Record<string, string> = {}

  for (const [key, value] of Object.entries(obj)) {
    if (Object.keys(result).length >= 8) break
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
      result[fullKey] = str.length > 60 ? str.slice(0, 57) + '…' : str
    } else if (value !== null && value !== undefined) {
      const str = String(value)
      result[fullKey] = str.length > 60 ? str.slice(0, 57) + '…' : str
    }
  }

  return result
}

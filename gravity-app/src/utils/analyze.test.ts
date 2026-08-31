import { describe, expect, it } from 'vitest'
import { analyzeRecords } from './analyze'
import type { DataRecord } from '../types/data'

const records: DataRecord[] = [
  { id: '1', source: 'test', fields: { name: 'North', revenue: '100', segment: 'A' } },
  { id: '2', source: 'test', fields: { name: 'South', revenue: '200', segment: '' } },
]

describe('analyzeRecords', () => {
  it('calculates numeric statistics and dataset completeness', () => {
    const result = analyzeRecords(records)
    const revenue = result.fieldStats.find(field => field.key === 'revenue')

    expect(revenue).toMatchObject({ type: 'numeric', min: 100, max: 200, avg: 150, sum: 300 })
    expect(result.completenessPct).toBe(83)
    expect(result.labelField).toBe('name')
  })

  it('returns a safe empty analysis', () => {
    expect(analyzeRecords([])).toMatchObject({ recordCount: 0, completenessPct: 100 })
  })
})

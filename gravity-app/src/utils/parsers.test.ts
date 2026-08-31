import { describe, expect, it } from 'vitest'
import { parseCSV, parseJSON } from './parsers'

describe('parseCSV', () => {
  it('preserves commas, escaped quotes, and newlines inside quoted cells', () => {
    const records = parseCSV('name,notes\n"Doe, Jane","Said ""hello""\non Monday"')

    expect(records).toHaveLength(1)
    expect(records[0].fields).toEqual({
      name: 'Doe, Jane',
      notes: 'Said "hello"\non Monday',
    })
  })

  it('detects semicolon and tab-delimited data', () => {
    expect(parseCSV('name;score\nAda;42')[0].fields).toEqual({ name: 'Ada', score: '42' })
    expect(parseCSV('name\tscore\nGrace\t99')[0].fields).toEqual({ name: 'Grace', score: '99' })
  })

  it('keeps duplicate and blank headers addressable', () => {
    expect(parseCSV('name,name,\nAda,Lovelace,Math')[0].fields).toEqual({
      name: 'Ada',
      name_2: 'Lovelace',
      col3: 'Math',
    })
  })

  it('rejects unterminated quoted fields', () => {
    expect(() => parseCSV('name,notes\nAda,"unfinished')).toThrow('unterminated quoted field')
  })
})

describe('parseJSON', () => {
  it('extracts wrapped arrays and flattens nested objects without truncation', () => {
    const longValue = 'x'.repeat(100)
    const records = parseJSON(JSON.stringify({ data: [{ name: 'Ada', profile: { bio: longValue } }] }))

    expect(records[0].fields['profile.bio']).toBe(longValue)
  })
})

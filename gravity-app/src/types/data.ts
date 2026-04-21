/**
 * Data types shared across the data import system
 */

export interface DataRecord {
  id: string
  source: string           // e.g. "CSV Upload", "REST Countries", etc.
  fields: Record<string, string>  // key-value pairs from the data
  color?: string           // optional accent color for the card
}

export type DataSourcePreset = {
  id: string
  label: string
  description: string
  emoji: string
  url: string
  transform: (raw: unknown) => DataRecord[]
  color: string
}

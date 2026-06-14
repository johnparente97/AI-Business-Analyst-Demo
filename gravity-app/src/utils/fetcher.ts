/**
 * Online Data Fetcher
 *
 * Fetches data from curated free public APIs and custom URLs.
 * All presets use CORS-friendly endpoints (no API key required).
 * Custom URL fetch uses a CORS proxy for arbitrary endpoints.
 */

import type { DataRecord, DataSourcePreset } from '../types/data'
import { parseJSON } from './parsers'
import { nanoid } from './nanoid'

// ─── Curated API Presets ─────────────────────────────────────────────────────

export const DATA_PRESETS: DataSourcePreset[] = [
  {
    id: 'countries',
    label: 'World Countries',
    description: 'Population, capital & region',
    emoji: '🌍',
    color: '#7c3aed',
    url: 'https://restcountries.com/v3.1/all?fields=name,capital,region,population,area',
    transform: (raw) => {
      const arr = Array.isArray(raw) ? raw : []
      return arr
        .filter((c: Record<string, unknown>) => c.name && c.capital)
        .sort(() => Math.random() - 0.5)
        .slice(0, 15)
        .map((c: Record<string, unknown>) => {
          const name = (c.name as Record<string, string>)?.common ?? 'Unknown'
          const capital = Array.isArray(c.capital) ? (c.capital as string[])[0] : String(c.capital ?? '')
          return {
            id: nanoid(),
            source: 'World Countries',
            fields: {
              Country: name,
              Capital: capital,
              Region: String(c.region ?? ''),
              Population: Number(c.population ?? 0).toLocaleString(),
              'Area (km²)': Number(c.area ?? 0).toLocaleString(),
            },
            color: '#7c3aed',
          }
        })
    },
  },
  {
    id: 'posts',
    label: 'Blog Posts',
    description: 'Sample posts from JSONPlaceholder',
    emoji: '📝',
    color: '#0891b2',
    url: 'https://jsonplaceholder.typicode.com/posts',
    transform: (raw) => {
      const arr = Array.isArray(raw) ? raw.slice(0, 15) : []
      return arr.map((p: Record<string, unknown>) => ({
        id: nanoid(),
        source: 'Blog Posts',
        fields: {
          Title: String(p.title ?? '').slice(0, 50),
          Author: `User #${p.userId ?? '?'}`,
          Body: String(p.body ?? '').split('\n')[0].slice(0, 60) + '…',
          'Post #': String(p.id ?? ''),
        },
        color: '#0891b2',
      }))
    },
  },
  {
    id: 'users',
    label: 'User Profiles',
    description: 'Fake user data from JSONPlaceholder',
    emoji: '👤',
    color: '#059669',
    url: 'https://jsonplaceholder.typicode.com/users',
    transform: (raw) => {
      const arr = Array.isArray(raw) ? raw : []
      return arr.map((u: Record<string, unknown>) => {
        const address = u.address as Record<string, string> | undefined
        const company = u.company as Record<string, string> | undefined
        return {
          id: nanoid(),
          source: 'User Profiles',
          fields: {
            Name: String(u.name ?? ''),
            Email: String(u.email ?? ''),
            City: address?.city ?? '',
            Company: company?.name ?? '',
            Website: String(u.website ?? ''),
          },
          color: '#059669',
        }
      })
    },
  },
  {
    id: 'cat-facts',
    label: 'Cat Facts',
    description: 'Random interesting cat facts',
    emoji: '🐱',
    color: '#d97706',
    url: 'https://catfact.ninja/facts?limit=15',
    transform: (raw) => {
      const items = (raw as Record<string, unknown[]>)?.data ?? []
      return (items as Record<string, unknown>[]).map((f, i) => ({
        id: nanoid(),
        source: 'Cat Facts',
        fields: {
          '💡 Fact': String(f.fact ?? '').slice(0, 80) + (String(f.fact ?? '').length > 80 ? '…' : ''),
          '#': String(i + 1),
          Length: `${String(f.length ?? '')} chars`,
        },
        color: '#d97706',
      }))
    },
  },
  {
    id: 'space',
    label: 'Space Events',
    description: 'Upcoming SpaceX launches',
    emoji: '🚀',
    color: '#9333ea',
    url: 'https://api.spacexdata.com/v4/launches/upcoming',
    transform: (raw) => {
      const arr = Array.isArray(raw) ? raw.slice(0, 15) : []
      return arr.map((l: Record<string, unknown>) => ({
        id: nanoid(),
        source: 'Space Events',
        fields: {
          Mission: String(l.name ?? ''),
          Date: l.date_utc ? new Date(String(l.date_utc)).toLocaleDateString() : 'TBD',
          Details: String(l.details ?? 'No details available').slice(0, 60),
          Rocket: String(l.rocket ?? '').slice(0, 24),
        },
        color: '#9333ea',
      }))
    },
  },
  {
    id: 'crypto',
    label: 'Crypto Prices',
    description: 'Top cryptocurrencies by market cap',
    emoji: '₿',
    color: '#ea580c',
    url: 'https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&order=market_cap_desc&per_page=15&page=1',
    transform: (raw) => {
      const arr = Array.isArray(raw) ? raw : []
      return arr.map((c: Record<string, unknown>) => ({
        id: nanoid(),
        source: 'Crypto Prices',
        fields: {
          Coin: String(c.name ?? ''),
          Symbol: String(c.symbol ?? '').toUpperCase(),
          Price: `$${Number(c.current_price ?? 0).toLocaleString()}`,
          '24h Change': `${Number(c.price_change_percentage_24h ?? 0).toFixed(2)}%`,
          'Market Cap': `$${(Number(c.market_cap ?? 0) / 1e9).toFixed(1)}B`,
        },
        color: '#ea580c',
      }))
    },
  },
]

// ─── Fetcher Functions ────────────────────────────────────────────────────────

/**
 * Fetch data from a preset using its transform function.
 */
export async function fetchPreset(preset: DataSourcePreset): Promise<DataRecord[]> {
  const response = await fetch(preset.url, {
    headers: { Accept: 'application/json' },
    signal: AbortSignal.timeout(8000),
  })

  if (!response.ok) {
    throw new Error(`API returned ${response.status}: ${response.statusText}`)
  }

  const raw = await response.json()
  const records = preset.transform(raw)

  if (records.length === 0) {
    throw new Error('API returned no usable data')
  }

  return records
}

/**
 * Fetch JSON from an arbitrary URL.
 * Tries direct fetch first, then falls back to a CORS proxy.
 */
export async function fetchFromUrl(url: string): Promise<DataRecord[]> {
  // Validate URL
  let parsed: URL
  try {
    parsed = new URL(url)
  } catch {
    throw new Error('Invalid URL — please enter a full URL starting with https://')
  }

  if (!['http:', 'https:'].includes(parsed.protocol)) {
    throw new Error('Only HTTP/HTTPS URLs are supported')
  }

  // Reject dangerous protocols that could sneak through
  if (parsed.protocol === 'javascript:' || parsed.protocol === 'data:') {
    throw new Error('Unsupported URL protocol')
  }

  let text: string
  let directError: string | null = null

  try {
    // Try direct fetch first
    const resp = await fetch(url, {
      headers: { Accept: 'application/json' },
      signal: AbortSignal.timeout(8000),
    })
    if (!resp.ok) throw new Error(`HTTP ${resp.status}`)
    text = await resp.text()
  } catch (e: unknown) {
    directError = (e as Error).message ?? 'Unknown error'
    // Fall back to allOrigins CORS proxy
    try {
      const proxyUrl = `https://api.allorigins.win/get?url=${encodeURIComponent(url)}`
      const proxyResp = await fetch(proxyUrl, {
        signal: AbortSignal.timeout(10000),
      })
      if (!proxyResp.ok) throw new Error(`Proxy returned ${proxyResp.status}`)
      const proxyJson = await proxyResp.json() as { contents: string }
      text = proxyJson.contents
    } catch (proxyErr: unknown) {
      // Surface the original error with context about the proxy failure
      throw new Error(
        `Could not fetch data. Direct: ${directError}. CORS proxy also failed: ${(proxyErr as Error).message ?? 'Unknown error'}. ` +
        `Make sure the URL returns valid JSON.`
      )
    }
  }

  return parseJSON(text, parsed.hostname)
}


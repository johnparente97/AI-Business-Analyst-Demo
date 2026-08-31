/**
 * LandingView — Step 1
 * Clean, focused import screen. No clutter, one job.
 */

import { useState } from 'react'
import { Upload, Globe, ArrowRight, Database, Sparkles, FileText, ShieldCheck, Zap, BarChart3 } from 'lucide-react'
import { DATA_PRESETS, fetchPreset } from '../utils/fetcher'
import { fetchFromUrl } from '../utils/fetcher'
import type { DataRecord } from '../types/data'

interface Props {
  isDark: boolean
  onOpenImport: () => void
  onDataLoaded: (records: DataRecord[], source: string) => void
}

const FEATURED = ['countries', 'crypto', 'users', 'posts', 'space', 'cat-facts']

const DEMO_RECORDS: DataRecord[] = [
  ['Jan', '128400', '31.2', 'North America', 'Enterprise'],
  ['Feb', '141800', '33.7', 'Europe', 'Partner'],
  ['Mar', '139200', '32.9', 'Asia Pacific', 'Self-serve'],
  ['Apr', '158600', '36.1', 'North America', 'Enterprise'],
  ['May', '172300', '37.4', 'Europe', 'Partner'],
  ['Jun', '189700', '39.8', 'Asia Pacific', 'Enterprise'],
].map(([month, revenue, margin, region, channel], index) => ({
  id: `demo-${index + 1}`,
  source: 'Executive revenue demo',
  fields: { month, revenue, margin, region, channel },
  color: '#7c3aed',
}))

export function LandingView({ isDark: dk, onOpenImport, onDataLoaded }: Props) {
  const [loading, setLoading] = useState<string | null>(null)
  const [customUrl, setCustomUrl] = useState('')
  const [error, setError] = useState<string | null>(null)

  const featured = DATA_PRESETS.filter(p => FEATURED.includes(p.id))

  const loadPreset = async (id: string) => {
    const preset = DATA_PRESETS.find(p => p.id === id)
    if (!preset || loading) return
    setLoading(id)
    setError(null)
    try {
      const records = await fetchPreset(preset)
      onDataLoaded(records, `${preset.emoji} ${preset.label}`)
    } catch (e: unknown) {
      setError(`Couldn't load ${preset.label}. ${(e as Error).message}`)
    } finally { setLoading(null) }
  }

  const loadUrl = async () => {
    if (!customUrl.trim() || loading) return
    setLoading('url')
    setError(null)
    try {
      const records = await fetchFromUrl(customUrl.trim())
      let hostname = 'API'
      try { hostname = new URL(customUrl.trim()).hostname } catch { /* keep fallback */ }
      onDataLoaded(records, hostname)
    } catch (e: unknown) {
      setError((e as Error).message)
    } finally { setLoading(null) }
  }

  return (
    <main className={`relative min-h-screen overflow-hidden px-4 py-10 sm:py-16 transition-colors ${dk ? 'bg-[#09090b]' : 'bg-[#fcfbff]'}`}>
      <div aria-hidden="true" className="absolute inset-0 landing-grid opacity-50" />
      <div aria-hidden="true" className="absolute -top-40 left-1/2 h-96 w-96 -translate-x-1/2 rounded-full bg-violet-500/20 blur-3xl" />
      <div className="relative mx-auto flex max-w-6xl flex-col items-center">

      {/* Logo */}
      <div className="flex items-center gap-3 mb-8 animate-fade-in-up" style={{ animationDelay: '0s' }}>
        <div className="w-11 h-11 rounded-2xl bg-gradient-to-br from-violet-600 to-purple-600 flex items-center justify-center shadow-lg shadow-violet-500/30">
          <Sparkles size={20} className="text-white" />
        </div>
        <div>
          <h1 className={`text-lg font-bold ${dk ? 'text-zinc-100' : 'text-zinc-900'}`}>InsightBridge AI</h1>
          <p className={`text-xs ${dk ? 'text-zinc-500' : 'text-zinc-500'}`}>Decision intelligence, without the busywork</p>
        </div>
      </div>

      {/* Hero */}
      <div className="text-center max-w-3xl animate-fade-in-up" style={{ animationDelay: '0.06s' }}>
        <div className={`mx-auto mb-5 inline-flex items-center gap-2 rounded-full border px-3 py-1.5 text-xs font-semibold ${dk ? 'border-violet-500/20 bg-violet-500/10 text-violet-300' : 'border-violet-200 bg-violet-50 text-violet-700'}`}>
          <Zap size={12} /> Browser-native analytics in seconds
        </div>
        <h2 className={`text-4xl sm:text-6xl font-extrabold tracking-[-0.04em] leading-[1.05] mb-5 ${dk ? 'text-zinc-100' : 'text-zinc-950'}`}>
          From raw data to{' '}
          <span className="bg-gradient-to-r from-violet-600 via-fuchsia-500 to-cyan-500 bg-clip-text text-transparent">clear decisions.</span>
        </h2>
        <p className={`text-base leading-relaxed mb-8 ${dk ? 'text-zinc-400' : 'text-zinc-500'}`}>
          Profile a dataset, surface the signals that matter, and ask better questions—without spreadsheets, setup, or sending your file to a server.
        </p>

        {/* Primary CTA: Upload */}
        <button
          onClick={onOpenImport}
          className="
            group inline-flex items-center gap-3 px-8 py-4 rounded-2xl
            bg-gradient-to-r from-violet-600 to-purple-600
            text-white text-base font-bold
            shadow-xl shadow-violet-500/25
            hover:shadow-2xl hover:shadow-violet-500/35
            hover:scale-105 active:scale-95
            transition-all duration-200 mb-3
          "
        >
          <Upload size={18} className="group-hover:-translate-y-0.5 transition-transform" />
          Upload CSV or JSON
          <ArrowRight size={15} className="group-hover:translate-x-1 transition-transform" />
        </button>

        <button
          onClick={() => onDataLoaded(DEMO_RECORDS, '📈 Executive revenue demo')}
          className={`group ml-0 sm:ml-3 inline-flex items-center gap-2 px-6 py-4 rounded-2xl border text-sm font-bold transition-all hover:-translate-y-0.5 ${dk ? 'border-zinc-700 bg-zinc-900/70 text-zinc-200 hover:border-violet-600' : 'border-zinc-200 bg-white text-zinc-800 shadow-sm hover:border-violet-300 hover:shadow-md'}`}
        >
          <BarChart3 size={17} /> Explore the demo
        </button>

        <p className={`text-xs mb-1 ${dk ? 'text-zinc-600' : 'text-zinc-400'}`}>
          <ShieldCheck size={12} className="inline mr-1" /> Your uploaded files stay in this browser
        </p>
      </div>

      {/* URL fetch */}
      <div className="w-full max-w-md mt-6 animate-fade-in-up" style={{ animationDelay: '0.12s' }}>
        <div className={`flex gap-2 p-1.5 rounded-2xl border ${dk ? 'bg-[#111113] border-[#1f1f23]' : 'bg-gray-50 border-gray-200'}`}>
          <div className="flex items-center gap-2 flex-1 px-3">
            <Globe size={14} className={dk ? 'text-zinc-500' : 'text-zinc-400'} />
            <input
              type="url"
              value={customUrl}
              onChange={e => setCustomUrl(e.target.value)}
              onKeyDown={e => e.key === 'Enter' && loadUrl()}
              placeholder="Or paste any JSON API URL…"
              className={`flex-1 text-sm bg-transparent outline-none ${dk ? 'text-zinc-200 placeholder-zinc-600' : 'text-zinc-800 placeholder-zinc-400'}`}
            />
          </div>
          <button
            onClick={loadUrl}
            disabled={!customUrl.trim() || !!loading}
            className="px-4 py-2 rounded-xl bg-violet-600 text-white text-xs font-bold hover:bg-violet-500 transition-colors disabled:opacity-40"
          >
            {loading === 'url' ? '…' : 'Fetch'}
          </button>
        </div>
      </div>

      {error && (
        <p className="mt-3 text-xs text-red-500 text-center animate-fade-in-up max-w-sm">{error}</p>
      )}

      {/* Divider */}
      <div className="flex items-center gap-4 mt-8 mb-5 w-full max-w-lg animate-fade-in-up" style={{ animationDelay: '0.18s' }}>
        <div className={`flex-1 h-px ${dk ? 'bg-[#1f1f23]' : 'bg-gray-200'}`} />
        <span className={`text-xs font-semibold ${dk ? 'text-zinc-600' : 'text-zinc-400'}`}>or try a live dataset</span>
        <div className={`flex-1 h-px ${dk ? 'bg-[#1f1f23]' : 'bg-gray-200'}`} />
      </div>

      {/* Dataset grid */}
      <div className="grid grid-cols-3 sm:grid-cols-6 gap-2.5 w-full max-w-lg animate-fade-in-up" style={{ animationDelay: '0.22s' }}>
        {featured.map(preset => (
          <button
            key={preset.id}
            onClick={() => loadPreset(preset.id)}
            disabled={!!loading}
            className={`
              flex flex-col items-center gap-2 p-3 rounded-2xl border
              transition-all duration-200 hover:scale-105 active:scale-95
              disabled:opacity-50 disabled:cursor-not-allowed
              ${dk
                ? 'bg-[#111113] border-[#1f1f23] hover:border-violet-800'
                : 'bg-white border-gray-100 hover:border-violet-200 shadow-sm hover:shadow-md'
              }
            `}
          >
            {loading === preset.id
              ? <div className="w-6 h-6 border-2 border-violet-500 border-t-transparent rounded-full animate-spin" />
              : <span className="text-xl">{preset.emoji}</span>
            }
            <span className={`text-[10px] font-semibold text-center leading-tight ${dk ? 'text-zinc-400' : 'text-zinc-600'}`}>
              {preset.label}
            </span>
          </button>
        ))}
      </div>

      {/* Feature row */}
      <div className="flex flex-wrap justify-center gap-3 mt-8 max-w-md animate-fade-in-up" style={{ animationDelay: '0.28s' }}>
        {[
          { icon: <Sparkles size={11} />, label: 'AI expert analysis' },
          { icon: <FileText size={11} />, label: 'CSV & JSON' },
          { icon: <Globe size={11} />, label: 'Live APIs' },
          { icon: <Database size={11} />, label: 'Any field type' },
        ].map(({ icon, label }) => (
          <div key={label} className={`flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-medium border ${dk ? 'border-[#1f1f23] text-zinc-500' : 'border-gray-200 text-zinc-400'}`}>
            <span className="text-violet-500">{icon}</span>{label}
          </div>
        ))}
      </div>
      <p className={`mt-8 text-center text-[11px] ${dk ? 'text-zinc-700' : 'text-zinc-400'}`}>No account required · Works with CSV and JSON · AI is optional</p>
      </div>
    </main>
  )
}

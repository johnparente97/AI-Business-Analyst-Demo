/**
 * Dashboard — Analytics + AI Chat
 *
 * Layout:
 * ┌─────────────── Header ────────────────────────────────────┐
 * │ Left (2/3): Charts, Stat Cards, Category Bars             │
 * │ Right (1/3): AI Chat Panel (full height, sticky)         │
 * └────────────────────────────────────────────────────────────┘
 * Below: Data Table
 */

import { useState, useMemo } from 'react'
import {
  BarChart, Bar, XAxis, YAxis, Tooltip,
  ResponsiveContainer, Cell, CartesianGrid,
} from 'recharts'
import {
  RefreshCw, ArrowUp, ArrowDown, ArrowUpDown,
  Search, Database, TrendingUp, Hash, Tag, Key
} from 'lucide-react'
import type { DataInsights, FieldStat } from '../utils/analyze'
import type { DataRecord } from '../types/data'
import { ChatPanel } from './ChatPanel'
import { AISetupModal } from './AISetupModal'

const CHART_COLORS = [
  '#8b5cf6','#6366f1','#3b82f6','#06b6d4','#10b981',
  '#84cc16','#f59e0b','#f97316','#ef4444','#ec4899',
]

type SortDir = 'asc' | 'desc'

interface DashboardProps {
  records: DataRecord[]
  source: string
  insights: DataInsights
  isDark: boolean
  onChangeData: () => void
}

export function Dashboard({ records, source, insights, isDark, onChangeData }: DashboardProps) {
  const dk = isDark
  const [showAISetup, setShowAISetup] = useState(false)
  const [activeChartField, setActiveChartField] = useState<string>(
    insights.fieldStats.find(s => s.type === 'numeric' && s.chartBars?.length)?.key ?? ''
  )
  const [search, setSearch] = useState('')
  const [sortKey, setSortKey] = useState<string | null>(null)
  const [sortDir, setSortDir] = useState<SortDir>('asc')

  // Theme tokens
  const bg    = dk ? 'bg-[#09090b]'    : 'bg-gray-50'
  const card  = dk ? 'bg-[#111113] border-[#1f1f23]' : 'bg-white border-gray-100'
  const t1    = dk ? 'text-zinc-100'   : 'text-zinc-900'
  const t2    = dk ? 'text-zinc-400'   : 'text-zinc-500'
  const t3    = dk ? 'text-zinc-600'   : 'text-zinc-300'
  const bdr   = dk ? 'border-[#1f1f23]' : 'border-gray-100'
  const iBg   = dk ? 'bg-[#1a1a1e] border-[#2a2a30]' : 'bg-gray-50 border-gray-200'
  const hRow  = dk ? 'hover:bg-white/[0.04]' : 'hover:bg-violet-50/50'

  const numericFields = insights.fieldStats.filter(s => s.type === 'numeric')
  const catFields     = insights.fieldStats.filter(s => s.type === 'categorical')
  const tableKeys     = records[0] ? Object.keys(records[0].fields) : []

  // Table logic
  const filteredRecords = useMemo(() => {
    let rows = [...records]
    if (search.trim()) {
      const q = search.toLowerCase()
      rows = rows.filter(r => Object.values(r.fields).some(v => v.toLowerCase().includes(q)))
    }
    if (sortKey) {
      rows.sort((a, b) => {
        const av = a.fields[sortKey] ?? ''
        const bv = b.fields[sortKey] ?? ''
        const an = parseFloat(av.replace(/[$%,\s]/g, ''))
        const bn = parseFloat(bv.replace(/[$%,\s]/g, ''))
        const cmp = !isNaN(an) && !isNaN(bn) ? an - bn : av.localeCompare(bv)
        return sortDir === 'asc' ? cmp : -cmp
      })
    }
    return rows
  }, [records, search, sortKey, sortDir])

  const handleSort = (key: string) => {
    if (sortKey === key) setSortDir(d => d === 'asc' ? 'desc' : 'asc')
    else { setSortKey(key); setSortDir('asc') }
  }

  const chartData = useMemo(() => {
    const stat = insights.fieldStats.find(s => s.key === activeChartField)
    return stat?.chartBars?.map((b, i) => ({
      name: b.label,
      value: b.value,
      fill: CHART_COLORS[i % CHART_COLORS.length],
    })) ?? []
  }, [activeChartField, insights])

  return (
    <div className={`min-h-screen ${bg} transition-colors duration-300`}>

      {/* ── Sticky header ── */}
      <header className={`sticky top-0 z-40 flex items-center gap-3 px-4 sm:px-6 py-3 border-b backdrop-blur-xl ${dk ? 'bg-[#09090b]/90 border-[#1f1f23]' : 'bg-gray-50/90 border-gray-200'}`}>
        <div className="flex items-center gap-2.5 min-w-0 flex-1">
          <div className="w-8 h-8 rounded-xl bg-gradient-to-br from-violet-600 to-purple-600 flex items-center justify-center shrink-0">
            <Database size={14} className="text-white" />
          </div>
          <div className="min-w-0">
            <p className={`text-sm font-bold truncate ${t1}`}>{source}</p>
            <p className={`text-[11px] ${t2}`}>{records.length.toLocaleString()} records · {insights.fieldCount} fields</p>
          </div>
        </div>
        <div className="flex items-center gap-1.5">
          <button
            onClick={() => setShowAISetup(true)}
            className={`flex items-center gap-1.5 px-2.5 py-1.5 rounded-lg text-xs font-semibold transition-colors border ${
              dk
                ? 'text-zinc-400 border-[#2a2a30] hover:border-violet-700 hover:text-violet-400'
                : 'text-zinc-500 border-gray-200 hover:border-violet-300 hover:text-violet-600'
            }`}
          >
            <Key size={11} /> AI Model
          </button>
          <button
            onClick={onChangeData}
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold transition-colors border ${
              dk ? 'text-zinc-400 border-[#2a2a30] hover:border-[#3a3a40] hover:text-zinc-200' : 'text-zinc-500 border-gray-200 hover:text-zinc-700 hover:bg-gray-100'
            }`}
          >
            <RefreshCw size={11} /> New Dataset
          </button>
        </div>
      </header>

      {/* ── Main content ── */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6">

        {/* ── Row 1: Analytics + Chat side by side ── */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-5 pt-5">

          {/* Analytics left column — 2/3 */}
          <div className="lg:col-span-2 space-y-5">

            {/* Overview stat pills */}
            <div className="grid grid-cols-4 gap-3">
              <StatPill label="Records" value={records.length} color="violet" />
              <StatPill label="Fields" value={insights.fieldCount} color="blue" />
              <StatPill label="Numeric" value={numericFields.length} color="emerald" />
              <StatPill label="Category" value={catFields.length} color="amber" />
            </div>

            {/* Numeric stat cards */}
            {numericFields.length > 0 && (
              <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-3 gap-3">
                {numericFields.slice(0, 6).map(stat => (
                  <NumericCard key={stat.key} stat={stat} dk={dk} card={card} t1={t1} t2={t2} bdr={bdr} />
                ))}
              </div>
            )}

            {/* Bar chart */}
            {numericFields.length > 0 && chartData.length > 0 && (
              <div className={`rounded-2xl border ${card}`}>
                <div className={`flex flex-wrap items-center justify-between gap-2 px-4 py-3 border-b ${bdr}`}>
                  <div className="flex items-center gap-2">
                    <TrendingUp size={14} className="text-violet-500" />
                    <h2 className={`text-sm font-bold ${t1}`}>Top Values</h2>
                  </div>
                  <div className="flex gap-1 flex-wrap">
                    {numericFields.slice(0, 5).map(s => (
                      <button
                        key={s.key}
                        onClick={() => setActiveChartField(s.key)}
                        className={`px-2.5 py-1 rounded-lg text-[11px] font-semibold transition-colors ${
                          activeChartField === s.key
                            ? 'bg-violet-600 text-white'
                            : dk ? 'text-zinc-500 hover:text-zinc-300 hover:bg-white/10' : 'text-zinc-400 hover:text-zinc-600 hover:bg-gray-100'
                        }`}
                      >
                        {s.key.length > 12 ? s.key.slice(0, 11) + '…' : s.key}
                      </button>
                    ))}
                  </div>
                </div>
                <div className="p-4 h-56">
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={chartData} layout="vertical" margin={{ top: 4, right: 8, left: 0, bottom: 4 }}>
                      <CartesianGrid strokeDasharray="3 3" stroke={dk ? '#1f1f23' : '#f3f4f6'} horizontal={false} />
                      <XAxis
                        type="number"
                        tick={{ fontSize: 10, fill: dk ? '#52525b' : '#9ca3af' }}
                        tickFormatter={shortNum}
                      />
                      <YAxis
                        type="category"
                        dataKey="name"
                        width={75}
                        tick={{ fontSize: 11, fill: dk ? '#a1a1aa' : '#6b7280' }}
                      />
                      <Tooltip
                        contentStyle={{
                          background: dk ? '#18181b' : '#fff',
                          border: `1px solid ${dk ? '#27272a' : '#e5e7eb'}`,
                          borderRadius: 10,
                          fontSize: 12,
                          color: dk ? '#f4f4f5' : '#18181b',
                        }}
                        formatter={(v: unknown) => [shortNum(v as number), activeChartField]}
                      />
                      <Bar dataKey="value" radius={[0, 4, 4, 0]}>
                        {chartData.map((entry, i) => (
                          <Cell key={i} fill={entry.fill} fillOpacity={0.85} />
                        ))}
                      </Bar>
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              </div>
            )}

            {/* Category distributions */}
            {catFields.length > 0 && (
              <div className={`rounded-2xl border ${card}`}>
                <div className={`flex items-center gap-2 px-4 py-3 border-b ${bdr}`}>
                  <Tag size={14} className="text-violet-500" />
                  <h2 className={`text-sm font-bold ${t1}`}>Distributions</h2>
                </div>
                <div className="p-4 grid grid-cols-1 sm:grid-cols-2 gap-5">
                  {catFields.slice(0, 6).map(stat => (
                    <CatBar key={stat.key} stat={stat} dk={dk} t2={t2} />
                  ))}
                </div>
              </div>
            )}
          </div>

          {/* Chat Panel — 1/3, sticky */}
          <div className="lg:col-span-1">
            <div className="sticky top-[62px] h-[calc(100vh-82px)]">
              <ChatPanel
                records={records}
                source={source}
                insights={insights}
                isDark={dk}
                onNeedApiKey={() => setShowAISetup(true)}
              />
            </div>
          </div>
        </div>

        {/* ── Data Table ── */}
        <div className={`my-5 rounded-2xl border overflow-hidden ${card}`}>
          <div className={`flex flex-wrap items-center gap-3 px-4 py-3 border-b ${bdr}`}>
            <div className="flex items-center gap-2 flex-1">
              <Hash size={14} className="text-violet-500" />
              <h2 className={`text-sm font-bold ${t1}`}>All Records</h2>
              <span className={`text-xs px-2 py-0.5 rounded-full ${dk ? 'bg-white/10 text-zinc-400' : 'bg-gray-100 text-zinc-500'}`}>
                {filteredRecords.length.toLocaleString()}/{records.length.toLocaleString()}
              </span>
            </div>
            <div className={`flex items-center gap-2 px-3 py-1.5 rounded-xl border ${iBg}`}>
              <Search size={12} className={t2} />
              <input
                type="search"
                value={search}
                onChange={e => setSearch(e.target.value)}
                placeholder="Search all fields…"
                className={`w-40 text-xs outline-none bg-transparent ${t1}`}
              />
            </div>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-xs">
              <thead className={`sticky top-0 ${dk ? 'bg-[#111113]' : 'bg-gray-50'}`}>
                <tr>
                  <th className={`px-4 py-2.5 text-left text-[10px] font-bold uppercase tracking-wider ${t2}`}>#</th>
                  {tableKeys.map(key => (
                    <th
                      key={key}
                      onClick={() => handleSort(key)}
                      className={`px-4 py-2.5 text-left text-[10px] font-bold uppercase tracking-wider cursor-pointer whitespace-nowrap select-none transition-colors ${t2} hover:text-violet-500`}
                    >
                      <div className="flex items-center gap-1">
                        {key.length > 14 ? key.slice(0, 13) + '…' : key}
                        {sortKey === key
                          ? sortDir === 'asc' ? <ArrowUp size={9} className="text-violet-500" /> : <ArrowDown size={9} className="text-violet-500" />
                          : <ArrowUpDown size={9} className="opacity-25" />
                        }
                      </div>
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody className={`divide-y ${bdr}`}>
                {filteredRecords.length === 0 ? (
                  <tr>
                    <td colSpan={tableKeys.length + 1} className={`px-4 py-10 text-center text-sm ${t2}`}>
                      No records match your filter
                    </td>
                  </tr>
                ) : (
                  filteredRecords.map((record, i) => (
                    <tr key={record.id} className={`transition-colors ${hRow}`}>
                      <td className={`px-4 py-2.5 text-[11px] font-medium tabular-nums ${t3}`}>{i + 1}</td>
                      {tableKeys.map(key => (
                        <td key={key} className={`px-4 py-2.5 max-w-48 truncate ${t1}`}>
                          {record.fields[key] ?? <span className={t3}>—</span>}
                        </td>
                      ))}
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>
      </div>

      {showAISetup && <AISetupModal isDark={dk} onClose={() => setShowAISetup(false)} />}
    </div>
  )
}

// ─── Sub-components ───────────────────────────────────────────────────────────

function StatPill({ label, value, color }: {
  label: string; value: number; color: string
}) {
  const colors: Record<string, string> = {
    violet: 'text-violet-500 bg-violet-500/10',
    blue: 'text-blue-500 bg-blue-500/10',
    emerald: 'text-emerald-500 bg-emerald-500/10',
    amber: 'text-amber-500 bg-amber-500/10',
  }
  return (
    <div className={`flex flex-col items-center justify-center p-3 rounded-2xl ${colors[color]} transition-transform hover:scale-105`}>
      <span className="text-xl font-extrabold leading-none">{value.toLocaleString()}</span>
      <span className="text-[10px] font-semibold mt-1 opacity-70">{label}</span>
    </div>
  )
}

function NumericCard({ stat, dk, card, t1, t2, bdr }: {
  stat: FieldStat; dk: boolean; card: string; t1: string; t2: string; bdr: string
}) {
  const pct = stat.max && stat.min !== undefined && stat.max !== stat.min
    ? Math.round(((stat.avg ?? 0) - stat.min) / (stat.max - stat.min) * 100)
    : 50
  return (
    <div className={`rounded-2xl border p-4 ${card}`}>
      <p className={`text-[10px] font-bold uppercase tracking-wider truncate mb-3 ${t2}`}>{stat.key}</p>
      <div className="space-y-2">
        <div className="flex justify-between items-center">
          <span className={`text-[11px] flex items-center gap-1 text-emerald-500`}><ArrowUp size={9} />Max</span>
          <span className={`text-sm font-extrabold ${t1}`}>{shortNum(stat.max ?? 0)}</span>
        </div>
        {/* Average bar */}
        <div>
          <div className="flex justify-between items-center mb-1">
            <span className={`text-[11px] ${t2}`}>Avg</span>
            <span className="text-sm font-bold text-violet-500">{shortNum(stat.avg ?? 0)}</span>
          </div>
          <div className={`h-1.5 rounded-full overflow-hidden ${dk ? 'bg-white/10' : 'bg-gray-100'}`}>
            <div
              className="h-full rounded-full bg-gradient-to-r from-violet-500 to-purple-400"
              style={{ width: `${Math.max(4, pct)}%` }}
            />
          </div>
        </div>
        <div className="flex justify-between items-center">
          <span className={`text-[11px] flex items-center gap-1 text-rose-500`}><ArrowDown size={9} />Min</span>
          <span className={`text-sm font-extrabold ${t1}`}>{shortNum(stat.min ?? 0)}</span>
        </div>
      </div>
      {stat.maxLabel && (
        <p className={`text-[10px] truncate mt-2 pt-2 border-t ${bdr} ${t2}`}>
          ↑ {stat.maxLabel}
        </p>
      )}
    </div>
  )
}

function CatBar({ stat, dk, t2 }: { stat: FieldStat; dk: boolean; t2: string }) {
  const top = stat.topValues?.slice(0, 6) ?? []
  const maxPct = top[0]?.pct ?? 1
  return (
    <div>
      <p className={`text-[10px] font-bold uppercase tracking-wider mb-2.5 ${t2}`}>{stat.key}</p>
      <div className="space-y-2">
        {top.map(({ value, pct }) => (
          <div key={value}>
            <div className="flex justify-between items-center mb-0.5">
              <span className={`text-[11px] truncate max-w-[70%] ${dk ? 'text-zinc-300' : 'text-zinc-700'}`}>{value}</span>
              <span className="text-[11px] font-bold text-violet-500">{pct}%</span>
            </div>
            <div className={`h-1.5 rounded-full overflow-hidden ${dk ? 'bg-white/10' : 'bg-gray-100'}`}>
              <div
                className="h-full rounded-full bg-gradient-to-r from-violet-500 to-purple-400 transition-all duration-700"
                style={{ width: `${Math.max(4, (pct / maxPct) * 100)}%` }}
              />
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}

function shortNum(n: number): string {
  if (Math.abs(n) >= 1e9) return `${(n / 1e9).toFixed(1)}B`
  if (Math.abs(n) >= 1e6) return `${(n / 1e6).toFixed(1)}M`
  if (Math.abs(n) >= 1e3) return `${(n / 1e3).toFixed(1)}K`
  return n % 1 === 0 ? n.toLocaleString() : n.toFixed(2)
}

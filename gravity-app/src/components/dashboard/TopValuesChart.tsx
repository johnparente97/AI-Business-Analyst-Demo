import { useMemo } from 'react'
import {
  BarChart, Bar, XAxis, YAxis, Tooltip,
  ResponsiveContainer, Cell, CartesianGrid,
} from 'recharts'
import { TrendingUp } from 'lucide-react'
import type { DataInsights } from '../../utils/analyze'
import { formatNum } from '../../utils/format'
import { useTheme } from '../../hooks/useTheme'

const CHART_COLORS = [
  '#8b5cf6','#6366f1','#3b82f6','#06b6d4','#10b981',
  '#84cc16','#f59e0b','#f97316','#ef4444','#ec4899',
]

interface TopValuesChartProps {
  insights: DataInsights
  activeChartField: string
  setActiveChartField: (key: string) => void
  isDark: boolean
}

export function TopValuesChart({
  insights, activeChartField, setActiveChartField, isDark
}: TopValuesChartProps) {
  const { dk, card, t1, bdr } = { dk: isDark, ...useTheme(isDark) }
  const numericFields = insights.fieldStats.filter(s => s.type === 'numeric')

  const chartData = useMemo(() => {
    const stat = insights.fieldStats.find(s => s.key === activeChartField)
    return stat?.chartBars?.map((b, i) => ({
      name: b.label,
      value: b.value,
      fill: CHART_COLORS[i % CHART_COLORS.length],
    })) ?? []
  }, [activeChartField, insights])

  if (numericFields.length === 0 || chartData.length === 0) return null

  return (
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
              tickFormatter={formatNum}
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
              formatter={(v: unknown) => [formatNum(v as number), activeChartField]}
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
  )
}

import { ArrowUp, ArrowDown } from 'lucide-react'
import type { FieldStat } from '../../utils/analyze'
import { formatNum } from '../../utils/format'
import { useTheme } from '../../hooks/useTheme'

interface NumericCardProps {
  stat: FieldStat
  isDark: boolean
}

export function NumericCard({ stat, isDark }: NumericCardProps) {
  const { dk, card, t1, t2, bdr } = { dk: isDark, ...useTheme(isDark) }

  const pct = stat.max && stat.min !== undefined && stat.max !== stat.min
    ? Math.round(((stat.avg ?? 0) - stat.min) / (stat.max - stat.min) * 100)
    : 50

  return (
    <div className={`rounded-2xl border p-4 ${card}`}>
      <p className={`text-[10px] font-bold uppercase tracking-wider truncate mb-3 ${t2}`}>{stat.key}</p>
      <div className="space-y-2">
        <div className="flex justify-between items-center">
          <span className={`text-[11px] flex items-center gap-1 text-emerald-500`}><ArrowUp size={9} />Max</span>
          <span className={`text-sm font-extrabold ${t1}`}>{formatNum(stat.max ?? 0)}</span>
        </div>
        {/* Average bar */}
        <div>
          <div className="flex justify-between items-center mb-1">
            <span className={`text-[11px] ${t2}`}>Avg</span>
            <span className="text-sm font-bold text-violet-500">{formatNum(stat.avg ?? 0)}</span>
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
          <span className={`text-sm font-extrabold ${t1}`}>{formatNum(stat.min ?? 0)}</span>
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

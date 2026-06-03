import type { FieldStat } from '../../utils/analyze'
import { useTheme } from '../../hooks/useTheme'

interface CatBarProps {
  stat: FieldStat
  isDark: boolean
}

export function CatBar({ stat, isDark }: CatBarProps) {
  const { dk, t2 } = { dk: isDark, ...useTheme(isDark) }

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

import { Database, RefreshCw, Key } from 'lucide-react'
import type { DataInsights } from '../../utils/analyze'
import type { DataRecord } from '../../types/data'
import { useTheme } from '../../hooks/useTheme'

interface DashboardHeaderProps {
  source: string
  records: DataRecord[]
  insights: DataInsights
  isDark: boolean
  onNeedApiKey: () => void
  onChangeData: () => void
}

export function DashboardHeader({
  source, records, insights, isDark, onNeedApiKey, onChangeData
}: DashboardHeaderProps) {
  const { dk, t1, t2 } = { dk: isDark, ...useTheme(isDark) }

  return (
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
          onClick={onNeedApiKey}
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
  )
}

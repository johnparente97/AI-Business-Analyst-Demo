import { useState } from 'react'
import type { DataInsights } from '../utils/analyze'
import type { DataRecord } from '../types/data'
import { ChatPanel } from './ChatPanel'
import { AISetupModal } from './AISetupModal'
import { useTheme } from '../hooks/useTheme'
import { DashboardHeader } from './dashboard/DashboardHeader'
import { StatPills } from './dashboard/StatPills'
import { NumericCard } from './dashboard/NumericCard'
import { CatBar } from './dashboard/CatBar'
import { TopValuesChart } from './dashboard/TopValuesChart'
import { DataTable } from './dashboard/DataTable'

interface DashboardProps {
  records: DataRecord[]
  source: string
  insights: DataInsights
  isDark: boolean
  onChangeData: () => void
}

export function Dashboard({ records, source, insights, isDark, onChangeData }: DashboardProps) {
  const { bg } = useTheme(isDark)
  const [showAISetup, setShowAISetup] = useState(false)

  const numericFields = insights.fieldStats.filter(s => s.type === 'numeric')
  const catFields = insights.fieldStats.filter(s => s.type === 'categorical')

  const [activeChartField, setActiveChartField] = useState<string>(
    numericFields.find(s => s.chartBars?.length)?.key ?? ''
  )

  return (
    <div className={`min-h-screen ${bg} transition-colors duration-300`}>
      <DashboardHeader
        source={source}
        records={records}
        insights={insights}
        isDark={isDark}
        onNeedApiKey={() => setShowAISetup(true)}
        onChangeData={onChangeData}
      />

      <div className="max-w-7xl mx-auto px-4 sm:px-6">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-5 pt-5">
          {/* Analytics left column — 2/3 */}
          <div className="lg:col-span-2 space-y-5">
            <StatPills
              recordsCount={records.length}
              fieldCount={insights.fieldCount}
              numericCount={numericFields.length}
              catCount={catFields.length}
            />

            {numericFields.length > 0 && (
              <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-3 gap-3">
                {numericFields.slice(0, 6).map(stat => (
                  <NumericCard key={stat.key} stat={stat} isDark={isDark} />
                ))}
              </div>
            )}

            <TopValuesChart
              insights={insights}
              activeChartField={activeChartField}
              setActiveChartField={setActiveChartField}
              isDark={isDark}
            />

            {catFields.length > 0 && (
              <div className={`rounded-2xl border ${isDark ? 'bg-[#111113] border-[#1f1f23]' : 'bg-white border-gray-100'}`}>
                <div className={`flex items-center gap-2 px-4 py-3 border-b ${isDark ? 'border-[#1f1f23]' : 'border-gray-100'}`}>
                  <h2 className={`text-sm font-bold ${isDark ? 'text-zinc-100' : 'text-zinc-900'}`}>Distributions</h2>
                </div>
                <div className="p-4 grid grid-cols-1 sm:grid-cols-2 gap-5">
                  {catFields.slice(0, 6).map(stat => (
                    <CatBar key={stat.key} stat={stat} isDark={isDark} />
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
                isDark={isDark}
                onNeedApiKey={() => setShowAISetup(true)}
              />
            </div>
          </div>
        </div>

        <DataTable records={records} isDark={isDark} />
      </div>

      {showAISetup && <AISetupModal isDark={isDark} onClose={() => setShowAISetup(false)} />}
    </div>
  )
}

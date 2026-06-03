/**
 * App — DataInsight AI
 *
 * Clean 2-screen flow:
 *   Landing  → import data
 *   Dashboard → analytics + AI insights
 *
 * No physics. No complexity. Data first.
 */

import { useEffect, useMemo } from 'react'
import { useAppStore } from './store/useAppStore'
import { analyzeRecords } from './utils/analyze'
import { LandingView } from './components/LandingView'
import { Dashboard } from './components/Dashboard'
import { DataImportPanel } from './components/DataImportPanel'
import ErrorBoundary from './components/ErrorBoundary'
import type { DataRecord } from './types/data'

export default function App() {
  const {
    screen,
    records,
    source,
    isDataPanelOpen,
    isDarkMode,
    setRecords,
    clearRecords,
    setDataPanelOpen,
    toggleDarkMode,
  } = useAppStore()

  // Dark mode body class
  useEffect(() => {
    document.body.classList.toggle('dark', isDarkMode)
  }, [isDarkMode])

  // Escape key closes panel
  useEffect(() => {
    const handler = (e: KeyboardEvent) => {
      if (e.key === 'Escape') setDataPanelOpen(false)
    }
    window.addEventListener('keydown', handler)
    return () => window.removeEventListener('keydown', handler)
  }, [setDataPanelOpen])

  const handleDataLoaded = (newRecords: DataRecord[], newSource: string) => {
    setRecords(newRecords, newSource)
    setDataPanelOpen(false)
  }

  const handleChangeData = () => {
    setDataPanelOpen(true)
  }

  const handleClear = () => {
    clearRecords()
    setDataPanelOpen(false)
  }

  // Compute insights — memoised so it only re-runs when records change
  const insights = useMemo(() => analyzeRecords(records), [records])

  return (
    <ErrorBoundary>
      {/* Dark mode toggle — always top-right */}
      <button
        onClick={toggleDarkMode}
        className={`
          fixed top-4 right-4 z-[100]
          w-9 h-9 rounded-xl flex items-center justify-center text-base
          border transition-all duration-200 hover:scale-110
          ${isDarkMode
            ? 'bg-[#111113] border-[#2a2a30] hover:border-violet-700'
            : 'bg-white border-gray-200 shadow-sm hover:shadow-md'
          }
        `}
        title="Toggle dark mode"
        aria-label="Toggle dark mode"
      >
        {isDarkMode ? '☀️' : '🌙'}
      </button>

      {/* ── Screen: Landing ── */}
      {screen === 'landing' && (
        <LandingView
          isDark={isDarkMode}
          onOpenImport={() => setDataPanelOpen(true)}
          onDataLoaded={handleDataLoaded}
        />
      )}

      {/* ── Screen: Dashboard ── */}
      {screen === 'dashboard' && records.length > 0 && (
        <Dashboard
          records={records}
          source={source ?? 'Dataset'}
          insights={insights}
          isDark={isDarkMode}
          onChangeData={handleChangeData}
        />
      )}

      {/* ── Data Import Panel — overlays any screen ── */}
      {isDataPanelOpen && (
        <DataImportPanel
          onImport={handleDataLoaded}
          onClose={() => setDataPanelOpen(false)}
          isDark={isDarkMode}
          existingRecords={records}
          existingSource={source}
          onClear={handleClear}
        />
      )}
    </ErrorBoundary>
  )
}

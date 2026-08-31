/**
 * DataImportPanel Component
 *
 * A full-featured slide-up panel with 3 tabs:
 * 1. Upload  — drag-and-drop or file picker for CSV/JSON
 * 2. Online  — curated API presets + custom URL input
 * 3. Preview — table of imported records before spawning
 */

import { useState, useRef, useCallback, useEffect } from 'react'
import {
  X, Upload, Globe, Table, RefreshCw, ChevronRight,
  FileText, Link, Trash2, Play, AlertCircle, Check,
} from 'lucide-react'
import { parseCSV, parseJSON } from '../utils/parsers'
import { fetchPreset, fetchFromUrl, DATA_PRESETS } from '../utils/fetcher'
import type { DataRecord } from '../types/data'

interface DataImportPanelProps {
  onImport: (records: DataRecord[], source: string) => void
  onClose: () => void
  isDark: boolean
  existingRecords: DataRecord[]
  existingSource: string | null
  onClear: () => void
}

type Tab = 'upload' | 'online' | 'preview'
type FetchStatus = 'idle' | 'loading' | 'success' | 'error'

export function DataImportPanel({
  onImport,
  onClose,
  isDark,
  existingRecords,
  existingSource,
  onClear,
}: DataImportPanelProps) {
  const [activeTab, setActiveTab] = useState<Tab>(existingRecords.length > 0 ? 'preview' : 'upload')
  const [dragOver, setDragOver] = useState(false)
  const [parseError, setParseError] = useState<string | null>(null)
  const [previewRecords, setPreviewRecords] = useState<DataRecord[]>(existingRecords)
  const [previewSource, setPreviewSource] = useState<string | null>(existingSource)
  const [fetchStatus, setFetchStatus] = useState<Record<string, FetchStatus>>({})
  const [customUrl, setCustomUrl] = useState('')
  const [customFetchStatus, setCustomFetchStatus] = useState<FetchStatus>('idle')
  const [customError, setCustomError] = useState<string | null>(null)
  const fileInputRef = useRef<HTMLInputElement>(null)

  // Close on Escape
  useEffect(() => {
    const handler = (e: KeyboardEvent) => { if (e.key === 'Escape') onClose() }
    window.addEventListener('keydown', handler)
    return () => window.removeEventListener('keydown', handler)
  }, [onClose])

  // ─── File Processing ──────────────────────────────────────────────────────

  const processFile = useCallback(async (file: File) => {
    setParseError(null)
    const isCSV = file.name.toLowerCase().endsWith('.csv') || file.type === 'text/csv'
    const isJSON = file.name.toLowerCase().endsWith('.json') || file.type === 'application/json'

    if (!isCSV && !isJSON) {
      setParseError('Unsupported file type. Please upload a .csv or .json file.')
      return
    }

    try {
      const text = await file.text()
      const records = isCSV
        ? parseCSV(text, file.name.replace(/\.(csv|json)$/i, ''))
        : parseJSON(text, file.name.replace(/\.(csv|json)$/i, ''))

      setPreviewRecords(records)
      setPreviewSource(`📁 ${file.name}`)
      setActiveTab('preview')
    } catch (e) {
      setParseError(e instanceof Error ? e.message : 'Could not parse file')
    }
  }, [])

  const handleFileDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    setDragOver(false)
    const file = e.dataTransfer.files[0]
    if (file) processFile(file)
  }, [processFile])

  const handleFileChange = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (file) processFile(file)
  }, [processFile])

  // ─── Preset Fetch ─────────────────────────────────────────────────────────

  const handlePresetFetch = useCallback(async (presetId: string) => {
    const preset = DATA_PRESETS.find((p) => p.id === presetId)
    if (!preset) return

    setFetchStatus((s) => ({ ...s, [presetId]: 'loading' }))
    try {
      const records = await fetchPreset(preset)
      setPreviewRecords(records)
      setPreviewSource(`${preset.emoji} ${preset.label}`)
      setFetchStatus((s) => ({ ...s, [presetId]: 'success' }))
      setActiveTab('preview')
    } catch (e) {
      setFetchStatus((s) => ({ ...s, [presetId]: 'error' }))
      console.error('Preset fetch failed:', e)
    }
  }, [])

  // ─── Custom URL Fetch ─────────────────────────────────────────────────────

  const handleCustomFetch = useCallback(async () => {
    if (!customUrl.trim()) return
    setCustomFetchStatus('loading')
    setCustomError(null)
    try {
      const records = await fetchFromUrl(customUrl.trim())
      setPreviewRecords(records)
      setPreviewSource(`🔗 ${new URL(customUrl.trim()).hostname}`)
      setCustomFetchStatus('success')
      setActiveTab('preview')
    } catch (e) {
      setCustomFetchStatus('error')
      setCustomError(e instanceof Error ? e.message : 'Fetch failed')
    }
  }, [customUrl])

  // ─── Import ───────────────────────────────────────────────────────────────

  const handleImport = useCallback(() => {
    if (previewRecords.length > 0 && previewSource) {
      onImport(previewRecords, previewSource)
      onClose()
    }
  }, [previewRecords, previewSource, onImport, onClose])

  // ─── Shared styles ────────────────────────────────────────────────────────

  const tabClass = (tab: Tab) => `
    flex items-center gap-1.5 px-4 py-2 rounded-lg text-sm font-semibold transition-all duration-200
    ${activeTab === tab
      ? 'bg-purple-600 text-white shadow-md shadow-purple-500/30'
      : `${isDark ? 'text-gray-400 hover:text-gray-200' : 'text-gray-500 hover:text-gray-700'} hover:bg-gray-100 dark:hover:bg-gray-800`
    }
  `

  const cardBase = isDark
    ? 'bg-gray-800/80 border border-gray-700'
    : 'bg-white border border-gray-200'

  return (
    // Backdrop
    <div
      className="fixed inset-0 z-[200] flex items-end justify-center sm:items-center"
      onClick={(e) => { if (e.target === e.currentTarget) onClose() }}
    >
      <div className="absolute inset-0 bg-black/40 backdrop-blur-sm" onClick={onClose} />

      {/* Panel */}
      <div
        role="dialog"
        aria-modal="true"
        aria-labelledby="import-data-title"
        className={`
          relative z-10 w-full sm:max-w-2xl sm:mx-4
          rounded-t-3xl sm:rounded-3xl flex flex-col
          max-h-[88vh] overflow-hidden
          shadow-2xl shadow-black/30
          ${isDark ? 'bg-gray-900 border border-gray-800' : 'bg-gray-50 border border-gray-200'}
          animate-fade-in-up
        `}
        style={{ animationDuration: '0.35s' }}
      >
        {/* Header */}
        <div className={`flex items-center justify-between px-6 pt-6 pb-4 border-b ${isDark ? 'border-gray-800' : 'border-gray-200'}`}>
          <div>
            <h2 id="import-data-title" className={`text-lg font-bold ${isDark ? 'text-white' : 'text-gray-900'}`}>
              Import Data
            </h2>
            <p className={`text-xs mt-0.5 ${isDark ? 'text-gray-500' : 'text-gray-400'}`}>
              Upload files or connect to online sources to start analyzing.
            </p>
          </div>
          <button
            onClick={onClose}
            className={`flex items-center justify-center w-9 h-9 rounded-xl transition-colors ${
              isDark ? 'hover:bg-gray-800 text-gray-400 hover:text-gray-200' : 'hover:bg-gray-100 text-gray-400 hover:text-gray-700'
            }`}
            aria-label="Close panel"
          >
            <X size={18} />
          </button>
        </div>

        {/* Tab bar */}
        <div className={`flex gap-1 px-6 py-3 ${isDark ? 'bg-gray-900' : 'bg-gray-50'}`}>
          <button className={tabClass('upload')} onClick={() => setActiveTab('upload')} aria-pressed={activeTab === 'upload'}>
            <Upload size={14} />
            <span>Upload</span>
          </button>
          <button className={tabClass('online')} onClick={() => setActiveTab('online')} aria-pressed={activeTab === 'online'}>
            <Globe size={14} />
            <span>Online</span>
          </button>
          <button
            className={tabClass('preview')}
            onClick={() => setActiveTab('preview')}
            aria-pressed={activeTab === 'preview'}
          >
            <Table size={14} />
            <span>Preview</span>
            {previewRecords.length > 0 && (
              <span className="ml-1 bg-purple-500 text-white text-[10px] px-1.5 py-0.5 rounded-full font-bold leading-none">
                {previewRecords.length}
              </span>
            )}
          </button>
        </div>

        {/* Tab content */}
        <div className="flex-1 overflow-y-auto px-6 pb-6 space-y-4">

          {/* ── Upload Tab ── */}
          {activeTab === 'upload' && (
            <div className="space-y-4 pt-2">
              {/* Drop zone */}
              <div
                onDragOver={(e) => { e.preventDefault(); setDragOver(true) }}
                onDragLeave={() => setDragOver(false)}
                onDrop={handleFileDrop}
                onClick={() => fileInputRef.current?.click()}
                className={`
                  relative flex flex-col items-center justify-center gap-3
                  py-12 px-8 rounded-2xl border-2 border-dashed cursor-pointer
                  transition-all duration-200
                  ${dragOver
                    ? 'border-purple-500 bg-purple-50 dark:bg-purple-900/20 scale-[1.01]'
                    : isDark
                      ? 'border-gray-700 hover:border-purple-600 hover:bg-gray-800/50'
                      : 'border-gray-200 hover:border-purple-300 hover:bg-purple-50/50'
                  }
                `}
              >
                <div className={`flex items-center justify-center w-14 h-14 rounded-2xl ${
                  dragOver ? 'bg-purple-500' : isDark ? 'bg-gray-800' : 'bg-white'
                } shadow-md transition-colors duration-200`}>
                  <Upload size={24} className={dragOver ? 'text-white' : 'text-purple-500'} />
                </div>
                <div className="text-center">
                  <p className={`font-semibold ${isDark ? 'text-gray-200' : 'text-gray-700'}`}>
                    {dragOver ? 'Drop to import!' : 'Drop your file here'}
                  </p>
                  <p className={`text-sm mt-1 ${isDark ? 'text-gray-500' : 'text-gray-400'}`}>
                    or <span className="text-purple-500 font-medium">click to browse</span>
                  </p>
                  <p className={`text-xs mt-2 ${isDark ? 'text-gray-600' : 'text-gray-400'}`}>
                    Supports .CSV and .JSON • Up to 15 rows displayed
                  </p>
                </div>
                <input
                  ref={fileInputRef}
                  type="file"
                  accept=".csv,.json,text/csv,application/json"
                  className="sr-only"
                  onChange={handleFileChange}
                />
              </div>

              {/* Parse error */}
              {parseError && (
                <div className="flex items-start gap-3 p-4 rounded-xl bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800">
                  <AlertCircle size={16} className="text-red-500 mt-0.5 shrink-0" />
                  <div>
                    <p className="text-sm font-semibold text-red-700 dark:text-red-400">Parse Error</p>
                    <p className="text-xs text-red-600 dark:text-red-500 mt-0.5">{parseError}</p>
                  </div>
                </div>
              )}

              {/* Format guide */}
              <div className={`grid grid-cols-2 gap-3`}>
                {[
                  {
                    icon: <FileText size={16} className="text-green-500" />,
                    label: 'CSV Format',
                    example: 'name,age,city\nAlice,30,NYC\nBob,25,LA',
                  },
                  {
                    icon: <FileText size={16} className="text-blue-500" />,
                    label: 'JSON Format',
                    example: '[{"name":"Alice",\n  "age":30},\n {"name":"Bob"}]',
                  },
                ].map(({ icon, label, example }) => (
                  <div key={label} className={`p-3 rounded-xl ${cardBase}`}>
                    <div className="flex items-center gap-2 mb-2">
                      {icon}
                      <span className={`text-xs font-semibold ${isDark ? 'text-gray-300' : 'text-gray-600'}`}>{label}</span>
                    </div>
                    <pre className={`text-[10px] font-mono rounded p-1.5 overflow-hidden leading-relaxed ${
                      isDark ? 'bg-gray-900 text-gray-400' : 'bg-gray-50 text-gray-500'
                    }`}>
                      {example}
                    </pre>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* ── Online Tab ── */}
          {activeTab === 'online' && (
            <div className="space-y-4 pt-2">
              {/* Custom URL */}
              <div className={`p-4 rounded-2xl ${cardBase} space-y-3`}>
                <div className="flex items-center gap-2">
                  <Link size={15} className="text-purple-500" />
                  <span className={`text-sm font-semibold ${isDark ? 'text-gray-200' : 'text-gray-700'}`}>
                    Fetch from URL
                  </span>
                </div>
                <div className="flex gap-2">
                  <input
                    type="url"
                    value={customUrl}
                    onChange={(e) => { setCustomUrl(e.target.value); setCustomFetchStatus('idle'); setCustomError(null) }}
                    onKeyDown={(e) => { if (e.key === 'Enter') handleCustomFetch() }}
                    placeholder="https://api.example.com/data.json"
                    className={`
                      flex-1 px-3 py-2 rounded-xl text-sm font-mono outline-none border
                      transition-colors duration-200
                      ${isDark
                        ? 'bg-gray-900 border-gray-700 text-gray-200 placeholder:text-gray-600 focus:border-purple-500'
                        : 'bg-white border-gray-200 text-gray-800 placeholder:text-gray-400 focus:border-purple-400'
                      }
                    `}
                  />
                  <button
                    onClick={handleCustomFetch}
                    disabled={!customUrl.trim() || customFetchStatus === 'loading'}
                    className="
                      flex items-center gap-1.5 px-4 py-2 rounded-xl
                      bg-purple-600 text-white text-sm font-semibold
                      hover:bg-purple-700 active:scale-95 transition-all duration-150
                      disabled:opacity-50 disabled:cursor-not-allowed
                      shadow-md shadow-purple-500/30
                    "
                  >
                    {customFetchStatus === 'loading'
                      ? <RefreshCw size={14} className="animate-spin" />
                      : <ChevronRight size={14} />
                    }
                    {customFetchStatus === 'loading' ? 'Fetching…' : 'Fetch'}
                  </button>
                </div>
                {customError && (
                  <p className="text-xs text-red-500 dark:text-red-400 flex items-center gap-1">
                    <AlertCircle size={12} /> {customError}
                  </p>
                )}
                <p className={`text-xs ${isDark ? 'text-gray-600' : 'text-gray-400'}`}>
                  Must return a JSON array or an object with a data/results array. CORS proxy applied automatically.
                </p>
              </div>

              {/* Preset grid */}
              <div>
                <p className={`text-xs font-semibold uppercase tracking-wider mb-3 ${isDark ? 'text-gray-500' : 'text-gray-400'}`}>
                  Quick Load
                </p>
                <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
                  {DATA_PRESETS.map((preset) => {
                    const status = fetchStatus[preset.id] ?? 'idle'
                    return (
                      <button
                        key={preset.id}
                        onClick={() => handlePresetFetch(preset.id)}
                        disabled={status === 'loading'}
                        className={`
                          group relative flex flex-col gap-1.5 p-3 rounded-xl text-left
                          border transition-all duration-200
                          hover:scale-[1.02] active:scale-[0.98]
                          disabled:opacity-70 disabled:cursor-not-allowed
                          ${isDark
                            ? 'bg-gray-800 border-gray-700 hover:border-purple-600'
                            : 'bg-white border-gray-200 hover:border-purple-300 hover:shadow-md'
                          }
                          ${status === 'success' ? 'ring-2 ring-green-400/50' : ''}
                          ${status === 'error' ? 'ring-2 ring-red-400/50' : ''}
                        `}
                      >
                        <div className="flex items-center justify-between">
                          <span className="text-2xl">{preset.emoji}</span>
                          {status === 'loading' && <RefreshCw size={12} className="text-purple-500 animate-spin" />}
                          {status === 'success' && <Check size={12} className="text-green-500" />}
                          {status === 'error' && <AlertCircle size={12} className="text-red-500" />}
                        </div>
                        <p className={`text-xs font-bold leading-tight ${isDark ? 'text-gray-200' : 'text-gray-700'}`}>
                          {preset.label}
                        </p>
                        <p className={`text-[10px] leading-tight ${isDark ? 'text-gray-500' : 'text-gray-400'}`}>
                          {preset.description}
                        </p>
                      </button>
                    )
                  })}
                </div>
              </div>
            </div>
          )}

          {/* ── Preview Tab ── */}
          {activeTab === 'preview' && (
            <div className="space-y-3 pt-2">
              {previewRecords.length === 0 ? (
                <div className="flex flex-col items-center justify-center py-16 text-center">
                  <div className={`w-16 h-16 rounded-2xl flex items-center justify-center mb-4 ${isDark ? 'bg-gray-800' : 'bg-gray-100'}`}>
                    <Table size={28} className="text-gray-400" />
                  </div>
                  <p className={`font-semibold ${isDark ? 'text-gray-400' : 'text-gray-500'}`}>No data imported yet</p>
                  <p className={`text-sm mt-1 ${isDark ? 'text-gray-600' : 'text-gray-400'}`}>
                    Upload a file or load from an online source
                  </p>
                  <div className="flex gap-2 mt-4">
                    <button onClick={() => setActiveTab('upload')} className="text-sm text-purple-500 font-medium hover:underline">
                      Upload →
                    </button>
                    <span className="text-gray-300">·</span>
                    <button onClick={() => setActiveTab('online')} className="text-sm text-purple-500 font-medium hover:underline">
                      Online →
                    </button>
                  </div>
                </div>
              ) : (
                <>
                  {/* Source info */}
                  <div className={`flex items-center justify-between px-4 py-3 rounded-xl ${cardBase}`}>
                    <div>
                      <p className={`text-xs font-semibold ${isDark ? 'text-gray-400' : 'text-gray-500'}`}>Source</p>
                      <p className={`text-sm font-bold mt-0.5 ${isDark ? 'text-gray-200' : 'text-gray-800'}`}>{previewSource}</p>
                    </div>
                    <div className="text-right">
                      <p className={`text-xs font-semibold ${isDark ? 'text-gray-400' : 'text-gray-500'}`}>Records</p>
                      <p className="text-sm font-bold mt-0.5 text-purple-500">{previewRecords.length}</p>
                    </div>
                  </div>

                  {/* Table preview */}
                  <div className={`rounded-xl overflow-hidden border ${isDark ? 'border-gray-700' : 'border-gray-200'}`}>
                    <div className="overflow-x-auto max-h-64">
                      <table className="w-full text-xs">
                        <thead>
                          <tr className={isDark ? 'bg-gray-800' : 'bg-gray-50'}>
                            {Object.keys(previewRecords[0]?.fields ?? {}).slice(0, 5).map((key) => (
                              <th
                                key={key}
                                className={`text-left px-3 py-2 font-semibold uppercase tracking-wider whitespace-nowrap ${
                                  isDark ? 'text-gray-400' : 'text-gray-500'
                                }`}
                              >
                                {key}
                              </th>
                            ))}
                          </tr>
                        </thead>
                        <tbody className={`divide-y ${isDark ? 'divide-gray-800' : 'divide-gray-100'}`}>
                          {previewRecords.map((record, i) => (
                            <tr key={record.id} className={i % 2 === 0
                              ? isDark ? 'bg-gray-900' : 'bg-white'
                              : isDark ? 'bg-gray-800/50' : 'bg-gray-50/50'
                            }>
                              {Object.values(record.fields).slice(0, 5).map((val, j) => (
                                <td key={j} className={`px-3 py-2 truncate max-w-32 ${isDark ? 'text-gray-300' : 'text-gray-700'}`}>
                                  {val}
                                </td>
                              ))}
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  </div>
                </>
              )}
            </div>
          )}
        </div>

        {/* Footer actions */}
        <div className={`flex items-center justify-between gap-3 px-6 py-4 border-t ${isDark ? 'border-gray-800 bg-gray-900' : 'border-gray-200 bg-gray-50'}`}>
          {/* Clear button */}
          <button
            onClick={() => { onClear(); setPreviewRecords([]); setPreviewSource(null); setActiveTab('upload') }}
            className={`flex items-center gap-1.5 px-3 py-2 rounded-xl text-sm font-medium transition-all duration-150
              ${isDark ? 'text-gray-500 hover:text-red-400 hover:bg-red-900/20' : 'text-gray-400 hover:text-red-500 hover:bg-red-50'}
              ${previewRecords.length === 0 ? 'opacity-40 pointer-events-none' : ''}
            `}
          >
            <Trash2 size={14} />
            Clear
          </button>

          <div className="flex items-center gap-2">
            <button
              onClick={onClose}
              className={`px-4 py-2 rounded-xl text-sm font-semibold transition-colors ${
                isDark ? 'text-gray-400 hover:text-gray-200 hover:bg-gray-800' : 'text-gray-500 hover:text-gray-700 hover:bg-gray-100'
              }`}
            >
              Cancel
            </button>
            <button
              onClick={handleImport}
              disabled={previewRecords.length === 0}
              className="
                flex items-center gap-2 px-5 py-2 rounded-xl
                bg-gradient-to-r from-violet-600 to-purple-600
                text-white text-sm font-bold
                shadow-lg shadow-violet-500/30
                hover:shadow-xl hover:scale-105 active:scale-95
                transition-all duration-150
                disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:scale-100
              "
            >
              <Play size={14} />
              {previewRecords.length > 0 ? `Analyze ${previewRecords.length} Records` : 'Analyze'}
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}

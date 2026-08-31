/**
 * useAppStore — Unified application state
 */

import { create } from 'zustand'
import type { DataRecord } from '../types/data'
import type { LLMConfig } from '../utils/llm'
import { loadLLMConfig, saveLLMConfig, clearLLMConfig } from '../utils/llm'

export type AppScreen = 'landing' | 'dashboard'

export interface AppState {
  screen: AppScreen
  records: DataRecord[]
  source: string | null
  isDataPanelOpen: boolean
  isDarkMode: boolean

  // LLM
  llmConfig: LLMConfig | null

  // AI state (synced from ChatPanel for other consumers)
  aiInsights: string
  aiError: string | null
  isAiLoading: boolean

  // Actions
  setScreen: (screen: AppScreen) => void
  setRecords: (records: DataRecord[], source: string) => void
  clearRecords: () => void
  setDataPanelOpen: (open: boolean) => void
  toggleDarkMode: () => void
  setLLMConfig: (config: LLMConfig | null) => void
  setAiInsights: (text: string) => void
  appendAiInsights: (chunk: string) => void
  setAiLoading: (v: boolean) => void
  setAiError: (e: string | null) => void
  reset: () => void
}

export const useAppStore = create<AppState>((set) => ({
  screen: 'landing',
  records: [],
  source: null,
  isDataPanelOpen: false,
  isDarkMode: (() => {
    const saved = localStorage.getItem('insightbridge-theme')
    return saved ? saved === 'dark' : window.matchMedia('(prefers-color-scheme: dark)').matches
  })(),
  llmConfig: loadLLMConfig(),
  aiInsights: '',
  aiError: null,
  isAiLoading: false,

  setScreen: (screen) => set({ screen }),
  setRecords: (records, source) =>
    set({ records, source, screen: 'dashboard', aiInsights: '', aiError: null }),
  clearRecords: () =>
    set({ records: [], source: null, screen: 'landing', aiInsights: '', aiError: null }),
  setDataPanelOpen: (isDataPanelOpen) => set({ isDataPanelOpen }),
  toggleDarkMode: () =>
    set((s) => {
      const next = !s.isDarkMode
      document.body.classList.toggle('dark', next)
      localStorage.setItem('insightbridge-theme', next ? 'dark' : 'light')
      return { isDarkMode: next }
    }),
  setLLMConfig: (config) => {
    if (config) saveLLMConfig(config)
    else clearLLMConfig()
    set({ llmConfig: config })
  },
  setAiInsights: (aiInsights) => set({ aiInsights }),
  appendAiInsights: (chunk) => set((s) => ({ aiInsights: s.aiInsights + chunk })),
  setAiLoading: (isAiLoading) => set({ isAiLoading }),
  setAiError: (aiError) => set({ aiError }),
  reset: () =>
    set({ records: [], source: null, screen: 'landing', aiInsights: '', aiError: null, isAiLoading: false }),
}))

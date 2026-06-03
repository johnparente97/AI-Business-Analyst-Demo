import type { LLMProvider } from './models'

export interface LLMConfig {
  provider: LLMProvider
  model: string
  apiKey: string
}

const LS_KEY = 'datainsight_llm_config_v2'

export function saveLLMConfig(config: LLMConfig): void {
  localStorage.setItem(LS_KEY, JSON.stringify(config))
}

export function loadLLMConfig(): LLMConfig | null {
  try {
    const raw = localStorage.getItem(LS_KEY)
    if (!raw) return null
    return JSON.parse(raw) as LLMConfig
  } catch { return null }
}

export function clearLLMConfig(): void {
  localStorage.removeItem(LS_KEY)
}

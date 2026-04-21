/**
 * AISetupModal — Model selection + API key configuration
 *
 * Shows all available models grouped by provider with quality ratings.
 * Tests connection before saving. Keys stored in localStorage only.
 */

import { useState } from 'react'
import {
  X, Key, ExternalLink, Check, Eye, EyeOff,
  Loader2, Star, Zap, Lock
} from 'lucide-react'
import { useAppStore } from '../store/useAppStore'
import {
  MODELS, testConnection, saveLLMConfig, clearLLMConfig,
  loadLLMConfig
} from '../utils/llm'
import type { LLMProvider, ModelDef } from '../utils/llm'

interface Props { isDark: boolean; onClose: () => void }

const PROVIDER_INFO: Record<LLMProvider, {
  name: string
  free: boolean
  keyHint: string
  placeholder: string
  keyUrl: string
  keyUrlLabel: string
}> = {
  gemini: {
    name: 'Google Gemini',
    free: true,
    keyHint: 'Free — 15 req/min, 1M tokens/day. No credit card.',
    placeholder: 'AIza…',
    keyUrl: 'https://aistudio.google.com/apikey',
    keyUrlLabel: 'aistudio.google.com/apikey',
  },
  groq: {
    name: 'Groq',
    free: true,
    keyHint: 'Free — blazing fast open-source inference. No credit card.',
    placeholder: 'gsk_…',
    keyUrl: 'https://console.groq.com/keys',
    keyUrlLabel: 'console.groq.com/keys',
  },
  openai: {
    name: 'OpenAI',
    free: false,
    keyHint: 'Paid. ~$0.15/1M tokens for GPT-4o Mini. Very affordable.',
    placeholder: 'sk-…',
    keyUrl: 'https://platform.openai.com/api-keys',
    keyUrlLabel: 'platform.openai.com/api-keys',
  },
  anthropic: {
    name: 'Anthropic',
    free: false,
    keyHint: 'Paid. ~$0.25/1M tokens for Claude Haiku. Very affordable.',
    placeholder: 'sk-ant-…',
    keyUrl: 'https://console.anthropic.com/settings/keys',
    keyUrlLabel: 'console.anthropic.com',
  },
}

const PROVIDERS: LLMProvider[] = ['gemini', 'groq', 'openai', 'anthropic']

export function AISetupModal({ isDark, onClose }: Props) {
  const { llmConfig, setLLMConfig } = useAppStore()
  const [provider, setProvider] = useState<LLMProvider>(llmConfig?.provider ?? 'gemini')
  const [selectedModel, setSelectedModel] = useState<string>(
    llmConfig?.model ?? 'gemini-2.0-flash'
  )
  const [apiKey, setApiKey] = useState(llmConfig?.apiKey ?? '')
  const [showKey, setShowKey] = useState(false)
  const [testing, setTesting] = useState(false)
  const [testResult, setTestResult] = useState<'ok' | 'fail' | null>(null)
  const [testError, setTestError] = useState('')

  const dk = isDark

  const providerModels = MODELS.filter(m => m.provider === provider)
  const info = PROVIDER_INFO[provider]

  const handleProviderChange = (p: LLMProvider) => {
    setProvider(p)
    const saved = loadLLMConfig()
    if (saved?.provider === p) {
      setApiKey(saved.apiKey)
      setSelectedModel(saved.model)
    } else {
      setApiKey('')
      setSelectedModel(MODELS.find(m => m.provider === p && m.recommended)?.id ?? MODELS.find(m => m.provider === p)?.id ?? '')
    }
    setTestResult(null)
    setTestError('')
  }

  const testKey = async () => {
    if (!apiKey.trim() || !selectedModel) return
    setTesting(true)
    setTestResult(null)
    setTestError('')
    try {
      await testConnection({ provider, model: selectedModel, apiKey: apiKey.trim() })
      setTestResult('ok')
    } catch (e: unknown) {
      setTestResult('fail')
      setTestError((e as Error).message ?? 'Connection failed')
    } finally {
      setTesting(false)
    }
  }

  const save = () => {
    if (!apiKey.trim() || !selectedModel) return
    const config = { provider, model: selectedModel, apiKey: apiKey.trim() }
    saveLLMConfig(config)
    setLLMConfig(config)
    onClose()
  }

  const disconnect = () => {
    clearLLMConfig()
    setLLMConfig(null)
    setApiKey('')
    setTestResult(null)
    onClose()
  }

  return (
    <div className={`fixed inset-0 z-[200] flex items-center justify-center p-4 backdrop-blur-sm ${dk ? 'bg-black/70' : 'bg-black/40'}`}>
      <div className={`w-full max-w-lg rounded-2xl shadow-2xl overflow-hidden ${dk ? 'bg-[#111113] border border-[#1f1f23]' : 'bg-white border border-gray-200'}`}>

        {/* Header */}
        <div className={`flex items-center justify-between px-5 py-4 border-b ${dk ? 'border-[#1f1f23]' : 'border-gray-100'}`}>
          <div>
            <h2 className={`text-sm font-bold ${dk ? 'text-zinc-100' : 'text-zinc-900'}`}>AI Model Setup</h2>
            <p className={`text-xs mt-0.5 ${dk ? 'text-zinc-500' : 'text-zinc-400'}`}>
              Choose a model and connect your API key to enable chat + analysis
            </p>
          </div>
          <button onClick={onClose} className={`p-1.5 rounded-lg transition-colors ${dk ? 'text-zinc-500 hover:text-zinc-300 hover:bg-white/10' : 'text-zinc-400 hover:text-zinc-600 hover:bg-gray-100'}`}>
            <X size={16} />
          </button>
        </div>

        <div className="p-5 space-y-4 max-h-[75vh] overflow-y-auto">

          {/* Provider tabs */}
          <div>
            <p className={`text-[11px] font-bold uppercase tracking-wider mb-2 ${dk ? 'text-zinc-500' : 'text-zinc-400'}`}>Provider</p>
            <div className={`grid grid-cols-4 gap-1 p-1 rounded-xl ${dk ? 'bg-black/40' : 'bg-gray-100'}`}>
              {PROVIDERS.map(p => {
                const pInfo = PROVIDER_INFO[p]
                return (
                  <button
                    key={p}
                    onClick={() => handleProviderChange(p)}
                    className={`py-2 px-1 rounded-lg text-[11px] font-semibold transition-all flex flex-col items-center gap-0.5 ${
                      provider === p
                        ? 'bg-violet-600 text-white'
                        : dk ? 'text-zinc-400 hover:text-zinc-200 hover:bg-white/10' : 'text-zinc-500 hover:text-zinc-700 hover:bg-white'
                    }`}
                  >
                    <span>{pInfo.name}</span>
                    {pInfo.free
                      ? <span className={`text-[8px] font-bold ${provider === p ? 'text-violet-200' : 'text-emerald-500'}`}>FREE</span>
                      : <span className={`text-[8px] font-bold ${provider === p ? 'text-violet-200' : dk ? 'text-zinc-600' : 'text-zinc-400'}`}>PAID</span>
                    }
                  </button>
                )
              })}
            </div>
          </div>

          {/* Model selector */}
          <div>
            <p className={`text-[11px] font-bold uppercase tracking-wider mb-2 ${dk ? 'text-zinc-500' : 'text-zinc-400'}`}>Model</p>
            <div className="space-y-2">
              {providerModels.map(model => (
                <ModelCard
                  key={model.id}
                  model={model}
                  selected={selectedModel === model.id}
                  isDark={dk}
                  onSelect={() => { setSelectedModel(model.id); setTestResult(null) }}
                />
              ))}
            </div>
          </div>

          {/* Provider info + key link */}
          <div className={`p-3 rounded-xl text-xs ${dk ? 'bg-white/5 border border-white/10' : 'bg-gray-50 border border-gray-200'}`}>
            <div className="flex items-center gap-1.5 mb-2">
              {PROVIDER_INFO[provider].free
                ? <Zap size={12} className="text-emerald-500" />
                : <Lock size={12} className={dk ? 'text-zinc-400' : 'text-zinc-500'} />
              }
              <span className={dk ? 'text-zinc-300' : 'text-zinc-600'}>{info.keyHint}</span>
            </div>
            <a
              href={info.keyUrl}
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center gap-1 text-violet-500 hover:text-violet-400 font-medium transition-colors"
            >
              <ExternalLink size={10} /> Get API key → {info.keyUrlLabel}
            </a>
          </div>

          {/* API Key input */}
          <div>
            <p className={`text-[11px] font-bold uppercase tracking-wider mb-2 ${dk ? 'text-zinc-500' : 'text-zinc-400'}`}>API Key</p>
            <div className="relative">
              <input
                type={showKey ? 'text' : 'password'}
                value={apiKey}
                onChange={e => { setApiKey(e.target.value); setTestResult(null) }}
                onKeyDown={e => e.key === 'Enter' && testKey()}
                placeholder={info.placeholder}
                className={`w-full px-3 py-2.5 pr-10 rounded-xl text-sm border outline-none transition-colors font-mono focus:border-violet-500 ${
                  dk
                    ? 'bg-[#1a1a1e] border-[#2a2a30] text-zinc-100 placeholder-zinc-600'
                    : 'bg-gray-50 border-gray-200 text-zinc-900 placeholder-zinc-400'
                }`}
              />
              <button
                onClick={() => setShowKey(s => !s)}
                className={`absolute right-2.5 top-1/2 -translate-y-1/2 ${dk ? 'text-zinc-500 hover:text-zinc-300' : 'text-zinc-400 hover:text-zinc-600'}`}
              >
                {showKey ? <EyeOff size={14} /> : <Eye size={14} />}
              </button>
            </div>
            {apiKey && (
              <p className={`text-[10px] mt-1.5 ${dk ? 'text-zinc-600' : 'text-zinc-400'}`}>
                🔒 Stored locally in your browser only — never sent to our servers.
              </p>
            )}
          </div>

          {/* Test result */}
          {testResult === 'ok' && (
            <div className={`flex items-center gap-2 px-3 py-2.5 rounded-xl text-xs font-semibold ${dk ? 'bg-emerald-900/20 text-emerald-400 border border-emerald-800/30' : 'bg-emerald-50 text-emerald-700 border border-emerald-200'}`}>
              <Check size={13} /> Connection successful — ready to analyze!
            </div>
          )}
          {testResult === 'fail' && (
            <div className={`px-3 py-2.5 rounded-xl text-xs ${dk ? 'bg-red-900/20 text-red-400 border border-red-800/30' : 'bg-red-50 text-red-600 border border-red-200'}`}>
              <span className="font-bold">Error: </span>{testError}
            </div>
          )}

          {/* Actions */}
          <div className="flex gap-2 pt-1">
            {apiKey.trim() && (
              <button
                onClick={testKey}
                disabled={testing}
                className={`flex items-center gap-1.5 px-4 py-2.5 rounded-xl text-xs font-semibold border transition-colors disabled:opacity-50 ${
                  dk ? 'border-[#2a2a30] text-zinc-300 hover:bg-white/10' : 'border-gray-200 text-zinc-600 hover:bg-gray-50'
                }`}
              >
                {testing ? <Loader2 size={12} className="animate-spin" /> : <Key size={12} />}
                Test Connection
              </button>
            )}
            {llmConfig && (
              <button
                onClick={disconnect}
                className={`flex items-center gap-1.5 px-4 py-2.5 rounded-xl text-xs font-semibold border transition-colors ${
                  dk ? 'border-red-800/50 text-red-400 hover:bg-red-900/20' : 'border-red-200 text-red-600 hover:bg-red-50'
                }`}
              >
                Disconnect
              </button>
            )}
            <button
              onClick={save}
              disabled={!apiKey.trim() || !selectedModel}
              className="flex-1 flex items-center justify-center gap-2 px-4 py-2.5 rounded-xl bg-violet-600 text-white text-xs font-bold hover:bg-violet-500 transition-colors disabled:opacity-40 disabled:cursor-not-allowed"
            >
              <Check size={13} />
              {llmConfig ? 'Update & Save' : 'Activate AI'}
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}

// ─── Model Card ───────────────────────────────────────────────────────────────

function ModelCard({
  model, selected, isDark: dk, onSelect
}: {
  model: ModelDef
  selected: boolean
  isDark: boolean
  onSelect: () => void
}) {
  return (
    <button
      onClick={onSelect}
      className={`w-full text-left px-3.5 py-3 rounded-xl border transition-all ${
        selected
          ? dk
            ? 'border-violet-600 bg-violet-900/20'
            : 'border-violet-400 bg-violet-50'
          : dk
            ? 'border-[#2a2a30] hover:border-[#3a3a40] hover:bg-white/5'
            : 'border-gray-200 hover:border-gray-300 hover:bg-gray-50'
      }`}
    >
      <div className="flex items-start justify-between gap-2">
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 mb-0.5">
            <p className={`text-xs font-bold truncate ${dk ? 'text-zinc-100' : 'text-zinc-900'}`}>{model.name}</p>
            {model.recommended && (
              <span className="text-[9px] px-1.5 py-0.5 rounded-full bg-violet-600 text-white font-bold shrink-0">BEST</span>
            )}
            {model.tier === 'free' && (
              <span className={`text-[9px] px-1.5 py-0.5 rounded-full font-bold shrink-0 ${dk ? 'bg-emerald-900/30 text-emerald-400' : 'bg-emerald-50 text-emerald-600'}`}>FREE</span>
            )}
          </div>
          <p className={`text-[10px] leading-relaxed ${dk ? 'text-zinc-500' : 'text-zinc-400'}`}>{model.description}</p>
        </div>
        <div className="flex flex-col items-end gap-1 shrink-0">
          <Stars count={model.stars} selected={selected} />
          <span className={`text-[9px] font-medium ${
            model.speed === 'fast'
              ? 'text-emerald-500'
              : model.speed === 'medium'
                ? dk ? 'text-zinc-400' : 'text-zinc-500'
                : 'text-amber-500'
          }`}>
            {model.speed === 'fast' ? '⚡ fast' : model.speed === 'medium' ? '● medium' : '◐ slow'}
          </span>
        </div>
      </div>
    </button>
  )
}

function Stars({ count, selected }: { count: number; selected: boolean }) {
  return (
    <div className="flex gap-0.5">
      {Array.from({ length: 5 }).map((_, i) => (
        <Star
          key={i}
          size={9}
          className={i < count
            ? selected ? 'text-violet-400' : 'text-amber-400'
            : 'text-gray-300 opacity-40'
          }
          fill={i < count ? 'currentColor' : 'none'}
        />
      ))}
    </div>
  )
}

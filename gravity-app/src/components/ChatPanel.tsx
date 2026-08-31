import { useState, useRef, useEffect, useCallback, useMemo } from 'react'
import { Send, Sparkles, RotateCcw, Loader2, StopCircle } from 'lucide-react'
import type { DataInsights } from '../utils/analyze'
import type { DataRecord } from '../types/data'
import type { ChatMessage as IChatMessage } from '../utils/llm'
import {
  streamChat, buildSystemPrompt, buildInitialAnalysisPrompt,
} from '../utils/llm'
import { useAppStore } from '../store/useAppStore'
import { nanoid } from '../utils/nanoid'
import { useTheme } from '../hooks/useTheme'
import { ChatMessage } from './chat/ChatMessage'
import { SuggestedQuestions } from './chat/SuggestedQuestions'

interface ChatPanelProps {
  records: DataRecord[]
  source: string
  insights: DataInsights
  isDark: boolean
  onNeedApiKey: () => void
}

export function ChatPanel({
  records, source, insights, isDark, onNeedApiKey
}: ChatPanelProps) {
  const { llmConfig, aiInsights, setAiInsights, appendAiInsights, setAiLoading, setAiError, aiError } = useAppStore()
  const { dk } = { dk: isDark, ...useTheme(isDark) } // For simple dk check

  const [messages, setMessages] = useState<IChatMessage[]>([])
  const [input, setInput] = useState('')
  const [isStreaming, setIsStreaming] = useState(false)
  const [streamingId, setStreamingId] = useState<string | null>(null)
  const [copiedId, setCopiedId] = useState<string | null>(null)
  const [showSuggestions, setShowSuggestions] = useState(true)

  const abortRef = useRef<AbortController | null>(null)
  const bottomRef = useRef<HTMLDivElement>(null)
  const inputRef = useRef<HTMLTextAreaElement>(null)
  const initialRanRef = useRef(false)

  const systemPrompt = useMemo(
    () => buildSystemPrompt(source, insights.fieldStats, records),
    [source, insights, records]
  )

  const runInitialAnalysis = useCallback(async () => {
    if (!llmConfig) return
    abortRef.current?.abort()
    abortRef.current = new AbortController()

    const sysMsg: IChatMessage = { id: nanoid(), role: 'system', content: systemPrompt, timestamp: Date.now() }
    const userMsg: IChatMessage = { id: nanoid(), role: 'user', content: buildInitialAnalysisPrompt(), timestamp: Date.now() }
    const assistantId = nanoid()
    const assistantMsg: IChatMessage = { id: assistantId, role: 'assistant', content: '', timestamp: Date.now() }

    setMessages([userMsg, assistantMsg])
    setStreamingId(assistantId)
    setIsStreaming(true)
    setAiLoading(true)
    setAiError(null)

    try {
      await streamChat(
        llmConfig,
        [sysMsg, userMsg],
        (chunk) => {
          setMessages(prev => prev.map(m => m.id === assistantId ? { ...m, content: m.content + chunk } : m))
          appendAiInsights(chunk)
        },
        abortRef.current.signal
      )
    } catch (e: unknown) {
      if ((e as Error).name === 'AbortError') return
      const msg = (e as Error).message ?? 'Analysis failed'
      setAiError(msg)
      setMessages(prev => prev.map(m => m.id === assistantId ? { ...m, content: `❌ ${msg}` } : m))
    } finally {
      setStreamingId(null)
      setIsStreaming(false)
      setAiLoading(false)
    }
  }, [llmConfig, systemPrompt, appendAiInsights, setAiLoading, setAiError])

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  useEffect(() => {
    if (llmConfig && messages.length === 0 && records.length > 0 && !initialRanRef.current) {
      initialRanRef.current = true
      const timer = setTimeout(() => {
        runInitialAnalysis()
      }, 0)
      return () => clearTimeout(timer)
    }
  }, [llmConfig, messages.length, records.length, runInitialAnalysis])

  useEffect(() => {
    const lastAssistant = [...messages].reverse().find(m => m.role === 'assistant')
    if (lastAssistant && lastAssistant.content !== aiInsights) {
      setAiInsights(lastAssistant.content)
    }
  }, [messages, aiInsights, setAiInsights])

  const sendMessage = useCallback(async (text: string) => {
    const trimmed = text.trim()
    if (!trimmed || isStreaming) return
    if (!llmConfig) { onNeedApiKey(); return }

    setShowSuggestions(false)
    abortRef.current?.abort()
    abortRef.current = new AbortController()

    const userMsg: IChatMessage = { id: nanoid(), role: 'user', content: trimmed, timestamp: Date.now() }
    const assistantId = nanoid()
    const assistantMsg: IChatMessage = { id: assistantId, role: 'assistant', content: '', timestamp: Date.now() }

    setInput('')
    setMessages(prev => [...prev, userMsg, assistantMsg])
    setStreamingId(assistantId)
    setIsStreaming(true)

    const sysMsg: IChatMessage = { id: 'sys', role: 'system', content: systemPrompt, timestamp: 0 }
    const history = messages.filter(m => m.role !== 'system').slice(-12)

    try {
      await streamChat(
        llmConfig,
        [sysMsg, ...history, userMsg],
        (chunk) => {
          setMessages(prev => prev.map(m => m.id === assistantId ? { ...m, content: m.content + chunk } : m))
        },
        abortRef.current.signal
      )
    } catch (e: unknown) {
      if ((e as Error).name === 'AbortError') return
      const msg = (e as Error).message ?? 'Request failed'
      setMessages(prev => prev.map(m => m.id === assistantId ? { ...m, content: `❌ ${msg}` } : m))
    } finally {
      setStreamingId(null)
      setIsStreaming(false)
    }
  }, [isStreaming, llmConfig, messages, systemPrompt, onNeedApiKey])

  const stopStreaming = () => {
    abortRef.current?.abort()
    setStreamingId(null)
    setIsStreaming(false)
    setAiLoading(false)
  }

  const clearChat = () => {
    abortRef.current?.abort()
    setMessages([])
    setStreamingId(null)
    setIsStreaming(false)
    setShowSuggestions(true)
    setAiInsights('')
    setAiError(null)
  }

  const copyMessage = (id: string, content: string) => {
    navigator.clipboard.writeText(content)
    setCopiedId(id)
    setTimeout(() => setCopiedId(null), 2000)
  }

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      sendMessage(input)
    }
  }

  const userMessages = messages.filter(m => m.role === 'user')
  const hasMessages = messages.length > 0

  return (
    <div className={`flex flex-col h-full rounded-2xl border overflow-hidden ${dk ? 'bg-[#111113] border-[#1f1f23]' : 'bg-white border-gray-100'}`}>
      {/* Header */}
      <div className={`flex items-center justify-between px-4 py-3 border-b shrink-0 ${dk ? 'border-[#1f1f23]' : 'border-gray-100'}`}>
        <div className="flex items-center gap-2">
          <div className="w-6 h-6 rounded-lg bg-gradient-to-br from-violet-600 to-purple-600 flex items-center justify-center">
            <Sparkles size={12} className="text-white" />
          </div>
          <h3 className={`text-sm font-bold ${dk ? 'text-zinc-100' : 'text-zinc-900'}`}>AI Chat</h3>
          {llmConfig && (
            <span className={`text-[10px] px-2 py-0.5 rounded-full font-medium ${dk ? 'bg-violet-900/30 text-violet-400' : 'bg-violet-50 text-violet-600'}`}>
              {llmConfig.model.split('-').slice(0, 3).join('-')}
            </span>
          )}
          {isStreaming && (
            <span className={`text-[10px] ${dk ? 'text-zinc-500' : 'text-zinc-400'} flex items-center gap-1`}>
              <Loader2 size={10} className="animate-spin" /> generating…
            </span>
          )}
        </div>
        <div className="flex items-center gap-1">
          {hasMessages && (
            <button
              onClick={clearChat}
              className={`flex items-center gap-1 px-2 py-1 rounded-lg text-xs transition-colors ${dk ? 'text-zinc-500 hover:text-zinc-300 hover:bg-white/10' : 'text-zinc-400 hover:text-zinc-600 hover:bg-gray-100'}`}
              title="Clear conversation"
            >
              <RotateCcw size={11} /> Clear
            </button>
          )}
          {isStreaming && (
            <button
              onClick={stopStreaming}
              className={`flex items-center gap-1 px-2 py-1 rounded-lg text-xs text-red-500 hover:bg-red-500/10 transition-colors`}
            >
              <StopCircle size={11} /> Stop
            </button>
          )}
        </div>
      </div>

      {/* Message area */}
      <div className="flex-1 overflow-y-auto px-4 py-3 space-y-4 min-h-0">
        {!hasMessages && !llmConfig && (
          <div className="flex flex-col items-center justify-center h-full text-center py-8 gap-3">
            <div className={`w-14 h-14 rounded-2xl flex items-center justify-center ${dk ? 'bg-violet-900/20' : 'bg-violet-50'}`}>
              <Sparkles size={26} className="text-violet-500" />
            </div>
            <div>
              <p className={`text-sm font-bold mb-1 ${dk ? 'text-zinc-200' : 'text-zinc-800'}`}>Connect an AI model</p>
              <p className={`text-xs max-w-52 ${dk ? 'text-zinc-500' : 'text-zinc-400'}`}>
                Chat with your data — ask questions, find patterns, get expert analysis.
              </p>
            </div>
            <button
              onClick={onNeedApiKey}
              className="px-4 py-2 rounded-xl bg-violet-600 text-white text-xs font-bold hover:bg-violet-500 transition-colors"
            >
              Set up free API key
            </button>
          </div>
        )}

        {!hasMessages && llmConfig && (
          <div className="flex flex-col items-center justify-center h-full text-center py-8 gap-3">
            <Loader2 size={24} className="text-violet-500 animate-spin" />
            <p className={`text-xs ${dk ? 'text-zinc-400' : 'text-zinc-500'}`}>Analyzing your dataset…</p>
          </div>
        )}

        {messages.map((msg) => (
          <ChatMessage
            key={msg.id}
            msg={msg}
            isDark={dk}
            isStreaming={streamingId === msg.id}
            copiedId={copiedId}
            onCopy={copyMessage}
          />
        ))}

        {aiError && !hasMessages && (
          <div className={`px-3 py-2 rounded-xl text-xs ${dk ? 'bg-red-900/20 text-red-400' : 'bg-red-50 text-red-600'}`}>
            ❌ {aiError}
          </div>
        )}

        <div ref={bottomRef} />
      </div>

      {showSuggestions && hasMessages && userMessages.length < 2 && !isStreaming && (
        <SuggestedQuestions
          onSelect={sendMessage}
          onHide={() => setShowSuggestions(false)}
          isDark={dk}
        />
      )}

      {/* Input */}
      <div className={`px-3 py-3 border-t shrink-0 ${dk ? 'border-[#1f1f23]' : 'border-gray-100'}`}>
        <div className={`flex items-end gap-2 rounded-xl border px-3 py-2 transition-colors focus-within:border-violet-500 ${dk ? 'bg-[#1a1a1e] border-[#2a2a30]' : 'bg-gray-50 border-gray-200'}`}>
          <textarea
            ref={inputRef}
            value={input}
            onChange={e => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder={llmConfig ? 'Ask anything about this data… (Enter to send)' : 'Connect an AI model to chat…'}
            disabled={!llmConfig || isStreaming}
            rows={1}
            className={`flex-1 bg-transparent text-xs outline-none resize-none leading-relaxed max-h-24 disabled:opacity-50 disabled:cursor-not-allowed ${dk ? 'text-zinc-200 placeholder-zinc-600' : 'text-zinc-800 placeholder-zinc-400'}`}
            style={{ scrollbarWidth: 'none' }}
          />
          <button
            onClick={() => sendMessage(input)}
            disabled={!llmConfig || !input.trim() || isStreaming}
            className="flex items-center justify-center w-7 h-7 rounded-lg bg-violet-600 text-white shrink-0 hover:bg-violet-500 transition-colors disabled:opacity-30 disabled:cursor-not-allowed"
          >
            <Send size={13} />
          </button>
        </div>
        <p className={`text-[9px] mt-1 text-center ${dk ? 'text-zinc-700' : 'text-zinc-300'}`}>
          Shift+Enter for new line · Enter to send
        </p>
      </div>
    </div>
  )
}

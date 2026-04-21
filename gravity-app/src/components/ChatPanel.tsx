/**
 * ChatPanel.tsx — Full Conversational AI Interface
 *
 * Features:
 * - Persistent message history per dataset session
 * - Real-time streaming with typing indicator
 * - Auto-generates initial analysis when AI is connected
 * - Suggested questions that adapt to the data
 * - Markdown rendering (headers, bullets, numbered lists, bold)
 * - Copy message button, clear conversation
 * - Keyboard: Enter to send, Shift+Enter for newline
 */

import {
  useState, useRef, useEffect, useCallback, useMemo
} from 'react'
import {
  Send, Sparkles, RotateCcw, Copy, Check,
  Loader2, StopCircle, ChevronDown, User, Bot
} from 'lucide-react'
import type { DataInsights } from '../utils/analyze'
import type { DataRecord } from '../types/data'
import type { ChatMessage } from '../utils/llm'
import {
  streamChat, buildSystemPrompt, buildInitialAnalysisPrompt,
} from '../utils/llm'
import { useAppStore } from '../store/useAppStore'
import { nanoid } from '../utils/nanoid'

interface ChatPanelProps {
  records: DataRecord[]
  source: string
  insights: DataInsights
  isDark: boolean
  onNeedApiKey: () => void
}

const SUGGESTED_QUESTIONS = [
  'What are the most notable outliers in this data?',
  'Summarize the key patterns in one paragraph.',
  'Which records rank highest and lowest overall?',
  'Are there any data quality issues I should know about?',
  'What statistical tests would you recommend running?',
  'What external datasets would complement this analysis?',
  'Describe the distribution of the numeric fields.',
  'What is the most surprising finding in this data?',
]

export function ChatPanel({
  records, source, insights, isDark, onNeedApiKey
}: ChatPanelProps) {
  const { llmConfig, aiInsights, setAiInsights, appendAiInsights, setAiLoading, setAiError, aiError } = useAppStore()
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [input, setInput] = useState('')
  const [isStreaming, setIsStreaming] = useState(false)
  const [streamingId, setStreamingId] = useState<string | null>(null)
  const [copiedId, setCopiedId] = useState<string | null>(null)
  const [showSuggestions, setShowSuggestions] = useState(true)
  const abortRef = useRef<AbortController | null>(null)
  const bottomRef = useRef<HTMLDivElement>(null)
  const inputRef = useRef<HTMLTextAreaElement>(null)

  const dk = isDark

  // System prompt built from dataset context
  const systemPrompt = useMemo(
    () => buildSystemPrompt(source, insights.fieldStats, records),
    [source, insights, records]
  )

  // Auto-scroll to bottom on new messages
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  // Auto-run initial analysis when config is set and no messages yet
  useEffect(() => {
    if (llmConfig && messages.length === 0 && records.length > 0) {
      runInitialAnalysis()
    }
  }, [llmConfig, records]) // eslint-disable-line react-hooks/exhaustive-deps

  // Sync initial analysis with store (for Dashboard stat view)
  useEffect(() => {
    const lastAssistant = [...messages].reverse().find(m => m.role === 'assistant')
    if (lastAssistant && lastAssistant.content !== aiInsights) {
      setAiInsights(lastAssistant.content)
    }
  }, [messages]) // eslint-disable-line react-hooks/exhaustive-deps

  const runInitialAnalysis = useCallback(async () => {
    if (!llmConfig) return
    abortRef.current?.abort()
    abortRef.current = new AbortController()

    const sysMsg: ChatMessage = {
      id: nanoid(), role: 'system', content: systemPrompt, timestamp: Date.now()
    }
    const userMsg: ChatMessage = {
      id: nanoid(), role: 'user', content: buildInitialAnalysisPrompt(), timestamp: Date.now()
    }
    const assistantId = nanoid()
    const assistantMsg: ChatMessage = {
      id: assistantId, role: 'assistant', content: '', timestamp: Date.now()
    }

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
          setMessages(prev =>
            prev.map(m => m.id === assistantId ? { ...m, content: m.content + chunk } : m)
          )
          appendAiInsights(chunk)
        },
        abortRef.current.signal
      )
    } catch (e: unknown) {
      if ((e as Error).name === 'AbortError') return
      const msg = (e as Error).message ?? 'Analysis failed'
      setAiError(msg)
      setMessages(prev =>
        prev.map(m => m.id === assistantId
          ? { ...m, content: `❌ ${msg}` }
          : m
        )
      )
    } finally {
      setStreamingId(null)
      setIsStreaming(false)
      setAiLoading(false)
    }
  }, [llmConfig, systemPrompt, appendAiInsights, setAiLoading, setAiError])

  const sendMessage = useCallback(async (text: string) => {
    const trimmed = text.trim()
    if (!trimmed || isStreaming) return
    if (!llmConfig) { onNeedApiKey(); return }

    setShowSuggestions(false)
    abortRef.current?.abort()
    abortRef.current = new AbortController()

    const userMsg: ChatMessage = {
      id: nanoid(), role: 'user', content: trimmed, timestamp: Date.now()
    }
    const assistantId = nanoid()
    const assistantMsg: ChatMessage = {
      id: assistantId, role: 'assistant', content: '', timestamp: Date.now()
    }

    setInput('')
    setMessages(prev => [...prev, userMsg, assistantMsg])
    setStreamingId(assistantId)
    setIsStreaming(true)

    // Build full context for the model
    const sysMsg: ChatMessage = {
      id: 'sys', role: 'system', content: systemPrompt, timestamp: 0
    }
    const history = messages.filter(m => m.role !== 'system').slice(-12) // last 6 turns

    try {
      await streamChat(
        llmConfig,
        [sysMsg, ...history, userMsg],
        (chunk) => {
          setMessages(prev =>
            prev.map(m => m.id === assistantId ? { ...m, content: m.content + chunk } : m)
          )
        },
        abortRef.current.signal
      )
    } catch (e: unknown) {
      if ((e as Error).name === 'AbortError') return
      const msg = (e as Error).message ?? 'Request failed'
      setMessages(prev =>
        prev.map(m => m.id === assistantId ? { ...m, content: `❌ ${msg}` } : m)
      )
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

        {/* Empty state */}
        {!hasMessages && !llmConfig && (
          <div className="flex flex-col items-center justify-center h-full text-center py-8 gap-3">
            <div className={`w-14 h-14 rounded-2xl flex items-center justify-center ${dk ? 'bg-violet-900/20' : 'bg-violet-50'}`}>
              <Sparkles size={26} className="text-violet-500" />
            </div>
            <div>
              <p className={`text-sm font-bold mb-1 ${dk ? 'text-zinc-200' : 'text-zinc-800'}`}>
                Connect an AI model
              </p>
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

        {/* Messages */}
        {messages.map((msg) => {
          if (msg.role === 'user') {
            // Skip the initial analysis prompt  
            const isInitial = msg.content.startsWith('Please analyze this dataset')
            if (isInitial) return null
            return (
              <div key={msg.id} className="flex justify-end">
                <div className={`flex items-start gap-2 max-w-[85%]`}>
                  <div className={`px-3.5 py-2.5 rounded-2xl rounded-tr-sm text-xs leading-relaxed ${dk ? 'bg-violet-600 text-white' : 'bg-violet-600 text-white'}`}>
                    {msg.content}
                  </div>
                  <div className={`w-6 h-6 rounded-full flex items-center justify-center shrink-0 mt-0.5 ${dk ? 'bg-zinc-700' : 'bg-gray-200'}`}>
                    <User size={12} className={dk ? 'text-zinc-300' : 'text-zinc-600'} />
                  </div>
                </div>
              </div>
            )
          }

          return (
            <div key={msg.id} className="flex justify-start">
              <div className="flex items-start gap-2 max-w-[90%]">
                <div className="w-6 h-6 rounded-full bg-gradient-to-br from-violet-600 to-purple-600 flex items-center justify-center shrink-0 mt-0.5">
                  <Bot size={12} className="text-white" />
                </div>
                <div className="flex-1 min-w-0">
                  <div className={`px-3.5 py-2.5 rounded-2xl rounded-tl-sm ${dk ? 'bg-[#1a1a1e]' : 'bg-gray-50'}`}>
                    {msg.content ? (
                      <MdMessage
                        text={msg.content}
                        isDark={dk}
                        showCursor={streamingId === msg.id}
                      />
                    ) : (
                      <div className="flex gap-1 py-1">
                        <div className="w-1.5 h-1.5 rounded-full bg-violet-500 animate-bounce" style={{ animationDelay: '0ms' }} />
                        <div className="w-1.5 h-1.5 rounded-full bg-violet-500 animate-bounce" style={{ animationDelay: '150ms' }} />
                        <div className="w-1.5 h-1.5 rounded-full bg-violet-500 animate-bounce" style={{ animationDelay: '300ms' }} />
                      </div>
                    )}
                  </div>
                  {msg.content && streamingId !== msg.id && (
                    <button
                      onClick={() => copyMessage(msg.id, msg.content)}
                      className={`mt-1 flex items-center gap-1 text-[10px] transition-colors ${dk ? 'text-zinc-600 hover:text-zinc-400' : 'text-zinc-300 hover:text-zinc-500'}`}
                    >
                      {copiedId === msg.id ? <Check size={10} className="text-emerald-500" /> : <Copy size={10} />}
                      {copiedId === msg.id ? 'Copied' : 'Copy'}
                    </button>
                  )}
                </div>
              </div>
            </div>
          )
        })}

        {aiError && !hasMessages && (
          <div className={`px-3 py-2 rounded-xl text-xs ${dk ? 'bg-red-900/20 text-red-400' : 'bg-red-50 text-red-600'}`}>
            ❌ {aiError}
          </div>
        )}

        <div ref={bottomRef} />
      </div>

      {/* Suggested questions */}
      {showSuggestions && hasMessages && userMessages.length < 2 && !isStreaming && (
        <div className={`px-4 pb-2 shrink-0`}>
          <p className={`text-[10px] font-bold uppercase tracking-wider mb-2 ${dk ? 'text-zinc-600' : 'text-zinc-400'}`}>
            Suggested
          </p>
          <div className="flex flex-col gap-1.5">
            {SUGGESTED_QUESTIONS.slice(0, 4).map(q => (
              <button
                key={q}
                onClick={() => sendMessage(q)}
                className={`text-left px-3 py-2 rounded-xl text-xs border transition-all hover:scale-[1.01] active:scale-[0.99] ${
                  dk
                    ? 'border-[#2a2a30] text-zinc-400 hover:border-violet-700 hover:text-violet-300 hover:bg-violet-900/15'
                    : 'border-gray-200 text-zinc-500 hover:border-violet-300 hover:text-violet-700 hover:bg-violet-50/60'
                }`}
              >
                {q}
              </button>
            ))}
            <button
              onClick={() => setShowSuggestions(false)}
              className={`flex items-center gap-1 text-[10px] mt-1 ${dk ? 'text-zinc-600 hover:text-zinc-400' : 'text-zinc-300 hover:text-zinc-500'} transition-colors`}
            >
              <ChevronDown size={10} /> hide suggestions
            </button>
          </div>
        </div>
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

// ─── Markdown renderer ────────────────────────────────────────────────────────

function MdMessage({ text, isDark: dk, showCursor }: { text: string; isDark: boolean; showCursor?: boolean }) {
  const lines = text.split('\n')
  const nodes: React.ReactNode[] = []
  let key = 0

  for (let i = 0; i < lines.length; i++) {
    const line = lines[i]
    const trim = line.trim()

    if (!trim) {
      if (nodes.length > 0) nodes.push(<div key={key++} className="h-2" />)
      continue
    }

    // Heading
    if (trim.startsWith('## ')) {
      nodes.push(
        <p key={key++} className={`text-[11px] font-black uppercase tracking-widest mt-3 mb-1.5 ${dk ? 'text-violet-400' : 'text-violet-600'}`}>
          {trim.slice(3)}
        </p>
      )
    } else if (trim.startsWith('# ')) {
      nodes.push(
        <p key={key++} className={`text-xs font-black uppercase tracking-wide mt-3 mb-1.5 ${dk ? 'text-violet-400' : 'text-violet-600'}`}>
          {trim.slice(2)}
        </p>
      )
    // Bullet
    } else if (trim.startsWith('• ') || trim.startsWith('- ') || trim.startsWith('* ')) {
      nodes.push(
        <div key={key++} className="flex items-start gap-1.5 mb-1">
          <div className="w-1 h-1 rounded-full bg-violet-500 mt-1.5 shrink-0" />
          <span className={`text-xs leading-relaxed ${dk ? 'text-zinc-300' : 'text-zinc-700'}`}>
            {renderInline(trim.slice(2), dk)}
          </span>
        </div>
      )
    // Numbered list
    } else if (/^\d+[\.\)]\s/.test(trim)) {
      const num = trim.match(/^(\d+)/)?.[1]
      const rest = trim.replace(/^\d+[\.\)]\s*/, '')
      nodes.push(
        <div key={key++} className="flex items-start gap-1.5 mb-1">
          <span className={`text-[10px] font-bold text-violet-500 shrink-0 mt-0.5 w-4`}>{num}.</span>
          <span className={`text-xs leading-relaxed ${dk ? 'text-zinc-300' : 'text-zinc-700'}`}>
            {renderInline(rest, dk)}
          </span>
        </div>
      )
    // Normal paragraph
    } else {
      nodes.push(
        <p key={key++} className={`text-xs leading-relaxed mb-1 ${dk ? 'text-zinc-300' : 'text-zinc-700'}`}>
          {renderInline(trim, dk)}
        </p>
      )
    }
  }

  if (showCursor) {
    nodes.push(
      <span key="cursor" className="inline-block w-1 h-3.5 bg-violet-500 rounded-sm animate-pulse ml-0.5 align-middle" />
    )
  }

  return <div>{nodes}</div>
}

// Render **bold** and `code` inline
function renderInline(text: string, dk: boolean): React.ReactNode {
  const parts = text.split(/(\*\*[^*]+\*\*|`[^`]+`)/g)
  return parts.map((part, i) => {
    if (part.startsWith('**') && part.endsWith('**')) {
      return <strong key={i} className={`font-bold ${dk ? 'text-zinc-100' : 'text-zinc-900'}`}>{part.slice(2, -2)}</strong>
    }
    if (part.startsWith('`') && part.endsWith('`')) {
      return <code key={i} className={`text-[11px] font-mono px-1 rounded ${dk ? 'bg-zinc-800 text-violet-300' : 'bg-gray-100 text-violet-700'}`}>{part.slice(1, -1)}</code>
    }
    return part
  })
}

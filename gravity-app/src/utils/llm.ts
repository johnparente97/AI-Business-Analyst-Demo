/**
 * llm.ts — Universal LLM Client
 *
 * Supports every major free & paid model that works well for data analysis:
 *
 * Google Gemini (best free):
 *   - gemini-2.0-flash        ★★★★★ Best free model — fast + very smart
 *   - gemini-1.5-pro          ★★★★★ Most capable Gemini, lower rate limits
 *   - gemini-1.5-flash        ★★★★  Fast, generous free tier
 *
 * Groq (free, open-source, extremely fast inference):
 *   - llama-3.3-70b-versatile ★★★★★ Best OSS model — rivals GPT-4o
 *   - mixtral-8x7b-32768      ★★★★  Large context, very capable
 *   - llama-3.1-70b-versatile ★★★★  Strong alternative
 *   - llama-3.1-8b-instant    ★★★   Fastest, good for quick answers
 *
 * OpenAI (paid, optional):
 *   - gpt-4o                  ★★★★★ Best overall
 *   - gpt-4o-mini             ★★★★  Cheap + very capable
 *
 * Anthropic (paid, optional):
 *   - claude-3-5-sonnet       ★★★★★ Best for analysis
 *   - claude-3-haiku          ★★★★  Fast and cheap
 */

import type { FieldStat } from './analyze'
import type { DataRecord } from '../types/data'

// ─── Model Registry ───────────────────────────────────────────────────────────

export type LLMProvider = 'gemini' | 'groq' | 'openai' | 'anthropic'

export interface ModelDef {
  id: string
  name: string
  provider: LLMProvider
  tier: 'free' | 'paid'
  stars: number         // 1-5
  description: string
  contextK: number      // context window in K tokens
  speed: 'fast' | 'medium' | 'slow'
  recommended?: boolean
}

export const MODELS: ModelDef[] = [
  // ── Gemini ───────────────────────────────────────────────────────────────
  {
    id: 'gemini-2.0-flash',
    name: 'Gemini 2.0 Flash',
    provider: 'gemini',
    tier: 'free',
    stars: 5,
    description: 'Google\'s latest flagship model. Exceptional reasoning + very fast. Best free option.',
    contextK: 1000,
    speed: 'fast',
    recommended: true,
  },
  {
    id: 'gemini-1.5-pro',
    name: 'Gemini 1.5 Pro',
    provider: 'gemini',
    tier: 'free',
    stars: 5,
    description: 'Highest capability Gemini. 1M token context. Lower rate limits on free tier.',
    contextK: 1000,
    speed: 'medium',
  },
  {
    id: 'gemini-1.5-flash',
    name: 'Gemini 1.5 Flash',
    provider: 'gemini',
    tier: 'free',
    stars: 4,
    description: 'Fast, reliable, unlimited free tier. Great for real-time analysis.',
    contextK: 128,
    speed: 'fast',
  },
  // ── Groq ─────────────────────────────────────────────────────────────────
  {
    id: 'llama-3.3-70b-versatile',
    name: 'Llama 3.3 70B',
    provider: 'groq',
    tier: 'free',
    stars: 5,
    description: 'Meta\'s best open-source model. Rivals GPT-4o in many benchmarks. Extremely fast via Groq.',
    contextK: 128,
    speed: 'fast',
    recommended: true,
  },
  {
    id: 'mixtral-8x7b-32768',
    name: 'Mixtral 8x7B',
    provider: 'groq',
    tier: 'free',
    stars: 4,
    description: 'Excellent for structured analysis. 32K token context window. Very capable.',
    contextK: 32,
    speed: 'fast',
  },
  {
    id: 'llama-3.1-70b-versatile',
    name: 'Llama 3.1 70B',
    provider: 'groq',
    tier: 'free',
    stars: 4,
    description: 'Strong reasoning and instruction following. Great for complex data questions.',
    contextK: 128,
    speed: 'medium',
  },
  {
    id: 'llama-3.1-8b-instant',
    name: 'Llama 3.1 8B',
    provider: 'groq',
    tier: 'free',
    stars: 3,
    description: 'Fastest model. Best for rapid follow-up questions where speed matters.',
    contextK: 128,
    speed: 'fast',
  },
  // ── OpenAI ────────────────────────────────────────────────────────────────
  {
    id: 'gpt-4o',
    name: 'GPT-4o',
    provider: 'openai',
    tier: 'paid',
    stars: 5,
    description: 'OpenAI\'s flagship. Best overall intelligence for complex data analysis.',
    contextK: 128,
    speed: 'medium',
  },
  {
    id: 'gpt-4o-mini',
    name: 'GPT-4o Mini',
    provider: 'openai',
    tier: 'paid',
    stars: 4,
    description: 'Extremely cost-effective. Near GPT-4 level at a fraction of the cost.',
    contextK: 128,
    speed: 'fast',
  },
  // ── Anthropic ─────────────────────────────────────────────────────────────
  {
    id: 'claude-3-5-sonnet-20241022',
    name: 'Claude 3.5 Sonnet',
    provider: 'anthropic',
    tier: 'paid',
    stars: 5,
    description: 'Anthropic\'s best model. Exceptional for structured analysis and long reasoning.',
    contextK: 200,
    speed: 'medium',
  },
  {
    id: 'claude-3-haiku-20240307',
    name: 'Claude 3 Haiku',
    provider: 'anthropic',
    tier: 'paid',
    stars: 4,
    description: 'Fast and affordable. Excellent instruction following and data interpretation.',
    contextK: 200,
    speed: 'fast',
  },
]

export function getModelDef(modelId: string): ModelDef | undefined {
  return MODELS.find(m => m.id === modelId)
}

// ─── Config ───────────────────────────────────────────────────────────────────

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

// ─── Chat message types ───────────────────────────────────────────────────────

export interface ChatMessage {
  id: string
  role: 'user' | 'assistant' | 'system'
  content: string
  timestamp: number
}

// ─── Main streaming call ──────────────────────────────────────────────────────

export async function streamChat(
  config: LLMConfig,
  messages: ChatMessage[],
  onChunk: (text: string) => void,
  signal?: AbortSignal
): Promise<string> {
  switch (config.provider) {
    case 'gemini':  return streamGemini(config, messages, onChunk, signal)
    case 'groq':    return streamGroq(config, messages, onChunk, signal)
    case 'openai':  return streamOpenAI(config, messages, onChunk, signal)
    case 'anthropic': return streamAnthropic(config, messages, onChunk, signal)
    default: throw new Error(`Unknown provider: ${config.provider}`)
  }
}

// ─── Gemini ───────────────────────────────────────────────────────────────────

async function streamGemini(
  config: LLMConfig,
  messages: ChatMessage[],
  onChunk: (text: string) => void,
  signal?: AbortSignal
): Promise<string> {
  // Gemini uses its own message format
  const contents = messages
    .filter(m => m.role !== 'system')
    .map(m => ({
      role: m.role === 'assistant' ? 'model' : 'user',
      parts: [{ text: m.content }],
    }))

  const systemInstruction = messages.find(m => m.role === 'system')?.content

  const url = `https://generativelanguage.googleapis.com/v1beta/models/${config.model}:streamGenerateContent?alt=sse&key=${config.apiKey}`

  const res = await fetch(url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    signal,
    body: JSON.stringify({
      contents,
      ...(systemInstruction ? { systemInstruction: { parts: [{ text: systemInstruction }] } } : {}),
      generationConfig: { temperature: 0.4, maxOutputTokens: 3000 },
    }),
  })

  if (!res.ok) {
    const err = await res.json().catch(() => ({})) as { error?: { message?: string } }
    throw new Error(err?.error?.message ?? `Gemini error ${res.status}`)
  }

  return readSSEStream(res, (json) => {
    return (json as { candidates?: Array<{ content?: { parts?: Array<{ text?: string }> } }> })
      ?.candidates?.[0]?.content?.parts?.[0]?.text ?? ''
  }, onChunk)
}

// ─── Groq ─────────────────────────────────────────────────────────────────────

async function streamGroq(
  config: LLMConfig,
  messages: ChatMessage[],
  onChunk: (text: string) => void,
  signal?: AbortSignal
): Promise<string> {
  const res = await fetch('https://api.groq.com/openai/v1/chat/completions', {
    method: 'POST',
    signal,
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${config.apiKey}`,
    },
    body: JSON.stringify({
      model: config.model,
      messages: messages.map(m => ({ role: m.role, content: m.content })),
      temperature: 0.4,
      max_tokens: 3000,
      stream: true,
    }),
  })

  if (!res.ok) {
    const err = await res.json().catch(() => ({})) as { error?: { message?: string } }
    throw new Error(err?.error?.message ?? `Groq error ${res.status}`)
  }

  return readSSEStream(res, (json) => {
    return (json as { choices?: Array<{ delta?: { content?: string } }> })
      ?.choices?.[0]?.delta?.content ?? ''
  }, onChunk)
}

// ─── OpenAI ───────────────────────────────────────────────────────────────────

async function streamOpenAI(
  config: LLMConfig,
  messages: ChatMessage[],
  onChunk: (text: string) => void,
  signal?: AbortSignal
): Promise<string> {
  const res = await fetch('https://api.openai.com/v1/chat/completions', {
    method: 'POST',
    signal,
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${config.apiKey}`,
    },
    body: JSON.stringify({
      model: config.model,
      messages: messages.map(m => ({ role: m.role, content: m.content })),
      temperature: 0.4,
      max_tokens: 3000,
      stream: true,
    }),
  })

  if (!res.ok) {
    const err = await res.json().catch(() => ({})) as { error?: { message?: string } }
    throw new Error(err?.error?.message ?? `OpenAI error ${res.status}`)
  }

  return readSSEStream(res, (json) => {
    return (json as { choices?: Array<{ delta?: { content?: string } }> })
      ?.choices?.[0]?.delta?.content ?? ''
  }, onChunk)
}

// ─── Anthropic ────────────────────────────────────────────────────────────────

async function streamAnthropic(
  config: LLMConfig,
  messages: ChatMessage[],
  onChunk: (text: string) => void,
  signal?: AbortSignal
): Promise<string> {
  const systemMsg = messages.find(m => m.role === 'system')?.content ?? ''
  const chatMsgs = messages
    .filter(m => m.role !== 'system')
    .map(m => ({ role: m.role, content: m.content }))

  const res = await fetch('https://api.anthropic.com/v1/messages', {
    method: 'POST',
    signal,
    headers: {
      'Content-Type': 'application/json',
      'x-api-key': config.apiKey,
      'anthropic-version': '2023-06-01',
    },
    body: JSON.stringify({
      model: config.model,
      max_tokens: 3000,
      system: systemMsg,
      messages: chatMsgs,
      stream: true,
    }),
  })

  if (!res.ok) {
    const err = await res.json().catch(() => ({})) as { error?: { message?: string } }
    throw new Error(err?.error?.message ?? `Anthropic error ${res.status}`)
  }

  return readSSEStream(res, (json) => {
    const j = json as { type?: string; delta?: { text?: string }; content_block?: { text?: string } }
    if (j.type === 'content_block_delta') return j.delta?.text ?? ''
    if (j.type === 'content_block_start') return j.content_block?.text ?? ''
    return ''
  }, onChunk)
}

// ─── SSE reader ───────────────────────────────────────────────────────────────

async function readSSEStream(
  res: Response,
  extractText: (json: unknown) => string,
  onChunk: (text: string) => void
): Promise<string> {
  const reader = res.body?.getReader()
  if (!reader) throw new Error('No response body')

  let full = ''
  const decoder = new TextDecoder()

  while (true) {
    const { done, value } = await reader.read()
    if (done) break
    const raw = decoder.decode(value, { stream: true })

    for (const line of raw.split('\n')) {
      if (!line.startsWith('data: ') || line.includes('[DONE]')) continue
      try {
        const json = JSON.parse(line.slice(6))
        const text = extractText(json)
        if (text) { full += text; onChunk(text) }
      } catch { /* skip malformed */ }
    }
  }

  return full
}

// ─── Key tester ───────────────────────────────────────────────────────────────

export async function testConnection(config: LLMConfig): Promise<void> {
  const testMsg: ChatMessage = {
    id: 'test',
    role: 'user',
    content: 'Respond with exactly: "Connection successful"',
    timestamp: Date.now(),
  }
  await streamChat(config, [testMsg], () => {}, AbortSignal.timeout(10000))
}

// ─── System prompt builder ────────────────────────────────────────────────────

export function buildSystemPrompt(
  source: string,
  fieldStats: FieldStat[],
  records: DataRecord[]
): string {
  const count = records.length

  const numericSummary = fieldStats
    .filter(s => s.type === 'numeric')
    .map(s =>
      `  - ${s.key}: min=${fmt(s.min)}, max=${fmt(s.max)}, avg=${fmt(s.avg)}, sum=${fmt(s.sum)}` +
      (s.maxLabel ? ` | Highest: "${s.maxLabel}"` : '') +
      (s.minLabel ? ` | Lowest: "${s.minLabel}"` : '')
    ).join('\n')

  const categorySummary = fieldStats
    .filter(s => s.type === 'categorical' && s.topValues?.length)
    .map(s =>
      `  - ${s.key}: ${s.topValues!.slice(0, 6).map(v => `"${v.value}" ${v.pct}% (n=${v.count})`).join(', ')}`
    ).join('\n')

  const sampleRows = records.slice(0, 8)
    .map((r, i) =>
      `  [${i + 1}] ${Object.entries(r.fields).slice(0, 8).map(([k, v]) => `${k}="${v}"`).join(' | ')}`
    ).join('\n')

  return `You are DataInsight AI — a world-class data analyst embedded in an analytics platform. You have deep expertise in statistics, data science, and business intelligence.

You are analyzing this specific dataset:
DATASET: ${source}
RECORDS: ${count}
FIELDS (${fieldStats.length}): ${fieldStats.map(s => `${s.key} [${s.type}]`).join(', ')}

NUMERIC STATISTICS:
${numericSummary || '  (no numeric fields)'}

CATEGORY DISTRIBUTIONS:
${categorySummary || '  (no categorical fields)'}

SAMPLE DATA (first ${Math.min(8, count)} of ${count} records):
${sampleRows}

GUIDELINES:
- Always cite specific values, counts, and percentages from the data
- When asked to rank or compare, be precise and complete
- Identify outliers, anomalies, and patterns proactively
- Suggest follow-up analyses the user should consider
- If a question cannot be answered from available data, say so clearly and explain what data would be needed
- Keep responses focused and structured — use bullet points for lists, numbers for rankings
- You can see ALL ${count} records through the statistics above — reason about the full dataset, not just samples`
}

export function buildInitialAnalysisPrompt(): string {
  return `Please analyze this dataset comprehensively. Structure your response as follows:

## Executive Summary
2–3 sentences: what this dataset captures, its scope, and the single most important finding.

## Key Findings
8–10 specific, quantified bullet points. Reference exact values. Go beyond the obvious — find surprising or non-obvious insights.

## Patterns & Distributions
How is the data distributed? Any skew, clustering, or concentration? What does the spread tell us?

## Outliers & Anomalies
3–5 specific records or values that are extreme or unexpected. Name them precisely.

## Field Intelligence
For each important field: what it measures, its range/quality, and what it reveals.

## What To Explore Next
3–4 specific analytical next steps. What statistical tests, cross-references, or visualizations would unlock the most value?`
}

export function buildFollowUpPrompt(question: string): string {
  return question // The system prompt already has all the context
}

// ─── Helpers ─────────────────────────────────────────────────────────────────

function fmt(n: number | undefined): string {
  if (n === undefined || isNaN(n)) return 'N/A'
  if (Math.abs(n) >= 1e9) return `${(n / 1e9).toFixed(2)}B`
  if (Math.abs(n) >= 1e6) return `${(n / 1e6).toFixed(2)}M`
  if (Math.abs(n) >= 1e3) return `${(n / 1e3).toFixed(1)}K`
  return n % 1 === 0 ? n.toLocaleString() : n.toFixed(3)
}

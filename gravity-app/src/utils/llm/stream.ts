import type { ChatMessage } from './types'
import type { LLMConfig } from './config'

export async function streamChat(
  config: LLMConfig,
  messages: ChatMessage[],
  onChunk: (text: string) => void,
  signal?: AbortSignal
): Promise<string> {
  switch (config.provider) {
    case 'gemini':  return streamGemini(config, messages, onChunk, signal)
    case 'groq':
      return streamOpenAICompat(
        'https://api.groq.com/openai/v1/chat/completions',
        `Bearer ${config.apiKey}`,
        config, messages, onChunk, signal
      )
    case 'openai':
      return streamOpenAICompat(
        'https://api.openai.com/v1/chat/completions',
        `Bearer ${config.apiKey}`,
        config, messages, onChunk, signal
      )
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

// ─── Shared OpenAI / Groq ─────────────────────────────────────────────────────

async function streamOpenAICompat(
  apiUrl: string,
  authHeader: string,
  config: LLMConfig,
  messages: ChatMessage[],
  onChunk: (text: string) => void,
  signal?: AbortSignal
): Promise<string> {
  const res = await fetch(apiUrl, {
    method: 'POST',
    signal,
    headers: {
      'Content-Type': 'application/json',
      Authorization: authHeader,
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
    throw new Error(err?.error?.message ?? `${config.provider} error ${res.status}`)
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

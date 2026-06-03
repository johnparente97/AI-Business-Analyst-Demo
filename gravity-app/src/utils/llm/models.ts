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

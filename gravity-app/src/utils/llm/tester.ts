import type { LLMConfig } from './config'
import type { ChatMessage } from './types'
import { streamChat } from './stream'

export async function testConnection(config: LLMConfig): Promise<void> {
  const testMsg: ChatMessage = {
    id: 'test',
    role: 'user',
    content: 'Respond with exactly: "Connection successful"',
    timestamp: Date.now(),
  }
  await streamChat(config, [testMsg], () => {}, AbortSignal.timeout(10000))
}

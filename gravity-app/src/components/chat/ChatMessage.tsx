import { User, Bot, Copy, Check } from 'lucide-react'
import type { ChatMessage as IChatMessage } from '../../utils/llm'
import { MdRenderer } from './MdRenderer'

interface ChatMessageProps {
  msg: IChatMessage
  isDark: boolean
  isStreaming: boolean
  copiedId: string | null
  onCopy: (id: string, content: string) => void
}

export function ChatMessage({ msg, isDark, isStreaming, copiedId, onCopy }: ChatMessageProps) {
  const dk = isDark

  // Skip the initial analysis prompt visually
  if (msg.role === 'user' && msg.content.startsWith('Please analyze this dataset')) {
    return null
  }

  if (msg.role === 'user') {
    return (
      <div className="flex justify-end">
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
    <div className="flex justify-start">
      <div className="flex items-start gap-2 max-w-[90%]">
        <div className="w-6 h-6 rounded-full bg-gradient-to-br from-violet-600 to-purple-600 flex items-center justify-center shrink-0 mt-0.5">
          <Bot size={12} className="text-white" />
        </div>
        <div className="flex-1 min-w-0">
          <div className={`px-3.5 py-2.5 rounded-2xl rounded-tl-sm ${dk ? 'bg-[#1a1a1e]' : 'bg-gray-50'}`}>
            {msg.content ? (
              <MdRenderer
                text={msg.content}
                isDark={dk}
                showCursor={isStreaming}
              />
            ) : (
              <div className="flex gap-1 py-1">
                <div className="w-1.5 h-1.5 rounded-full bg-violet-500 animate-bounce" style={{ animationDelay: '0ms' }} />
                <div className="w-1.5 h-1.5 rounded-full bg-violet-500 animate-bounce" style={{ animationDelay: '150ms' }} />
                <div className="w-1.5 h-1.5 rounded-full bg-violet-500 animate-bounce" style={{ animationDelay: '300ms' }} />
              </div>
            )}
          </div>
          {msg.content && !isStreaming && (
            <button
              onClick={() => onCopy(msg.id, msg.content)}
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
}

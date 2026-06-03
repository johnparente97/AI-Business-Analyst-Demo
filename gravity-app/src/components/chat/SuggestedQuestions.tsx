import { ChevronDown } from 'lucide-react'

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

interface SuggestedQuestionsProps {
  onSelect: (q: string) => void
  onHide: () => void
  isDark: boolean
}

export function SuggestedQuestions({ onSelect, onHide, isDark: dk }: SuggestedQuestionsProps) {
  return (
    <div className={`px-4 pb-2 shrink-0`}>
      <p className={`text-[10px] font-bold uppercase tracking-wider mb-2 ${dk ? 'text-zinc-600' : 'text-zinc-400'}`}>
        Suggested
      </p>
      <div className="flex flex-col gap-1.5">
        {SUGGESTED_QUESTIONS.slice(0, 4).map(q => (
          <button
            key={q}
            onClick={() => onSelect(q)}
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
          onClick={onHide}
          className={`flex items-center gap-1 text-[10px] mt-1 ${dk ? 'text-zinc-600 hover:text-zinc-400' : 'text-zinc-300 hover:text-zinc-500'} transition-colors`}
        >
          <ChevronDown size={10} /> hide suggestions
        </button>
      </div>
    </div>
  )
}

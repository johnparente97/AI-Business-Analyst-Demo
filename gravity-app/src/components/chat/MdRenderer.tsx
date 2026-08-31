// ─── Markdown renderer ────────────────────────────────────────────────────────

export function MdRenderer({ text, isDark: dk, showCursor }: { text: string; isDark: boolean; showCursor?: boolean }) {
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
    } else if (/^\d+[.)]\s/.test(trim)) {
      const num = trim.match(/^(\d+)/)?.[1]
      const rest = trim.replace(/^\d+[.)]\s*/, '')
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

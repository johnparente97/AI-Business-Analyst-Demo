export function useTheme(isDark: boolean) {
  return {
    bg: isDark ? 'bg-[#09090b]' : 'bg-gray-50',
    card: isDark ? 'bg-[#111113] border-[#1f1f23]' : 'bg-white border-gray-100',
    t1: isDark ? 'text-zinc-100' : 'text-zinc-900',
    t2: isDark ? 'text-zinc-400' : 'text-zinc-500',
    t3: isDark ? 'text-zinc-600' : 'text-zinc-300',
    bdr: isDark ? 'border-[#1f1f23]' : 'border-gray-100',
    iBg: isDark ? 'bg-[#1a1a1e] border-[#2a2a30]' : 'bg-gray-50 border-gray-200',
    hRow: isDark ? 'hover:bg-white/[0.04]' : 'hover:bg-violet-50/50',
  };
}

interface StatPillsProps {
  recordsCount: number
  fieldCount: number
  numericCount: number
  catCount: number
}

export function StatPills({ recordsCount, fieldCount, numericCount, catCount }: StatPillsProps) {
  return (
    <div className="grid grid-cols-4 gap-3">
      <StatPill label="Records" value={recordsCount} color="violet" />
      <StatPill label="Fields" value={fieldCount} color="blue" />
      <StatPill label="Numeric" value={numericCount} color="emerald" />
      <StatPill label="Category" value={catCount} color="amber" />
    </div>
  )
}

function StatPill({ label, value, color }: {
  label: string; value: number; color: string
}) {
  const colors: Record<string, string> = {
    violet: 'text-violet-500 bg-violet-500/10',
    blue: 'text-blue-500 bg-blue-500/10',
    emerald: 'text-emerald-500 bg-emerald-500/10',
    amber: 'text-amber-500 bg-amber-500/10',
  }
  return (
    <div className={`flex flex-col items-center justify-center p-3 rounded-2xl ${colors[color]} transition-transform hover:scale-105`}>
      <span className="text-xl font-extrabold leading-none">{value.toLocaleString()}</span>
      <span className="text-[10px] font-semibold mt-1 opacity-70">{label}</span>
    </div>
  )
}

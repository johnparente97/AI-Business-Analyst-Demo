import { useState, useMemo } from 'react'
import { Search, Hash, ArrowUp, ArrowDown, ArrowUpDown } from 'lucide-react'
import type { DataRecord } from '../../types/data'
import { useTheme } from '../../hooks/useTheme'

type SortDir = 'asc' | 'desc'

interface DataTableProps {
  records: DataRecord[]
  isDark: boolean
}

export function DataTable({ records, isDark }: DataTableProps) {
  const { dk, card, t1, t2, t3, bdr, iBg, hRow } = { dk: isDark, ...useTheme(isDark) }

  const [search, setSearch] = useState('')
  const [sortKey, setSortKey] = useState<string | null>(null)
  const [sortDir, setSortDir] = useState<SortDir>('asc')

  const tableKeys = records[0] ? Object.keys(records[0].fields) : []

  const filteredRecords = useMemo(() => {
    let rows = [...records]
    if (search.trim()) {
      const q = search.toLowerCase()
      rows = rows.filter(r => Object.values(r.fields).some(v => v.toLowerCase().includes(q)))
    }
    if (sortKey) {
      rows.sort((a, b) => {
        const av = a.fields[sortKey] ?? ''
        const bv = b.fields[sortKey] ?? ''
        const an = parseFloat(av.replace(/[$%,\s]/g, ''))
        const bn = parseFloat(bv.replace(/[$%,\s]/g, ''))
        const cmp = !isNaN(an) && !isNaN(bn) ? an - bn : av.localeCompare(bv)
        return sortDir === 'asc' ? cmp : -cmp
      })
    }
    return rows
  }, [records, search, sortKey, sortDir])

  const handleSort = (key: string) => {
    if (sortKey === key) setSortDir(d => d === 'asc' ? 'desc' : 'asc')
    else { setSortKey(key); setSortDir('asc') }
  }

  return (
    <div className={`my-5 rounded-2xl border overflow-hidden ${card}`}>
      <div className={`flex flex-wrap items-center gap-3 px-4 py-3 border-b ${bdr}`}>
        <div className="flex items-center gap-2 flex-1">
          <Hash size={14} className="text-violet-500" />
          <h2 className={`text-sm font-bold ${t1}`}>All Records</h2>
          <span className={`text-xs px-2 py-0.5 rounded-full ${dk ? 'bg-white/10 text-zinc-400' : 'bg-gray-100 text-zinc-500'}`}>
            {filteredRecords.length.toLocaleString()}/{records.length.toLocaleString()}
          </span>
        </div>
        <div className={`flex items-center gap-2 px-3 py-1.5 rounded-xl border ${iBg}`}>
          <Search size={12} className={t2} />
          <input
            type="search"
            value={search}
            onChange={e => setSearch(e.target.value)}
            placeholder="Search all fields…"
            className={`w-40 text-xs outline-none bg-transparent ${t1}`}
          />
        </div>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-xs">
          <thead className={`sticky top-0 ${dk ? 'bg-[#111113]' : 'bg-gray-50'}`}>
            <tr>
              <th className={`px-4 py-2.5 text-left text-[10px] font-bold uppercase tracking-wider ${t2}`}>#</th>
              {tableKeys.map(key => (
                <th
                  key={key}
                  onClick={() => handleSort(key)}
                  className={`px-4 py-2.5 text-left text-[10px] font-bold uppercase tracking-wider cursor-pointer whitespace-nowrap select-none transition-colors ${t2} hover:text-violet-500`}
                >
                  <div className="flex items-center gap-1">
                    {key.length > 14 ? key.slice(0, 13) + '…' : key}
                    {sortKey === key
                      ? sortDir === 'asc' ? <ArrowUp size={9} className="text-violet-500" /> : <ArrowDown size={9} className="text-violet-500" />
                      : <ArrowUpDown size={9} className="opacity-25" />
                    }
                  </div>
                </th>
              ))}
            </tr>
          </thead>
          <tbody className={`divide-y ${bdr}`}>
            {filteredRecords.length === 0 ? (
              <tr>
                <td colSpan={tableKeys.length + 1} className={`px-4 py-10 text-center text-sm ${t2}`}>
                  No records match your filter
                </td>
              </tr>
            ) : (
              filteredRecords.map((record, i) => (
                <tr key={record.id} className={`transition-colors ${hRow}`}>
                  <td className={`px-4 py-2.5 text-[11px] font-medium tabular-nums ${t3}`}>{i + 1}</td>
                  {tableKeys.map(key => (
                    <td key={key} className={`px-4 py-2.5 max-w-48 truncate ${t1}`}>
                      {record.fields[key] ?? <span className={t3}>—</span>}
                    </td>
                  ))}
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  )
}

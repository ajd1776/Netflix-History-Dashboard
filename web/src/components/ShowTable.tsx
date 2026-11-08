import { useMemo, useState } from 'react'
import { fmt, fmtDate } from '../lib/aggregate'
import type { ShowStats } from '../lib/api'
import { Sparkline } from './charts/Sparkline'

type Col = { key: keyof ShowStats; label: string; num?: boolean; render?: (s: ShowStats) => string }

const COLS: Col[] = [
  { key: 'plays', label: 'Plays', num: true },
  { key: 'episodes', label: 'Episodes', num: true },
  { key: 'seasons', label: 'Seasons', num: true },
  { key: 'days', label: 'Days', num: true },
  { key: 'perDay', label: 'Per day', num: true, render: (s) => s.perDay.toFixed(1) },
  { key: 'binges', label: 'Binges', num: true },
  { key: 'first', label: 'Started', render: (s) => fmtDate(s.first) },
  { key: 'last', label: 'Last watched', render: (s) => fmtDate(s.last) },
]

/** Your most-watched shows, compared side by side. Click a heading to sort. */
export function ShowTable({ shows, years }: { shows: ShowStats[]; years: number[] }) {
  const [sort, setSort] = useState<{ key: keyof ShowStats; desc: boolean }>({ key: 'plays', desc: true })
  const rows = useMemo(() => {
    const dir = sort.desc ? -1 : 1
    return [...shows].sort((a, b) => (a[sort.key] > b[sort.key] ? dir : a[sort.key] < b[sort.key] ? -dir : 0))
  }, [shows, sort])
  const max = Math.max(1, ...shows.map((s) => s.plays))

  const head = (key: keyof ShowStats, label: string, num?: boolean) => (
    <th key={key} className={num ? 'num' : ''} aria-sort={sort.key === key ? (sort.desc ? 'descending' : 'ascending') : 'none'}>
      <button onClick={() => setSort({ key, desc: sort.key === key ? !sort.desc : true })}>
        {label}{sort.key === key && <span aria-hidden>{sort.desc ? ' ↓' : ' ↑'}</span>}
      </button>
    </th>
  )

  return (
    <div className="table-wrap">
      <table className="showtable">
        <thead>
          <tr>
            <th className="rank-col">#</th>
            {head('name', 'Show')}
            <th>{years[0]}–{years.at(-1)}</th>
            {COLS.map((c) => head(c.key, c.label, c.num))}
          </tr>
        </thead>
        <tbody>
          {rows.map((s, i) => (
            <tr key={s.name}>
              <td className="rank-col">{i + 1}</td>
              <td className="show-name">
                <span>{s.name}</span>
                <i className="share" style={{ width: `${(s.plays / max) * 100}%` }} />
              </td>
              <td><Sparkline values={s.byYear} labels={years} /></td>
              {COLS.map((c) => (
                <td key={c.key} className={c.num ? 'num' : 'muted nowrap'}>
                  {c.render ? c.render(s) : fmt.format(s[c.key] as number)}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}

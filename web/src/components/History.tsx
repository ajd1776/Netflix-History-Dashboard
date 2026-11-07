import { useDeferredValue, useMemo, useState } from 'react'
import { fmt, fmtDate, toCsv } from '../lib/aggregate'
import type { HistoryRow, Kind } from '../lib/api'
import { GlassCard, Segmented } from './Glass'

const PAGE = 25

export function History({ rows }: { rows: HistoryRow[] }) {
  const [query, setQuery] = useState('')
  const [kind, setKind] = useState<Kind | 'all'>('all')
  const [page, setPage] = useState(0)
  const q = useDeferredValue(query.trim().toLowerCase())

  const filtered = useMemo(
    () => rows.filter((r) => (kind === 'all' || r.kind === kind) && (!q || r.title.toLowerCase().includes(q))),
    [rows, kind, q],
  )
  const pages = Math.max(1, Math.ceil(filtered.length / PAGE))
  const p = Math.min(page, pages - 1)
  const shown = filtered.slice(p * PAGE, p * PAGE + PAGE)

  const download = () => {
    const url = URL.createObjectURL(new Blob([toCsv(filtered)], { type: 'text/csv' }))
    const a = Object.assign(document.createElement('a'), { href: url, download: 'ExpandedNetflixHistory.csv' })
    a.click()
    URL.revokeObjectURL(url)
  }

  return (
    <GlassCard className="history" title="Everything you've watched"
      subtitle={`${fmt.format(filtered.length)} of ${fmt.format(rows.length)}`}
      actions={<button className="btn" onClick={download}>Export CSV</button>}>
      <div className="history-tools">
        <label className="search glass inner">
          <svg width="16" height="16" viewBox="0 0 24 24" aria-hidden><circle cx="11" cy="11" r="7" fill="none" stroke="currentColor" strokeWidth="2" /><path d="m20 20-3.5-3.5" stroke="currentColor" strokeWidth="2" strokeLinecap="round" /></svg>
          <input placeholder="Search titles" value={query} aria-label="Search titles"
            onChange={(e) => { setQuery(e.target.value); setPage(0) }} />
        </label>
        <Segmented label="Filter by type" value={kind} onChange={(v) => { setKind(v); setPage(0) }}
          options={[{ value: 'all', label: 'All' }, { value: 'show', label: 'Shows' }, { value: 'movie', label: 'Movies' }]} />
      </div>
      <div className="table-wrap">
        <table>
          <thead>
            <tr><th>Date</th><th>Title</th><th>Season</th><th>Episode</th></tr>
          </thead>
          <tbody>
            {shown.map((r, i) => (
              <tr key={`${r.date}-${r.title}-${i}`}>
                <td className="nowrap">{fmtDate(r.date)}</td>
                <td><span className={`dot ${r.kind}`} />{r.name}</td>
                <td className="muted">{r.season || '—'}</td>
                <td className="muted">{r.episode || '—'}</td>
              </tr>
            ))}
            {!shown.length && <tr><td colSpan={4} className="muted center">No matches</td></tr>}
          </tbody>
        </table>
      </div>
      <nav className="pager" aria-label="Pages">
        <button className="btn icon" disabled={p === 0} onClick={() => setPage(p - 1)} aria-label="Previous page">‹</button>
        <span>Page {p + 1} of {pages}</span>
        <button className="btn icon" disabled={p >= pages - 1} onClick={() => setPage(p + 1)} aria-label="Next page">›</button>
      </nav>
    </GlassCard>
  )
}

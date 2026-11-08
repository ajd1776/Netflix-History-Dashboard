import { fmt } from '../../lib/aggregate'

export function TopTitles({ items, color }: { items: { name: string; count: number }[]; color: string }) {
  if (!items.length) return <div className="chart empty">Nothing watched in this range</div>
  const max = items[0].count
  return (
    <ol className="toplist">
      {items.map((t, i) => (
        <li key={t.name}>
          <span className="rank">{i + 1}</span>
          <div className="toplist-main">
            <div className="toplist-label"><span title={t.name}>{t.name}</span><b>{fmt.format(t.count)}</b></div>
            <div className="toplist-track">
              <div className="toplist-fill" style={{ width: `${(t.count / max) * 100}%`, background: color }} />
            </div>
          </div>
        </li>
      ))}
    </ol>
  )
}

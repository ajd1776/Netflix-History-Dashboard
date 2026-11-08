import { MONTHS, WEEKDAYS, fmt } from '../../lib/aggregate'

/** Weekday × month heatmap with the count in each cell. */
export function Matrix({ grid }: { grid: number[][] }) {
  const max = Math.max(1, ...grid.flat())
  const level = (n: number) => (n === 0 ? 0 : Math.min(4, Math.ceil((n / max) * 4)))
  return (
    <div className="matrix" role="table" aria-label="Plays by weekday and month">
      <span />
      {MONTHS.map((m) => <span key={m} className="axis matrix-col">{m[0]}<i>{m.slice(1)}</i></span>)}
      {grid.map((row, d) => (
        <div key={d} role="row" className="matrix-row">
          <span className="axis matrix-day">{WEEKDAYS[d]}</span>
          {row.map((n, m) => (
            <span key={m} role="cell" className={`matrix-cell heat l${level(n)}`}
              title={`${WEEKDAYS[d]}s in ${MONTHS[m]}: ${fmt.format(n)} watched`}>
              {n > 0 ? fmt.format(n) : ''}
            </span>
          ))}
        </div>
      ))}
    </div>
  )
}

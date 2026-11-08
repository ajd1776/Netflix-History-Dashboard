import { useState } from 'react'
import { MONTHS, WEEKDAYS, pad } from '../../lib/aggregate'
import { useWidth } from '../../lib/useWidth'
import { Tooltip } from '../Glass'

const LEFT = 30
const TOP = 18

/** A year of days, one column per week, Monday at the top. */
export function Calendar({ year, counts }: { year: number; counts: Map<string, number> }) {
  const [ref, width] = useWidth<HTMLDivElement>()
  const [hover, setHover] = useState<{ x: number; y: number; date: Date; n: number } | null>(null)

  const jan1 = new Date(year, 0, 1)
  const offset = (jan1.getDay() + 6) % 7 // Monday = 0
  const days = Math.round((+new Date(year + 1, 0, 1) - +jan1) / 864e5)
  const weeks = Math.ceil((days + offset) / 7)
  const step = Math.min(22, (width - LEFT) / weeks)
  const cell = step * 0.8
  const max = Math.max(1, ...counts.values())
  const level = (n: number) => (n === 0 ? 0 : Math.min(4, Math.ceil((n / max) * 4)))

  const cells = Array.from({ length: days }, (_, i) => {
    const date = new Date(year, 0, 1 + i)
    const k = `${year}-${pad(date.getMonth() + 1)}-${pad(date.getDate())}`
    const pos = i + offset
    return { date, n: counts.get(k) ?? 0, x: LEFT + Math.floor(pos / 7) * step, y: TOP + (pos % 7) * step }
  })
  const height = TOP + 7 * step

  return (
    <div className="chart calendar" ref={ref} style={{ height }} onPointerLeave={() => setHover(null)}>
      {width > 0 && (
        <svg width={width} height={height} role="img" aria-label={`Viewing calendar for ${year}`}>
          {MONTHS.map((m, i) => {
            const pos = Math.round((+new Date(year, i, 1) - +jan1) / 864e5) + offset
            return <text key={m} className="axis" x={LEFT + Math.floor(pos / 7) * step} y={11}>{m}</text>
          })}
          {[0, 2, 4].map((d) => (
            <text key={d} className="axis" x={0} y={TOP + d * step + cell * 0.8}>{WEEKDAYS[d]}</text>
          ))}
          {cells.map((c) => (
            <rect key={+c.date} x={c.x} y={c.y} width={cell} height={cell} rx={Math.min(4, cell / 3)}
              className={`heat l${level(c.n)}`}
              onPointerEnter={() => setHover({ x: c.x, y: c.y, date: c.date, n: c.n })} />
          ))}
        </svg>
      )}
      {hover && (
        <Tooltip x={Math.min(width - 150, Math.max(0, hover.x - 60))} y={hover.y - 64}>
          <strong>{hover.date.toLocaleDateString(undefined, { weekday: 'short', day: 'numeric', month: 'short' })}</strong>
          <div className="tt-row">{hover.n ? `${hover.n} watched` : 'Nothing watched'}</div>
        </Tooltip>
      )}
    </div>
  )
}

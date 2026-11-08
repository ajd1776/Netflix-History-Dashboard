import { scaleBand, scaleLinear } from 'd3-scale'
import { useId, useState } from 'react'
import { fmt, type Split } from '../../lib/aggregate'
import { useWidth } from '../../lib/useWidth'
import { Tooltip } from '../Glass'

const M = { t: 22, r: 4, b: 26, l: 34 }
const NAMES = { shows: 'Episodes', movies: 'Movies' }

/** Stacked shows/movies columns. Movies sit on top, so the stack's outline takes their colour. */
export function BarChart({
  data, height = 240, tickEvery = 1, tooltipLabel = (s: Split) => s.label, names = NAMES,
}: {
  data: Split[]
  height?: number
  tickEvery?: number
  tooltipLabel?: (s: Split) => string
  /** tooltip labels for the two series */
  names?: { shows: string; movies: string }
}) {
  const [ref, width] = useWidth<HTMLDivElement>()
  const [hover, setHover] = useState<number | null>(null)
  const id = useId().replace(/[^a-zA-Z0-9]/g, '')

  const iw = Math.max(0, width - M.l - M.r)
  const ih = height - M.t - M.b
  const max = Math.max(1, ...data.map((d) => d.shows + d.movies))
  const x = scaleBand(data.map((d) => d.label), [0, iw]).paddingInner(0.32).paddingOuter(0.12)
  const y = scaleLinear([0, max], [ih, 0]).nice(4)
  const bw = x.bandwidth()
  const r = Math.min(8, bw / 2)
  const showLabels = bw >= 22

  const h = hover === null ? null : data[hover]

  return (
    <div className="chart" ref={ref} style={{ height }} onPointerLeave={() => setHover(null)}>
      {width > 0 && (
        <svg width={width} height={height} role="img" aria-label="Bar chart">
          <defs>
            <linearGradient id={`s${id}`} x1="0" x2="0" y1="0" y2="1">
              <stop offset="0" style={{ stopColor: 'var(--show-hi)' }} />
              <stop offset="1" style={{ stopColor: 'var(--show)' }} />
            </linearGradient>
            <linearGradient id={`m${id}`} x1="0" x2="0" y1="0" y2="1">
              <stop offset="0" style={{ stopColor: 'var(--movie-hi)' }} />
              <stop offset="1" style={{ stopColor: 'var(--movie)' }} />
            </linearGradient>
            <clipPath id={`c${id}`}><rect width={iw} height={ih} /></clipPath>
          </defs>
          <g transform={`translate(${M.l},${M.t})`}>
            {y.ticks(4).map((t) => (
              <g key={t} transform={`translate(0,${y(t)})`} className="grid">
                <line x2={iw} />
                <text x={-10} dy="0.32em" textAnchor="end">{fmt.format(t)}</text>
              </g>
            ))}
            <g clipPath={`url(#c${id})`}>
              {data.map((d, i) => {
                const total = d.shows + d.movies
                const bx = x(d.label)!
                const dim = hover !== null && hover !== i
                return (
                  <g key={d.label} className={`bar ${dim ? 'dim' : ''}`}>
                    {/* full stack, rounded top; its bottom rounding hangs below the clip */}
                    <rect className="anim" x={bx} width={bw} rx={r} y={y(total)} height={ih - y(total) + r}
                      fill={`url(#${d.movies ? 'm' : 's'}${id})`} />
                    {d.movies > 0 && d.shows > 0 && (
                      <rect className="anim" x={bx} width={bw} y={y(d.shows)} height={ih - y(d.shows)}
                        fill={`url(#s${id})`} />
                    )}
                  </g>
                )
              })}
            </g>
            {showLabels && data.map((d) => {
              const total = d.shows + d.movies
              return total > 0 && (
                <text key={d.label} className="bar-value" x={x(d.label)! + bw / 2} y={y(total) - 6}
                  textAnchor="middle">{fmt.format(total)}</text>
              )
            })}
            {data.map((d, i) => (i % tickEvery === 0) && (
              <text key={d.label} className="axis" x={x(d.label)! + bw / 2} y={ih + 18}
                textAnchor="middle">{d.label}</text>
            ))}
            {data.map((d, i) => (
              <rect key={d.label} x={x(d.label)! - (x.step() - bw) / 2} width={x.step()} height={ih}
                fill="transparent" onPointerEnter={() => setHover(i)} />
            ))}
          </g>
        </svg>
      )}
      {h && hover !== null && (
        <Tooltip x={Math.min(width - 150, Math.max(0, M.l + x(h.label)! + bw / 2 - 70))}
          y={Math.max(0, M.t + y(h.shows + h.movies) - 92)}>
          <strong>{tooltipLabel(h)}</strong>
          <Row k={names.shows} v={h.shows} c="var(--show)" />
          <Row k={names.movies} v={h.movies} c="var(--movie)" />
        </Tooltip>
      )}
    </div>
  )
}

export function Row({ k, v, c }: { k: string; v: number; c: string }) {
  return (
    <div className="tt-row"><i style={{ background: c }} />{k}<b>{fmt.format(v)}</b></div>
  )
}

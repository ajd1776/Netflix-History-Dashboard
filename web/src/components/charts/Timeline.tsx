import { bisector } from 'd3-array'
import { scaleLinear, scaleTime } from 'd3-scale'
import { area, curveMonotoneX, line } from 'd3-shape'
import { useId, useState, type PointerEvent } from 'react'
import { fmt, type MonthPoint, type Range } from '../../lib/aggregate'
import { useWidth } from '../../lib/useWidth'
import { Tooltip } from '../Glass'
import { Row } from './BarChart'

type Point = MonthPoint
const M = { t: 16, r: 8, b: 26, l: 34 }

/** Stacked area of monthly activity, a 3-month trend line, and the filtered years highlighted. */
export function Timeline({ data, height = 230, range }: { data: Point[]; height?: number; range?: Range }) {
  const [ref, width] = useWidth<HTMLDivElement>()
  const [hover, setHover] = useState<number | null>(null)
  const id = useId().replace(/[^a-zA-Z0-9]/g, '')
  if (data.length < 2) {
    return <div className="chart empty" ref={ref} style={{ height }}>Not enough months to plot</div>
  }

  const iw = Math.max(0, width - M.l - M.r)
  const ih = height - M.t - M.b
  const x = scaleTime([data[0].date, data.at(-1)!.date], [0, iw])
  const y = scaleLinear([0, Math.max(1, ...data.map((d) => d.shows + d.movies))], [ih, 0]).nice(4)

  const shows = area<Point>().x((d) => x(d.date)).y0(ih).y1((d) => y(d.shows)).curve(curveMonotoneX)
  const movies = area<Point>().x((d) => x(d.date)).y0((d) => y(d.shows))
    .y1((d) => y(d.shows + d.movies)).curve(curveMonotoneX)
  const top = line<Point>().x((d) => x(d.date)).y((d) => y(d.shows + d.movies)).curve(curveMonotoneX)
  const trend = line<Point>().x((d) => x(d.date)).y((d) => y(d.avg)).curve(curveMonotoneX)
  // Shade the months outside the year filter.
  const x0 = range ? Math.max(0, x(new Date(range[0], 0, 1))) : 0
  const x1 = range ? Math.min(iw, x(new Date(range[1] + 1, 0, 1))) : iw

  const years = [...new Set(data.map((d) => d.date.getFullYear()))]
  const yearTicks = years.map((yr) => new Date(yr, 0, 1)).filter((d) => d >= data[0].date)

  const onMove = (e: PointerEvent<SVGRectElement>) => {
    const px = e.nativeEvent.offsetX - M.l
    const i = bisector<Point, Date>((d) => d.date).center(data, x.invert(px))
    setHover(i)
  }
  const h = hover === null ? null : data[hover]

  return (
    <div className="chart" ref={ref} style={{ height }} onPointerLeave={() => setHover(null)}>
      {width > 0 && (
        <svg width={width} height={height} role="img" aria-label="Monthly activity over time">
          <defs>
            <linearGradient id={`s${id}`} x1="0" x2="0" y1="0" y2="1">
              <stop offset="0" style={{ stopColor: 'var(--show)', stopOpacity: 0.85 }} />
              <stop offset="1" style={{ stopColor: 'var(--show)', stopOpacity: 0.12 }} />
            </linearGradient>
            <linearGradient id={`m${id}`} x1="0" x2="0" y1="0" y2="1">
              <stop offset="0" style={{ stopColor: 'var(--movie)', stopOpacity: 0.9 }} />
              <stop offset="1" style={{ stopColor: 'var(--movie)', stopOpacity: 0.35 }} />
            </linearGradient>
          </defs>
          <g transform={`translate(${M.l},${M.t})`}>
            {y.ticks(4).map((t) => (
              <g key={t} transform={`translate(0,${y(t)})`} className="grid">
                <line x2={iw} />
                <text x={-10} dy="0.32em" textAnchor="end">{fmt.format(t)}</text>
              </g>
            ))}
            {yearTicks.map((d) => (
              <g key={+d} transform={`translate(${x(d)},0)`} className="grid vertical">
                <line y2={ih} />
                <text y={ih + 18} textAnchor="middle">{d.getFullYear()}</text>
              </g>
            ))}
            <path d={shows(data)!} fill={`url(#s${id})`} />
            <path d={movies(data)!} fill={`url(#m${id})`} />
            <path d={top(data)!} className="area-line" />
            <path d={trend(data)!} className="trend-line" />
            {x0 > 0 && <rect className="outside" width={x0} height={ih} />}
            {x1 < iw && <rect className="outside" x={x1} width={iw - x1} height={ih} />}
            {h && (
              <g className="crosshair" transform={`translate(${x(h.date)},0)`}>
                <line y2={ih} />
                <circle cy={y(h.shows + h.movies)} r={5} />
              </g>
            )}
            <rect width={iw} height={ih} fill="transparent" onPointerMove={onMove} />
          </g>
        </svg>
      )}
      {h && (
        <Tooltip x={Math.min(width - 160, Math.max(0, M.l + x(h.date) + 14))} y={M.t}>
          <strong>{h.label}</strong>
          <Row k="Episodes" v={h.shows} c="var(--show)" />
          <Row k="Movies" v={h.movies} c="var(--movie)" />
          <Row k="3-month avg" v={Math.round(h.avg)} c="var(--text-2)" />
        </Tooltip>
      )}
    </div>
  )
}

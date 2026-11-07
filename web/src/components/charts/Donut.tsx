import { arc, pie } from 'd3-shape'
import { useState } from 'react'
import { fmt } from '../../lib/aggregate'

interface Slice { label: string; value: number; color: string }

export function Donut({ shows, movies, size = 200 }: { shows: number; movies: number; size?: number }) {
  const [hover, setHover] = useState<number | null>(null)
  const slices: Slice[] = [
    { label: 'Episodes', value: shows, color: 'var(--show)' },
    { label: 'Movies', value: movies, color: 'var(--movie)' },
  ]
  const total = shows + movies
  const r = size / 2
  const arcs = pie<Slice>().value((d) => d.value).sort(null).padAngle(total ? 0.035 : 0)(slices)
  const shape = arc<(typeof arcs)[number]>().innerRadius(r * 0.68).outerRadius(r).cornerRadius(10)
  const grow = arc<(typeof arcs)[number]>().innerRadius(r * 0.66).outerRadius(r + 4).cornerRadius(10)
  const focus = slices[hover ?? 0]
  const pct = total ? Math.round((focus.value / total) * 100) : 0

  return (
    <div className="donut">
      <svg width={size + 10} height={size + 10} viewBox={`${-r - 5} ${-r - 5} ${size + 10} ${size + 10}`}
        role="img" aria-label={`${pct}% ${focus.label.toLowerCase()}`}>
        <circle r={r * 0.84} className="donut-track" />
        {arcs.map((a, i) => (
          <path key={a.data.label} d={(hover === i ? grow : shape)(a)!} fill={a.data.color}
            className="donut-arc" onPointerEnter={() => setHover(i)} onPointerLeave={() => setHover(null)} />
        ))}
        <text className="donut-pct" dy="0.1em" textAnchor="middle">{pct}%</text>
        <text className="donut-label" dy="1.9em" textAnchor="middle">{focus.label}</text>
      </svg>
      <ul className="legend">
        {slices.map((s) => (
          <li key={s.label}><i style={{ background: s.color }} />{s.label}<b>{fmt.format(s.value)}</b></li>
        ))}
      </ul>
    </div>
  )
}

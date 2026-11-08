import type { CSSProperties, ReactNode } from 'react'

export function GlassCard({ title, subtitle, actions, children, className = '', style }: {
  title?: ReactNode
  subtitle?: ReactNode
  actions?: ReactNode
  children: ReactNode
  className?: string
  style?: CSSProperties
}) {
  return (
    <section className={`glass card ${className}`} style={style}>
      {(title || actions) && (
        <header className="card-head">
          <div>
            {title && <h2>{title}</h2>}
            {subtitle && <p className="sub">{subtitle}</p>}
          </div>
          {actions && <div className="card-actions">{actions}</div>}
        </header>
      )}
      {children}
    </section>
  )
}

export function Segmented<T extends string>({ options, value, onChange, label }: {
  options: { value: T; label: ReactNode }[]
  value: T
  onChange: (v: T) => void
  label: string
}) {
  const i = Math.max(0, options.findIndex((o) => o.value === value))
  return (
    <div className="segmented" role="radiogroup" aria-label={label}
      style={{ '--n': options.length, '--i': i } as CSSProperties}>
      <span className="segmented-thumb" aria-hidden />
      {options.map((o) => (
        <button key={o.value} role="radio" aria-checked={o.value === value}
          className={o.value === value ? 'on' : ''} onClick={() => onChange(o.value)}>
          {o.label}
        </button>
      ))}
    </div>
  )
}

const KNOB = 20

export function RangeSlider({ min, max, value, onChange, format = String, label }: {
  min: number
  max: number
  value: [number, number]
  onChange: (v: [number, number]) => void
  format?: (n: number) => string
  label: string
}) {
  const [a, b] = value
  const span = Math.max(1, max - min)
  const pct = (v: number) => ((v - min) / span) * 100
  // Native knobs travel from KNOB/2 to 100% - KNOB/2, so map positions the same way.
  const at = (p: number) => `calc(${KNOB / 2}px + ${p / 100} * (100% - ${KNOB}px))`
  // Value chips ride under each knob; when the knobs are close they merge into one.
  const merged = pct(b) - pct(a) < 26
  return (
    <div className="range" aria-label={label}>
      <div className="range-track">
        <div className="range-fill" style={{ left: at(pct(a)), right: `calc(100% - ${at(pct(b))})` }} />
        <input type="range" min={min} max={max} value={a} aria-label={`${label} from`}
          onChange={(e) => onChange([Math.min(+e.target.value, b), b])} />
        <input type="range" min={min} max={max} value={b} aria-label={`${label} to`}
          onChange={(e) => onChange([a, Math.max(+e.target.value, a)])} />
      </div>
      <div className="range-chips" aria-hidden>
        {merged ? (
          <span className="chip" style={{ left: at((pct(a) + pct(b)) / 2) }}>
            {a === b ? format(a) : `${format(a)} – ${format(b)}`}
          </span>
        ) : (
          <>
            <span className="chip" style={{ left: at(pct(a)) }}>{format(a)}</span>
            <span className="chip" style={{ left: at(pct(b)) }}>{format(b)}</span>
          </>
        )}
      </div>
    </div>
  )
}

export function Stepper({ min, max, value, onChange, label, unit }: {
  min: number; max: number; value: number; onChange: (v: number) => void; label: string; unit?: string
}) {
  return (
    <div className="stepper" role="group" aria-label={label}>
      <button aria-label={`Fewer ${label.toLowerCase()}`} disabled={value <= min}
        onClick={() => onChange(Math.max(min, value - 1))}>−</button>
      <output aria-live="polite">{value}{unit && <small> {unit}</small>}</output>
      <button aria-label={`More ${label.toLowerCase()}`} disabled={value >= max}
        onClick={() => onChange(Math.min(max, value + 1))}>+</button>
    </div>
  )
}

export function Tooltip({ x, y, children }: { x: number; y: number; children: ReactNode }) {
  return (
    <div className="glass tooltip" style={{ transform: `translate(${x}px, ${y}px)` }}>
      {children}
    </div>
  )
}

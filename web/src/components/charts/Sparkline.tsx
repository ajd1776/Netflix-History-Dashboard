/** Tiny bar chart, one bar per value. */
export function Sparkline({ values, labels, width = 88, height = 24 }: {
  values: number[]
  labels?: (string | number)[]
  width?: number
  height?: number
}) {
  const max = Math.max(1, ...values)
  const step = width / values.length
  const bw = Math.max(2, step - 2)
  return (
    <svg className="sparkline" width={width} height={height} aria-hidden>
      {values.map((v, i) => {
        const h = v ? Math.max(2, (v / max) * height) : 1
        return (
          <rect key={i} x={i * step} y={height - h} width={bw} height={h} rx={1.5}
            className={v ? 'on' : 'off'}>
            {labels && <title>{`${labels[i]}: ${v}`}</title>}
          </rect>
        )
      })}
    </svg>
  )
}

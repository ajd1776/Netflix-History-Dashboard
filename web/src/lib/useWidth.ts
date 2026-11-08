import { useLayoutEffect, useRef, useState } from 'react'

/** Width of an element, kept current with a ResizeObserver. */
export function useWidth<T extends HTMLElement>() {
  const ref = useRef<T>(null)
  const [width, setWidth] = useState(0)
  useLayoutEffect(() => {
    const el = ref.current
    if (!el) return
    // Measure now so charts draw on first paint; the observer only reports later changes.
    setWidth(el.clientWidth)
    const ro = new ResizeObserver(([e]) => setWidth(Math.floor(e.contentRect.width)))
    ro.observe(el)
    return () => ro.disconnect()
  }, [])
  return [ref, width] as const
}

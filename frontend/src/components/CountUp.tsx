/**
 * The KPI count-up of DESIGN-ship-1 §11 — under 600 ms, and the last frame is the FILE's number.
 *
 * It counts from where the card already stood, so a filter that changes a figure walks it to the
 * new one instead of dropping it to zero and climbing again.
 *
 * `prefers-reduced-motion: reduce` disables it. The stylesheet's global `animation: none` cannot:
 * this is a script writing text into the DOM, and a reader who asked the system for no motion
 * would still get 600 ms of moving digits. So the query is ASKED here, and the value is set once.
 *
 * A HIDDEN document is the second case, and it is not decoration but correctness: a background tab
 * gets no animation frame at all — measured, 0 frames in 300 ms — so a card whose figure changed
 * would keep PAINTING THE OLD NUMBER, and a card mounting there would paint 0. Both are figures no
 * file carries. Hidden means the value, at once.
 */

import { useEffect, useRef, useState } from 'react'

const DURATION_MS = 600

/** Cubic ease-out: fast first, settled by the end — the same curve the card hover uses. */
function ease(k: number): number {
  return 1 - (1 - k) ** 3
}

export function reducedMotion(): boolean {
  try {
    return window.matchMedia('(prefers-reduced-motion: reduce)').matches
  } catch {
    return false
  }
}

export function useCountUp(value: number): number {
  // the first RENDER decides what the first paint shows, and the effect below runs after it: a card
  // that must not animate would otherwise paint `0` for a frame — a figure no file carries
  const still = reducedMotion() || document.hidden
  const from = useRef(still ? value : 0)
  const [shown, setShown] = useState(from.current)

  useEffect(() => {
    const start = from.current
    if (reducedMotion() || document.hidden) {
      from.current = value
      setShown(value)
      return
    }
    let frame = 0
    const began = performance.now()
    const step = (now: number): void => {
      const k = Math.min(1, (now - began) / DURATION_MS)
      // k === 1 lands on `value` exactly: the number that settles is the export's, not a rounding
      const next = Math.round(start + (value - start) * ease(k))
      from.current = next
      setShown(next)
      if (k < 1) frame = requestAnimationFrame(step)
    }
    frame = requestAnimationFrame(step)
    return () => cancelAnimationFrame(frame)
  }, [value])

  return shown
}

export interface CountUpProps {
  value: number
  format: (value: number) => string
}

export function CountUp({ value, format }: CountUpProps): React.JSX.Element {
  const shown = useCountUp(value)
  return <span className="countup">{format(shown)}</span>
}

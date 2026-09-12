/**
 * KpiCard — label (with its ⓘ), value, context line, status badge (DESIGN-ship-1 §5).
 *
 * The value arrives FORMATTED: the formatting is the caller's, because the caller is the one
 * holding the field and its unit — a string, or the <CountUp> of §11 walking to it. Colour never
 * carries the status alone — the badge is an icon and a word.
 */

import { Info } from './Info.tsx'
import { StatusBadge, type StatusKind } from './StatusBadge.tsx'

export interface KpiCardProps {
  label: string
  value: React.ReactNode
  context?: string
  status?: { kind: StatusKind; label: string }
  info?: { lines: string[]; provenance: string; label: string }
}

export function KpiCard({ label, value, context, status, info }: KpiCardProps): React.JSX.Element {
  return (
    <article className="card tile">
      <h3>
        {label}
        {info !== undefined && (
          <Info lines={info.lines} provenance={info.provenance} label={info.label} />
        )}
      </h3>
      <p className="figure">{value}</p>
      {status !== undefined && <StatusBadge kind={status.kind} label={status.label} />}
      {context !== undefined && <p className="context">{context}</p>}
    </article>
  )
}

/**
 * A status is an ICON, a WORD and a colour — never a colour alone (DESIGN-ship-1 §3, §8).
 */

export type StatusKind = 'good' | 'warning' | 'serious' | 'critical'

const GLYPH: Record<StatusKind, string> = {
  good: '✓',
  warning: '!',
  serious: '!',
  critical: '✕',
}

export function StatusBadge({
  kind,
  label,
}: {
  kind: StatusKind
  label: string
}): React.JSX.Element {
  return (
    <span className={`status ${kind}`}>
      <span aria-hidden="true">{GLYPH[kind]}</span>
      {label}
    </span>
  )
}

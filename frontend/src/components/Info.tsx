/**
 * The ⓘ of DESIGN-ship-1 §5: what a figure means, how to read it, and WHICH FILE it came from.
 *
 * A real `<button aria-expanded>` and a plain positioned panel — no library. Every figure on the
 * app can say its provenance, which is the one feature that makes a number on a screen checkable.
 */

import { useId, useState } from 'react'

export interface InfoProps {
  /** the lines of the explanation, in the reader's language */
  lines: string[]
  /** `file :: field` — always shown, last */
  provenance: string
  label: string
}

export function Info({ lines, provenance, label }: InfoProps): React.JSX.Element {
  const [open, setOpen] = useState(false)
  const id = useId()
  return (
    <span className="holder">
      <button
        type="button"
        className="info"
        aria-expanded={open}
        aria-controls={id}
        aria-label={label}
        onClick={() => setOpen(!open)}
      >
        ⓘ
      </button>
      <span className="popover" id={id} hidden={!open} role="note">
        {lines.map((line) => (
          <p key={line}>{line}</p>
        ))}
        <p className="muted">
          <code>{provenance}</code>
        </p>
      </span>
    </span>
  )
}

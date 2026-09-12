/**
 * The flyer at full size — a native `<dialog>`, the way DESIGN-ship-1 §5 opens a drawer.
 *
 * `showModal()` brings the focus trap, the Esc key, the backdrop and the inertness of everything
 * behind it with it; a library would bring the same four and a dependency. Left/Right walk the
 * pages of the set the card opened, and a single page (a table row's own leaflet) simply has no
 * neighbours to walk to.
 *
 * **Closing is the caller's state, never the `close` event.** Measured in this browser, on a plain
 * `<dialog>` outside React as well as on this one: `close()` and the Esc key fire NO `close` event,
 * so a component that learns of its closing from `onClose` (React's prop or a listener on the
 * element) stays mounted with the dialog shut — and the card that opened it cannot open it again,
 * because nothing remounts. So the two ways out — the button and Esc — call {@link onClose}
 * themselves, the state clears, and the unmount takes the dialog out of the top layer.
 */

import { useEffect, useRef, useState } from 'react'

import type { Translate } from '../i18n/t.ts'

export interface LightboxProps {
  t: Translate
  title: string
  /** the page names of this set, in the channel's own page order */
  pages: string[]
  start: number
  urlOf: (name: string) => string
  onClose: () => void
}

export function Lightbox({ t, title, pages, start, urlOf, onClose }: LightboxProps): React.JSX.Element {
  const dialog = useRef<HTMLDialogElement>(null)
  const [at, setAt] = useState(start)
  const [gone, setGone] = useState<string | null>(null)

  useEffect(() => {
    dialog.current?.showModal()
  }, [])

  const page = pages[Math.min(at, pages.length - 1)]
  const step = (by: number): void => setAt((now) => Math.min(pages.length - 1, Math.max(0, now + by)))

  return (
    <dialog
      className="lightbox"
      ref={dialog}
      onKeyDown={(event) => {
        if (event.key === 'Escape') onClose()
        if (event.key === 'ArrowRight') step(1)
        if (event.key === 'ArrowLeft') step(-1)
      }}
    >
      <header>
        <b>{title}</b>
        {pages.length > 1 && (
          <span className="muted">
            {t('common.page')} {at + 1} / {pages.length}
          </span>
        )}
        <button type="button" onClick={onClose}>
          {t('media.close')}
        </button>
      </header>
      {page === undefined || page === gone ? (
        // a checkout without the photos stages none of them, and the card that opened this dialog
        // is still clickable: the page says so instead of showing a broken image
        <p className="muted">{page === undefined ? t('common.absent') : t('media.no_page')}</p>
      ) : (
        <img src={urlOf(page)} alt={`${title} — ${page}`} onError={() => setGone(page)} />
      )}
      {pages.length > 1 && (
        <footer>
          <button type="button" disabled={at === 0} onClick={() => step(-1)}>
            {t('common.prev')}
          </button>
          <code>{page}</code>
          <button type="button" disabled={at + 1 >= pages.length} onClick={() => step(1)}>
            {t('common.next')}
          </button>
        </footer>
      )}
    </dialog>
  )
}

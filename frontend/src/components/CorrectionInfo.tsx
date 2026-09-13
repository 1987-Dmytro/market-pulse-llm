/**
 * The ⓘ a hand-corrected row carries: what a human changed, against which page, and who read it.
 *
 * Eight rows of this window carry a figure their own leaflet page contradicts — the model misread a
 * photograph, and the readings of ruling (yy) were written down in `config/price_corrections.yaml`
 * rather than left on the screen. A corrected figure with nothing beside it would be the worst of
 * both: a number no file explains. So wherever a corrected card is rendered, this sits next to it
 * and says the row was corrected by hand, what it said before, and which page answers for it.
 *
 * Every word here is the dictionary's and every figure is the card's own: the component states
 * nothing of its own (DESIGN-ship-1 §3).
 */

import { count, price } from '../format.ts'
import type { Lang, Translate } from '../i18n/t.ts'
import type { Correction } from '../types.ts'
import { Info } from './Info.tsx'

/** What this ⓘ needs of whatever carries it: a `PriceCard` has these four fields, and a position
 *  row keeps its size inside `item`, so the table spreads the two together at the call site. */
export interface Corrected {
  correction?: Correction
  promo_price?: number
  size_value?: number
  size_unit?: string
}

export function CorrectionInfo({
  card,
  lang,
  t,
}: {
  card: Corrected
  lang: Lang
  t: Translate
}): React.JSX.Element | null {
  const fixed = card.correction
  if (fixed === undefined) return null
  const lines = [t('prices.corrected')]
  if (fixed.was.promo_price !== undefined && card.promo_price !== undefined)
    lines.push(
      t('prices.corrected.was', {
        was: price(lang, fixed.was.promo_price),
        now: price(lang, card.promo_price),
      }),
    )
  if (fixed.was.size_value !== undefined && card.size_value !== undefined)
    lines.push(
      t('prices.corrected.was', {
        was: `${count(lang, fixed.was.size_value)} ${card.size_unit ?? ''}`,
        now: `${count(lang, card.size_value)} ${card.size_unit ?? ''}`,
      }),
    )
  lines.push(t('prices.corrected.by', { who: fixed.verified_by.join(', ') }))
  return <Info lines={lines} provenance={`${fixed.from} :: ${fixed.page}`} label={lines[0] ?? ''} />
}

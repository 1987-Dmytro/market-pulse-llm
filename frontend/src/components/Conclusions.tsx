/**
 * «Три висновки тижня» — the message at the top of the page (DESIGN-ship-1 §12, the pyramid).
 *
 * Every sentence is produced by a code rule in `scripts/export_front_data.py` over the same price
 * block the exhibits below draw, and each carries the path of every figure it states: the ⓘ lists
 * them, so a reader who doubts a sentence can open the field it stands on. This component renders
 * and words nothing — a week whose rules found nothing shows no block at all rather than a frame
 * with an invented reading in it.
 */

import { useApp } from '../app-state.ts'
import { TRENDS_FIELD, findingText, trends } from '../data/front.ts'
import { FRONT_FILE } from '../data/load.ts'
import { Info } from './Info.tsx'

export function Conclusions(): React.JSX.Element | null {
  const { front, lang, t } = useApp()
  const block = trends(front)
  if (block.conclusions.length === 0) return null

  return (
    <section className="card conclusions">
      <h2>{t('trends.conclusions.title')}</h2>
      <ol>
        {block.conclusions.map((finding) => (
          <li key={finding.id}>
            {findingText(finding, lang)}
            <Info
              lines={[t('trends.conclusions.rule'), ...Object.keys(finding.stands_on)]}
              provenance={`${FRONT_FILE} :: ${TRENDS_FIELD}.conclusions`}
              label={t('common.info')}
            />
          </li>
        ))}
      </ol>
    </section>
  )
}

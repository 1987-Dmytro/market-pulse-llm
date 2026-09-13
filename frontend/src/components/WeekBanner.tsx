/**
 * «Тиждень W… · dates» — the ONE weekly frame both promo tabs carry (operator's rule (б), 13.09).
 *
 * The week is the export's own `reporting_week`: the newest ISO week ANY chain has leaflet pages
 * in, with the dates those pages carry. That is one chain's week and not the market's — today
 * Маркетопт's 2026-W36 while nine chains' newest set is W35 — so the banner carries the ⓘ that
 * says how many chains are in it, and every chain's card prints its own newest week beside its
 * dates. A banner that let a reader take the whole screen for one week's reading would be the
 * frame making a claim the data does not.
 */

import { useApp } from '../app-state.ts'
import { WEEK_FIELD, reportingWeek, span } from '../data/front.ts'
import { FRONT_FILE } from '../data/load.ts'
import { count } from '../format.ts'
import { Info } from './Info.tsx'

export function WeekBanner(): React.JSX.Element {
  const { front, lang, t } = useApp()
  const week = reportingWeek(front)
  const label = t('week.banner', { week: week.week, dates: span(week.since, week.until) })
  return (
    <p className="week-banner">
      <b>{label}</b>
      <Info
        lines={[
          t('week.rule', {
            chains: count(lang, week.chains.length),
            total: count(lang, week.chains_with_a_set),
          }),
        ]}
        provenance={`${FRONT_FILE} :: ${WEEK_FIELD}`}
        label={label}
      />
    </p>
  )
}

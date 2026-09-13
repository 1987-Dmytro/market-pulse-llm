/**
 * Who is cheapest in the week's biggest category — chains ranked by their median, with the market
 * median of the same category as the reference line (DESIGN-ship-1 §12).
 *
 * The ranking is cut INSIDE one (category × unit) basis, never across categories: a chain's median
 * over everything it prices would put cheese beside milk and read the chain with more cheese on
 * its leaflet as the expensive one. The basis is the producer's choice — the one with the most
 * priced rows — and its rows are the producer's medians, read here and recomputed nowhere.
 *
 * `n` stands beside every bar because one row is also a median: no floor drops a thin chain, so
 * the reader sees the count and decides what to make of it.
 */

import { useApp } from '../app-state.ts'
import { exhibitTitle, findingText, rankedBasis } from '../data/front.ts'
import { FRONT_FILE } from '../data/load.ts'
import { count, perUnit } from '../format.ts'
import { CATEGORY_FIELD } from './CategoryPrices.tsx'
import { ChartCard } from './ChartCard.tsx'

export function ChainRanking(): React.JSX.Element | null {
  const { front, lang, t } = useApp()
  const ranked = rankedBasis(front)
  if (ranked === undefined || ranked.basis.chains.length === 0) return null

  const { basis, category } = ranked
  const rows = basis.chains
  const title = exhibitTitle(front, 'chain_ranking')
  // the bars are scaled to the dearest MEDIAN, not to the dearest row: the exhibit compares
  // medians, and a single expensive pack would otherwise squash every bar beside it
  const ceiling = Math.max(...rows.map((row) => row.median), basis.median ?? 0)
  const at = (value: number): string => `${((value / ceiling) * 100).toFixed(2)}%`
  const lowest = rows[0]?.median

  return (
    <ChartCard
      t={t}
      wide
      title={title === undefined ? t('trends.exhibit.untitled') : findingText(title, lang)}
      subtitle={`${category.name} · ${t('trends.ranking.subtitle')}`}
      provenance={`${FRONT_FILE} :: ${CATEGORY_FIELD}.categories[].bases[].chains`}
      info={[
        t('trends.ranking.rule'),
        ...(basis.median === null
          ? []
          : [t('trends.ranking.market', { value: perUnit(lang, t, basis.median, basis.unit) })]),
      ]}
      // the caveat rides UNDER the exhibit, not inside the ⓘ: three of these bars are one
      // retailer's three channels, and a reader who does not know that reads three chains
      note={t('trends.ranking.channels')}
      table={{
        head: [
          t('trends.ranking.col.chain'),
          t('common.rows'),
          t('trends.prices.col.min'),
          t('trends.prices.median'),
          t('trends.prices.col.max'),
        ],
        rows: rows.map((row) => [row.name, row.n, row.min, row.median, row.max]),
      }}
    >
      <div className="ranking">
        {rows.map((row) => (
          <div className="rank-row" key={row.chain}>
            <span className="rank-name">{row.name}</span>
            <span className="track">
              {/* the message's series in colour, the context greyed: the lowest median is what
                  the exhibit's title says, and a tie wears the accent on every chain that holds it */}
              <span
                className={row.median === lowest ? 'bar accent' : 'bar'}
                style={{ width: at(row.median) }}
                title={perUnit(lang, t, row.median, basis.unit)}
              />
              {basis.median !== null && (
                <span className="ref" style={{ left: at(basis.median) }} />
              )}
            </span>
            <span className="rank-value">
              {perUnit(lang, t, row.median, basis.unit)}{' '}
              <span className="muted">{count(lang, row.n)}</span>
            </span>
          </div>
        ))}
      </div>
    </ChartCard>
  )
}

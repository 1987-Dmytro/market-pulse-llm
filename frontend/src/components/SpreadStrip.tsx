/**
 * The min–median–max dot-range strip, one row per (category × unit) — DESIGN-ship-1 §12's form for
 * a spread.
 *
 * The axis is SHARED INSIDE ONE UNIT and never across two: ₴/кг and ₴/л on one scale would invite
 * the reader to compare a kilogram with a litre, which is the sum with no unit the price block was
 * cut in two to avoid. Each group therefore carries its own axis, and the unit is written on it.
 *
 * Every figure is a field of `category_prices`; the only arithmetic here is the position of a mark
 * along its own group's axis, which is layout, not a reading. The row the week's rule named — the
 * widest spread — wears the accent and the rest are context grey (§12: one message per exhibit).
 */

import { useApp } from '../app-state.ts'
import { CATEGORY_FIELD } from './CategoryPrices.tsx'
import { categoryPrices, exhibitTitle, findingText, trends } from '../data/front.ts'
import { FRONT_FILE } from '../data/load.ts'
import { count, perUnit, unitWord } from '../format.ts'
import type { CategoryBasis, CategoryPrices } from '../types.ts'
import { ChartCard } from './ChartCard.tsx'

/** One strip: a basis whose three ends the file carries. A basis with a null end is left out of
 *  the exhibit and stays on the cards — a strip cannot draw a range one side of which is absent. */
interface Strip {
  key: string
  name: string
  unit: string
  n: number
  min: number
  median: number
  max: number
  accent: boolean
}

function stripsOf(
  categories: CategoryPrices[],
  widest: { category: string; unit: string } | null,
): Strip[] {
  const rows: Strip[] = []
  for (const category of categories) {
    for (const basis of category.bases as CategoryBasis[]) {
      const { min, median, max } = basis
      if (min === null || median === null || max === null) continue
      rows.push({
        key: `${category.category}:${basis.unit}`,
        name: category.name,
        unit: basis.unit,
        n: basis.n,
        min,
        median,
        max,
        accent: widest !== null && widest.category === category.category && widest.unit === basis.unit,
      })
    }
  }
  // the dearest median first: a director reads the top of a ranking, and the sort is the file's
  // own numbers, ties broken by the pair's key so the exhibit is the same on every build
  return rows.sort((left, right) => right.median - left.median || left.key.localeCompare(right.key))
}

export function SpreadStrip(): React.JSX.Element | null {
  const { front, lang, t } = useApp()
  const block = categoryPrices(front)
  const title = exhibitTitle(front, 'spread')
  const strips = stripsOf(block.categories, trends(front).widest)
  if (strips.length === 0) return null

  // one axis per unit, in the order the units first appear — each group is scaled to its own
  // dearest row, so a row is read against the prices of its own kind and no other
  const units = [...new Set(strips.map((row) => row.unit))]
  const ceiling = new Map(
    units.map((unit) => [
      unit,
      Math.max(...strips.filter((row) => row.unit === unit).map((row) => row.max)),
    ]),
  )
  const at = (value: number, unit: string): string =>
    `${((value / (ceiling.get(unit) ?? value)) * 100).toFixed(2)}%`

  return (
    <ChartCard
      t={t}
      wide
      title={title === undefined ? t('trends.exhibit.untitled') : findingText(title, lang)}
      subtitle={t('trends.spread.subtitle')}
      provenance={`${FRONT_FILE} :: ${CATEGORY_FIELD}.categories[].bases[]`}
      info={[t('trends.spread.rule')]}
      table={{
        head: [
          t('trends.prices.col.category'),
          t('trends.prices.col.unit'),
          t('common.rows'),
          t('trends.prices.col.min'),
          t('trends.prices.median'),
          t('trends.prices.col.max'),
        ],
        rows: strips.map((row) => [
          row.name,
          unitWord(t, row.unit),
          row.n,
          row.min,
          row.median,
          row.max,
        ]),
      }}
    >
      <div className="strips">
        {units.map((unit) => (
          <div className="strip-group" key={unit}>
            <p className="strip-unit">
              {t('trends.spread.scale', { max: perUnit(lang, t, ceiling.get(unit) ?? 0, unit) })}
            </p>
            {strips
              .filter((row) => row.unit === unit)
              .map((row) => (
                <div className="strip-row" key={row.key}>
                  <span className="strip-name">
                    {row.name} <span className="muted">{count(lang, row.n)}</span>
                  </span>
                  <span className="track">
                    <span
                      className="range"
                      style={{ left: at(row.min, unit), width: at(row.max - row.min, unit) }}
                    />
                    <span
                      className={row.accent ? 'dot accent' : 'dot'}
                      style={{ left: at(row.median, unit) }}
                      title={perUnit(lang, t, row.median, unit)}
                    />
                  </span>
                  <span className="strip-values">
                    {perUnit(lang, t, row.min, unit)} · <b>{perUnit(lang, t, row.median, unit)}</b> ·{' '}
                    {perUnit(lang, t, row.max, unit)}
                  </span>
                </div>
              ))}
          </div>
        ))}
      </div>
    </ChartCard>
  )
}

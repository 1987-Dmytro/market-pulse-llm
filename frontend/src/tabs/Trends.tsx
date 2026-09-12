/**
 * Промо · Тренди — how promo moves week by week and who discounts deeper (DESIGN-ship-1 §7).
 *
 * `promo_screen_data.json :: screen.rollup`, `screen.weeks` and `screen.depth_by_chain_and_brand`,
 * read and re-computed nowhere. Every rollup and depth row is keyed on (chain, brand, week) and its
 * `chain` is a CHANNEL HANDLE — `@atb_market_official`, not a folded chain id — so a chain × week
 * cell, or one bar per chain, would have to SUM ACROSS BRANDS. That sum is a figure no file
 * carries, which is why this tab picks ONE brand and ONE metric and why every mark on it is one
 * row's own `value`.
 *
 * What the tab refuses: a price-by-week line (the export carries no such series, and
 * `trends.no_price_series` says so instead of a line drawn from something near it); a zero where a
 * week has no row (the point is absent, the line breaks, the cell stays empty); and any total over
 * brands or chains — including an «усі» option on the brand select.
 */

import { Fragment } from 'react'
import {
  Bar,
  BarChart,
  CartesianGrid,
  LabelList,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'

import { useApp } from '../app-state.ts'
import { ChartCard } from '../components/ChartCard.tsx'
import { colourByIndex, orderChains } from '../data/chains.ts'
import { PROMO_FILE } from '../data/load.ts'
import { depthRows, rollup, rollupMetrics, rollupOf, weeks } from '../data/promo.ts'
import { count, percent } from '../format.ts'
import type { Lang } from '../i18n/t.ts'
import { paramOf, setParam, useRoute } from '../router.ts'
import type { RollupRow } from '../types.ts'

/** The three fields this tab reads. `data/promo.ts` spells the same three inside its own `must()`
 *  calls and exports a constant for `screen.positions` only. */
const ROLLUP_FIELD = 'screen.rollup'
const WEEKS_FIELD = 'screen.weeks'
const DEPTH_FIELD = 'screen.depth_by_chain_and_brand'

/** CHART 3's metric — the file's own name for «positions that carried a price». */
const PRICED_METRIC = 'priced_positions'

/**
 * `depth_mean` is a SHARE in the file (0.4671); `priced_positions` and `sku_count` are counts of
 * rows. The metric's own name is the only thing that says which unit a value wears — and a metric
 * that is absent cannot be the share, so its values format as counts.
 */
const SHARE_METRIC = 'depth_mean'

function valueText(lang: Lang, metric: string | undefined, value: number): string {
  return metric === SHARE_METRIC ? percent(value) : count(lang, value)
}

/** The value the hash asks for while the file still carries it, else the first of the list;
 *  `undefined` only when the list itself is empty. */
function pick(values: string[], wanted: string | undefined): string | undefined {
  return wanted !== undefined && values.includes(wanted) ? wanted : values[0]
}

/** One x position of CHART 1: the week, and one key per channel handle that HAS a row for it. A
 *  handle with no row is ABSENT from the point — that hole is what breaks the line. */
type WeekPoint = Record<string, string | number>

/** The heatmap's band: the count itself is the band (1 → `--ramp-1` … ≥ 7 → `--ramp-7`), so the
 *  colour is read off the row's own value and no scale is computed from the data. */
function rampOf(value: number): number {
  return Math.min(7, Math.max(1, Math.round(value)))
}

/** The ramp tokens are the same in both themes, so a cell's text colour follows the RAMP and not
 *  the theme: the palette's two text ends, dark on the light bands and white on the dark ones
 *  (§8 asks 4.5:1). */
function rampTextColour(ramp: number): string {
  return ramp >= 5 ? '#ffffff' : '#0b0b0b'
}

/** The tooltip wears the card's own surface, so a mark's value is read in the page's theme. */
const TOOLTIP_STYLE = {
  background: 'var(--surface-1)',
  border: '1px solid var(--border)',
  borderRadius: 4,
  color: 'var(--text-1)',
  fontSize: 12,
}

const TICK = { fill: 'var(--text-2)', fontSize: 11 }

export function TrendsTab(): React.JSX.Element {
  const { promo, lang, t } = useApp()
  const route = useRoute()

  const allWeeks = weeks(promo)
  const rollupAll = rollup(promo)
  const depthAll = depthRows(promo)

  const metrics = rollupMetrics(promo)
  const brands = [...new Set(rollupAll.map((row) => row.brand))].sort((left, right) =>
    left.localeCompare(right, 'uk'),
  )
  const metric = pick(metrics, paramOf(route, 'metric'))
  const brand = pick(brands, paramOf(route, 'brand'))

  // the week select, the bars and the heatmap columns read ONE week order — the export's own
  // `screen.weeks`; the default is the LAST week the depth rows reach, not the oldest
  const depthWeeks = allWeeks.filter((one) => depthAll.some((row) => row.week === one))
  const wantedWeek = paramOf(route, 'week')
  const week =
    wantedWeek !== undefined && depthWeeks.includes(wantedWeek) ? wantedWeek : depthWeeks.at(-1)

  const series: RollupRow[] =
    brand === undefined || metric === undefined
      ? []
      : rollupOf(promo, metric).filter((row) => row.brand === brand)
  const lineHandles = orderChains(series.map((row) => row.chain))
  const points: WeekPoint[] = allWeeks.map((one) => {
    const point: WeekPoint = { week: one }
    // one row per (chain, brand, week, metric) — the export's own key, so no cell is written twice
    for (const row of series) if (row.week === one) point[row.chain] = row.value
    return point
  })

  // no week to show (the field carries no rows) leaves the filter empty, which is the same state
  // the cards say out loud — deeper bars first, the label breaking every tie
  const depthOfWeek = depthAll
    .filter((row) => row.week === week)
    .sort(
      (left, right) =>
        right.depth_mean - left.depth_mean ||
        `${left.chain} ${left.brand}`.localeCompare(`${right.chain} ${right.brand}`, 'uk'),
    )
  const bars = depthOfWeek.map((row) => ({
    label: `${row.chain} · ${row.brand}`,
    depth_mean: row.depth_mean,
    depth_text: percent(row.depth_mean),
  }))

  const priced: RollupRow[] =
    brand === undefined ? [] : rollupOf(promo, PRICED_METRIC).filter((row) => row.brand === brand)
  const heatHandles = orderChains(priced.map((row) => row.chain))
  const cells = new Map<string, number>()
  for (const row of priced) cells.set(`${row.chain}|${row.week}`, row.value)

  const select = (name: string, label: string, values: string[], current: string | undefined) => (
    <label>
      {label}
      <select value={current ?? ''} onChange={(event) => setParam(route, name, event.target.value)}>
        {values.map((value) => (
          <option key={value} value={value}>
            {value}
          </option>
        ))}
      </select>
    </label>
  )

  /** «rows not exported» when the block's field carries no rows at all, «none in the data» when it
   *  has rows but none for the brand, metric or week the reader picked (DESIGN §10). */
  const emptyNote = (exported: number): React.JSX.Element => (
    <p className="note">{exported === 0 ? t('common.not_exported') : t('common.absent')}</p>
  )

  return (
    <>
      <h2 className="question">{t('trends.question')}</h2>
      <p className="population">
        {t('trends.col.week')}: {count(lang, allWeeks.length)} · {t('trends.col.chain')}:{' '}
        {count(lang, new Set(rollupAll.map((row) => row.chain)).size)} · {t('trends.col.brand')}:{' '}
        {count(lang, brands.length)} · {t('common.rows')}: {count(lang, rollupAll.length)}
      </p>

      {/* no «усі» option on the brand select: «усі» would be a sum across the brands of a handle,
          and that sum is exactly the figure the export does not carry */}
      <div className="filters">
        {select('metric', t('trends.filter.metric'), metrics, metric)}
        {select('brand', t('trends.filter.brand'), brands, brand)}
        {select('week', t('trends.col.week'), depthWeeks, week)}
      </div>

      <div className="charts">
        <ChartCard
          t={t}
          wide
          title={`${t('trends.col.metric')}: ${metric ?? t('common.absent')}`}
          subtitle={`${t('trends.filter.brand')}: ${brand ?? t('common.absent')} · ${t('trends.col.week')}`}
          provenance={`${PROMO_FILE} :: ${ROLLUP_FIELD}, ${WEEKS_FIELD}`}
          note={`${t('common.empty_week')} · ${t('trends.no_price_series')}`}
          legend={lineHandles.map((handle, index) => ({
            colour: colourByIndex(index),
            label: handle,
          }))}
          table={{
            head: [
              t('trends.col.week'),
              t('trends.col.chain'),
              t('trends.col.brand'),
              t('trends.col.metric'),
              t('common.value'),
            ],
            rows: [...series]
              .sort(
                (left, right) =>
                  left.week.localeCompare(right.week) || left.chain.localeCompare(right.chain),
              )
              .map((row) => [
                row.week,
                row.chain,
                row.brand,
                row.metric,
                valueText(lang, row.metric, row.value),
              ]),
          }}
        >
          {lineHandles.length === 0 ? (
            emptyNote(rollupAll.length)
          ) : (
            <ResponsiveContainer width="100%" height={280}>
              <LineChart data={points} margin={{ top: 8, right: 16, bottom: 0, left: 0 }}>
                <CartesianGrid stroke="var(--border)" vertical={false} />
                <XAxis dataKey="week" tick={TICK} stroke="var(--text-3)" />
                <YAxis
                  width={64}
                  tickFormatter={(value: number) => valueText(lang, metric, value)}
                  tick={TICK}
                  stroke="var(--text-3)"
                />
                <Tooltip
                  contentStyle={TOOLTIP_STYLE}
                  formatter={(value) =>
                    typeof value === 'number' ? valueText(lang, metric, value) : String(value)
                  }
                />
                {/* the rollup's chain has no slot in the registry's table (it is a handle), so the
                    colour comes from the position in THIS chart's ordered handle list */}
                {lineHandles.map((handle, index) => (
                  <Line
                    key={handle}
                    name={handle}
                    type="linear"
                    dataKey={handle}
                    stroke={colourByIndex(index)}
                    strokeWidth={2}
                    dot={{ r: 3 }}
                    connectNulls={false}
                    isAnimationActive={false}
                  />
                ))}
              </LineChart>
            </ResponsiveContainer>
          )}
        </ChartCard>

        <ChartCard
          t={t}
          title={t('trends.depth.title')}
          subtitle={`${t('trends.col.week')}: ${week ?? t('common.absent')} · ${t('trends.depth.subtitle')}`}
          provenance={`${PROMO_FILE} :: ${DEPTH_FIELD}`}
          note={t('common.empty_week')}
          table={{
            head: [
              t('trends.col.week'),
              t('trends.col.chain'),
              t('trends.col.brand'),
              t('trends.col.depth'),
            ],
            rows: depthOfWeek.map((row) => [
              row.week,
              row.chain,
              row.brand,
              percent(row.depth_mean),
            ]),
          }}
        >
          {bars.length === 0 ? (
            emptyNote(depthAll.length)
          ) : (
            <ResponsiveContainer width="100%" height={Math.max(200, bars.length * 22 + 48)}>
              <BarChart data={bars} layout="vertical" margin={{ top: 4, right: 72, bottom: 4, left: 4 }}>
                <CartesianGrid stroke="var(--border)" horizontal={false} />
                <XAxis
                  type="number"
                  tickFormatter={(value: number) => percent(value, 0)}
                  tick={TICK}
                  stroke="var(--text-3)"
                />
                <YAxis
                  type="category"
                  dataKey="label"
                  width={300}
                  interval={0}
                  tick={TICK}
                  stroke="var(--text-3)"
                />
                <Tooltip
                  contentStyle={TOOLTIP_STYLE}
                  formatter={(value) => (typeof value === 'number' ? percent(value) : String(value))}
                />
                {/* one measure, sorted: ONE colour. The handle and the brand are on the bar's own
                    label, so a colour per chain would encode what the label already says */}
                <Bar
                  dataKey="depth_mean"
                  fill="var(--s1)"
                  radius={[0, 4, 4, 0]}
                  isAnimationActive={false}
                >
                  <LabelList
                    dataKey="depth_text"
                    position="right"
                    fill="var(--text-2)"
                    fontSize={11}
                  />
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          )}
        </ChartCard>

        <ChartCard
          t={t}
          wide
          title={t('trends.priced.title')}
          subtitle={`${t('trends.priced.subtitle')} · ${t('trends.filter.brand')}: ${brand ?? t('common.absent')}`}
          provenance={`${PROMO_FILE} :: ${ROLLUP_FIELD} (${PRICED_METRIC}), ${WEEKS_FIELD}`}
          note={t('common.empty_week')}
          table={{
            head: [t('trends.col.chain'), ...allWeeks],
            rows: heatHandles.map((handle) => [
              handle,
              ...allWeeks.map((one) => {
                const value = cells.get(`${handle}|${one}`)
                return value === undefined ? '' : count(lang, value)
              }),
            ]),
          }}
        >
          {heatHandles.length === 0 ? (
            // a file that stopped emitting this metric is «not exported», not «none in the data»
            emptyNote(metrics.includes(PRICED_METRIC) ? rollupAll.length : 0)
          ) : (
            <div className="scroll">
              <div
                className="heatmap"
                style={{ gridTemplateColumns: `auto repeat(${allWeeks.length}, minmax(56px, 1fr))` }}
              >
                <span className="head" />
                {allWeeks.map((one) => (
                  <span className="head" key={one}>
                    {one}
                  </span>
                ))}
                {heatHandles.map((handle) => (
                  <Fragment key={handle}>
                    <span className="head">{handle}</span>
                    {allWeeks.map((one) => {
                      const value = cells.get(`${handle}|${one}`)
                      // a week this handle has no row for stays EMPTY and says so — never a 0
                      if (value === undefined) {
                        return <span className="cell" key={one} title={t('common.empty_week')} />
                      }
                      const ramp = rampOf(value)
                      return (
                        <span
                          className="cell"
                          key={one}
                          style={{ background: `var(--ramp-${ramp})`, color: rampTextColour(ramp) }}
                          title={`${handle} · ${one}`}
                        >
                          {count(lang, value)}
                        </span>
                      )
                    })}
                  </Fragment>
                ))}
              </div>
            </div>
          )}
        </ChartCard>
      </div>

      <p className="sources">
        {t('common.sources')}: <code>{PROMO_FILE} :: {ROLLUP_FIELD}</code> ·{' '}
        <code>{PROMO_FILE} :: {WEEKS_FIELD}</code> · <code>{PROMO_FILE} :: {DEPTH_FIELD}</code>
      </p>
    </>
  )
}

/**
 * Командний центр — T0…T8 over `front_data.json :: command_center` (DESIGN-ship-1 §7).
 *
 * The block is `results/dashboard_data_w1.json` by reference, so every figure on these nine tabs is
 * a field of a file and none is computed here: the tabs format, sort, link, and say which field
 * they read. Three laws run through all of them.
 *
 * * **One window is a point, not a trend.** `not_computable.trend_vs_previous_window` is the
 *   file's own sentence about it, and it is printed on every KPI card's status rather than implied
 *   by an arrow nobody could justify: window-1 is the base, and the comparison arrives with the
 *   second paid window.
 * * **Two populations, and the FILE says which is the headline.** «bought» is everything the
 *   session paid for, «payable» the rows that carry words — 1 361 apart. {@link headline} reads
 *   the file's `headline_sample` and no tab picks one for itself. NSR prints the second reading
 *   beside the first, because that difference is the window's first finding; the other sampled
 *   blocks name the population in their ⓘ and print one reading — the gap is named in
 *   `docs/plans/ship-1.PROGRESS.md`, not papered over here.
 * * **A reading this window cannot carry is a SENTENCE, never an empty frame** (§10): T6 and T7 are
 *   the file's own `not_computable` entries with their reason and what unlocks them, and a cut that
 *   exports counts but not rows says «rows not exported» where the drill-down would be.
 */

import { useApp } from '../app-state.ts'
import { ChartCard } from '../components/ChartCard.tsx'
import { Info } from '../components/Info.tsx'
import { KpiCard } from '../components/KpiCard.tsx'
import { seriesColour } from '../data/chains.ts'
import {
  aspectShare,
  ccPath,
  ccWindow,
  centre,
  coverage,
  cut,
  headline,
  modelVerdict,
  notComputable,
  negativeShare,
  nsr,
  pressureByChain,
  promoDepth,
  promoPressure,
  samplesOf,
  shares,
  sov,
  volume,
} from '../data/cc.ts'
import { conclusions, metricById, sources } from '../data/front.ts'
import { FRONT_FILE } from '../data/load.ts'
import { count, percent, ratio } from '../format.ts'
import type { Lang, Translate } from '../i18n/t.ts'
import { CC_TABS } from '../router.ts'
import type { Share } from '../data/cc.ts'
import type { CommentCut, FrontExport, NotComputable, Sampled, Spread } from '../types.ts'

/** The dictionary writes its pair as `ua`/`en`; the app's own language token is `uk`/`en`. One
 *  place holds the difference, so no tab spells a language code twice. */
function say(pair: { ua: string; en: string }, lang: Lang): string {
  return lang === 'uk' ? pair.ua : pair.en
}

function sayEach(pair: { ua: string[]; en: string[] }, lang: Lang): string[] {
  return lang === 'uk' ? pair.ua : pair.en
}

const CC_PREFIX = '/cc/'

/** The brand the watchlist is built around — its own row wears the message colour, every other
 *  brand is context grey. `own_brands` is the FILE's list, so this is not a name typed here. */
function brandColour(own: string[], brand: string): string {
  return own.includes(brand) ? 'var(--s1)' : 'var(--text-3)'
}

/** The ⓘ of a metric: the dictionary's own definition, how to read it and its traps — the same
 *  words `docs/metrics.md` holds, in the reader's language, plus the field the card printed. */
function metricInfo(
  front: FrontExport,
  lang: Lang,
  t: Translate,
  id: string,
  field: string,
): { lines: string[]; provenance: string; label: string } {
  const entry = metricById(front, id)
  const lines =
    entry === undefined
      ? [t('cc.info.absent')]
      : [say(entry.definition, lang), say(entry.how_to_read, lang), ...sayEach(entry.pitfalls, lang)]
  return { lines: [...lines, notComputable(front, 'trend_vs_previous_window').reason], provenance: `${FRONT_FILE} :: ${field}`, label: t('common.info') }
}

/** Horizontal bars, sorted, with the value written at the end of the row (§6). One series, so the
 *  scale is the largest row: a share exhibit that scaled to 100% would print eight empty tracks. */
function Bars({
  rows,
  colour,
  label,
  figure = (row) => (
    <>
      <b>{percent(row.value)}</b> · {count('uk', row.count)}
    </>
  ),
}: {
  rows: Share[]
  colour: (key: string) => string
  label: (key: string) => string
  /** What is written at the end of the row. The default reads the row as a SHARE; an exhibit whose
   *  export carries a count and no share passes its own, so no percent is invented for it. */
  figure?: (row: Share) => React.ReactNode
}): React.JSX.Element {
  const ceiling = Math.max(...rows.map((row) => row.value), 0)
  return (
    <div className="strips">
      {rows.map((row) => (
        <div className="rank-row" key={row.key}>
          <span className="rank-name">{label(row.key)}</span>
          <span className="track">
            <span
              className="bar"
              style={{
                width: ceiling === 0 ? '0%' : `${(row.value / ceiling) * 100}%`,
                background: colour(row.key),
              }}
            />
          </span>
          <span className="strip-values">{figure(row)}</span>
        </div>
      ))}
    </div>
  )
}

/** A 100% stacked share bar — the form §6 gives a composition, never a pie. */
function Stacked({ parts }: { parts: { key: string; value: number; colour: string }[] }): React.JSX.Element {
  const total = parts.reduce((sum, part) => sum + part.value, 0)
  return (
    <span className="stack">
      {parts.map((part) => (
        <span
          key={part.key}
          className="slice"
          style={{ width: total === 0 ? '0%' : `${(part.value / total) * 100}%`, background: part.colour }}
          title={`${part.key}: ${part.value}`}
        />
      ))}
    </span>
  )
}

/** The sentence a reading this window cannot carry gets instead of a frame (§10). */
function Absent({ block, t }: { block: NotComputable; t: Translate }): React.JSX.Element {
  return (
    <div className="note">
      <p>{block.reason}</p>
      <p className="muted">
        {t('cc.absent.unlock')}: {block.unlock}
      </p>
    </div>
  )
}

/** The other populations of a sampled metric, printed under the headline card. */
function OtherSamples<T>({
  block,
  field,
  read,
  t,
}: {
  block: Sampled<T>
  field: string
  read: (reading: T) => string
  t: Translate
}): React.JSX.Element {
  return (
    <p className="context">
      {samplesOf(block)
        .filter((name) => name !== block.headline_sample)
        .map((name) => `${t(`cc.sample.${name}`)}: ${read(block.by_sample[name] as T)}`)
        .join(' · ')}
      <Info
        lines={[block.sample.reading]}
        provenance={`${FRONT_FILE} :: ${field}.by_sample`}
        label={t('common.info')}
      />
    </p>
  )
}

function spreadOf(t: Translate, spread: Spread): string {
  return spread.median === null
    ? t('common.absent')
    : `${percent(spread.median)} (${percent(spread.q1 ?? 0)} – ${percent(spread.q3 ?? 0)})`
}

/* ─────────────────────────────── T0 Огляд ─────────────────────────────── */

export function Overview(): React.JSX.Element {
  const { front, lang, t } = useApp()
  const rows = conclusions(front)
  const base = { kind: 'warning' as const, label: t('cc.status.base') }
  const window = ccWindow(front)

  const vol = volume(front)
  const sentiment = nsr(front)
  const negative = negativeShare(front)
  const share = sov(front)
  const depth = promoDepth(front)
  const reach = coverage(front)
  const head = {
    nsr: headline(sentiment, ccPath('metrics', 'nsr')),
    negative: headline(negative, ccPath('metrics', 'negative_share_sarcasm_adjusted')),
    sov: headline(share, ccPath('metrics', 'sov')),
  }

  return (
    <>
      <h2 className="question">{t('cc.t0.question')}</h2>
      <p className="population">
        {t('cc.window', { id: window.id, since: window.since.slice(0, 10), until: window.until.slice(0, 10) })}
      </p>

      <div className="kpis">
        <KpiCard
          label={t('cc.kpi.volume')}
          value={count(lang, vol.comments.bought)}
          context={t('cc.kpi.volume.context', {
            payable: count(lang, vol.comments.payable),
            text_less: count(lang, vol.comments.text_less),
            pages: count(lang, vol.leaflet_pages),
            positions: count(lang, vol.position_rows),
          })}
          status={base}
          info={metricInfo(front, lang, t, 'volume', ccPath('metrics', 'volume'))}
        />
        <KpiCard
          label={t('cc.kpi.nsr')}
          value={percent(head.nsr.nsr, 2)}
          context={t('cc.kpi.nsr.context', {
            positive: count(lang, head.nsr.positive),
            negative: count(lang, head.nsr.negative),
            sample: t(`cc.sample.${sentiment.headline_sample}`),
          })}
          status={base}
          info={metricInfo(front, lang, t, 'nsr', ccPath('metrics', 'nsr'))}
        />
        <KpiCard
          label={t('cc.kpi.negative')}
          value={percent(head.negative.negative_share_sarcasm_adjusted, 2)}
          context={t('cc.kpi.negative.context', {
            plain: percent(head.negative.negative_share, 2),
            sarcasm: count(lang, head.negative.reclassified_from_sarcasm),
          })}
          status={base}
          info={metricInfo(
            front,
            lang,
            t,
            'negative_share_sarcasm_adjusted',
            ccPath('metrics', 'negative_share_sarcasm_adjusted'),
          )}
        />
        <KpiCard
          label={t('cc.kpi.sov')}
          value={count(lang, head.sov.total_mentions)}
          context={t('cc.kpi.sov.context', {
            rows: count(lang, share.sample.rows ?? 0),
            of: count(lang, share.sample.of ?? 0),
          })}
          status={base}
          info={metricInfo(front, lang, t, 'sov', ccPath('metrics', 'sov'))}
        />
        <KpiCard
          label={t('cc.kpi.depth')}
          value={spreadOf(t, depth.readings.from_printed_badge)}
          context={t('cc.kpi.depth.context', {
            n: count(lang, depth.readings.from_printed_badge.n),
            disagree: count(lang, depth.printed_disagrees_with_computed),
          })}
          status={base}
          info={metricInfo(front, lang, t, 'promo_depth', ccPath('metrics', 'promo_depth'))}
        />
        <KpiCard
          label={t('cc.kpi.coverage')}
          value={percent(reach.channels.share)}
          context={t('cc.kpi.coverage.context', {
            channels: count(lang, reach.channels.with_a_row),
            registry: count(lang, reach.channels.in_registry),
            segments: count(lang, reach.segments.with_a_row),
            of: count(lang, reach.segments.in_registry),
          })}
          status={base}
          info={metricInfo(front, lang, t, 'coverage', ccPath('metrics', 'coverage'))}
        />
      </div>

      <section className="block conclusions">
        <h2>{t('cc.conclusions.title')}</h2>
        {rows.length === 0 ? (
          <p className="muted">{t('common.absent')}</p>
        ) : (
          <ol>
            {rows.map((row) => (
              <li key={row.id}>
                {lang === 'uk' ? row.ua : row.en}
                <Info
                  lines={[t('cc.conclusions.rule'), ...row.stands_on]}
                  provenance={`${FRONT_FILE} :: ${ccPath('conclusions')}`}
                  label={t('common.info')}
                />
              </li>
            ))}
          </ol>
        )}
      </section>

      <Sources fields={['metrics', 'conclusions', 'window']} t={t} />
    </>
  )
}

/* ──────────────────────── T1 Тональність і бренди ─────────────────────── */

export function Sentiment(): React.JSX.Element {
  const { front, lang, t } = useApp()
  const block = nsr(front)
  const field = ccPath('metrics', 'nsr')
  const reading = headline(block, field)
  const negative = negativeShare(front)
  const negativeHead = headline(negative, ccPath('metrics', 'negative_share_sarcasm_adjusted'))
  const share = sov(front)
  const shareHead = headline(share, ccPath('metrics', 'sov'))
  const brands = cut(front, 'brand_by_sentiment')

  const parts = [
    { key: t('cc.sentiment.positive'), value: reading.positive, colour: 'var(--s3)' },
    { key: t('cc.sentiment.neutral'), value: reading.neutral, colour: 'var(--surface-2)' },
    { key: t('cc.sentiment.negative'), value: reading.negative, colour: 'var(--s8)' },
  ]

  return (
    <>
      <h2 className="question">{t('cc.t1.question')}</h2>
      <p className="population">
        {t('cc.population', { sample: t(`cc.sample.${block.headline_sample}`), rows: count(lang, reading.scored) })}
      </p>

      <div className="kpis">
        <KpiCard
          label={t('cc.kpi.nsr')}
          value={percent(reading.nsr, 2)}
          context={t('cc.kpi.nsr.context', {
            positive: count(lang, reading.positive),
            negative: count(lang, reading.negative),
            sample: t(`cc.sample.${block.headline_sample}`),
          })}
          status={{ kind: 'warning', label: t('cc.status.base') }}
          info={metricInfo(front, lang, t, 'nsr', field)}
        />
        <KpiCard
          label={t('cc.kpi.negative')}
          value={percent(negativeHead.negative_share_sarcasm_adjusted, 2)}
          context={t('cc.t1.sarcasm', { n: count(lang, negativeHead.reclassified_from_sarcasm) })}
          status={{ kind: 'warning', label: t('cc.status.base') }}
          info={metricInfo(
            front,
            lang,
            t,
            'negative_share_sarcasm_adjusted',
            ccPath('metrics', 'negative_share_sarcasm_adjusted'),
          )}
        />
      </div>

      <section className="block">
        <h2>{t('cc.t1.mix')}</h2>
        <Stacked parts={parts} />
        <p className="context">
          {parts.map((part) => `${part.key} ${count(lang, part.value)}`).join(' · ')}
        </p>
        <OtherSamples block={block} field={field} t={t} read={(other) => percent(other.nsr, 2)} />
      </section>

      <div className="charts">
        <ChartCard
          t={t}
          title={t('cc.t1.sov.title')}
          subtitle={t('cc.t1.sov.subtitle', { total: count(lang, shareHead.total_mentions) })}
          provenance={`${FRONT_FILE} :: ${ccPath('metrics', 'sov')}`}
          info={[share.sample.reading]}
          table={{
            head: [t('cc.col.brand'), t('cc.col.share'), t('cc.col.mentions')],
            rows: shares(shareHead.share, shareHead.mentions).map((row) => [
              row.key,
              ratio(row.value),
              row.count,
            ]),
          }}
        >
          <Bars
            rows={shares(shareHead.share, shareHead.mentions)}
            colour={(key) => brandColour(shareHead.own_brands, key)}
            label={(key) => key}
          />
        </ChartCard>

        <ChartCard
          t={t}
          title={t('cc.t1.brands.title')}
          subtitle={t('cc.t1.brands.subtitle')}
          provenance={`${FRONT_FILE} :: ${ccPath('cuts', 'brand_by_sentiment')}`}
          info={[brands.sample.reading]}
          note={t('common.not_exported')}
          table={{
            head: [t('cc.col.brand'), t('cc.sentiment.positive'), t('cc.sentiment.neutral'), t('cc.sentiment.negative')],
            rows: Object.entries(brands.rows).map(([brand, cells]) => [
              brand,
              cells['positive'] ?? 0,
              cells['neutral'] ?? 0,
              cells['negative'] ?? 0,
            ]),
          }}
        >
          <div className="strips">
            {Object.entries(brands.rows).map(([brand, cells]) => (
              <div className="rank-row" key={brand}>
                <span className="rank-name">{brand}</span>
                <Stacked
                  parts={[
                    { key: t('cc.sentiment.positive'), value: cells['positive'] ?? 0, colour: 'var(--s3)' },
                    { key: t('cc.sentiment.neutral'), value: cells['neutral'] ?? 0, colour: 'var(--surface-2)' },
                    { key: t('cc.sentiment.negative'), value: cells['negative'] ?? 0, colour: 'var(--s8)' },
                  ]}
                />
                <span className="strip-values">
                  {count(lang, Object.values(cells).reduce((sum, value) => sum + value, 0))}
                </span>
              </div>
            ))}
          </div>
        </ChartCard>
      </div>

      <Sources fields={['metrics.nsr', 'metrics.sov', 'cuts.brand_by_sentiment']} t={t} />
    </>
  )
}

/* ────────────────────────────── T2 Аспекти ───────────────────────────── */

export function Aspects(): React.JSX.Element {
  const { front, lang, t } = useApp()
  const block = aspectShare(front)
  const field = ccPath('metrics', 'aspect_share')
  const reading = headline(block, field)
  const rows = shares(reading.share, reading.labels)

  return (
    <>
      <h2 className="question">{t('cc.t2.question')}</h2>
      <p className="population">
        {t('cc.population', { sample: t(`cc.sample.${block.headline_sample}`), rows: count(lang, reading.scored) })}
      </p>

      <div className="charts">
        <ChartCard
          t={t}
          wide
          title={t('cc.t2.title')}
          subtitle={t('cc.t2.subtitle', {
            labels: count(lang, reading.total_labels),
            silent: count(lang, reading.rows_with_no_aspect),
          })}
          provenance={`${FRONT_FILE} :: ${field}`}
          info={[block.sample.reading]}
          table={{
            head: [t('cc.col.aspect'), t('cc.col.share'), t('cc.col.labels')],
            rows: rows.map((row) => [t(`cc.aspect.${row.key}`), ratio(row.value), row.count]),
          }}
        >
          <Bars rows={rows} colour={() => 'var(--s1)'} label={(key) => t(`cc.aspect.${key}`)} />
        </ChartCard>
      </div>

      <section className="block">
        <h2>{t('cc.t2.negative.title')}</h2>
        <p className="note">
          {t('cc.t2.negative.body')} <code>{FRONT_FILE} :: {ccPath('cuts', 'aspect_by_sentiment')}</code>
        </p>
      </section>

      <Sources fields={['metrics.aspect_share']} t={t} />
    </>
  )
}

/* ───────────────────────────── T3 Сегменти ───────────────────────────── */

/** The three loudest of a cut, by count — the card shows what the segment talks about, and the
 *  full frequency table is the file's. */
function top(table: Record<string, number>, n = 3): [string, number][] {
  return Object.entries(table ?? {})
    .filter(([, value]) => value > 0)
    .sort((left, right) => right[1] - left[1] || left[0].localeCompare(right[0]))
    .slice(0, n)
}

export function Segments(): React.JSX.Element {
  const { front, lang, t } = useApp()
  const cuts = cut(front, 'comment_by_segment')
  const entries = Object.entries(cuts).sort(
    (left, right) => right[1].payable.rows - left[1].payable.rows || left[0].localeCompare(right[0]),
  )

  return (
    <>
      <h2 className="question">{t('cc.t3.question')}</h2>
      <p className="population">{t('cc.t3.population', { segments: count(lang, entries.length) })}</p>

      <div className="kpis">
        {entries.map(([segment, block]) => (
          <SegmentCard key={segment} segment={segment} block={block.payable} channels={block.channels_with_a_row} registry={block.registry_channels} />
        ))}
      </div>

      <Sources fields={['cuts.comment_by_segment']} t={t} />
    </>
  )
}

function SegmentCard({
  segment,
  block,
  channels,
  registry,
}: {
  segment: string
  block: CommentCut
  channels: string[]
  registry: number
}): React.JSX.Element {
  const { front, lang, t } = useApp()
  // the brands counted HERE are the anchor's matcher, and T1's share of voice is r1: the same
  // brand can read 1 on this card and 0 on that tab, so the file's own sentence about it travels
  // with the card rather than leaving a reader to find two numbers and no explanation
  const rules = cut(front, 'brand_attribution_in_the_comment_cuts')
  const aspects = top(block.intents.frequency)
  const brands = top(block.brand_attribution.mentions)
  return (
    <article className="card tile">
      <h3>
        {segment}
        <Info
          lines={[t('cc.t3.card.info'), rules.reading]}
          provenance={`${FRONT_FILE} :: ${ccPath('cuts', 'comment_by_segment', segment)}`}
          label={t('common.info')}
        />
      </h3>
      <p className="figure">{count(lang, block.rows)}</p>
      {/* a segment with no rows gets NO bar: an empty track is the same shape as an all-neutral
          one, and a shape that reads as a finding where there is no row is a claim (§10) */}
      {block.rows > 0 && (
        <Stacked
          parts={[
            { key: t('cc.sentiment.positive'), value: block.sentiment['positive'] ?? 0, colour: 'var(--s3)' },
            { key: t('cc.sentiment.neutral'), value: block.sentiment['neutral'] ?? 0, colour: 'var(--surface-2)' },
            { key: t('cc.sentiment.negative'), value: block.sentiment['negative'] ?? 0, colour: 'var(--s8)' },
          ]}
        />
      )}
      <p className="context">
        {t('cc.t3.aspects')}:{' '}
        {aspects.length === 0
          ? t('common.absent')
          : aspects.map(([key, value]) => `${t(`cc.aspect.${key}`)} ${value}`).join(' · ')}
      </p>
      <p className="context">
        {t('cc.t3.brands', { rules: rules.watchlist_rules })}:{' '}
        {brands.length === 0
          ? t('common.absent')
          : brands.map(([key, value]) => `${key} ${value}`).join(' · ')}
      </p>
      <p className="context">
        {t('cc.t3.channels', { with: count(lang, channels.length), registry: count(lang, registry) })}
      </p>
    </article>
  )
}

/* ──────────────────────────── T4 Конкуренти ──────────────────────────── */

export function Competitors(): React.JSX.Element {
  const { front, lang, t } = useApp()
  const share = sov(front)
  const field = ccPath('metrics', 'sov')
  const reading = headline(share, field)
  const brands = cut(front, 'brand_by_sentiment')
  const own = reading.own_brands[0] ?? ''
  const ownShare = reading.share[own] ?? 0
  const rows = shares(reading.share, reading.mentions)

  return (
    <>
      <h2 className="question">{t('cc.t4.question')}</h2>
      <p className="population">
        {t('cc.t4.population', {
          rows: count(lang, share.sample.rows ?? 0),
          of: count(lang, share.sample.of ?? 0),
          rules: reading.watchlist_rules,
        })}
      </p>

      <div className="scroll">
        <table>
          <caption>{t('cc.t4.table')}</caption>
          <thead>
            <tr>
              <th scope="col">{t('cc.col.brand')}</th>
              <th scope="col">{t('cc.col.share')}</th>
              <th scope="col">{t('cc.col.mentions')}</th>
              <th scope="col">{t('cc.col.delta')}</th>
              <th scope="col">{t('cc.col.sentiment')}</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((row) => {
              const cells = brands.rows[row.key] ?? {}
              const delta = row.value - ownShare
              return (
                <tr key={row.key}>
                  <th scope="row">
                    {row.key}
                    {reading.own_brands.includes(row.key) && ` · ${t('cc.t4.own')}`}
                  </th>
                  <td className="num">{ratio(row.value)}</td>
                  <td className="num">{count(lang, row.count)}</td>
                  <td className="num" style={{ color: delta === 0 ? 'var(--text-2)' : delta > 0 ? 'var(--s8)' : 'var(--s1)' }}>
                    {delta === 0 ? '—' : ratio(delta)}
                  </td>
                  <td className="num">
                    {Object.keys(cells).length === 0
                      ? t('common.absent')
                      : Object.entries(cells)
                          .map(([kind, value]) => `${t(`cc.sentiment.${kind}`)} ${value}`)
                          .join(' · ')}
                  </td>
                </tr>
              )
            })}
          </tbody>
        </table>
      </div>
      <p className="note">{t('cc.t4.note')}</p>

      <Sources fields={['metrics.sov', 'cuts.brand_by_sentiment']} t={t} />
    </>
  )
}

/* ───────────────────────── T5 Промо і ціни ───────────────────────────── */

export function PromoAndPrices(): React.JSX.Element {
  const { front, lang, t } = useApp()
  const depth = promoDepth(front)
  const pressure = promoPressure(front)
  const gap = notComputable(front, 'leaflet_depth_for_silpo_varus_marketopt')
  const chains = pressureByChain(front)
  const byBrand = shares(pressure.share, pressure.by_brand)

  return (
    <>
      <h2 className="question">{t('cc.t5.question')}</h2>
      <p className="population">
        {t('cc.t5.population', {
          rows: count(lang, pressure.position_rows),
          unresolved: count(lang, pressure.rows_with_no_resolved_brand),
        })}
      </p>

      <div className="note">
        <p>{gap.reason}</p>
        <p className="muted">
          {t('cc.t5.promo_tabs')} <a href="#/promo/positions">{t('nav.promo.positions')}</a> ·{' '}
          <a href="#/promo/trends">{t('nav.promo.trends')}</a>
        </p>
      </div>

      <div className="kpis">
        {Object.entries(depth.by_carrier).map(([carrier, row]) => (
          <KpiCard
            key={carrier}
            label={t(`cc.carrier.${carrier}`)}
            value={spreadOf(t, row.from_printed_badge)}
            context={t('cc.t5.depth.context', {
              n: count(lang, row.from_printed_badge.n),
              rows: count(lang, row.position_rows),
              disagree: count(lang, row.printed_disagrees_with_computed),
            })}
            status={{ kind: 'warning', label: t('cc.status.base') }}
            info={{
              lines: [depth.law],
              provenance: `${FRONT_FILE} :: ${ccPath('metrics', 'promo_depth', 'by_carrier', carrier)}`,
              label: t('common.info'),
            }}
          />
        ))}
      </div>

      <div className="charts">
        <ChartCard
          t={t}
          title={t('cc.t5.brands.title')}
          subtitle={t('cc.t5.brands.subtitle')}
          provenance={`${FRONT_FILE} :: ${ccPath('metrics', 'promo_pressure', 'share')}`}
          info={[pressure.sample.reading]}
          table={{
            head: [t('cc.col.brand'), t('cc.col.share'), t('cc.col.rows')],
            rows: byBrand.map((row) => [row.key, ratio(row.value), row.count]),
          }}
        >
          <Bars rows={byBrand} colour={() => 'var(--s1)'} label={(key) => key} />
        </ChartCard>

        <ChartCard
          t={t}
          title={t('cc.t5.chains.title')}
          subtitle={t('cc.t5.chains.subtitle')}
          provenance={`${FRONT_FILE} :: ${ccPath('metrics', 'promo_pressure', 'by_chain')}`}
          info={[pressure.sample.reading, t('cc.t5.chains.info')]}
          table={{
            head: [t('cc.col.chain'), t('cc.col.rows')],
            rows: chains.map((row) => [row.key, row.count]),
          }}
        >
          <Bars
            rows={chains}
            colour={(key) => seriesColour(key)}
            label={(key) => key}
            figure={(row) => <b>{count(lang, row.count)}</b>}
          />
        </ChartCard>
      </div>

      <Sources fields={['metrics.promo_depth', 'metrics.promo_pressure']} t={t} />
    </>
  )
}

/* ─────────────────── T6 Категорії · T7 Алерти (the stubs) ─────────────── */

export function Categories(): React.JSX.Element {
  const { front, lang, t } = useApp()
  const block = notComputable(front, 'category_layer')
  const observed = cut(front, 'positions_by_category')
  const rows = Object.entries(observed).sort(
    (left, right) => right[1] - left[1] || left[0].localeCompare(right[0]),
  )

  return (
    <>
      <h2 className="question">{t('cc.t6.question')}</h2>
      <p className="population">{t('cc.t6.population')}</p>
      <Absent block={block} t={t} />

      <section className="block">
        <h2>{t('cc.t6.taxonomy')}</h2>
        <div className="scroll">
          <table>
            <caption>{t('cc.t6.taxonomy')}</caption>
            <thead>
              <tr>
                <th scope="col">{t('cc.col.category')}</th>
                <th scope="col">{t('cc.col.rows')}</th>
              </tr>
            </thead>
            <tbody>
              {rows.map(([category, n]) => (
                <tr key={category}>
                  <th scope="row">{category}</th>
                  <td className="num">{count(lang, n)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <p className="note">{t('cc.t6.note')}</p>
      </section>

      <Sources fields={['not_computable.category_layer', 'cuts.positions_by_category']} t={t} />
    </>
  )
}

export function Alerts(): React.JSX.Element {
  const { front, t } = useApp()
  const block = notComputable(front, 'alert_baselines')

  return (
    <>
      <h2 className="question">{t('cc.t7.question')}</h2>
      <p className="population">{t('cc.t7.population')}</p>
      <Absent block={block} t={t} />

      <section className="block">
        <h2>{t('cc.t7.preview')}</h2>
        <ul className="rows">
          <li>{t('cc.t7.rule.deviation')}</li>
          <li>{t('cc.t7.rule.both')}</li>
          <li>{t('cc.t7.rule.delivery')}</li>
          <li>{t('cc.t7.rule.threshold')}</li>
        </ul>
        <p className="note">{t('cc.t7.no_numbers')}</p>
      </section>

      <Sources fields={['not_computable.alert_baselines']} t={t} />
    </>
  )
}

/* ─────────────────────────── T8 Методологія ──────────────────────────── */

export function Method(): React.JSX.Element {
  const { front, lang, t } = useApp()
  const block = centre(front)
  const window = ccWindow(front)
  const limits = Object.entries(block.not_computable)

  return (
    <>
      <h2 className="question">{t('cc.t8.question')}</h2>
      <p className="population">{window.reading}</p>

      <section className="block">
        <h2>{t('cc.t8.window')}</h2>
        <p className="context">
          {t('cc.window', { id: window.id, since: window.since.slice(0, 10), until: window.until.slice(0, 10) })} ·{' '}
          {window.rule}
        </p>
        <p className="context">
          {Object.entries(window.populations)
            .map(([name, rows]) => `${name} ${count(lang, rows)}`)
            .join(' · ')}
        </p>
      </section>

      <section className="block">
        <h2>{t('cc.t8.glossary')}</h2>
        <dl className="glossary">
          {(front.dictionary?.metrics ?? []).map((entry) => (
            <div key={entry.id}>
              <dt>{say(entry.name, lang)}</dt>
              <dd>
                {say(entry.definition, lang)}
                <p className="muted">
                  <code>{entry.formula}</code>
                </p>
                <p className="context">{say(entry.how_to_read, lang)}</p>
                <ul className="rows">
                  {sayEach(entry.pitfalls, lang).map((line) => (
                    <li key={line}>{line}</li>
                  ))}
                </ul>
              </dd>
            </div>
          ))}
        </dl>
      </section>

      <section className="block">
        <h2>{t('cc.t8.model')}</h2>
        <p className="context">
          {t('cc.t8.model.line', modelVerdict(front))}
        </p>
        <p className="muted">
          <code>{front.model.from}</code>
        </p>
      </section>

      <section className="block">
        <h2>{t('cc.t8.limits')}</h2>
        <ul className="rows">
          {limits.map(([key, limit]) => (
            <li key={key}>
              <b>{key}</b> — {limit.reason} <span className="muted">({limit.surface})</span>
            </li>
          ))}
        </ul>
      </section>

      <section className="block">
        <h2>{t('common.provenance')}</h2>
        <div className="scroll">
          <table>
            <caption>{t('cc.t8.manifest')}</caption>
            <thead>
              <tr>
                <th scope="col">{t('common.file')}</th>
                <th scope="col">{t('cc.col.bytes')}</th>
                <th scope="col">sha256</th>
              </tr>
            </thead>
            <tbody>
              {sources(front).map((row) => (
                <tr key={row.file}>
                  <th scope="row">{row.file}</th>
                  <td className="num">{count(lang, row.bytes)}</td>
                  <td>
                    <code>{row.sha256.slice(0, 12)}</code>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>

      <Sources fields={['window', 'not_computable', 'convergence']} t={t} />
    </>
  )
}

/* ───────────────────────────── the shared foot ───────────────────────── */

function Sources({ fields, t }: { fields: string[]; t: Translate }): React.JSX.Element {
  return (
    <p className="sources">
      {t('common.sources')}:{' '}
      {fields.map((field, index) => (
        <span key={field}>
          {index > 0 && ' · '}
          <code>
            {FRONT_FILE} :: {ccPath(field)}
          </code>
        </span>
      ))}
    </p>
  )
}

/* ────────────────────────────── the router ───────────────────────────── */

const TABS: Record<string, () => React.JSX.Element> = {
  t0: Overview,
  t1: Sentiment,
  t2: Aspects,
  t3: Segments,
  t4: Competitors,
  t5: PromoAndPrices,
  t6: Categories,
  t7: Alerts,
  t8: Method,
}

/**
 * Every `#/cc/*` path, and every path the shell matched nothing else for. A hand-typed `#/cc/t9`
 * and a `#/nonsense` both arrive here and neither names a tab: they get the sentence that says so,
 * never a blank screen and never T0's figures under another tab's name.
 */
export function CommandCentreTab({ path }: { path: string }): React.JSX.Element {
  const { t } = useApp()
  const id = path.startsWith(CC_PREFIX) ? path.slice(CC_PREFIX.length) : ''
  const Tab = CC_TABS.includes(id as (typeof CC_TABS)[number]) ? TABS[id] : undefined
  if (Tab === undefined) {
    return (
      <>
        <h2 className="question">{t('cc.unknown.title')}</h2>
        <p className="population">{t('cc.unknown.body', { path })}</p>
      </>
    )
  }
  return <Tab />
}

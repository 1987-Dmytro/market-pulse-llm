/**
 * Промо · Реакції — what buyers say under promo posts (DESIGN-ship-1 §13).
 *
 * One block answers this tab: `front_data.json :: reactions_v2`, counted by the producer over
 * `results/promo_signals/`. The page order is §13's — the question, the coverage in one muted
 * sentence, three answer exhibits titled BY THE EXPORT, the loudest threads with their own promo
 * post, the product's own voice, and only then the full feed. The process counters (queue, not
 * collected, the tick's recorded rows) sit in the footer: they are how the reading was made, not
 * what it found.
 *
 * The tab counts nothing. Every figure — a matrix cell, a share of a stack, a month's complaint
 * share, a card's signal count — is a field of that block, and the three exhibit titles are
 * sentences code rules wrote in both languages. A share divided here would be a second reading of
 * the same rows ([[a_sentence_that_orders_the_numbers_beside_it]]).
 */

import {
  CartesianGrid,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'

import { useApp } from '../app-state.ts'
import { ChartCard } from '../components/ChartCard.tsx'
import { type Column, DataTable } from '../components/DataTable.tsx'
import { Info } from '../components/Info.tsx'
import { S2Table } from '../components/S2Table.tsx'
import { REACTIONS_FIELD, reactionsV2, s2, saidText } from '../data/front.ts'
import { FRONT_FILE, PROMO_FILE } from '../data/load.ts'
import { tableRows, telegramLink } from '../data/promo.ts'
import { count, percent } from '../format.ts'
import type { Lang, Translate } from '../i18n/t.ts'
import { paramOf, setParam, useRoute } from '../router.ts'
import type { ReactionsBlock, SignalRow, ThreadCard } from '../types.ts'

const TABLE_ROWS_FIELD = 'screen.table_rows'
const COVERAGE_FIELD = `${REACTIONS_FIELD}.coverage`

/** The tooltip wears the card's own surface, so a mark's value is read in the page's theme. */
const TOOLTIP_STYLE = {
  background: 'var(--surface-1)',
  border: '1px solid var(--border)',
  borderRadius: 4,
  color: 'var(--text-1)',
  fontSize: 12,
}
const TICK = { fill: 'var(--text-2)', fontSize: 11 }

/**
 * A colour per signal TYPE, never per position in a list.
 *
 * The law `data/chains.ts` states for chains: the order of the types on a stack follows their
 * counts, so an index-based hue would repaint «жалоба» the moment a quieter month changed the
 * ranking. A type the reading law grows later takes the «інші» grey and keeps its name everywhere.
 */
const TYPE_COLOUR: Record<string, string> = {
  жалоба: 'var(--s8)',
  похвала: 'var(--s3)',
  спрос: 'var(--s1)',
  цена: 'var(--s4)',
  привычка: 'var(--s6)',
}

function typeColour(type: string): string {
  return TYPE_COLOUR[type] ?? 'var(--text-3)'
}

/**
 * A feed row and its identity. The comment's address is NOT a row identity: one comment can carry
 * several signal rows (`@VARUS_channel/2978` carries five, one per signal the reader found), so the
 * key adds the row's own position in the block's feed — the export's order, not a new figure.
 */
interface FeedEntry {
  key: string
  row: ReactionsBlock['feed'][number]
}

function distinctOf(entries: FeedEntry[], of: (row: FeedEntry['row']) => string): string[] {
  return [...new Set(entries.map((entry) => of(entry.row)))].sort((left, right) =>
    left.localeCompare(right, 'uk'),
  )
}

export function ReactionsTab(): React.JSX.Element {
  const { promo, front, lang, t } = useApp()
  const route = useRoute()

  const block = reactionsV2(front)
  const reach = block.coverage
  const recorded = tableRows(promo)
  const evidenceRows = recorded['evidence']
  const signalRows = recorded['signal']

  const entries: FeedEntry[] = block.feed.map((row, index) => ({
    key: `${row.channel}/${row.msg_id}#${index}`,
    row,
  }))

  const signal = paramOf(route, 'signal')
  const about = paramOf(route, 'about')
  const channel = paramOf(route, 'channel')
  const rows = entries.filter(
    (entry) =>
      (signal === undefined || entry.row.type === signal) &&
      (about === undefined || entry.row.subject_type === about) &&
      (channel === undefined || entry.row.channel === channel),
  )

  const columns: Column<FeedEntry>[] = [
    {
      key: 'signal',
      label: t('reactions.col.signal'),
      // the export's own vocabulary (жалоба · похвала · цена …): data, never a translation key
      render: (entry) => (
        <span className="badge" style={{ borderColor: typeColour(entry.row.type) }}>
          {entry.row.type}
        </span>
      ),
    },
    {
      key: 'about',
      label: t('reactions.col.about'),
      render: (entry) => (
        <>
          <span className="badge">{entry.row.subject_type}</span>{' '}
          {entry.row.subject ?? <span className="muted">{t('common.absent')}</span>}
        </>
      ),
    },
    { key: 'quote', label: t('reactions.col.quote'), render: (entry) => <Quote row={entry.row} /> },
    { key: 'channel', label: t('reactions.col.channel'), render: (entry) => entry.row.channel },
    {
      key: 'thread',
      label: t('reactions.col.thread'),
      num: true,
      render: (entry) => entry.row.thread_root,
    },
  ]

  /**
   * §13 (5)'s chips: one per value, each wearing the EXPORT's own count — never a count made here.
   * Pressing the chip that is already on clears the filter, so the group needs no «усі» of its own
   * beyond the first chip; the state lives in the hash, so a filtered view is a link.
   */
  const chips = (
    name: string,
    label: string,
    values: string[],
    of: Record<string, number>,
    swatch: (value: string) => string | undefined,
  ) => {
    const chosen = paramOf(route, name)
    return (
      <div className="chips" role="group" aria-label={label}>
        <button
          type="button"
          aria-pressed={chosen === undefined}
          onClick={() => setParam(route, name, undefined)}
        >
          {label}: {t('common.all')}
        </button>
        {values.map((value) => {
          const colour = swatch(value)
          return (
            <button
              key={value}
              type="button"
              aria-pressed={chosen === value}
              onClick={() => setParam(route, name, chosen === value ? undefined : value)}
            >
              {colour !== undefined && <i className="swatch" style={{ background: colour }} />}
              {value} <span className="muted">{count(lang, of[value] ?? 0)}</span>
            </button>
          )
        })}
      </div>
    )
  }

  const select = (name: string, label: string, values: string[], of: Record<string, number>) => (
    <label>
      {label}
      <select
        value={paramOf(route, name) ?? ''}
        onChange={(event) => setParam(route, name, event.target.value)}
      >
        <option value="">{t('common.all')}</option>
        {values.map((value) => (
          <option key={value} value={value}>
            {value} · {count(lang, of[value] ?? 0)}
          </option>
        ))}
      </select>
    </label>
  )

  const perChannel = Object.fromEntries(
    block.mix_by_channel.channels.map((one) => [one.channel, one.signals]),
  )
  const s2Rows = s2(front)

  return (
    <>
      <h2 className="question">{t('reactions.question')}</h2>
      {/* a <div>, not a <p>: the ⓘ popover renders its own <p>s, which may not nest inside one */}
      <div className="population">
        {t('reactions.coverage', {
          read: count(lang, reach.read),
          product: count(lang, reach.product_population),
          channels: count(lang, reach.channels),
        })}
        <Info
          lines={[block.reading, reach.from]}
          provenance={`${FRONT_FILE} :: ${COVERAGE_FIELD}`}
          label={t('common.info')}
        />
      </div>

      {block.rows === 0 ? (
        // nothing was bought, so there is nothing to draw: the exhibits would be five empty frames,
        // and an empty frame reads as «the market said nothing» (DESIGN §10). The queue beside the
        // sentence says what is waiting instead.
        <p className="note">
          {t('reactions.empty')} — {t('loop.queue.title')}: {count(lang, reach.queue)}
        </p>
      ) : (
        <>
          <div className="charts">
            <Complaints block={block} lang={lang} t={t} />
            <Mix block={block} lang={lang} t={t} />
            <Monthly block={block} lang={lang} t={t} />
          </div>

          <Matrix block={block} lang={lang} t={t} />

          <section className="block">
            <h2>{t('reactions.threads.title')}</h2>
            {block.threads.title !== null && (
              <p className="note">{saidText(block.threads.title, lang)}</p>
            )}
            <div className="cards">
              {block.threads.cards.map((card) => (
                <ThreadPanel
                  key={`${card.channel}/${card.thread_root}`}
                  card={card}
                  lang={lang}
                  t={t}
                />
              ))}
            </div>
          </section>

          <section className="block">
            <h2>{t('reactions.voice.title')}</h2>
            <p className="note">{saidText(block.sku_voice.title, lang)}</p>
            {block.sku_voice.groups.map((group) => (
              <div className="voice" key={group.type}>
                <h3>
                  {saidText(group.title, lang)} <span className="muted">{count(lang, group.n)}</span>
                </h3>
                <ul className="rows">
                  {group.rows.map((row, index) => (
                    <li key={`${row.channel}/${row.thread_root}#${index}`}>
                      <b>{row.subject ?? t('common.absent')}</b> <Quote row={row} />{' '}
                      <span className="muted">{row.channel}</span>{' '}
                      <ThreadLink channel={row.channel} root={row.thread_root} />
                    </li>
                  ))}
                </ul>
              </div>
            ))}
          </section>

          <section className="block">
            <h2>{t('reactions.feed.title')}</h2>
            {chips(
              'signal',
              t('reactions.filter.signal'),
              distinctOf(entries, (row) => row.type),
              block.matrix.by_type,
              typeColour,
            )}
            {chips(
              'about',
              t('reactions.filter.subject'),
              distinctOf(entries, (row) => row.subject_type),
              block.matrix.by_subject_type,
              () => undefined,
            )}
            <div className="filters">
              {select(
                'channel',
                t('reactions.filter.channel'),
                distinctOf(entries, (row) => row.channel),
                perChannel,
              )}
            </div>

            <DataTable
              t={t}
              caption={t('reactions.question')}
              columns={columns}
              rows={rows}
              total={entries.length}
              keyOf={(entry) => entry.key}
              expand={(entry) => <Evidence row={entry.row} />}
            />
          </section>
        </>
      )}

      <section className="block">
        <h2>{t('quality.s2.title')}</h2>
        {s2Rows.length === 0 ? (
          <p className="note">{t('common.not_exported')}</p>
        ) : (
          <S2Table t={t} rows={s2Rows} boundary={front.s2_boundary} />
        )}
      </section>

      {/* §13 (1): the process numbers live here, under the answers, never above them */}
      <div className="note muted">
        {t('reactions.queue', {
          read: count(lang, reach.read),
          queue: count(lang, reach.queue),
          not_collected: count(lang, reach.not_collected),
        })}{' '}
        ·{' '}
        {t('reactions.population', {
          product: count(lang, reach.product_population),
          population: count(lang, reach.population),
        })}{' '}
        · {t('positions.col.evidence')}:{' '}
        {evidenceRows === undefined ? t('common.not_exported') : count(lang, evidenceRows)} ·{' '}
        {t('reactions.col.signal')}:{' '}
        {signalRows === undefined ? t('common.not_exported') : count(lang, signalRows)}
        <Info
          lines={[reach.from, t('loop.tick.tables')]}
          provenance={`${FRONT_FILE} :: ${COVERAGE_FIELD} · ${PROMO_FILE} :: ${TABLE_ROWS_FIELD}`}
          label={t('common.info')}
        />
      </div>

      <p className="sources">
        {t('common.sources')}:{' '}
        <code>
          {FRONT_FILE} :: {REACTIONS_FIELD}
        </code>{' '}
        ·{' '}
        <code>
          {PROMO_FILE} :: {TABLE_ROWS_FIELD}
        </code>{' '}
        · <code>{FRONT_FILE} :: s2_readings</code>
      </p>
    </>
  )
}

/** §13 (2) exhibit 1: the service-vs-product pair, titled by the rule that compared the two. */
function Complaints({
  block,
  lang,
  t,
}: {
  block: ReactionsBlock
  lang: Lang
  t: Translate
}): React.JSX.Element {
  const pair = block.complaints
  const ceiling = Math.max(...pair.bars.map((bar) => bar.n), 0)
  const word = (key: string): string => {
    const said = block.matrix.subject_words[key]
    return said === undefined ? key : saidText(said, lang)
  }
  return (
    <ChartCard
      t={t}
      title={saidText(pair.title, lang)}
      subtitle={`${pair.type} · ${t('reactions.complaints.subtitle')}`}
      provenance={`${FRONT_FILE} :: ${REACTIONS_FIELD}.complaints`}
      info={[block.reading]}
      note={t('reactions.complaints.other', { other: count(lang, pair.other) })}
      table={{
        head: [t('reactions.col.about'), t('common.value')],
        rows: pair.bars.map((bar) => [word(bar.subject_type), bar.n]),
      }}
    >
      <div className="strips">
        {pair.bars.map((bar) => (
          <div className="rank-row" key={bar.subject_type}>
            <span className="rank-name">{word(bar.subject_type)}</span>
            <span className="track">
              <span
                className="bar"
                // bar geometry against the taller of the two — the one arithmetic §3 leaves the app
                style={{
                  width: ceiling === 0 ? '0%' : `${(bar.n / ceiling) * 100}%`,
                  background: typeColour(pair.type),
                }}
              />
            </span>
            <span className="rank-value">{count(lang, bar.n)}</span>
          </div>
        ))}
      </div>
    </ChartCard>
  )
}

/** §13 (2) exhibit 2: the signal mix per channel, one hundred-percent stack per row. */
function Mix({
  block,
  lang,
  t,
}: {
  block: ReactionsBlock
  lang: Lang
  t: Translate
}): React.JSX.Element {
  const mix = block.mix_by_channel
  return (
    <ChartCard
      t={t}
      title={mix.title === null ? t('reactions.mix.col.channel') : saidText(mix.title, lang)}
      subtitle={t('reactions.mix.subtitle')}
      provenance={`${FRONT_FILE} :: ${REACTIONS_FIELD}.mix_by_channel`}
      info={[block.reading]}
      legend={block.matrix.types.map((type) => ({ colour: typeColour(type), label: type }))}
      table={{
        head: [t('reactions.mix.col.channel'), ...block.matrix.types],
        rows: mix.channels.map((one) => [
          one.channel,
          ...block.matrix.types.map((type) => one.parts.find((part) => part.type === type)?.n ?? 0),
        ]),
      }}
    >
      <div className="strips">
        {mix.channels.map((one) => (
          <div className="rank-row" key={one.channel}>
            <span className="rank-name">{one.channel}</span>
            <span className="stack">
              {one.parts.map((part) => (
                <span
                  key={part.type}
                  className="slice"
                  // the share is the export's own field; turning it into a width is geometry
                  style={{
                    width: `${(part.share * 100).toFixed(2)}%`,
                    background: typeColour(part.type),
                  }}
                  title={`${part.type}: ${count(lang, part.n)} · ${percent(part.share)}`}
                />
              ))}
            </span>
            <span className="rank-value">{count(lang, one.signals)}</span>
          </div>
        ))}
      </div>
    </ChartCard>
  )
}

/** §13 (2) exhibit 3: the complaint share by month, with the month's own size greyed beside it. */
function Monthly({
  block,
  lang,
  t,
}: {
  block: ReactionsBlock
  lang: Lang
  t: Translate
}): React.JSX.Element {
  const series = block.monthly
  const shareLabel = t('reactions.monthly.share')
  return (
    <ChartCard
      t={t}
      wide
      title={series.title === null ? shareLabel : saidText(series.title, lang)}
      subtitle={t('reactions.monthly.subtitle')}
      provenance={`${FRONT_FILE} :: ${REACTIONS_FIELD}.monthly`}
      info={[
        block.reading,
        t('reactions.monthly.undated', { n: count(lang, series.without_a_date) }),
      ]}
      legend={[
        { colour: typeColour(series.type), label: shareLabel },
        { colour: 'var(--text-3)', label: t('reactions.monthly.signals') },
      ]}
      table={{
        head: [t('reactions.monthly.col.month'), shareLabel, t('reactions.monthly.signals')],
        rows: series.months.map((one) => [one.month, percent(one.share), one.signals]),
      }}
    >
      <ResponsiveContainer width="100%" height={280}>
        <LineChart data={series.months} margin={{ top: 8, right: 16, bottom: 0, left: 0 }}>
          <CartesianGrid stroke="var(--border)" vertical={false} />
          <XAxis dataKey="month" tick={TICK} stroke="var(--text-3)" />
          <YAxis
            yAxisId="share"
            width={64}
            tickFormatter={(value: number) => percent(value, 0)}
            tick={TICK}
            stroke="var(--text-3)"
          />
          {/* the context axis, greyed: a full complaint share over two signals and over forty are
              different findings, and a share drawn alone cannot say which one a month is */}
          <YAxis
            yAxisId="signals"
            orientation="right"
            width={48}
            tickFormatter={(value: number) => count(lang, value)}
            tick={TICK}
            stroke="var(--text-3)"
          />
          <Tooltip
            contentStyle={TOOLTIP_STYLE}
            formatter={(value, name) =>
              typeof value !== 'number'
                ? String(value)
                : name === shareLabel
                  ? percent(value)
                  : count(lang, value)
            }
          />
          <Line
            yAxisId="signals"
            name={t('reactions.monthly.signals')}
            type="linear"
            dataKey="signals"
            stroke="var(--text-3)"
            strokeDasharray="4 3"
            strokeWidth={1}
            dot={false}
            isAnimationActive={false}
          />
          <Line
            yAxisId="share"
            name={shareLabel}
            type="linear"
            dataKey="share"
            stroke={typeColour(series.type)}
            strokeWidth={2}
            dot={{ r: 3 }}
            isAnimationActive={false}
          />
        </LineChart>
      </ResponsiveContainer>
    </ChartCard>
  )
}

/** The matrix itself, as a table: PHASE §2 asks for the type × subject counts, and §10's default
 *  for a form the brief does not draw is a table with its provenance visible. */
function Matrix({
  block,
  lang,
  t,
}: {
  block: ReactionsBlock
  lang: Lang
  t: Translate
}): React.JSX.Element {
  const cell = (type: string, subject: string): number =>
    block.matrix.cells.find((one) => one.type === type && one.subject_type === subject)?.n ?? 0
  const word = (key: string): string => {
    const said = block.matrix.subject_words[key]
    return said === undefined ? key : saidText(said, lang)
  }
  return (
    <section className="block">
      <h2>{t('reactions.matrix.title')}</h2>
      <div className="scroll">
        <table>
          <caption>{t('reactions.matrix.title')}</caption>
          <thead>
            <tr>
              <th scope="col">{t('reactions.col.signal')}</th>
              {block.matrix.subject_types.map((subject) => (
                <th scope="col" className="num" key={subject}>
                  {word(subject)}
                </th>
              ))}
              <th scope="col" className="num">
                {t('reactions.matrix.total')}
              </th>
            </tr>
          </thead>
          <tbody>
            {block.matrix.types.map((type) => (
              <tr key={type}>
                <th scope="row">
                  <span className="badge" style={{ borderColor: typeColour(type) }}>
                    {type}
                  </span>
                </th>
                {block.matrix.subject_types.map((subject) => (
                  <td className="num" key={subject}>
                    {count(lang, cell(type, subject))}
                  </td>
                ))}
                <td className="num">
                  <b>{count(lang, block.matrix.by_type[type] ?? 0)}</b>
                </td>
              </tr>
            ))}
            <tr>
              <th scope="row">{t('reactions.matrix.total')}</th>
              {block.matrix.subject_types.map((subject) => (
                <td className="num" key={subject}>
                  <b>{count(lang, block.matrix.by_subject_type[subject] ?? 0)}</b>
                </td>
              ))}
              <td className="num">
                <b>{count(lang, block.rows)}</b>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
      <p className="sources">
        {t('common.sources')}:{' '}
        <code>
          {FRONT_FILE} :: {REACTIONS_FIELD}.matrix
        </code>
      </p>
    </section>
  )
}

/** §13 (3): the root promo post, and under it the signals its thread drew. */
function ThreadPanel({
  card,
  lang,
  t,
}: {
  card: ThreadCard
  lang: Lang
  t: Translate
}): React.JSX.Element {
  const link = telegramLink(card.channel, Number(card.thread_root))
  return (
    <article className="card thread">
      <div className="chain-head">
        <b>{card.channel}</b>
        <span className="muted">{card.date ?? t('common.absent')}</span>
        <span className="badge">
          {t('reactions.threads.signals', { n: count(lang, card.signals) })}
        </span>
        {link !== null && (
          <a href={link} target="_blank" rel="noreferrer noopener">
            {t('positions.link')}
          </a>
        )}
      </div>
      {card.text === null ? (
        <p className="muted">{t('reactions.threads.no_text')}</p>
      ) : (
        <p className="clamp">{card.text}</p>
      )}
      <ul className="rows">
        {card.rows.map((row, index) => (
          <li key={`${row.type}#${index}`}>
            <span className="badge" style={{ borderColor: typeColour(row.type) }}>
              {row.type}
            </span>{' '}
            <span className="badge">{row.subject ?? row.subject_type}</span> <Quote row={row} />
          </li>
        ))}
      </ul>
    </article>
  )
}

/** A quote, and the badge §13 asks for on a row the reader was not sure of — never a hidden row.
 *  Narrower than `SignalRow` on purpose: the voice rows carry their type in their group's heading. */
function Quote({ row }: { row: Pick<SignalRow, 'quote' | 'confidence'> }): React.JSX.Element {
  const { t } = useApp()
  return (
    <span className="quote">
      {row.quote ?? t('common.absent')}
      {row.confidence !== null && row.confidence < 1 && (
        <>
          {' '}
          <span className="badge">{t('reactions.low_confidence')}</span>
        </>
      )}
    </span>
  )
}

function ThreadLink({ channel, root }: { channel: string; root: string }): React.JSX.Element {
  const { t } = useApp()
  const link = telegramLink(channel, Number(root))
  return link === null ? (
    <span className="muted">{t('positions.link.private')}</span>
  ) : (
    <a href={link} target="_blank" rel="noreferrer noopener">
      {t('positions.link')}
    </a>
  )
}

function Evidence({ row }: { row: ReactionsBlock['feed'][number] }): React.JSX.Element {
  const { t } = useApp()
  const link = telegramLink(row.channel, row.msg_id)
  return (
    <p className="pair">
      <span>
        <code>
          {row.channel}/{row.msg_id}
        </code>
      </span>
      <span>
        {t('reactions.col.thread')}: <code>{row.thread_root}</code>
      </span>
      {link === null ? (
        <span className="muted">{t('positions.link.private')}</span>
      ) : (
        <a href={link} target="_blank" rel="noreferrer noopener">
          {t('positions.link')}
        </a>
      )}
    </p>
  )
}

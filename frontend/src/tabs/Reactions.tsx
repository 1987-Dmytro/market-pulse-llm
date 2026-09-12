/**
 * Промо · Реакції — how buyers react under promo posts (DESIGN-ship-1 §7).
 *
 * `promo_screen_data.json :: screen.feed` is the evidence the paid reading bought, `screen.threads`
 * is the queue it was drawn from and `screen.table_rows` is what the tick recorded; the S2 block is
 * `front_data.json :: s2_readings`, rendered by the one component that spells it.
 *
 * The tab counts, filters and links, and re-derives nothing: the share of the queue that was read,
 * a per-signal percentage of the feed and a sentiment balance over the quotes are all figures no
 * export carries, so they are not on this page. The bars are the graders' own — S2Table compares
 * nothing here either — and `screen.threads.from` is the export's own sentence about how the queue
 * was counted, quoted in the ⓘ rather than paraphrased.
 */

import { useApp } from '../app-state.ts'
import { type Column, DataTable } from '../components/DataTable.tsx'
import { Info } from '../components/Info.tsx'
import { KpiCard } from '../components/KpiCard.tsx'
import { S2Table } from '../components/S2Table.tsx'
import { s2 } from '../data/front.ts'
import { FRONT_FILE, PROMO_FILE } from '../data/load.ts'
import { feed, tableRows, telegramLink, threads } from '../data/promo.ts'
import { count } from '../format.ts'
import { paramOf, setParam, useRoute } from '../router.ts'
import type { FeedRow } from '../types.ts'

const THREADS_FIELD = 'screen.threads'
const FEED_FIELD = 'screen.feed'
const TABLE_ROWS_FIELD = 'screen.table_rows'

/**
 * A feed row and its identity. The comment's address is NOT a row identity: one comment can carry
 * several signal rows (`@VARUS_channel/2978` carries five, one per signal the reader found), so the
 * key adds the row's own position in `screen.feed` — the export's order, not a new figure.
 */
interface FeedEntry {
  key: string
  row: FeedRow
}

function distinctOf(entries: FeedEntry[], of: (row: FeedRow) => string): string[] {
  return [...new Set(entries.map((entry) => of(entry.row)))].sort((left, right) =>
    left.localeCompare(right, 'uk'),
  )
}

export function ReactionsTab(): React.JSX.Element {
  const { promo, front, lang, t } = useApp()
  const route = useRoute()

  const queue = threads(promo)
  const recorded = tableRows(promo)
  const evidenceRows = recorded['evidence']
  const signalRows = recorded['signal']

  const entries: FeedEntry[] = feed(promo).map((row, index) => ({
    key: `${row.channel}/${row.msg_id}#${index}`,
    row,
  }))

  const signal = paramOf(route, 'signal')
  const channel = paramOf(route, 'channel')
  const rows = entries.filter(
    (entry) =>
      (signal === undefined || entry.row.type === signal) &&
      (channel === undefined || entry.row.channel === channel),
  )

  const columns: Column<FeedEntry>[] = [
    {
      key: 'signal',
      label: t('reactions.col.signal'),
      // the export's own vocabulary (жалоба · похвала · цена …): data, never a translation key
      render: (entry) => <span className="badge">{entry.row.type}</span>,
    },
    {
      key: 'quote',
      label: t('reactions.col.quote'),
      render: (entry) => <span className="quote">{entry.row.quote}</span>,
    },
    { key: 'channel', label: t('reactions.col.channel'), render: (entry) => entry.row.channel },
    {
      key: 'thread',
      label: t('reactions.col.thread'),
      num: true,
      render: (entry) => entry.row.thread_root,
    },
  ]

  const select = (name: string, label: string, values: string[]) => (
    <label>
      {label}
      <select
        value={paramOf(route, name) ?? ''}
        onChange={(event) => setParam(route, name, event.target.value)}
      >
        <option value="">{t('common.all')}</option>
        {values.map((value) => (
          <option key={value} value={value}>
            {value}
          </option>
        ))}
      </select>
    </label>
  )

  const s2Rows = s2(front)

  return (
    <>
      <h2 className="question">{t('reactions.question')}</h2>
      {/* a <div>, not a <p>: the ⓘ popover renders its own <p>s, which may not nest inside one */}
      <div className="population">
        {t('reactions.queue', {
          read: count(lang, queue.read),
          queue: count(lang, queue.queue),
          not_collected: count(lang, queue.not_collected),
        })}{' '}
        ·{' '}
        {t('reactions.population', {
          product: count(lang, queue.product_population),
          population: count(lang, queue.population),
        })}
        <Info
          lines={[queue.from]}
          provenance={`${PROMO_FILE} :: ${THREADS_FIELD}`}
          label={t('common.info')}
        />
      </div>

      <div className="kpis">
        <KpiCard
          label={t('header.threads')}
          value={count(lang, queue.read)}
          info={{
            lines: [queue.from],
            provenance: `${PROMO_FILE} :: ${THREADS_FIELD}`,
            label: t('common.info'),
          }}
        />
        <KpiCard label={t('loop.queue.title')} value={count(lang, queue.queue)} />
        <KpiCard label={t('common.not_collected')} value={count(lang, queue.not_collected)} />
        <KpiCard
          label={t('positions.col.evidence')}
          value={evidenceRows === undefined ? t('common.not_exported') : count(lang, evidenceRows)}
          context={`${t('reactions.col.signal')}: ${
            signalRows === undefined ? t('common.not_exported') : count(lang, signalRows)
          }`}
          info={{
            lines: [t('loop.tick.tables')],
            provenance: `${PROMO_FILE} :: ${TABLE_ROWS_FIELD}`,
            label: t('common.info'),
          }}
        />
      </div>

      {entries.length === 0 ? (
        // the feed is empty because nothing was bought, not because the market said nothing: the
        // queue count beside the sentence says what is waiting. A filter that matches no row is a
        // different state and falls through to the table's own «показано 0 з N».
        <p className="note">
          {t('reactions.empty')} — {t('loop.queue.title')}: {count(lang, queue.queue)}
        </p>
      ) : (
        <>
          <div className="filters">
            {select(
              'signal',
              t('reactions.filter.signal'),
              distinctOf(entries, (row) => row.type),
            )}
            {select(
              'channel',
              t('reactions.filter.channel'),
              distinctOf(entries, (row) => row.channel),
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

      <p className="sources">
        {t('common.sources')}:{' '}
        <code>
          {PROMO_FILE} :: {FEED_FIELD}, {THREADS_FIELD}, {TABLE_ROWS_FIELD}
        </code>{' '}
        · <code>{FRONT_FILE} :: s2_readings</code>
      </p>
    </>
  )
}

function Evidence({ row }: { row: FeedRow }): React.JSX.Element {
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

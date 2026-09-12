/**
 * Промо · Позиції — what the chains promote and at what price (DESIGN-ship-1 §7, §11).
 *
 * `promo_screen_data.json :: screen.positions`, all windows, filtered and sorted here and computed
 * nowhere: the depth a row shows is the PRINTED badge's own reading, and the extracted old price
 * and the arithmetic depth are not on this page at all — beside a row's promo price they give the
 * old price back to the kopiyka (SPEC 3.21 (4), 3.18 (1), 3.22 (1)). §11's mockup asks for the old
 * price struck through beside the promo one; no file carries it, and the two numbers beside each
 * other are the pair that law forbids, so the sentence under the table says so instead.
 *
 * The photos are §11's: the chain chips over «Свіжі листівки» — one card per chain, its newest
 * flyer set — and a 40 px page thumbnail on every row that has one. Both open the same lightbox.
 * The row's ⓘ still opens its evidence: channel, message id and the t.me link. A private invite
 * handle has no public message address, so that row says so instead of linking somewhere else.
 */

import { useState } from 'react'

import { useApp } from '../app-state.ts'
import { CountUp } from '../components/CountUp.tsx'
import { DataTable } from '../components/DataTable.tsx'
import type { Column } from '../components/DataTable.tsx'
import { KpiCard } from '../components/KpiCard.tsx'
import { Lightbox } from '../components/Lightbox.tsx'
import { chainName, orderChains, seriesColour } from '../data/chains.ts'
import { FRONT_FILE, PROMO_FILE } from '../data/load.ts'
import { MEDIA_FIELD, flyers, mediaOf, pageOf, pageUrl } from '../data/media.ts'
import {
  POSITIONS_FIELD,
  type SortKey,
  asDayMonth,
  distinct,
  filterPositions,
  positionKey,
  positions,
  productOf,
  sortPositions,
  telegramLink,
  volumeOf,
  withPrintedBadge,
  withPromoPrice,
} from '../data/promo.ts'
import { count, price, printed } from '../format.ts'
import { paramOf, setParam, useRoute } from '../router.ts'
import type { Position } from '../types.ts'

const SORTS: Record<string, SortKey> = {
  brand: 'brand',
  product: 'product',
  price: 'price',
  printed: 'printed',
  chain: 'chain',
  carrier: 'carrier',
}

/** What the lightbox is showing: a flyer set from a card, or the one page behind a row. */
interface Opened {
  title: string
  pages: string[]
  start: number
}

export function PositionsTab(): React.JSX.Element {
  const { promo, front, chains, lang, t } = useApp()
  const route = useRoute()
  const [sortKey, setSortKey] = useState<SortKey>('chain')
  const [direction, setDirection] = useState<'asc' | 'desc'>('asc')
  const [opened, setOpened] = useState<Opened | null>(null)

  const media = mediaOf(front)
  const all = positions(promo)
  const chosenChain = paramOf(route, 'chain')
  const filters = {
    ...(chosenChain === undefined ? {} : { chain: chosenChain }),
    ...(paramOf(route, 'brand') === undefined ? {} : { brand: paramOf(route, 'brand') as string }),
    ...(paramOf(route, 'carrier') === undefined
      ? {}
      : { carrier: paramOf(route, 'carrier') as string }),
    ...(paramOf(route, 'category') === undefined
      ? {}
      : { category: paramOf(route, 'category') as string }),
    ...(paramOf(route, 'q') === undefined ? {} : { text: paramOf(route, 'q') as string }),
  }
  const rows = sortPositions(filterPositions(all, filters), sortKey, direction)

  const onSort = (key: string): void => {
    const next = SORTS[key]
    if (next === undefined) return
    if (next === sortKey) setDirection(direction === 'asc' ? 'desc' : 'asc')
    else {
      setSortKey(next)
      setDirection('asc')
    }
  }

  const openPage = (row: Position, name: string): void =>
    setOpened({
      title: `${chainName(chains, row.chain.id)} · ${row.evidence.channel}/${String(row.evidence.msg_id)}`,
      pages: [name],
      start: 0,
    })

  const columns: Column<Position>[] = [
    {
      key: 'page',
      label: t('positions.col.page'),
      render: (row) => {
        const name = pageOf(media, row)
        if (name === null) return <span className="muted tiny">{t('media.no_page')}</span>
        return <Thumb name={name} src={pageUrl(media, name)} onOpen={() => openPage(row, name)} />
      },
    },
    {
      key: 'brand',
      label: t('positions.col.brand'),
      sortable: true,
      render: (row) => (
        <>
          {row.brand.display}
          {row.brand.own === true && (
            <span className="badge" title={t('positions.own_brand')}>
              ●
            </span>
          )}
        </>
      ),
    },
    { key: 'product', label: t('positions.col.product'), sortable: true, render: (row) => productOf(row.item) },
    { key: 'category', label: t('positions.col.category'), render: (row) => row.item.category },
    {
      key: 'volume',
      label: t('positions.col.volume'),
      render: (row) => volumeOf(row.item) ?? <span className="muted">{t('common.absent')}</span>,
    },
    {
      key: 'price',
      label: t('positions.col.price'),
      num: true,
      sortable: true,
      render: (row) =>
        row.promo_price === undefined ? (
          <span className="muted">{t('common.absent')}</span>
        ) : (
          <b className="price">{price(lang, row.promo_price)}</b>
        ),
    },
    {
      key: 'printed',
      label: t('positions.col.printed'),
      num: true,
      sortable: true,
      render: (row) =>
        row.printed_pct === undefined ? (
          <span className="muted">{t('common.absent')}</span>
        ) : (
          <span className="depth">
            <span className="badge">{printed(row.printed_pct)}</span>
            {/* the bar's WIDTH is the badge the leaflet printed, the same field the badge beside it
                prints — not a second reading of the discount and not the arithmetic depth */}
            {row.depth !== undefined && (
              <span className="bar" aria-hidden="true">
                <i style={{ width: `${String(row.depth * 100)}%` }} />
              </span>
            )}
          </span>
        ),
    },
    {
      key: 'chain',
      label: t('positions.col.chain'),
      sortable: true,
      render: (row) => (
        <>
          <i className="swatch" style={{ background: seriesColour(row.chain.id) }} />
          {chainName(chains, row.chain.id)}
        </>
      ),
    },
    { key: 'carrier', label: t('positions.col.carrier'), sortable: true, render: (row) => row.carrier },
  ]

  const select = (name: string, label: string, values: string[], show?: (one: string) => string) => (
    <label>
      {label}
      <select
        value={paramOf(route, name) ?? ''}
        onChange={(event) => setParam(route, name, event.target.value)}
      >
        <option value="">{t('common.all')}</option>
        {values.map((value) => (
          <option key={value} value={value}>
            {show === undefined ? value : show(value)}
          </option>
        ))}
      </select>
    </label>
  )

  const chainIds = orderChains(all.map((row) => row.chain.id))
  const perChain = new Map(chainIds.map((id) => [id, all.filter((row) => row.chain.id === id).length]))
  const sets = flyers(media, orderChains)

  return (
    <>
      <h2 className="question">{t('positions.question')}</h2>
      <p className="population">{t('positions.population')}</p>

      <div className="chips" role="group" aria-label={t('positions.filter.chain')}>
        <button
          type="button"
          aria-pressed={chosenChain === undefined}
          onClick={() => setParam(route, 'chain', undefined)}
        >
          {t('common.all')}
        </button>
        {chainIds.map((id) => (
          <button
            key={id}
            type="button"
            aria-pressed={chosenChain === id}
            onClick={() => setParam(route, 'chain', chosenChain === id ? undefined : id)}
          >
            <i className="swatch" style={{ background: seriesColour(id) }} />
            {chainName(chains, id)}
            <span className="muted">{count(lang, perChain.get(id) ?? 0)}</span>
          </button>
        ))}
      </div>

      <div className="kpis">
        <KpiCard
          label={t('positions.kpi.rows')}
          value={<CountUp value={rows.length} format={(value) => count(lang, value)} />}
          context={t('common.shown', { shown: count(lang, rows.length), total: count(lang, all.length) })}
          info={{
            lines: [t('positions.population')],
            provenance: `${PROMO_FILE} :: ${POSITIONS_FIELD}`,
            label: t('common.info'),
          }}
        />
        {/* No context line: DESIGN-ship-1 §5 gives the card a short reading aid and puts the
            `file :: field` line in the ⓘ and the tab's footer, which already carries this one.
            Spelled into the context slot it ran to three wrapped lines of path inside the card and
            read as the card's own source, while the value is a count of the SHOWN rows. */}
        <KpiCard
          label={t('positions.kpi.chains')}
          value={
            <CountUp value={distinct(rows, (row) => row.chain.id).length} format={(value) => count(lang, value)} />
          }
        />
        <KpiCard
          label={t('positions.kpi.brands')}
          value={
            <CountUp value={distinct(rows, (row) => row.brand.display).length} format={(value) => count(lang, value)} />
          }
        />
        <KpiCard
          label={t('positions.kpi.printed')}
          value={<CountUp value={withPrintedBadge(rows)} format={(value) => count(lang, value)} />}
          context={t('positions.kpi.priced') + ': ' + count(lang, withPromoPrice(rows))}
        />
      </div>

      <section className="block">
        <h2>{t('media.fresh')}</h2>
        <p className="population">{t('media.fresh.rule')}</p>
        {sets.length === 0 ? (
          <p className="muted">{t('media.none')}</p>
        ) : (
          <div className="gallery">
            {sets.map((set, index) => (
              <button
                key={set.chain}
                type="button"
                className="flyer"
                style={{ '--i': index } as React.CSSProperties}
                onClick={() =>
                  setOpened({ title: chainName(chains, set.chain), pages: set.pages, start: 0 })
                }
              >
                <Cover src={pageUrl(media, set.cover)} name={set.cover} />
                <b>
                  <i className="swatch" style={{ background: seriesColour(set.chain) }} />
                  {chainName(chains, set.chain)}
                </b>
                <span className="muted">
                  {set.since === set.until
                    ? asDayMonth(set.since)
                    : `${asDayMonth(set.since)}–${asDayMonth(set.until)}`}
                </span>
                <span className="muted">
                  {t('media.set', {
                    pages: count(lang, set.pages.length),
                    positions: count(lang, set.positions),
                  })}
                </span>
              </button>
            ))}
          </div>
        )}
      </section>

      <div className="filters">
        {select('brand', t('positions.filter.brand'), distinct(all, (row) => row.brand.display))}
        {select('category', t('positions.filter.category'), distinct(all, (row) => row.item.category))}
        {select('carrier', t('positions.filter.carrier'), distinct(all, (row) => row.carrier))}
        <label>
          {t('positions.filter.text')}
          <input
            type="search"
            value={paramOf(route, 'q') ?? ''}
            onChange={(event) => setParam(route, 'q', event.target.value)}
          />
        </label>
        <button type="button" onClick={() => (window.location.hash = '#/promo/positions')}>
          {t('common.reset')}
        </button>
      </div>

      <DataTable
        t={t}
        caption={t('positions.question')}
        columns={columns}
        rows={rows}
        total={all.length}
        keyOf={positionKey}
        sort={{ key: sortKey, direction, onSort }}
        expand={(row) => <Evidence row={row} />}
      />

      <p className="note">{t('positions.no_old_price')}</p>
      <p className="note">
        {t('media.rows_without_a_page', {
          rows: count(lang, media.rows_without_a_page),
          total: count(lang, all.length),
        })}
      </p>
      <p className="sources">
        {t('common.sources')}: <code>{PROMO_FILE} :: {POSITIONS_FIELD}</code> ·{' '}
        <code>{front.chains.from}</code> · <code>{FRONT_FILE} :: {MEDIA_FIELD}</code>
      </p>

      {opened !== null && (
        <Lightbox
          /* a new target is a new dialog: `start` is read once, into state, and `showModal()` runs
             on mount — so without a key a second click would swap the pages under a dialog that
             never re-opened. Measured: the flyer card's set replaced the row's page and the dialog
             stayed shut. */
          key={`${opened.title}:${opened.pages.join(',')}`}
          t={t}
          title={opened.title}
          pages={opened.pages}
          start={opened.start}
          urlOf={(name) => pageUrl(media, name)}
          onClose={() => setOpened(null)}
        />
      )}
    </>
  )
}

/**
 * A staged photo — or the same «no photo» the pageless rows show, when the file did not arrive.
 *
 * The export names every page the RECORDS carry, because a producer that listed only the files it
 * could see would write a different `front_data.json` on every checkout. The photos themselves are
 * gitignored, so a clean clone stages none of them: without this the table would paint 402 broken
 * images there, and a broken image says «this page is lost», which is not what happened.
 */
function Thumb({ name, src, onOpen }: { name: string; src: string; onOpen: () => void }): React.JSX.Element {
  const { t } = useApp()
  const [gone, setGone] = useState(false)
  if (gone) return <span className="muted tiny">{t('media.no_page')}</span>
  return (
    <button type="button" className="thumb" aria-label={t('media.open_page')} onClick={onOpen}>
      <img
        src={src}
        alt={name}
        loading="lazy"
        decoding="async"
        onError={() => setGone(true)}
      />
    </button>
  )
}

function Cover({ name, src }: { name: string; src: string }): React.JSX.Element {
  const { t } = useApp()
  const [gone, setGone] = useState(false)
  if (gone) return <span className="cover-gone muted tiny">{t('media.no_page')}</span>
  return (
    <img src={src} alt={name} loading="lazy" decoding="async" onError={() => setGone(true)} />
  )
}

function Evidence({ row }: { row: Position }): React.JSX.Element {
  const { t } = useApp()
  const link = telegramLink(row.evidence.channel, row.evidence.msg_id)
  return (
    <p className="pair">
      <span>
        <code>
          {row.evidence.channel}/{row.evidence.msg_id}
        </code>
      </span>
      <span>
        <code>{row.row_id}</code>
      </span>
      <span>{row.tier}</span>
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

/**
 * Промо · Позиції — what the chains promote and at what price (DESIGN-ship-1 §7).
 *
 * `promo_screen_data.json :: screen.positions`, all windows, filtered and sorted here and computed
 * nowhere: the depth a row shows is the PRINTED badge's own reading, and the extracted old price
 * and the arithmetic depth are not on this page at all — beside a row's promo price they give the
 * old price back to the kopiyka (SPEC 3.21 (4), 3.18 (1), 3.22 (1)).
 *
 * The row's ⓘ opens its evidence: channel, message id and the t.me link. A private invite handle
 * has no public message address, so that row says so instead of linking somewhere else.
 */

import { useState } from 'react'

import { useApp } from '../app-state.ts'
import { DataTable } from '../components/DataTable.tsx'
import type { Column } from '../components/DataTable.tsx'
import { KpiCard } from '../components/KpiCard.tsx'
import { chainName, seriesColour } from '../data/chains.ts'
import { PROMO_FILE } from '../data/load.ts'
import {
  POSITIONS_FIELD,
  type SortKey,
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

export function PositionsTab(): React.JSX.Element {
  const { promo, front, chains, lang, t } = useApp()
  const route = useRoute()
  const [sortKey, setSortKey] = useState<SortKey>('chain')
  const [direction, setDirection] = useState<'asc' | 'desc'>('asc')

  const all = positions(promo)
  const filters = {
    ...(paramOf(route, 'chain') === undefined ? {} : { chain: paramOf(route, 'chain') as string }),
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

  const columns: Column<Position>[] = [
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
          price(lang, row.promo_price)
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
          <span className="badge">{printed(row.printed_pct)}</span>
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

  return (
    <>
      <h2 className="question">{t('positions.question')}</h2>
      <p className="population">{t('positions.population')}</p>

      <div className="kpis">
        <KpiCard
          label={t('positions.kpi.rows')}
          value={count(lang, rows.length)}
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
          value={count(lang, distinct(rows, (row) => row.chain.id).length)}
        />
        <KpiCard
          label={t('positions.kpi.brands')}
          value={count(lang, distinct(rows, (row) => row.brand.display).length)}
        />
        <KpiCard
          label={t('positions.kpi.printed')}
          value={count(lang, withPrintedBadge(rows))}
          context={t('positions.kpi.priced') + ': ' + count(lang, withPromoPrice(rows))}
        />
      </div>

      <div className="filters">
        {select(
          'chain',
          t('positions.filter.chain'),
          distinct(all, (row) => row.chain.id),
          (id) => chainName(chains, id),
        )}
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
      <p className="sources">
        {t('common.sources')}: <code>{PROMO_FILE} :: {POSITIONS_FIELD}</code> ·{' '}
        <code>{front.chains.from}</code>
      </p>
    </>
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

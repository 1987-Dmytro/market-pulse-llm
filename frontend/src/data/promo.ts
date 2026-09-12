/**
 * The promo screen's adapter: `results/promo_screen_data.json`, typed and READ — never re-computed
 * (PHASE-ship-1 §3). Every function here either hands a block over, formats one field, or filters
 * and sorts rows the export already decided. The counts it does state are counts of the rows it is
 * about to render, and each says which file and field they came from.
 */

import type {
  DepthRow,
  FeedRow,
  Position,
  PromoExport,
  RollupRow,
  Threads,
  Window,
} from '../types.ts'
import { PROMO_FILE, must } from './load.ts'

export const POSITIONS_FIELD = 'screen.positions'

export function positions(promo: PromoExport): Position[] {
  return must(promo.screen?.positions, PROMO_FILE, POSITIONS_FIELD)
}

/**
 * A position's identity on the screen: `(carrier, row_id)`, the pair the store deduped the union
 * by (PHASE-ship-1 §2 «w3»). `row_id` alone is a channel's own message counter and it REPEATS —
 * seven of the 1 301 rows share an id with a row of the other carrier, two different products read
 * off one post and one leaflet page. Keyed on `row_id`, a click on such a row's ⓘ opened BOTH
 * rows' provenance at once, because the open row is remembered by this key.
 */
export function positionKey(row: Position): string {
  return `${row.carrier}:${row.row_id}`
}

export function feed(promo: PromoExport): FeedRow[] {
  return must(promo.screen?.feed, PROMO_FILE, 'screen.feed')
}

export function threads(promo: PromoExport): Threads {
  return must(promo.screen?.threads, PROMO_FILE, 'screen.threads')
}

export function weeks(promo: PromoExport): string[] {
  return must(promo.screen?.weeks, PROMO_FILE, 'screen.weeks')
}

export function depthRows(promo: PromoExport): DepthRow[] {
  return must(promo.screen?.depth_by_chain_and_brand, PROMO_FILE, 'screen.depth_by_chain_and_brand')
}

export function rollup(promo: PromoExport): RollupRow[] {
  return must(promo.screen?.rollup, PROMO_FILE, 'screen.rollup')
}

export function tableRows(promo: PromoExport): Record<string, number> {
  return must(promo.screen?.table_rows, PROMO_FILE, 'screen.table_rows')
}

export function windows(promo: PromoExport): Window[] {
  return must(promo.windows, PROMO_FILE, 'windows')
}

export function notCollected(promo: PromoExport): { channels: string[]; position_rows: number } {
  return must(promo.not_collected, PROMO_FILE, 'not_collected')
}

/** The metrics the rollup actually carries, so a chart offers no series the file lacks. */
export function rollupMetrics(promo: PromoExport): string[] {
  return [...new Set(rollup(promo).map((row) => row.metric))].sort()
}

export function rollupOf(promo: PromoExport, metric: string): RollupRow[] {
  return rollup(promo).filter((row) => row.metric === metric)
}

/**
 * A date, from either spelling of a window bound: w1's are ISO datetimes and w2/w3's are dates —
 * each seal's own wording (ruling 10.09 (ss) 3). The app formats both as the day they carry and
 * rewrites no source.
 */
export function asDate(iso: string): string {
  return iso.slice(0, 10)
}

/** «12.07» — the day and month a window banner prints, from the same ten characters. */
export function asDayMonth(iso: string): string {
  const [, month, day] = asDate(iso).split('-')
  return month === undefined || day === undefined ? asDate(iso) : `${day}.${month}`
}

/**
 * The row's evidence link, or null for a channel that has no public address.
 *
 * `+Ejz6ubzm21IyMTQy` is a private invite handle: t.me/+… is an invite, not a message, so a link
 * built from it would send the reader somewhere that is not the evidence. Null, and the row says
 * so (DESIGN-ship-1 §5).
 */
export function telegramLink(channel: string, msgId: number): string | null {
  if (!channel.startsWith('@')) return null
  return `https://t.me/${channel.slice(1)}/${msgId}`
}

/** «400 г», or null when the row carries no size — absent is absent, never «0». */
export function volumeOf(item: Position['item']): string | null {
  if (item.size_value === undefined || item.size_unit === undefined) return null
  const value = Number.isInteger(item.size_value) ? item.size_value : item.size_value.toFixed(1)
  const pack = item.pack_count === undefined ? '' : ` ×${item.pack_count}`
  return `${value} ${item.size_unit}${pack}`
}

/** The printed product: the line the leaflet printed, else the category the row was placed in. */
export function productOf(item: Position['item']): string {
  return item.line ?? item.category
}

export interface PositionFilters {
  chain?: string
  brand?: string
  carrier?: string
  category?: string
  text?: string
}

export function filterPositions(rows: Position[], filters: PositionFilters): Position[] {
  const needle = filters.text?.trim().toLocaleLowerCase('uk') ?? ''
  return rows.filter((row) => {
    if (filters.chain !== undefined && row.chain.id !== filters.chain) return false
    if (filters.brand !== undefined && row.brand.display !== filters.brand) return false
    if (filters.carrier !== undefined && row.carrier !== filters.carrier) return false
    if (filters.category !== undefined && row.item.category !== filters.category) return false
    if (needle === '') return true
    const haystack = `${row.brand.display} ${productOf(row.item)}`.toLocaleLowerCase('uk')
    return haystack.includes(needle)
  })
}

export type SortKey = 'brand' | 'product' | 'price' | 'printed' | 'chain' | 'carrier'
export type SortDirection = 'asc' | 'desc'

function sortValue(row: Position, key: SortKey): string | number {
  switch (key) {
    case 'brand':
      return row.brand.display
    case 'product':
      return productOf(row.item)
    case 'price':
      return row.promo_price ?? Number.NEGATIVE_INFINITY
    case 'printed':
      return row.printed_pct ?? Number.NEGATIVE_INFINITY
    case 'chain':
      return row.chain.id
    case 'carrier':
      return row.carrier
  }
}

/** A stable sort on one column; `row_id` breaks every tie so two renders agree. */
export function sortPositions(
  rows: Position[],
  key: SortKey,
  direction: SortDirection,
): Position[] {
  const sign = direction === 'asc' ? 1 : -1
  return [...rows].sort((left, right) => {
    const [a, b] = [sortValue(left, key), sortValue(right, key)]
    if (a === b) return left.row_id.localeCompare(right.row_id)
    if (typeof a === 'number' && typeof b === 'number') return (a - b) * sign
    return String(a).localeCompare(String(b), 'uk') * sign
  })
}

export function distinct(rows: Position[], of: (row: Position) => string | undefined): string[] {
  const values = new Set<string>()
  for (const row of rows) {
    const value = of(row)
    if (value !== undefined) values.add(value)
  }
  return [...values].sort((left, right) => left.localeCompare(right, 'uk'))
}

/** How many of the rendered rows carry a printed badge — a property of the rows, not a new figure. */
export function withPrintedBadge(rows: Position[]): number {
  return rows.filter((row) => row.printed_pct !== undefined).length
}

export function withPromoPrice(rows: Position[]): number {
  return rows.filter((row) => row.promo_price !== undefined).length
}

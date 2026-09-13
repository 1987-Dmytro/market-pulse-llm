/**
 * `results/front_data.json`: the readings, the status and the provenance, READ (DESIGN-ship-1 §7).
 *
 * The bars are the graders' own — value, bar and the file's own `held` flag — and this module never
 * decides whether one holds: a threshold compared again here would be a second judge
 * ([[a_published_number_has_one_reader]]).
 */

import type {
  CategoryPricesBlock,
  Conclusion,
  FrontExport,
  MetricEntry,
  PositionsBlock,
  RegionsBlock,
  ReportingWeek,
  S1Reading,
  S2Row,
  Status,
} from '../types.ts'
import { FRONT_FILE, must } from './load.ts'
import { asDayMonth } from './promo.ts'

export function s1(front: FrontExport): S1Reading {
  return must(front.s1_reading, FRONT_FILE, 's1_reading')
}

export function s2(front: FrontExport): S2Row[] {
  return must(front.s2_readings, FRONT_FILE, 's2_readings')
}

export function statusOf(front: FrontExport): Status {
  return must(front.status, FRONT_FILE, 'status')
}

export function conclusions(front: FrontExport): Conclusion[] {
  return must(front.command_center?.conclusions, FRONT_FILE, 'command_center.conclusions')
}

export function dataUntil(front: FrontExport): { date: string; from: string } {
  return must(front.data_until, FRONT_FILE, 'data_until')
}

export function metrics(front: FrontExport): MetricEntry[] {
  return must(front.dictionary?.metrics, FRONT_FILE, 'dictionary.metrics')
}

export function metricById(front: FrontExport, id: string): MetricEntry | undefined {
  return metrics(front).find((entry) => entry.id === id)
}

export interface SourceRow {
  file: string
  sha256: string
  bytes: number
}

/** The provenance manifest, sorted by file — «which screen ← which file» in one place. */
export function sources(front: FrontExport): SourceRow[] {
  const rows = must(front.sources, FRONT_FILE, 'sources')
  return Object.entries(rows)
    .map(([file, digest]) => ({ file, ...digest }))
    .sort((left, right) => left.file.localeCompare(right.file))
}

/** A bar as a status: the FILE's own `held` flag decides, never a comparison made here. */
export function barStatus(held: boolean): 'good' | 'critical' {
  return held ? 'good' : 'critical'
}

export function categoryPrices(front: FrontExport): CategoryPricesBlock {
  return must(front.category_prices, FRONT_FILE, 'category_prices')
}

export const POSITIONS_BLOCK_FIELD = 'positions'
export const WEEK_FIELD = 'reporting_week'

/**
 * The positions the table shows: the sealed screen export's rows with the leaflet pages' own
 * figures in them, corrected ONCE by the producer (ruling (aaa) 13.09).
 *
 * The table used to read `promo_screen_data.json :: screen.positions` straight, and kept printing
 * the eight figures the pages contradict beside price cards that had already been corrected. That
 * file is sealed and keeps its bytes; the correction is applied where every other priced block
 * gets it — in `export_front_data.page_true` — and read here. Nothing is merged on this side: a
 * second place applying the record is a second spelling of it.
 */
export function positionsBlock(front: FrontExport): PositionsBlock {
  return must(front.positions, FRONT_FILE, POSITIONS_BLOCK_FIELD)
}

/** The reporting week: one banner for the app, and the chains it actually covers. */
export function reportingWeek(front: FrontExport): ReportingWeek {
  return must(front.reporting_week, FRONT_FILE, WEEK_FIELD)
}

/** «25.08–26.08», or one day when a set carries one date — the dates the pages themselves carry. */
export function span(since: string, until: string): string {
  return since === until ? asDayMonth(since) : `${asDayMonth(since)}–${asDayMonth(until)}`
}

/**
 * Is this chain's own week earlier than the one the banner names?
 *
 * The comparison is the producer's own: ISO week ids of one shape, ordered as the strings its
 * `max()` ordered. A card in an earlier week says so where it is read — the banner names the
 * newest week ANY chain has pages in, and nine of the eleven chains are not in it.
 */
export function earlierThanReported(week: string, reported: ReportingWeek): boolean {
  return week < reported.week
}

export function regions(front: FrontExport): RegionsBlock {
  return must(front.regions, FRONT_FILE, 'regions')
}

/**
 * A telegram handle → the chain id the `chains` table names, for the blocks keyed on handles.
 *
 * `screen.rollup[].chain` is a raw handle and `screen.positions[].chain.id` is a folded chain id,
 * so Тренди had no name to put on a bar and printed `+Ejz6ubzm21IyMTQy`. The fold is the producer's
 * — read here, never computed ([[a_fold_is_not_a_membership_test]]).
 */
export function chainOfChannel(front: FrontExport): Record<string, string> {
  return must(front.chains?.by_channel, FRONT_FILE, 'chains.by_channel')
}

/**
 * `results/front_data.json`: the readings, the status and the provenance, READ (DESIGN-ship-1 §7).
 *
 * The bars are the graders' own — value, bar and the file's own `held` flag — and this module never
 * decides whether one holds: a threshold compared again here would be a second judge
 * ([[a_published_number_has_one_reader]]).
 */

import type { Conclusion, FrontExport, MetricEntry, S1Reading, S2Row, Status } from '../types.ts'
import { FRONT_FILE, must } from './load.ts'

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

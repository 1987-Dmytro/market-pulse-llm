/**
 * `front_data.json :: command_center` — the window's own readings, READ (DESIGN-ship-1 §7).
 *
 * The block is `results/dashboard_data_w1.json` by reference: every figure on T0–T8 is a field of
 * it, and nothing here computes one. Two rules live in this file and nowhere else:
 *
 * * **The headline population is the FILE's.** A metric cut over two samples carries
 *   `headline_sample`, and {@link headline} reads that field. An app that picked «payable» itself
 *   would be publishing a population choice as if it were the producer's
 *   ([[a_published_number_has_one_reader]]) — and the other reading stays on the screen beside it,
 *   because the two differ by 1 361 word-less rows and the difference is the finding.
 * * **A missing field is a NAMED refusal**, never a blank and never a zero: `must` throws
 *   `SourceMissing(file, field)` and the shell renders the red panel for that tab's band.
 */

import type {
  AspectReading,
  CcCuts,
  CcMetrics,
  CommandCentre,
  Coverage,
  FrontExport,
  NegativeShareReading,
  NotComputable,
  NsrReading,
  PromoDepth,
  PromoPressure,
  Sampled,
  SovReading,
  Volume,
} from '../types.ts'
import { FRONT_FILE, must } from './load.ts'

export const CC_FIELD = 'command_center'

export function centre(front: FrontExport): CommandCentre {
  return must(front.command_center, FRONT_FILE, CC_FIELD)
}

/** `command_center.<path>` — the provenance line a tab prints, spelled in one place. */
export function ccPath(...parts: string[]): string {
  return [CC_FIELD, ...parts].join('.')
}

function metric<K extends keyof CcMetrics>(front: FrontExport, name: K): CcMetrics[K] {
  return must(centre(front).metrics?.[name], FRONT_FILE, ccPath('metrics', String(name)))
}

/**
 * The reading of a two-sample metric at the population the FILE calls its headline.
 *
 * A sample the block does not carry is a refusal by name rather than an undefined on a card: the
 * `headline_sample` field and the `by_sample` map are written by the same producer, and a
 * disagreement between them is a defect somebody has to see.
 */
export function headline<T>(block: Sampled<T>, field: string): T {
  return must(block.by_sample?.[block.headline_sample], FRONT_FILE, `${field}.by_sample.${block.headline_sample}`)
}

/** Every sample name the block carries, headline FIRST — the order the cards are read in. */
export function samplesOf<T>(block: Sampled<T>): string[] {
  const names = Object.keys(block.by_sample ?? {})
  return [
    ...names.filter((name) => name === block.headline_sample),
    ...names.filter((name) => name !== block.headline_sample),
  ]
}

export function volume(front: FrontExport): Volume {
  return metric(front, 'volume')
}

export function nsr(front: FrontExport): Sampled<NsrReading> {
  return metric(front, 'nsr')
}

export function negativeShare(front: FrontExport): Sampled<NegativeShareReading> {
  return metric(front, 'negative_share_sarcasm_adjusted')
}

export function sov(front: FrontExport): Sampled<SovReading> & { watchlist_rules: string } {
  return metric(front, 'sov')
}

export function aspectShare(front: FrontExport): Sampled<AspectReading> {
  return metric(front, 'aspect_share')
}

export function promoDepth(front: FrontExport): PromoDepth {
  return metric(front, 'promo_depth')
}

export function promoPressure(front: FrontExport): PromoPressure {
  return metric(front, 'promo_pressure')
}

export function coverage(front: FrontExport): Coverage {
  return metric(front, 'coverage')
}

export function cut<K extends keyof CcCuts>(front: FrontExport, name: K): CcCuts[K] {
  return must(centre(front).cuts?.[name], FRONT_FILE, ccPath('cuts', String(name)))
}

export function notComputable(front: FrontExport, key: string): NotComputable {
  return must(centre(front).not_computable?.[key], FRONT_FILE, ccPath('not_computable', key))
}

/** The window every figure of the command centre was read over — one point, never a trend. */
export function ccWindow(front: FrontExport): CommandCentre['window'] {
  return must(centre(front).window, FRONT_FILE, ccPath('window'))
}

export interface Share {
  key: string
  value: number
  count: number
}

/**
 * A `{key: share}` map as rows, dearest first — the shape every horizontal bar exhibit reads.
 *
 * The key breaks a tie so the bars are in the same order on every build, and a key whose share is
 * zero KEEPS its row: «0 mentions» is a reading about a watchlist brand, and dropping it would
 * quietly shrink the watchlist the operator is looking at.
 */
export function shares(share: Record<string, number>, counts: Record<string, number>): Share[] {
  return Object.entries(share ?? {})
    .map(([key, value]) => ({ key, value, count: counts?.[key] ?? 0 }))
    .sort((left, right) => right.value - left.value || left.key.localeCompare(right.key))
}

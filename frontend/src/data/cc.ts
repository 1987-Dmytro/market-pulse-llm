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
 *   `SourceMissing(file, field)`. A field the BOOT reads is caught by the shell and drawn as §5's
 *   red panel; a field a tab reads during its own render has no boundary above it today, so the
 *   throw unmounts the root instead — named as a debt in `docs/plans/ship-1.PROGRESS.md`, because
 *   an error boundary is not a thing this phase asked for.
 */

import type {
  AspectReading,
  CcCuts,
  CcMetrics,
  CommandCentre,
  Coverage,
  DeltaVsOwn,
  FrontExport,
  NegativeShareReading,
  NotComputable,
  NsrReading,
  PromoDepth,
  PromoPressure,
  Sampled,
  SampledOf,
  SovReading,
  Volume,
} from '../types.ts'
import { FRONT_FILE, must } from './load.ts'

export const CC_FIELD = 'command_center'

/** The producer's own block beside it — a figure the brief orders and the sealed file does not
 *  carry, computed once in `export_front_data.py` and only read here (ruling (ddd) 2). */
export const CC_DERIVED_FIELD = 'command_center_derived'

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
export function headline<T>(block: SampledOf<T>, field: string): T {
  return must(block.by_sample?.[block.headline_sample], FRONT_FILE, `${field}.by_sample.${block.headline_sample}`)
}

/** Every sample name the block carries, headline FIRST — the order the cards are read in. */
export function samplesOf<T>(block: SampledOf<T>): string[] {
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

/**
 * Promo pressure per chain — the export's own `position_rows`, and nothing divided here.
 *
 * `promo_pressure.share` is keyed by BRAND; `by_chain` carries counts and no share of any kind, so
 * a per-chain share would be this app's own arithmetic wearing a field's provenance line. The bar
 * is therefore the count the file holds ([[the_app_computes_no_figure]]).
 */
export function pressureByChain(front: FrontExport): Share[] {
  const rows = Object.fromEntries(
    Object.entries(promoPressure(front).by_chain).map(([chain, row]) => [chain, row.position_rows]),
  )
  return shares(rows, rows)
}

/**
 * T4's «Δ до свого» column — the producer's field, at the same population its shares are read at.
 *
 * The app used to subtract `share[brand] − share[own_brands[0]]` while it rendered the row. Both
 * halves of that were the app's own: the arithmetic, and the choice of which own brand the column
 * compares against — and the record lists two ([[the_app_computes_no_figure]]). The block mirrors
 * `metrics.sov`, so {@link headline} picks the population here exactly as it does there.
 */
export function deltaVsOwn(front: FrontExport): DeltaVsOwn {
  const field = `${CC_DERIVED_FIELD}.sov_delta_vs_own`
  return headline(must(front.command_center_derived?.sov_delta_vs_own, FRONT_FILE, field), field)
}

/** The model's verdict as the four strings T8 prints. `decision` is a BLOCK in the record, so the
 *  line names the arm it SELECTED — stringifying the block itself printed «[object Object]». */
export function modelVerdict(front: FrontExport): Record<'step' | 'decision' | 'passed' | 'of' | 'testset', string> {
  const verdict = front.model.verdict
  const decision = (verdict['decision'] ?? {}) as Record<string, unknown>
  return {
    step: String(verdict['step'] ?? ''),
    decision: String(decision['selected'] ?? ''),
    passed: String(verdict['passed'] ?? ''),
    of: String(verdict['of'] ?? ''),
    testset: String(verdict['testset_version'] ?? ''),
  }
}

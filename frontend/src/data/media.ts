/**
 * The flyer photos: `front_data.json :: media`, READ (DESIGN-ship-1 §11).
 *
 * The producer did the join — a position row's `(channel, msg_id)` into the post-media records —
 * and this module only addresses what it wrote. The one thing decided here is the URL: the build
 * stages the referenced photos into the app's own `media/`, so a page is `./media/<name>` in both
 * modes (served mounts `dashboard/app/` at `/`).
 *
 * A row whose page no record carries is absent from `pages` and stays absent on the screen: a
 * placeholder tile would say «this position had no leaflet», which is a claim about the leaflet.
 */

import type { FlyerSet, FrontExport, MediaBlock, Position } from '../types.ts'
import { FRONT_FILE, must } from './load.ts'

export const MEDIA_FIELD = 'media'

export function mediaOf(front: FrontExport): MediaBlock {
  return must(front.media, FRONT_FILE, MEDIA_FIELD)
}

/** The producer's own key for a page: the channel and the message the photo IS. */
export function pageKey(evidence: Position['evidence']): string {
  return `${evidence.channel}:${String(evidence.msg_id)}`
}

/** The staged name of the page a row was read off, or null when no record carries it. */
export function pageOf(media: MediaBlock, row: Position): string | null {
  return media.pages[pageKey(row.evidence)] ?? null
}

/** Where the build put a staged page. The name comes from the export; nothing is guessed. */
export function pageUrl(media: MediaBlock, name: string): string {
  return `./${media.dir}/${encodeURIComponent(name)}`
}

/** The flyer sets, in the chain order the app uses everywhere else — the caller passes it in. */
export function flyers(media: MediaBlock, order: (ids: Iterable<string>) => string[]): FlyerSet[] {
  const byChain = new Map(media.flyers.map((set) => [set.chain, set]))
  return order(byChain.keys()).flatMap((chain) => {
    const set = byChain.get(chain)
    return set === undefined ? [] : [set]
  })
}

/**
 * Every staged name the screen can ask for: the pages behind the rows, and the flyer sets' own
 * pages and covers. This is what `media.files` has to cover — exactly, in both directions.
 */
export function referencedNames(media: MediaBlock): Set<string> {
  const names = new Set(Object.values(media.pages))
  for (const set of media.flyers) {
    names.add(set.cover)
    for (const page of set.pages) names.add(page)
  }
  return names
}

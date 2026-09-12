/**
 * The photos of DESIGN-ship-1 §11, and the tab the static build does not ship (PHASE-ship-1 §2
 * «design-pass»): does the staging list cover exactly what the screen can ask for, and does the
 * mode gate hold on the ROUTE and not only in the navigation?
 *
 * TWO tests, because the check names two — one both ways on the media set, one both ways on the
 * mode flag. `results/front_data.json` is opened off disk, like `adapters.test.ts` opens it: the
 * file the app ships, no fixture. Nothing here looks at `dashboard/app/`: the photos are gitignored
 * and a checkout without them must still read green, so how many of them the build FOUND is a count
 * `--stage` prints into `data/manifest.json` (referenced · staged · missing), not an assertion about
 * this machine's disk.
 */

import { readFileSync } from 'node:fs'
import { fileURLToPath } from 'node:url'
import { describe, expect, it } from 'vitest'

import { orderChains } from '../src/data/chains.ts'
import { flyers, mediaOf, pageKey, pageOf, pageUrl, referencedNames } from '../src/data/media.ts'
import { positions } from '../src/data/promo.ts'
import { PROMO_TABS, SERVED_ONLY, promoTabs, servedOnly } from '../src/router.ts'
import type { FrontExport, PromoExport } from '../src/types.ts'

const root = fileURLToPath(new URL('../../', import.meta.url))
const promo = JSON.parse(readFileSync(`${root}results/promo_screen_data.json`, 'utf8')) as PromoExport
const front = JSON.parse(readFileSync(`${root}results/front_data.json`, 'utf8')) as FrontExport

const media = mediaOf(front)
const all = positions(promo)

describe('media — the staging list and the set the screen can ask for are one set', () => {
  it('covers every name a row or a flyer names, carries none that nothing names, and marks the rest absent', () => {
    const staged = media.files.map((row) => row.name)
    const referenced = referencedNames(media)
    // the export has to HAVE the three blocks: every assertion below is satisfiable by emptiness,
    // and a producer that stopped writing them would otherwise read green
    expect(staged.length).toBeGreaterThan(0)
    expect(referenced.size).toBeGreaterThan(0)
    expect(media.flyers.length).toBeGreaterThan(0)
    expect(new Set(staged).size).toBe(staged.length) // a name is staged once

    // forward: nothing the app can put in a src is missing from what the build copies
    expect([...referenced].filter((name) => !staged.includes(name)).sort()).toEqual([])
    // and the blind direction: nothing is copied that no row and no flyer points at
    expect(staged.filter((name) => !referenced.has(name)).sort()).toEqual([])
    for (const row of media.files) {
      expect(row.file.endsWith(`/${row.name}`)).toBe(true) // the staged name is the file's own
      expect(row.bytes).toBeGreaterThan(0)
    }

    // a row has its own page, or none — and the rows with none are counted, not silently dropped
    const withPage = all.filter((row) => pageOf(media, row) !== null)
    const without = all.filter((row) => pageOf(media, row) === null)
    expect(withPage.length + without.length).toBe(all.length)
    expect(without.length).toBe(media.rows_without_a_page) // the producer's count, on the ROWS
    expect(withPage.length).toBeGreaterThan(0)
    expect(without.length).toBeGreaterThan(0) // both legs are on the shipped export
    for (const row of withPage) {
      const name = pageOf(media, row)
      if (name === null) throw new Error(`no page for ${row.row_id}`)
      expect(media.pages[pageKey(row.evidence)]).toBe(name)
      expect(referenced.has(name)).toBe(true)
      expect(pageUrl(media, name)).toBe(`./${media.dir}/${encodeURIComponent(name)}`)
    }

    // one flyer set per chain, its cover among its own pages, its week in the export's spelling
    const sets = flyers(media, orderChains)
    expect(sets.length).toBe(media.flyers.length)
    expect(new Set(sets.map((set) => set.chain)).size).toBe(sets.length)
    for (const set of sets) {
      expect(set.pages).toContain(set.cover)
      expect(set.pages.length).toBeGreaterThan(0)
      expect(set.positions).toBeGreaterThanOrEqual(set.pages.length)
      expect(set.since <= set.until).toBe(true)
      expect(set.week).toMatch(/^\d{4}-W\d{2}$/) // the ISO week `trends.iso_week` writes
      for (const page of set.pages) expect(referenced.has(page)).toBe(true)
    }
  })
})

describe('the static build does not ship Якість', () => {
  it('drops the tab from the navigation AND answers its route, in both modes', () => {
    expect(promoTabs('served')).toEqual([...PROMO_TABS])
    expect(promoTabs('static')).not.toContain(SERVED_ONLY)
    expect(promoTabs('static').length).toBe(PROMO_TABS.length - 1)
    expect(PROMO_TABS).toContain(SERVED_ONLY) // the tab the gate is about still exists
    // the route, which a link already in someone's hands still asks for
    expect(servedOnly(`/promo/${SERVED_ONLY}`, 'static')).toBe(true)
    expect(servedOnly(`/promo/${SERVED_ONLY}`, 'served')).toBe(false)
    for (const tab of promoTabs('static')) expect(servedOnly(`/promo/${tab}`, 'static')).toBe(false)
  })
})

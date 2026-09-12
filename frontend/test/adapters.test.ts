/**
 * The adapters against the SHIPPED exports (PHASE-ship-1 §2 «front-1»): does the app READ the
 * producers' numbers?
 *
 * `results/promo_screen_data.json` and `results/front_data.json` are opened off disk with node's
 * own `fs` — the files the app ships, never a fixture copied beside the test: a copy pins
 * yesterday's schema and stays green while the app breaks on today's export. Every expected value
 * is a field of the file it is asserted against, and the suite re-derives no market figure; two
 * literals are allowed, each with the line that says why. No component is rendered — §3 of the
 * phase forbids a browser suite here — and `describe`/`it`/`expect` are IMPORTED, not global:
 * `vite.config.ts` sets no `test.globals`, so `vitest/globals` types satisfy tsc, nothing runtime.
 */

import { readFileSync } from 'node:fs'
import { fileURLToPath } from 'node:url'
import { describe, expect, it } from 'vitest'

import { SLOTS, chainName, chainTable, slotOf } from '../src/data/chains.ts'
import { barStatus, s1, s2, sources } from '../src/data/front.ts'
import {
  asDate, asDayMonth, filterPositions, positionKey, positions, productOf, rollup, sortPositions,
  tableRows, telegramLink, threads, volumeOf, weeks, windows,
} from '../src/data/promo.ts'
import type { Bar, FrontExport, Position, PromoExport } from '../src/types.ts'

const root = fileURLToPath(new URL('../../', import.meta.url))
const promo = JSON.parse(readFileSync(`${root}results/promo_screen_data.json`, 'utf8')) as PromoExport
const front = JSON.parse(readFileSync(`${root}results/front_data.json`, 'utf8')) as FrontExport

/** The count PHASE-ship-1 §2 «w3» PUBLISHED — the one figure this file may carry as a literal. */
const PUBLISHED_POSITIONS = 1301
/** DESIGN-ship-1 §6: eight chains, eight slots — indexes of a fixed palette, not a measurement. */
const SLOT_COUNT = 8

/** What the export is expected to carry: absent, it REDS the suite instead of skipping silently. */
function carried<T>(value: T | undefined, what: string): T {
  if (value === undefined) throw new Error(`the export carries no ${what}`)
  return value
}

const all = positions(promo)
const rowWith = (of: (row: Position) => boolean, what: string): Position => carried(all.find(of), what)
const rowIds = (rows: Position[]): string[] => rows.map((row) => row.row_id).sort()
const chainsOnRows = [...new Set(all.map((row) => row.chain.id))]

describe('promo.ts over promo_screen_data.json', () => {
  it('keys a position on (carrier, row_id), which row_id alone does not do', () => {
    // BOTH WAYS on the shipped export. The defect this pins was measured in the browser: the table
    // remembers the open row by its key, so two rows sharing one key opened two provenance panels
    // on one click. `row_id` is a channel's message counter and it repeats across carriers.
    const keys = new Set(all.map(positionKey))
    expect(keys.size).toBe(all.length) // the pair is unique over every shipped row
    expect(keys.size).toBe(PUBLISHED_POSITIONS)

    const bare = new Set(all.map((row) => row.row_id))
    expect(bare.size).toBeLessThan(all.length) // and the id alone is NOT — the blind direction
    const repeated = carried(
      all.find((row) => all.some((other) => other !== row && other.row_id === row.row_id)),
      'a row whose row_id another row repeats',
    )
    const twin = carried(
      all.find((other) => other !== repeated && other.row_id === repeated.row_id),
      'the second row of that id',
    )
    expect(positionKey(twin)).not.toBe(positionKey(repeated)) // same id, different carrier, two keys
    expect(twin.carrier).not.toBe(repeated.carrier)
  })

  it('hands the positions block over and carries the published count', () => {
    expect(all).toBe(promo.screen.positions) // the same array: the adapter copies nothing
    expect(all.length).toBe(promo.screen.positions.length)
    expect(all.length).toBe(PUBLISHED_POSITIONS)
    for (const row of all) {
      const fields = [row.row_id, row.chain.id, row.carrier, row.item.category, row.brand.display]
      for (const field of fields) expect(field.length).toBeGreaterThan(0)
    }
  })

  it('weeks is the export list, ascending, and covers every rollup week', () => {
    const list = weeks(promo)
    expect(list).toBe(promo.screen.weeks)
    expect(list).toEqual([...list].sort()) // ISO weeks sort as they run
    expect(new Set(list).size).toBe(list.length)
    for (const row of rollup(promo)) expect(list).toContain(row.week)
  })

  it('the KPIs the promo tabs show are the file’s own counters', () => {
    for (const key of ['read', 'queue', 'not_collected', 'population', 'product_population'] as const) {
      expect(threads(promo)[key]).toBe(promo.screen.threads[key])
    }
    expect(tableRows(promo)).toEqual(promo.screen.table_rows)
  })

  it('a chain filter keeps that chain, and the partition loses no row', () => {
    let seen = 0
    for (const id of chainsOnRows) {
      const rows = filterPositions(all, { chain: id })
      for (const row of rows) expect(row.chain.id).toBe(id)
      seen += rows.length
    }
    expect(seen).toBe(all.length) // total: every row belongs to exactly one chain
    expect(seen).toBe(PUBLISHED_POSITIONS)
  })

  it('a sort is total and deterministic, price ascending with the priceless rows first', () => {
    const sorted = sortPositions(all, 'price', 'asc')
    expect(sorted.length).toBe(all.length)
    expect(rowIds(sorted)).toEqual(rowIds(all)) // the same row_id MULTISET: the export repeats some
    const again = sortPositions(all, 'price', 'asc') // the same input twice, the same order out
    expect(again.map((row) => row.row_id)).toEqual(sorted.map((row) => row.row_id))
    const priceless = all.filter((row) => row.promo_price === undefined).length
    for (const row of sorted.slice(0, priceless)) expect(row.promo_price).toBeUndefined()
    let previous = Number.NEGATIVE_INFINITY
    for (const row of sorted.slice(priceless)) {
      const value = carried(row.promo_price, `promo price on ${row.row_id}`)
      expect(value).toBeGreaterThanOrEqual(previous)
      previous = value
    }
  })

  it('volumeOf and productOf print what a row carries and refuse what it does not', () => {
    const plain = (item: Position['item']): boolean =>
      Number.isInteger(item.size_value) && item.size_unit !== undefined && item.pack_count === undefined
    const sized = rowWith((row) => plain(row.item), 'row with a whole size and no pack count')
    expect(volumeOf(sized.item)).toBe(`${String(sized.item.size_value)} ${String(sized.item.size_unit)}`)
    const bare = rowWith((row) => row.item.size_value === undefined, 'row without a size value')
    expect(volumeOf(bare.item)).toBeNull()
    const printed = rowWith((row) => row.item.line !== undefined, 'row with a printed line')
    expect(productOf(printed.item)).toBe(printed.item.line)
    const unnamed = rowWith((row) => row.item.line === undefined, 'row with no printed line')
    expect(productOf(unnamed.item)).toBe(unnamed.item.category)
  })

  it('telegramLink addresses a public handle and refuses the private invite of the export', () => {
    const open = rowWith((row) => row.evidence.channel.startsWith('@'), 'row with a public handle')
    expect(telegramLink(open.evidence.channel, open.evidence.msg_id)).toBe(
      `https://t.me/${open.evidence.channel.slice(1)}/${String(open.evidence.msg_id)}`,
    )
    const invite = rowWith((row) => row.evidence.channel.startsWith('+'), 'row with an invite handle')
    expect(telegramLink(invite.evidence.channel, invite.evidence.msg_id)).toBeNull()
  })

  it('asDate and asDayMonth fold both window spellings to one day', () => {
    const list = windows(promo)
    expect(carried(list.find((one) => one.id === 'w1'), 'window w1').since).toContain('T') // w1's seal
    for (const one of list.filter((other) => other.id !== 'w1')) expect(one.since).not.toContain('T')
    for (const one of list) {
      for (const bound of [one.anchor, one.since, one.until]) {
        const date = asDate(bound)
        expect(date).toBe(bound.slice(0, 10)) // ten characters, both spellings
        expect(date).toMatch(/^\d{4}-\d{2}-\d{2}$/)
        expect(asDayMonth(bound)).toBe(`${date.slice(8, 10)}.${date.slice(5, 7)}`) // «dd.mm»
      }
    }
  })
})

describe('front.ts over front_data.json', () => {
  it('the S1 and S2 readings are the graders’ own, field by field', () => {
    expect(s1(front)).toBe(front.s1_reading)
    const reading = s1(front).reading
    const file = front.s1_reading.reading
    if (reading === null || file === null) throw new Error('front_data.json :: s1_reading.reading is null')
    for (const name of ['completeness', 'price_accuracy'] as const) {
      expect(reading.bars[name].value).toBe(file.bars[name].value)
      expect(reading.bars[name].bar).toBe(file.bars[name].bar)
      expect(reading.bars[name].held).toBe(file.bars[name].held)
    }
    expect(s2(front)).toBe(front.s2_readings) // the block, handed over
    for (const [index, row] of s2(front).entries()) {
      const s2File = carried(front.s2_readings[index], `s2_readings[${String(index)}]`)
      for (const name of ['subject_agreement', 'signal_type_agreement'] as const) {
        expect(row.bars[name].value).toBe(s2File.bars[name].value)
        expect(row.bars[name].bar).toBe(s2File.bars[name].bar)
        expect(row.bars[name].held).toBe(s2File.bars[name].held)
      }
    }
  })

  it('barStatus follows the file’s `held` flag in both directions', () => {
    const reading = s1(front).reading
    if (reading === null) throw new Error('front_data.json :: s1_reading.reading is null')
    const s2Bars = s2(front).flatMap((row) => [row.bars.subject_agreement, row.bars.signal_type_agreement])
    const bars: Bar[] = [reading.bars.completeness, reading.bars.price_accuracy, ...s2Bars]
    for (const bar of bars) expect(barStatus(bar.held)).toBe(bar.held ? 'good' : 'critical')
    // both legs exercised on the file's own flags: a held bar AND a broken one are in there
    expect([...new Set(bars.map((bar) => barStatus(bar.held)))].sort()).toEqual(['critical', 'good'])
  })

  it('sources is sorted by file, and every row carries a sha256 and a byte count', () => {
    const rows = sources(front)
    expect(rows.length).toBe(Object.keys(front.sources).length)
    let previous = ''
    for (const row of rows) {
      expect(row.file.localeCompare(previous)).toBeGreaterThanOrEqual(0) // the adapter's comparator
      previous = row.file
      const digest = carried(front.sources[row.file], `digest for ${row.file}`)
      expect(row.sha256).toBe(digest.sha256)
      expect(row.sha256).toMatch(/^[0-9a-f]{64}$/) // a sha256 in hex is 64 characters wide
      expect(row.bytes).toBe(digest.bytes)
      expect(row.bytes).toBeGreaterThan(0)
    }
  })
})

describe('chains.ts — the names from the export, the slots from the brief', () => {
  it('a chain id resolves to its registry name, an unknown id keeps itself, the eight hold 1..8', () => {
    const table = chainTable(front)
    for (const id of chainsOnRows) {
      const row = carried(front.chains.rows.find((one) => one.id === id), `chains row for ${id}`)
      expect(chainName(table, id)).toBe(row.name)
    }
    const folded = 'marketopt_private' // folded away by «chain-fold»: no row carries it any more
    expect(front.chains.rows.some((row) => row.id === folded)).toBe(false)
    expect(chainName(table, folded)).toBe(folded)
    expect(SLOTS.length).toBe(SLOT_COUNT)
    for (const [index, id] of SLOTS.entries()) expect(slotOf(id)).toBe(index + 1)
    const outside = carried(chainsOnRows.find((id) => !SLOTS.includes(id)), 'chain id outside the eight')
    expect(slotOf(outside)).toBe(0)
  })
})

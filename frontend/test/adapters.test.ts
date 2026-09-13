/**
 * The adapters against the SHIPPED exports (PHASE-ship-1 §2 «front-1»): does the app READ the
 * producers' numbers?
 *
 * `results/promo_screen_data.json` and `results/front_data.json` are opened off disk with node's
 * own `fs` — the files the app ships, never a fixture copied beside the test: a copy pins
 * yesterday's schema and stays green while the app breaks on today's export. Every expected value
 * is a field of the file it is asserted against, and the suite re-derives no market figure; three
 * literals are allowed, each with the line that says why. No component is rendered — §3 of the
 * phase forbids a browser suite here — and `describe`/`it`/`expect` are IMPORTED, not global:
 * `vite.config.ts` sets no `test.globals`, so `vitest/globals` types satisfy tsc, nothing runtime.
 */

import { readFileSync } from 'node:fs'
import { fileURLToPath } from 'node:url'
import { describe, expect, it } from 'vitest'

import { SLOTS, chainName, chainTable, handleColour, seriesColour, slotOf } from '../src/data/chains.ts'
import {
  barStatus,
  chainOfChannel,
  earlierThanReported,
  exhibitTitle,
  findingText,
  rankedBasis,
  trends,
  positionsBlock,
  reportingWeek,
  s1,
  s2,
  sources,
  span,
} from '../src/data/front.ts'
import {
  asDate, asDayMonth, filterPositions, positionKey, positions, productOf, rollup, sortPositions,
  tableRows, telegramLink, threads, volumeOf, weeks, windows,
} from '../src/data/promo.ts'
import {
  coverage, deltaVsOwn, headline, modelVerdict, negativeShare, nsr, pressureByChain, promoDepth,
  samplesOf, sov, volume,
} from '../src/data/cc.ts'
import type {
  Bar, FrontExport, NegativeShareReading, NsrReading, Position, PromoExport, SovReading,
} from '../src/types.ts'

const root = fileURLToPath(new URL('../../', import.meta.url))
const promo = JSON.parse(readFileSync(`${root}results/promo_screen_data.json`, 'utf8')) as PromoExport
const front = JSON.parse(readFileSync(`${root}results/front_data.json`, 'utf8')) as FrontExport

/** The count PHASE-ship-1 §2 «w3» PUBLISHED — the one figure this file may carry as a literal. */
const PUBLISHED_POSITIONS = 1301
/** DESIGN-ship-1 §6: eight chains, eight slots — indexes of a fixed palette, not a measurement. */
const SLOT_COUNT = 8
/** The rows `config/price_corrections.yaml` names — the eight of ruling (yy) 1, six corrected
 *  against their page and two whose page prints no price. The record is a config file this suite
 *  does not parse, so its size is the one thing about it that is carried here as a literal. */
const RECORDED_ROWS = 8

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

describe('front.ts :: positions — the table reads the page-true rows, not the sealed export', () => {
  it('the record’s eight rows land field by field, and the population moves by exactly the two', () => {
    // The defect this pins is the one ruling (aaa) 3 routed here: the table read
    // `promo_screen_data.json :: screen.positions` straight and kept printing the eight figures the
    // leaflet pages contradict, beside price cards already corrected. BOTH ways — the corrected
    // rows differ from the sealed file in the corrected fields ONLY, and the sealed file is
    // untouched, still carrying what it carried.
    const block = positionsBlock(front)
    const sealed = new Map(all.map((row) => [positionKey(row), row]))

    expect(block.rows.length).toBe(all.length - block.excluded.n) // 1 299 of the 1 301
    expect(block.excluded.n).toBe(block.excluded.rows.length)
    expect(new Set(block.rows.map(positionKey)).size).toBe(block.rows.length)

    const shown = new Set(block.rows.map(positionKey))
    for (const row of block.excluded.rows) {
      const key = `${row.carrier}:${row.row_id}` // the adapter's own key, spelled by its two fields
      expect(sealed.has(key)).toBe(true) // in the sealed export…
      expect(shown.has(key)).toBe(false) // …and out of the table
      expect(row.why.length).toBeGreaterThan(0) // counted WITH the sentence it was dropped for
    }

    const corrected = block.rows.filter((row) => row.correction !== undefined)
    expect(corrected.length).toBe(block.corrected)
    for (const row of corrected) {
      const was = carried(sealed.get(positionKey(row)), `the sealed row for ${positionKey(row)}`)
      const fixed = carried(row.correction, `the correction on ${positionKey(row)}`)
      expect(fixed.verified_by.length).toBeGreaterThan(0)
      expect(fixed.page.length).toBeGreaterThan(0)
      if (fixed.was.promo_price === undefined) expect(row.promo_price).toBe(was.promo_price)
      else {
        expect(was.promo_price).toBe(fixed.was.promo_price) // the sealed file still says the old one
        expect(row.promo_price).not.toBe(was.promo_price) // and the table does not
      }
      if (fixed.was.size_value === undefined) expect(row.item.size_value).toBe(was.item.size_value)
      else {
        expect(was.item.size_value).toBe(fixed.was.size_value)
        expect(row.item.size_value).not.toBe(was.item.size_value)
      }
      // and NOTHING else moved: the two fields the record may touch blanked on both sides, the
      // rest of the row has to be the sealed row's, field for field
      const flat = (one: Position): unknown => ({
        ...one,
        promo_price: 0,
        correction: undefined,
        item: { ...one.item, size_value: 0 },
      })
      expect(flat(row)).toEqual(flat(was))
    }
    expect(corrected.length + block.excluded.n).toBe(RECORDED_ROWS)
  })

  it('the reporting week is the newest week any chain has pages in, on those pages’ own dates', () => {
    const week = reportingWeek(front)
    const sets = front.media.flyers
    expect(week.week).toMatch(/^\d{4}-W\d{2}$/)
    expect(week.week).toBe([...sets].map((set) => set.week).sort().at(-1))
    expect(week.chains_with_a_set).toBe(sets.length)

    const onIt = sets.filter((set) => set.week === week.week)
    expect([...week.chains].sort()).toEqual(onIt.map((set) => set.chain).sort())
    expect(week.since).toBe(onIt.map((set) => set.since).sort()[0])
    expect(week.until).toBe(onIt.map((set) => set.until).sort().at(-1))
    expect(span(week.since, week.until)).toBe(
      week.since === week.until ? asDayMonth(week.since)
        : `${asDayMonth(week.since)}–${asDayMonth(week.until)}`,
    )

    // both ways on the card's own dating: a chain outside the banner's week is earlier than it and
    // is NOT in its list, and the banner's own week is not earlier than itself
    const earlier = sets.filter((set) => set.week !== week.week)
    expect(earlier.length).toBeGreaterThan(0) // the screen really does carry chains of other weeks
    for (const set of earlier) {
      expect(earlierThanReported(set.week, week)).toBe(true)
      expect(week.chains).not.toContain(set.chain)
    }
    expect(earlierThanReported(week.week, week)).toBe(false)
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

describe('trends — the week’s findings, worded by the producer (PHASE-ship-1 §2 «insight-1»)', () => {
  /** Walk a `stands_on` path the way a reader does: `categories[ice-cream]` picks the row whose
   *  own key is that name, `chains[0]` an index. The paths are the producer's, and a path that
   *  names nothing resolves to `undefined` — which the negative control below relies on. */
  const KEYS = ['category', 'unit', 'chain', 'id'] as const
  function resolve(path: string): unknown {
    let value: unknown = front as unknown
    for (const part of path.split('.')) {
      const found = /^(\w+)(?:\[([^\]]+)])?$/.exec(part)
      if (found === undefined || found === null || value === undefined || value === null) {
        return undefined
      }
      const [, name = '', key] = found
      const next = (value as Record<string, unknown>)[name]
      if (key === undefined) {
        value = next
        continue
      }
      const rows = (next ?? []) as Record<string, unknown>[]
      value = /^\d+$/.test(key)
        ? rows[Number(key)]
        : rows.find((row) => KEYS.some((field) => row[field] === key))
    }
    return value
  }

  /** The digits of a string, separators dropped: «1 247,92» and «1,247.92» are the same figure
   *  said in two languages, and what is compared is the number, never the punctuation. */
  const digits = (text: string): string => text.replace(/\D/g, '')

  const findings = [...trends(front).conclusions, ...trends(front).exhibits]

  it('every sentence states the export’s own fields, in both languages', () => {
    expect(findings.length).toBeGreaterThan(0)
    for (const finding of findings) {
      expect(Object.keys(finding.stands_on).length).toBeGreaterThan(0)
      for (const [path, value] of Object.entries(finding.stands_on)) {
        // the figure the rule recorded IS the field of this export it names
        expect(resolve(path), path).toBe(value)
        // ...and the sentence the reader sees carries that figure, in both languages
        const printed = Number.isInteger(value) ? String(value) : value.toFixed(2)
        for (const lang of ['uk', 'en'] as const) {
          expect(digits(findingText(finding, lang)), `${finding.id} ${lang} ${path}`).toContain(
            digits(printed),
          )
        }
      }
      expect(findingText(finding, 'uk')).toBe(finding.ua)
      expect(findingText(finding, 'en')).toBe(finding.en)
    }
    // the instrument can fail: a path naming a category the block does not carry finds nothing
    expect(resolve('category_prices.categories[no-such-category].bases[uah_per_kg].median')).toBe(
      undefined,
    )
    expect(resolve('category_prices.categories[ice-cream].bases[uah_per_kg].n')).toBe(
      carried(
        front.category_prices.categories.find((row) => row.category === 'ice-cream'),
        'the ice-cream category',
      ).bases.find((one) => one.unit === 'uah_per_kg')?.n,
    )
  })

  it('every exhibit the tab draws is titled by the export, and no title is drawn by nothing', () => {
    // The ids are READ from the components that ask for them — a source scan, the shape
    // `i18n.test.ts` uses for the same question about labels. A list typed here would pass on a
    // renamed id: the test would agree with itself while the tab printed «правило не знайшло
    // висновку» over an exhibit the export had titled ([[a_number_typed_into_its_own_checker]]).
    const sources = [
      'components/CategoryPrices.tsx',
      'components/SpreadStrip.tsx',
      'components/ChainRanking.tsx',
      'tabs/Trends.tsx',
    ]
      .map((name) => readFileSync(`${root}frontend/src/${name}`, 'utf8'))
      .join('\n')
    const drawn = [...sources.matchAll(/exhibitTitle\(front,\s*'([\w-]+)'\)/g)].map((found) => found[1])
    expect(drawn.length).toBeGreaterThan(0) // the scan itself found something to compare

    const titled = trends(front).exhibits.map((finding) => finding.id)
    expect(new Set(titled).size).toBe(titled.length) // one message per exhibit
    // both ways at once: every exhibit the tab draws is titled, and no title is drawn by nothing
    expect([...new Set(drawn)].sort()).toEqual([...titled].sort())
    for (const id of titled) expect(exhibitTitle(front, id)?.id).toBe(id)
    expect(exhibitTitle(front, 'no-such-exhibit')).toBe(undefined)
    expect(new Set(trends(front).conclusions.map((one) => one.id)).size).toBe(
      trends(front).conclusions.length,
    )
  })

  it('the ranking is a basis’s own chain rows, cheapest first, against that basis’s median', () => {
    const ranked = carried(rankedBasis(front), 'the ranked basis')
    const { ranking, basis, category } = ranked
    expect(category.category).toBe(ranking.category)
    expect(basis.unit).toBe(ranking.unit)
    expect(ranking.name).toBe(category.name)
    expect(ranking.ranked).toBe(basis.chains.length)
    expect(basis.chains.length).toBeGreaterThan(0)

    // the rows are the block's own, ordered by the median with the chain id breaking a tie
    const ordered = [...basis.chains].sort(
      (left, right) => left.median - right.median || left.chain.localeCompare(right.chain),
    )
    expect(basis.chains).toEqual(ordered)
    // every chain of the ranking is a chain the export names, and its n is a row count, not a floor
    const table = chainTable(front)
    for (const row of basis.chains) {
      expect(row.name).toBe(chainName(table, row.chain))
      expect(row.n).toBeGreaterThan(0)
      expect(row.min).toBeLessThanOrEqual(row.median)
      expect(row.median).toBeLessThanOrEqual(row.max)
    }
    // the sum of the chains' rows is the basis's own n: the ranking drops no priced row
    expect(basis.chains.reduce((total, row) => total + row.n, 0)).toBe(basis.n)
    // and the basis the strip accents is one the block carries
    const widest = trends(front).widest
    if (widest === null) throw new Error('the export names no widest basis for the strip')
    const strip = front.category_prices.categories.find((row) => row.category === widest.category)
    expect(strip?.bases.some((one) => one.unit === widest.unit)).toBe(true)
  })

  it('a series takes its CHAIN’s colour through the fold, never the handle’s own', () => {
    // The palette's two anchors, from DESIGN-ship-1 §3/§6: slot 1 is the first series token and a
    // chain the brief names no slot for is the «інші» grey. They are identities of a fixed palette,
    // not measurements — and without them a `seriesColour` that returned ONE colour for every chain
    // would satisfy every comparison below.
    expect(seriesColour(SLOTS[0] ?? '')).toBe('var(--s1)')
    expect(seriesColour('no-such-chain')).toBe('var(--text-3)')

    const fold = chainOfChannel(front)
    // a handle whose CHAIN the brief gives a slot: the series wears the chain's colour, and NOT the
    // colour the raw handle would take — the blind direction, and the s52 defect itself (a fold
    // that is read and then not applied leaves every line in the «інші» grey)
    const slotted = carried(
      Object.entries(fold).find(([handle, id]) => SLOTS.includes(id) && handle !== id),
      'a handle whose chain the brief gives a slot',
    )
    expect(handleColour(fold, slotted[0])).toBe(seriesColour(slotted[1]))
    expect(handleColour(fold, slotted[0])).not.toBe(seriesColour(slotted[0]))

    // two handles of ONE chain are one colour, and it is that chain's own
    const byChain = new Map<string, string[]>()
    for (const [handle, id] of Object.entries(fold)) byChain.set(id, [...(byChain.get(id) ?? []), handle])
    const [shared, handles] = carried(
      [...byChain.entries()].find((entry) => entry[1].length > 1),
      'a chain reached through two handles',
    )
    for (const handle of handles) expect(handleColour(fold, handle)).toBe(seriesColour(shared))

    // a handle no fold carries keeps itself and goes recessive — never a crash, never a slot
    expect(handleColour(fold, '@no-such-handle')).toBe('var(--text-3)')

    // and the tab reaches the fold, not the by-position colour it used to (the source, as i18n does)
    const tab = readFileSync(`${root}frontend/src/tabs/Trends.tsx`, 'utf8')
    expect(tab).toContain('handleColour(folded,')
    expect(tab).not.toContain('colourByIndex')
  })
})

describe('the command centre (front-2)', () => {
  /** A dotted path into the RAW export — the second, independent way to the same figure. An
   *  assertion that only ever called the adapter would hold over an adapter that invented the
   *  number ([[a_number_typed_into_its_own_checker]]). */
  function field(dotted: string): unknown {
    return dotted
      .split('.')
      .reduce<unknown>((node, key) => (node as Record<string, unknown>)?.[key], front)
  }

  it('every KPI of T0 is the export’s own field, read at the export’s own headline population', () => {
    const vol = volume(front)
    expect(vol.comments.bought).toBe(field('command_center.metrics.volume.comments.bought'))
    expect(vol.comments.payable).toBe(field('command_center.metrics.volume.comments.payable'))
    expect(vol.leaflet_pages).toBe(field('command_center.metrics.volume.leaflet_pages'))
    expect(vol.position_rows).toBe(field('command_center.metrics.volume.position_rows'))

    // the three sampled metrics: the card shows the reading of the sample the FILE calls the
    // headline, and the other sample's value is a DIFFERENT number — so a card that read the
    // wrong population would print a figure this suite can see
    for (const [name, block, key, read] of [
      ['nsr', nsr(front), 'nsr', (one: NsrReading) => one.nsr],
      [
        'negative_share_sarcasm_adjusted',
        negativeShare(front),
        'negative_share_sarcasm_adjusted',
        (one: NegativeShareReading) => one.negative_share_sarcasm_adjusted,
      ],
      ['sov', sov(front), 'total_mentions', (one: SovReading) => one.total_mentions],
    ] as const) {
      const chosen = block.headline_sample
      expect(chosen).toBe(field(`command_center.metrics.${name}.headline_sample`))
      expect(read(headline(block as never, name) as never)).toBe(
        field(`command_center.metrics.${name}.by_sample.${chosen}.${key}`),
      )
      for (const other of samplesOf(block as never).filter((one) => one !== chosen))
        expect(read(block.by_sample[other] as never)).toBe(
          field(`command_center.metrics.${name}.by_sample.${other}.${key}`),
        )
    }
    // the two populations of the window really do differ — without this the check above would
    // hold over a `headline()` that always returned the first sample it found
    expect(headline(nsr(front), 'nsr').nsr).not.toBe(
      field('command_center.metrics.nsr.by_sample.bought.nsr'),
    )

    const depth = promoDepth(front)
    expect(depth.readings.from_printed_badge.median).toBe(
      field('command_center.metrics.promo_depth.readings.from_printed_badge.median'),
    )
    expect(depth.printed_disagrees_with_computed).toBe(
      field('command_center.metrics.promo_depth.printed_disagrees_with_computed'),
    )

    const reach = coverage(front)
    expect(reach.channels.share).toBe(field('command_center.metrics.coverage.channels.share'))
    expect(reach.segments.with_a_row).toBe(
      field('command_center.metrics.coverage.segments.with_a_row'),
    )

    // and T0 is the tab that reads them: the six adapters are called there, not re-derived
    const tab = readFileSync(`${root}frontend/src/tabs/CommandCentre.tsx`, 'utf8')
    for (const call of ['volume(front)', 'nsr(front)', 'negativeShare(front)', 'sov(front)',
                        'promoDepth(front)', 'coverage(front)']) expect(tab).toContain(call)
  })

  /** s59: the chain exhibit printed «73.1 %» — 106 ÷ 145 divided in the browser — under a
   *  provenance line naming a block that carries no share at all. */
  it('T5’s chain exhibit prints the count the file holds, and no share is divided here', () => {
    const byChain = field('command_center.metrics.promo_pressure.by_chain') as Record<string, unknown>
    const rows = pressureByChain(front)
    expect(rows.length).toBe(Object.keys(byChain).length)

    for (const row of rows) {
      const path = `command_center.metrics.promo_pressure.by_chain.${row.key}`
      expect(row.value).toBe(field(`${path}.position_rows`))
      expect(row.count).toBe(row.value)
      // nothing under the named block could have backed a share
      expect(field(`${path}.share`)).toBeUndefined()
    }
    // the only `share` in the metric is keyed by BRAND, so no chain has one to read
    const brandShare = field('command_center.metrics.promo_pressure.share') as Record<string, number>
    for (const row of rows) expect(brandShare[row.key]).toBeUndefined()

    // the division is gone from the tab, and the exhibit reads the adapter
    const tab = readFileSync(`${root}frontend/src/tabs/CommandCentre.tsx`, 'utf8')
    expect(tab).not.toContain('/ pressure.position_rows')
    expect(tab).toContain('pressureByChain(front)')
  })

  /** Ruling (ddd) 2: T4 printed `row.value - ownShare` — a difference the app subtracted while it
   *  rendered the row, against a reference IT chose out of the record's two own brands. */
  it('T4’s Δ is the producer’s field, against the own brand that field names', () => {
    const block = sov(front)
    const reading = headline(block, 'command_center.metrics.sov')
    const deltas = deltaVsOwn(front)
    const path = `command_center_derived.sov_delta_vs_own.by_sample.${block.headline_sample}`

    // the same population as the shares it is a difference of, and the block itself, not a copy
    expect(field('command_center_derived.sov_delta_vs_own.headline_sample')).toBe(block.headline_sample)
    expect(deltas).toBe(field(path))
    // the record names TWO own brands, so «the own brand» is a choice — the field states it
    expect(reading.own_brands.length).toBeGreaterThan(1)
    expect(deltas.reference).toBe(reading.own_brands[0])

    // and every value IS the difference, re-derived here off the sealed shares
    expect(Object.keys(deltas.delta).sort()).toEqual(Object.keys(reading.share).sort())
    const base = carried(reading.share[deltas.reference], 'a share for the reference own brand')
    for (const [brand, share] of Object.entries(reading.share)) {
      expect(deltas.delta[brand]).toBe(field(`${path}.delta.${brand}`))
      expect(deltas.delta[brand]).toBeCloseTo(share - base, 4)
    }
    expect(deltas.delta[deltas.reference]).toBe(0)
    // today the digits alone cannot tell a Δ from a share: Гармонія is mentioned 0 times in this
    // window, so the reference is 0 and every Δ EQUALS the share beside it. What separates them is
    // the named reference and the subtraction above ([[an_inequality_that_holds_for_the_wrong_reason]])
    expect(base).toBe(0)

    // the subtraction is gone from the tab, and the column reads the adapter
    const tab = readFileSync(`${root}frontend/src/tabs/CommandCentre.tsx`, 'utf8')
    expect(tab).not.toContain('row.value - ownShare')
    expect(tab).toContain('deltaVsOwn(front)')
  })

  /** s59: `decision` is a ten-key block, so `String(...)` printed «рішення [object Object]» on T8. */
  it('T8’s model line names the arm the verdict selected, never the block’s stringification', () => {
    const line = modelVerdict(front)

    expect(line.decision).toBe(field('model.verdict.decision.selected'))
    expect(line.decision).not.toBe('[object Object]')
    expect(line.decision.length).toBeGreaterThan(0)
    // the defect is reachable, not hypothetical: the field the line used to print IS an object
    expect(typeof field('model.verdict.decision')).toBe('object')
    expect(String(field('model.verdict.decision'))).toBe('[object Object]')

    expect(line.step).toBe(field('model.verdict.step'))
    expect(line.passed).toBe(String(field('model.verdict.passed')))
    expect(line.of).toBe(String(field('model.verdict.of')))
    expect(line.testset).toBe(field('model.verdict.testset_version'))

    const tab = readFileSync(`${root}frontend/src/tabs/CommandCentre.tsx`, 'utf8')
    expect(tab).toContain("t('cc.t8.model.line', modelVerdict(front))")
  })
})

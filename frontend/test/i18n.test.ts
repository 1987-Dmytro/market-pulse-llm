/**
 * The app's WORDS, guarded as files — what `tests/test_ui_strings.py` is for the static page
 * (DESIGN-ship-1 §2, SPEC 3.20 (1)). It reads `src/i18n/{uk,en}.json` and every `.ts`/`.tsx` file
 * under `src/`, and fails on: a key one dictionary carries and the other does not, an empty value,
 * a value that states a figure of its own, a template that lost a `{placeholder}` in one language,
 * a key the app renders and no dictionary holds, and a label nothing under `src/` reaches.
 *
 * What it refuses to judge is the WORDING: all a test can hold is that the two languages say it
 * about the same things, and that no number was typed into a label instead of arriving as a fill.
 */

import { readFileSync, readdirSync } from 'node:fs'
import { fileURLToPath } from 'node:url'

import { translate } from '../src/i18n/t.ts'

const src = fileURLToPath(new URL('../src/', import.meta.url))
const dictionary = (name: string): Record<string, string> =>
  JSON.parse(readFileSync(`${src}i18n/${name}`, 'utf8')) as Record<string, string>

const uk = dictionary('uk.json')
const en = dictionary('en.json')
const BOTH: [string, Record<string, string>][] = [['uk', uk], ['en', en]]

/** Every `.ts`/`.tsx` file under `src/`, read once — `src` ends in a slash, so a path appends. */
function sources(dir: string): string[] {
  return readdirSync(dir, { withFileTypes: true }).flatMap((entry) => {
    if (entry.isDirectory()) return sources(`${dir}${entry.name}/`)
    return /\.tsx?$/.test(entry.name) ? [readFileSync(`${dir}${entry.name}`, 'utf8')] : []
  })
}

const CODE = sources(src)

function keysMatching(patterns: RegExp[]): Set<string> {
  const keys = new Set<string>()
  for (const code of CODE)
    for (const pattern of patterns)
      for (const found of code.matchAll(pattern)) if (found[1] !== undefined) keys.add(found[1])
  return keys
}

/** What the app ASKS for, spelled out at the call: `t('k')`, `t("k")`, `translate(lang, 'k')`. */
const CALLED = keysMatching([/\bt\(\s*['"]([\w.]+)['"]/g, /\btranslate\(\s*[^,()]+,\s*['"]([\w.]+)['"]/g])

/** Wider on purpose: a key inside a ternary (`t(mode ? 'a.b' : 'c.d')`) sits at no call's own quote,
 *  and «did this label go stale» is a question about the tree, not about one call site. */
const MENTIONED = keysMatching([/['"]([\w.]+)['"]/g])

const NAV = "App.tsx's nav template, over the router's own tab list"
const FRONT_2 = 'the same template; front-2 renders this tab'

/**
 * The labels no source line spells out: `App.tsx` renders both nav groups through
 * `t(nav.promo.${tab})` and `t(nav.cc.${tab})` over PROMO_TABS and CC_TABS, so the scan above
 * cannot see them. t1–t8 stay template-reached until front-2 builds the command-centre tabs.
 */
const REACHED_BY_TEMPLATE: Record<string, string> = {
  'nav.promo.positions': NAV, 'nav.promo.trends': NAV, 'nav.promo.reactions': NAV,
  'nav.promo.quality': NAV, 'nav.promo.loop': NAV, 'nav.cc.t0': NAV,
  'nav.cc.t1': FRONT_2, 'nav.cc.t2': FRONT_2, 'nav.cc.t3': FRONT_2, 'nav.cc.t4': FRONT_2,
  'nav.cc.t5': FRONT_2, 'nav.cc.t6': FRONT_2, 'nav.cc.t7': FRONT_2, 'nav.cc.t8': FRONT_2,
}

/** What a digit may be part of: an IDENTITY that cannot go stale — a criterion's name, a law's
 *  number, a phase step — never a measurement. Each key allowed one is named below, one by one. */
const IDENTITY = /\bS[1-4]\b|\bfront-[12]\b|SPEC \d+\.\d+(?: \(\d+\))?/g

const MAY_NAME_A_NUMBER: Record<string, string> = {
  'quality.s1.title': 'names criterion S1 — the bar itself, not a reading of it',
  'quality.s2.title': 'names criterion S2 — likewise',
  'cc.placeholder.body': 'names the step that builds the command centre, front-2',
}

describe('uk.json and en.json', () => {
  it('carry exactly the same keys, and no empty value', () => {
    expect({
      missing_in_en: Object.keys(uk).filter((key) => !(key in en)),
      missing_in_uk: Object.keys(en).filter((key) => !(key in uk)),
    }).toEqual({ missing_in_en: [], missing_in_uk: [] })
    for (const [lang, table] of BOTH)
      for (const [key, value] of Object.entries(table))
        expect(value.trim(), `${lang}:${key}`).not.toBe('')
  })

  it('state no figure of their own: a number reaches a label as a {placeholder}', () => {
    const offenders: string[] = []
    for (const [lang, table] of BOTH)
      for (const [key, value] of Object.entries(table)) {
        if (!/\d/.test(value)) continue
        const rest = key in MAY_NAME_A_NUMBER ? value.replace(IDENTITY, '') : value
        if (/\d/.test(rest)) offenders.push(`${lang}:${key}: ${rest}`)
      }
    expect(offenders).toEqual([])
    // an exemption whose key cites nothing any more — or is gone — is an exemption to drop
    for (const [key, why] of Object.entries(MAY_NAME_A_NUMBER))
      expect(/\d/.test(uk[key] ?? '') || /\d/.test(en[key] ?? ''), `${key}: ${why}`).toBe(true)
  })

  it('ask for the same values in both languages', () => {
    const holes = (text: string): string[] =>
      [...text.matchAll(/\{(\w+)\}/g)].map((found) => found[1] ?? '').sort()
    for (const key of Object.keys(uk)) expect(holes(uk[key] ?? ''), key).toEqual(holes(en[key] ?? ''))
  })

  it('carry every key the app renders', () => {
    expect([...CALLED].filter((key) => !(key in uk) || !(key in en)).sort()).toEqual([])
  })

  it('carry no label nothing reaches', () => {
    const orphans = Object.keys(uk).filter((key) => !MENTIONED.has(key) && !(key in REACHED_BY_TEMPLATE))
    expect(orphans).toEqual([])
    const stale = Object.keys(REACHED_BY_TEMPLATE).filter((key) => MENTIONED.has(key) || !(key in uk))
    expect(stale).toEqual([])
  })
})

describe('translate', () => {
  it('fills a template, and hands back a key it does not know', () => {
    expect(uk['common.shown']).toContain('{shown}')
    const filled = translate('uk', 'common.shown', { shown: 12, total: 40 })
    expect(filled).not.toMatch(/[{}]/)
    expect(filled).toContain('12')
    expect(filled).toContain('40')
    expect(translate('uk', 'no.such.key')).toBe('no.such.key')
  })
})

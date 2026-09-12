/**
 * `t(key)` — twenty lines, not a library (DESIGN-ship-1 §2).
 *
 * Two dictionaries of UI strings, one key set. Numbers arrive as `{placeholders}` filled from the
 * export: a label that carried a digit went stale the moment a second chain was collected
 * (`config/ui_strings.yaml`'s own rule, SPEC 3.20 (1)), and the same rule holds here — the only
 * digits in these files are the ones inside a word.
 *
 * A key the dictionaries lack is a defect, not a blank: `t` returns the key itself so the miss is
 * visible on the screen, and `test/i18n.test.ts` fails on it before it ships.
 */

import en from './en.json' with { type: 'json' }
import uk from './uk.json' with { type: 'json' }

export type Lang = 'uk' | 'en'

export const DICTIONARIES: Record<Lang, Record<string, string>> = { uk, en }

export function translate(lang: Lang, key: string, fill?: Record<string, string | number>): string {
  const template = DICTIONARIES[lang][key]
  if (template === undefined) return key
  if (fill === undefined) return template
  return Object.entries(fill).reduce(
    (text, [name, value]) => text.replaceAll(`{${name}}`, String(value)),
    template,
  )
}

export type Translate = (key: string, fill?: Record<string, string | number>) => string

export function translator(lang: Lang): Translate {
  return (key, fill) => translate(lang, key, fill)
}

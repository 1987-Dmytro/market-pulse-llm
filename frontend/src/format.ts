/**
 * Formatting — the app's whole arithmetic (PHASE-ship-1 §3: it formats, filters, sorts and links).
 *
 * A value arrives as the field the file carries and leaves as the string the reader sees. Nothing
 * here sums, shares or compares: the one thing these functions decide is how many digits of a
 * number the screen shows, and they never round a value the file published at more of them without
 * the reader being able to open the file beside it.
 */

import type { Lang, Translate } from './i18n/t.ts'

const LOCALE: Record<Lang, string> = { uk: 'uk-UA', en: 'en-GB' }

/** «1 301» — a count, grouped the reader's way. */
export function count(lang: Lang, value: number): string {
  return new Intl.NumberFormat(LOCALE[lang]).format(value)
}

/** A share as a percentage, at the digits the caller asks for — the file's value, not a new one. */
export function percent(value: number, digits = 1): string {
  return `${(value * 100).toFixed(digits)} %`
}

/** A bar reading as the graders publish it: four decimals, unrounded. */
export function ratio(value: number, digits = 4): string {
  return value.toFixed(digits)
}

/** A printed badge: «−31 %», the leaflet's own number. */
export function printed(value: number): string {
  return `−${value.toFixed(value % 1 === 0 ? 0 : 1)} %`
}

/** A promo price in hryvnia, at the kopiyka the extraction carries. */
export function price(lang: Lang, value: number): string {
  return new Intl.NumberFormat(LOCALE[lang], {
    style: 'currency',
    currency: 'UAH',
    maximumFractionDigits: 2,
  }).format(value)
}

export function money(value: number): string {
  return `$${value.toFixed(4)}`
}

/** «кг» or «л» — the dictionary's word for a basis's unit, never a second spelling of it. */
export function unitWord(t: Translate, unit: string): string {
  return unit === 'uah_per_l' ? t('trends.prices.per_l') : t('trends.prices.per_kg')
}

/** «297,00 ₴/кг» — a price beside the unit it is per. Three blocks print one; this is the one
 *  place that says how, so a card, a strip and a bar cannot disagree about the same figure. */
export function perUnit(lang: Lang, t: Translate, value: number, unit: string): string {
  return `${price(lang, value)}/${unitWord(t, unit)}`
}

/** A datetime or a date, as the day it carries (ruling 10.09 (ss) 3). */
export function day(iso: string): string {
  return iso.slice(0, 10)
}

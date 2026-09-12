/**
 * What every tab is handed: the two exports, the mode, the language, and the chain-name table.
 *
 * One load at boot, one context, no store library. The language lives in the hash (so a link
 * carries it) and in `localStorage` (so a reload keeps it) — read through try/catch, because a
 * private window throws on both and a preference is not worth a blank page.
 */

import { createContext, useContext } from 'react'

import type { ChainName } from './data/chains.ts'
import type { Loaded } from './data/load.ts'
import type { Lang, Translate } from './i18n/t.ts'

export interface App extends Loaded {
  lang: Lang
  t: Translate
  chains: Map<string, ChainName>
}

export const AppContext = createContext<App | null>(null)

export function useApp(): App {
  const app = useContext(AppContext)
  if (app === null) throw new Error('useApp outside the app shell')
  return app
}

const LANG_KEY = 'market-pulse.lang'
const THEME_KEY = 'market-pulse.theme'

export type ThemeChoice = 'system' | 'light' | 'dark'

export function remembered(key: string): string | undefined {
  try {
    return window.localStorage.getItem(key) ?? undefined
  } catch {
    return undefined
  }
}

export function remember(key: string, value: string): void {
  try {
    window.localStorage.setItem(key, value)
  } catch {
    /* a private window refuses to store a preference; the page does not care */
  }
}

export function rememberedLang(): Lang | undefined {
  const value = remembered(LANG_KEY)
  return value === 'uk' || value === 'en' ? value : undefined
}

export function rememberLang(lang: Lang): void {
  remember(LANG_KEY, lang)
}

/**
 * DARK is the default (DESIGN-ship-1 §11): the system preference no longer picks it. What a reader
 * chose here still wins, and `?theme=system` still hands the choice back to the OS — but a first
 * visit opens on the tonality the operator approved, and `index.html` carries the same attribute so
 * the first paint is already it.
 */
export function rememberedTheme(): ThemeChoice {
  const value = remembered(THEME_KEY)
  return value === 'light' || value === 'dark' ? value : 'dark'
}

export function rememberTheme(choice: ThemeChoice): void {
  remember(THEME_KEY, choice)
}

/**
 * `<html lang>` follows the toggle (DESIGN-ship-1 §8). It is not decoration: a screen reader picks
 * its voice and its phonemes from this attribute, so an English interface left declared `uk` is
 * read out in Ukrainian, word for word — and the same attribute drives hyphenation and spell-check.
 */
export function applyLang(lang: Lang): void {
  document.documentElement.lang = lang
}

/**
 * The toggle sets `data-theme` on `<html>`, which flips `color-scheme` and the token blocks
 * together; «system» removes the attribute so `prefers-color-scheme` decides again.
 */
export function applyTheme(choice: ThemeChoice): void {
  const root = document.documentElement
  if (choice === 'system') root.removeAttribute('data-theme')
  else root.setAttribute('data-theme', choice)
}

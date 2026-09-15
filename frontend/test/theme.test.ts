/**
 * What a FIRST visit gets (DESIGN-ship-1 §11, PHASE-ship-1 §2 «dark-default»): the approved
 * tonality is dark and the OS no longer picks it.
 *
 * Two lines decide that, and a unit test can only see one of them, so this file holds both:
 * `src/app-state.ts :: rememberedTheme()` — what the bundle starts from when the browser remembers
 * nothing (or remembers the retired «system» of the pre-12.09 build, which is still sitting in a
 * returning reader's storage) — and `index.html`'s own `data-theme`, read off disk, which is what
 * paints the page BEFORE the bundle runs. Drop the attribute and the suite would stay green while
 * every visitor gets a white flash on a light-mode Mac.
 *
 * Both ways, always: a reader's OWN light choice still wins over the default, and «system» still
 * removes the attribute so `prefers-color-scheme` decides again (the `?theme=system` escape hatch).
 *
 * `vite.config.ts` runs this suite under `environment: 'node'` — there is no DOM here, so `window`
 * and `document` are stubbed for the two functions that touch them; jsdom would be a dependency
 * this phase did not ask for (DESIGN-ship-1 §10).
 */

import { readFileSync } from 'node:fs'
import { fileURLToPath } from 'node:url'
import { afterEach, describe, expect, it } from 'vitest'

import { applyTheme, rememberedTheme } from '../src/app-state.ts'

const THEME_KEY = 'market-pulse.theme'

/** A browser whose storage holds exactly `stored` — `null` is the key no visit has written yet. */
const browserRemembering = (stored: string | null): void => {
  Reflect.set(globalThis, 'window', {
    localStorage: { getItem: (key: string): string | null => (key === THEME_KEY ? stored : null) },
  })
}

/** A private window: `localStorage` is there and throws on touch (`remembered()` catches it). */
const browserRefusingStorage = (): void => {
  Reflect.set(globalThis, 'window', {
    localStorage: {
      getItem: (): string => {
        throw new Error('the storage of a private window refuses to be read')
      },
    },
  })
}

/** `<html>` with nothing on it, so `applyTheme` can be watched setting and removing the attribute. */
const documentRoot = (): { attribute: () => string | null } => {
  const attributes = new Map<string, string>()
  Reflect.set(globalThis, 'document', {
    documentElement: {
      setAttribute: (name: string, value: string): void => {
        attributes.set(name, value)
      },
      removeAttribute: (name: string): void => {
        attributes.delete(name)
      },
    },
  })
  return { attribute: (): string | null => attributes.get('data-theme') ?? null }
}

afterEach(() => {
  Reflect.deleteProperty(globalThis, 'window')
  Reflect.deleteProperty(globalThis, 'document')
})

describe('the theme a first visit opens on', () => {
  it('is DARK when the browser remembers nothing', () => {
    browserRemembering(null)
    expect(rememberedTheme()).toBe('dark')
  })

  it('is DARK when the browser remembers the retired «system»', () => {
    browserRemembering('system')
    expect(rememberedTheme()).toBe('dark')
  })

  it('is DARK when storage itself refuses', () => {
    browserRefusingStorage()
    expect(rememberedTheme()).toBe('dark')
  })

  it('is the reader’s OWN light choice when they made one', () => {
    browserRemembering('light')
    expect(rememberedTheme()).toBe('light')
  })

  it('is dark when they chose dark', () => {
    browserRemembering('dark')
    expect(rememberedTheme()).toBe('dark')
  })
})

describe('what the choice does to `<html>`', () => {
  it('writes the attribute for dark and for light', () => {
    const root = documentRoot()
    applyTheme('dark')
    expect(root.attribute()).toBe('dark')
    applyTheme('light')
    expect(root.attribute()).toBe('light')
  })

  it('removes it for «system», handing the page back to `prefers-color-scheme`', () => {
    const root = documentRoot()
    applyTheme('dark')
    applyTheme('system')
    expect(root.attribute()).toBe(null)
  })
})

describe('the first paint, before the bundle runs', () => {
  it('has `data-theme="dark"` on `<html>` in index.html', () => {
    const html = readFileSync(fileURLToPath(new URL('../index.html', import.meta.url)), 'utf8')
    const tag = /<html\b[^>]*>/.exec(html)?.[0] ?? ''
    expect(tag).toMatch(/\bdata-theme="dark"/)
  })
})

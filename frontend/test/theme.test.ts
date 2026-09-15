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

/**
 * What the PRINTER gets (DESIGN-ship-1 §8: print is non-negotiable; ruling (lll) 3).
 *
 * A browser drops backgrounds when it prints, so a dark `--text-1` is white ink on white paper.
 * The remedy is a medium, not a theme: `@media print` re-points the tokens to the light palette
 * whatever `data-theme` says. The list of tokens it owes is DERIVED from the stylesheet — every
 * property some screen rule gives a value other than the bare `:root` one — so a token added to
 * the dark palette tomorrow and forgotten on paper reds this file instead of printing blank.
 *
 * Both ways: paper is light (each derived token equals its `:root` value under print), and the
 * SCREEN still gets the dark palette (the derived set is non-empty, `--text-1` white among it) —
 * deleting the dark tokens would «fix» print and is caught here.
 */

interface Declaration {
  media: string
  selector: string
  property: string
  value: string
}

/** Every custom-property declaration of a stylesheet with the `@media` and selector that gate it. */
const declarationsOf = (css: string): Declaration[] => {
  const source = css.replace(/\/\*[\s\S]*?\*\//g, '')
  const token = /@media([^{]*)\{|([^{}@;]+)\{|(\})|--([\w-]+)\s*:\s*([^;]+);/g
  const stack: { media: string; selector: string }[] = []
  const found: Declaration[] = []
  for (let match = token.exec(source); match !== null; match = token.exec(source)) {
    const [, query, selector, close, property, value] = match
    if (query !== undefined) stack.push({ media: query.trim(), selector: '' })
    else if (selector !== undefined) stack.push({ media: '', selector: selector.trim() })
    else if (close !== undefined) stack.pop()
    else if (property !== undefined && value !== undefined)
      found.push({
        media: stack.map((frame) => frame.media).filter(Boolean).join(' '),
        selector: stack.map((frame) => frame.selector).filter(Boolean).join(' '),
        property,
        value: value.trim(),
      })
  }
  return found
}

describe('the tokens a page is printed with', () => {
  const css = readFileSync(fileURLToPath(new URL('../src/styles/tokens.css', import.meta.url)), 'utf8')
  const declarations = declarationsOf(css)
  const onPaper = (declaration: Declaration): boolean => declaration.media.includes('print')

  /** The light palette: the bare `:root` block, which every medium starts from. */
  const light = new Map(
    declarations
      .filter((d) => d.media === '' && d.selector === ':root')
      .map((d) => [d.property, d.value] as const),
  )
  /** What a screen rule overrides — the dark palette, whoever selected it. */
  const overridden = declarations.filter(
    (d) => !onPaper(d) && light.has(d.property) && light.get(d.property) !== d.value,
  )
  const printed = new Map(declarations.filter(onPaper).map((d) => [d.property, d.value] as const))

  it('still hands the SCREEN a dark palette to override the light one with', () => {
    expect(overridden.length).toBeGreaterThan(0)
    expect(overridden.map((d) => d.property)).toContain('text-1')
    expect(overridden.filter((d) => d.property === 'text-1').map((d) => d.value)).toEqual(['#ffffff', '#ffffff'])
  })

  it('re-points EVERY token the screen darkens back to its light value', () => {
    const paper = [...new Set(overridden.map((d) => d.property))].map((property) => [
      property,
      printed.get(property),
    ])
    expect(paper).toEqual(
      [...new Set(overridden.map((d) => d.property))].map((property) => [property, light.get(property)]),
    )
  })

  it('reads dark-on-white: the two tokens that decide a printed page', () => {
    expect(printed.get('text-1')).toBe('#0b0b0b')
    expect(printed.get('surface-0')).toBe('#fcfcfb')
  })

  it('is written where the cascade lets it win — after both dark blocks', () => {
    const source = css.replace(/\/\*[\s\S]*?\*\//g, '')
    expect(source.indexOf('@media print')).toBeGreaterThan(source.indexOf('@media (prefers-color-scheme: dark)'))
    expect(source.indexOf('@media print')).toBeGreaterThan(source.indexOf(":root[data-theme='dark']"))
  })
})

/**
 * URL-hash routing: a view is a LINK (DESIGN-ship-1 §2).
 *
 * `#/promo/positions?chain=atb&lang=en` — the path picks the tab, the query carries the filters,
 * the sort and the language, so what the operator is looking at can be pasted into a message and
 * opened again. Sixty lines of `hashchange`, because a router library would be a dependency for
 * one event.
 */

import { useEffect, useState } from 'react'

import type { Mode } from './data/load.ts'

export const PROMO_TABS = ['positions', 'trends', 'reactions', 'quality', 'loop'] as const
export const CC_TABS = ['t0', 't1', 't2', 't3', 't4', 't5', 't6', 't7', 't8'] as const

/** The tab the STATIC client build does not ship (DESIGN-ship-1 §11, the operator's word 12.09). */
export const SERVED_ONLY = 'quality'

/**
 * The promo tabs of a mode. The static build is the public showcase and Якість is the tab that
 * reads the RED S1 bar, so it is not in it — and «not in the navigation» is not the same as «not
 * reachable»: `#/promo/quality` is a link someone already has. {@link servedOnly} answers the
 * route with the same rule this list is built from, so one of them cannot drift open.
 */
export function promoTabs(mode: Mode): readonly string[] {
  return mode === 'served' ? PROMO_TABS : PROMO_TABS.filter((tab) => tab !== SERVED_ONLY)
}

/** Does this path ask for a tab this mode does not carry? */
export function servedOnly(path: string, mode: Mode): boolean {
  return mode !== 'served' && path === `/promo/${SERVED_ONLY}`
}

/**
 * Front-1 lands on the promo half: the brief's `#/cc/t0` is a tab front-2 builds, and a default
 * route to a placeholder would open the app on its one empty screen.
 */
export const DEFAULT_PATH = '/promo/positions'

export interface Route {
  path: string
  query: URLSearchParams
}

export function parseHash(hash: string): Route {
  const raw = hash.replace(/^#/, '')
  const [path, search] = raw.split('?')
  return {
    path: path === undefined || path === '' ? DEFAULT_PATH : path,
    query: new URLSearchParams(search ?? ''),
  }
}

export function hrefFor(path: string, query?: URLSearchParams): string {
  const search = query === undefined ? '' : query.toString()
  return `#${path}${search === '' ? '' : `?${search}`}`
}

/** The current route, and a re-render on every hash change — including the back button's. */
export function useRoute(): Route {
  const [hash, setHash] = useState(() => window.location.hash)
  useEffect(() => {
    const onChange = (): void => setHash(window.location.hash)
    window.addEventListener('hashchange', onChange)
    return () => window.removeEventListener('hashchange', onChange)
  }, [])
  return parseHash(hash)
}

/**
 * One query parameter, written into the hash without touching the others. An empty value REMOVES
 * the parameter, so a link never carries `?chain=` meaning «every chain».
 */
export function setParam(route: Route, name: string, value: string | undefined): void {
  const query = new URLSearchParams(route.query)
  if (value === undefined || value === '') query.delete(name)
  else query.set(name, value)
  window.location.hash = hrefFor(route.path, query)
}

export function paramOf(route: Route, name: string): string | undefined {
  return route.query.get(name) ?? undefined
}

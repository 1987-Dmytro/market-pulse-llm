/**
 * The two exports, the two modes, and the one refusal (DESIGN-ship-1 §2).
 *
 * On load the shell asks `GET /api/status` once with a one-second timeout. An answer means SERVED
 * mode — the Петля tab can write the schedule, «тик зараз» works, the status is live. Anything
 * else means STATIC mode: the same tabs over `./data/`, the loop tab read-only with a note. No
 * other behaviour differs between them.
 *
 * A missing or malformed file throws {@link SourceMissing}, which the shell renders as a red panel
 * naming the file — never a blank and never a zero: a blank where a figure belongs reads as «none
 * in the market», which is a claim about the market.
 */

import type { FrontExport, PromoExport, Schedule, Status } from '../types.ts'

export class SourceMissing extends Error {
  readonly file: string
  readonly field: string | undefined

  constructor(file: string, field?: string, options?: { cause?: unknown }) {
    super(field === undefined ? file : `${file} :: ${field}`, options)
    this.name = 'SourceMissing'
    this.file = file
    this.field = field
  }
}

/** A required field of a loaded file: absent is a named refusal, not `undefined` on a screen. */
export function must<T>(value: T | null | undefined, file: string, field: string): T {
  if (value === null || value === undefined) throw new SourceMissing(file, field)
  return value
}

export type Mode = 'served' | 'static'

export const PROMO_FILE = 'promo_screen_data.json'
export const FRONT_FILE = 'front_data.json'

/** Where a mode reads its files: the server's own route, or the static build's `data/`. */
export function dataUrl(name: string, mode: Mode): string {
  return mode === 'served' ? `/api/exports/${name}` : `./data/${name}`
}

async function readJson<T>(url: string, file: string): Promise<T> {
  let response: Response
  try {
    response = await fetch(url)
  } catch (cause) {
    throw new SourceMissing(file, undefined, { cause })
  }
  if (!response.ok) throw new SourceMissing(file, `HTTP ${response.status}`)
  try {
    return (await response.json()) as T
  } catch (cause) {
    throw new SourceMissing(file, 'not JSON', { cause })
  }
}

const STATUS_TIMEOUT_MS = 1000

/** The live status, or null — which is also the mode question, asked once. */
export async function liveStatus(): Promise<Status | null> {
  const abort = new AbortController()
  const timer = setTimeout(() => abort.abort(), STATUS_TIMEOUT_MS)
  try {
    const response = await fetch('/api/status', { signal: abort.signal })
    return response.ok ? ((await response.json()) as Status) : null
  } catch {
    return null
  } finally {
    clearTimeout(timer)
  }
}

export interface Loaded {
  mode: Mode
  promo: PromoExport
  front: FrontExport
  status: Status
}

export async function loadAll(): Promise<Loaded> {
  const live = await liveStatus()
  const mode: Mode = live === null ? 'static' : 'served'
  const [promo, front] = await Promise.all([
    readJson<PromoExport>(dataUrl(PROMO_FILE, mode), PROMO_FILE),
    readJson<FrontExport>(dataUrl(FRONT_FILE, mode), FRONT_FILE),
  ])
  // `front.status` is the static build's whole answer for the Петля tab, and it is the ONE required
  // block that used to be read straight off the parsed document: an export without it (a stale
  // `dashboard/app/data/` from an older producer, a hand-trimmed copy) threw inside the render
  // instead of at the adapter, React unmounted the tree, and the page came up BLANK — measured, not
  // reasoned about. `must()` turns it into the SourceMissing the shell already knows how to draw.
  return { mode, promo, front, status: live ?? must(front.status, FRONT_FILE, 'status') }
}

/** The loop's schedule — served mode only; the static build has no API to ask. */
export async function getSchedule(): Promise<Schedule> {
  return readJson<Schedule>('/api/schedule', 'data/schedule.json')
}

export interface Refusal {
  status: number
  detail: string
}

/**
 * `PUT /api/schedule`. The server's own 422 comes back verbatim: the rule it refused by is the
 * server's, and re-phrasing it here would give the operator a second, softer sentence.
 */
export async function putSchedule(body: Schedule): Promise<Schedule | Refusal> {
  const response = await fetch('/api/schedule', {
    method: 'PUT',
    headers: { 'content-type': 'application/json' },
    body: JSON.stringify({
      min_interval_hours: body.min_interval_hours,
      default_interval_hours: body.default_interval_hours,
    }),
  })
  if (response.ok) return (await response.json()) as Schedule
  return { status: response.status, detail: JSON.stringify(await response.json()) }
}

export interface TickRun {
  exit_code: number
  stdout: string
  stderr: string
  state: { at: string | null; new_rows?: Record<string, number> } | null
}

/** «Тик зараз» — `POST /api/tick`, the $0 promotion. It never starts the paid reading. */
export async function postTick(): Promise<TickRun> {
  const response = await fetch('/api/tick', { method: 'POST' })
  if (!response.ok) throw new SourceMissing('POST /api/tick', `HTTP ${response.status}`)
  return (await response.json()) as TickRun
}

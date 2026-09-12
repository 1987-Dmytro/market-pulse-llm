/**
 * Промо · Петля — what the loop did last time and when it will do the next (DESIGN-ship-1 §7).
 *
 * Reads the status the shell already loaded — `/api/status` in served mode, `front_data.json ::
 * status` in static mode, the same fields either way — and in SERVED mode only the two routes of
 * `scripts/serve.py` the operator may use: the schedule it writes and the $0 tick it runs.
 *
 * What it refuses to show: `data/schedule.json :: note` (ruling 10.09 (ss) 3) — only the two
 * interval fields ever leave an answer, so the field cannot reach a screen; a budget — `money` is
 * the LAST RECORDED line of the cycle-3 ledger, a display value and never a balance; a re-worded
 * refusal — the server's 422 arrives verbatim, because the rule it refused by is the server's; and
 * a counter the tick did not write, which is one of the three empty sentences, never a zero.
 */

import { useEffect, useState } from 'react'

import { useApp } from '../app-state.ts'
import { KpiCard } from '../components/KpiCard.tsx'
import { SourceMissingPanel } from '../components/SourceMissingPanel.tsx'
import { PROMO_FILE, SourceMissing, getSchedule, postTick, putSchedule } from '../data/load.ts'
import type { TickRun } from '../data/load.ts'
import { count, day, money } from '../format.ts'
import type { Lang, Translate } from '../i18n/t.ts'
import type { TableRows, TickReading } from '../types.ts'

/** The file `GET /api/schedule` answers from — named so a transport failure can name it. */
const SCHEDULE_FILE = 'data/schedule.json'
const TICK_ROUTE = 'POST /api/tick'
/** The command that serves both routes: what the red panel tells the reader to run. */
const TARGET = 'make serve'

type Saved = { ok: true } | { ok: false; detail: string }
type Ran = { ok: true; run: TickRun } | { ok: false; missing: SourceMissing }

/** The hour and minute of a timestamp, from the same string the day came out of. */
function hourMinute(iso: string): string {
  return iso.slice(11, 16)
}

function asMissing(file: string, error: unknown): SourceMissing {
  return error instanceof SourceMissing ? error : new SourceMissing(file, String(error))
}

export function LoopTab(): React.JSX.Element {
  const { status, mode, lang, t } = useApp()
  const served = mode === 'served'
  const [minHours, setMinHours] = useState('')
  const [defaultHours, setDefaultHours] = useState('')
  const [scheduleMissing, setScheduleMissing] = useState<SourceMissing | null>(null)
  const [saved, setSaved] = useState<Saved | null>(null)
  const [running, setRunning] = useState(false)
  const [ran, setRan] = useState<Ran | null>(null)

  // Served mode only: the static build has no API, and asking one that is not there would name a
  // file as missing that is not missing at all.
  useEffect(() => {
    if (!served) return
    getSchedule()
      .then((answer) => {
        // the two intervals and nothing else — a `Schedule` in state is one spread away from
        // rendering the note this tab may not render
        setMinHours(String(answer.min_interval_hours))
        setDefaultHours(String(answer.default_interval_hours))
      })
      .catch((error: unknown) => setScheduleMissing(asMissing(SCHEDULE_FILE, error)))
  }, [served])

  const save = (event: React.FormEvent<HTMLFormElement>): void => {
    event.preventDefault()
    if (!served) return
    setSaved(null)
    // No min/step/required on the inputs: the rule lives in `serve.py :: Schedule`, and a browser
    // that blocked the submit would keep the operator from ever reading the server's sentence.
    putSchedule({
      min_interval_hours: Number(minHours),
      default_interval_hours: Number(defaultHours),
    })
      .then((answer) => {
        if ('status' in answer) {
          setSaved({ ok: false, detail: answer.detail })
          return
        }
        setMinHours(String(answer.min_interval_hours))
        setDefaultHours(String(answer.default_interval_hours))
        setSaved({ ok: true })
      })
      .catch((error: unknown) => setSaved({ ok: false, detail: String(error) }))
  }

  const tickNow = (): void => {
    setRunning(true)
    setRan(null)
    postTick()
      .then((run) => setRan({ ok: true, run }))
      .catch((error: unknown) => setRan({ ok: false, missing: asMissing(TICK_ROUTE, error) }))
      .finally(() => setRunning(false))
  }

  const at = status.tick.at
  const threads = status.threads
  const population = t('reactions.population', {
    product: count(lang, threads.product_population),
    population: count(lang, threads.population),
  })

  return (
    <>
      <h2 className="question">{t('loop.question')}</h2>

      <section className="block">
        <h2>{t('loop.tick.title')}</h2>
        {at === null ? (
          <>
            <p>{t('loop.tick.never')}</p>
            {/* the export's own sentence, which names the file that would carry a tick */}
            {status.tick.why !== undefined && <p className="muted">{status.tick.why}</p>}
          </>
        ) : (
          <>
            <p>
              {day(at)} {hourMinute(at)}
            </p>
            <TickCounters t={t} lang={lang} tick={status.tick} />
          </>
        )}
      </section>

      <section className="block">
        <h2>{t('loop.windows.title')}</h2>
        {status.windows.length === 0 ? (
          <p className="muted">{t('common.not_exported')}</p>
        ) : (
          <div className="scroll">
            <table>
              <caption>{t('loop.windows.title')}</caption>
              <thead>
                <tr>
                  <th scope="col">{t('loop.col.window')}</th>
                  <th scope="col">{t('loop.col.anchor')}</th>
                  <th scope="col" className="num">
                    {t('loop.col.days')}
                  </th>
                  <th scope="col">{t('loop.col.since')}</th>
                  <th scope="col">{t('loop.col.until')}</th>
                </tr>
              </thead>
              <tbody>
                {status.windows.map((one) => (
                  <tr key={one.id}>
                    <th scope="row">{one.id}</th>
                    {/* w1's bounds are ISO datetimes and w2/w3's are dates — each seal's own
                        wording; the app prints the day both carry and rewrites no source */}
                    <td>{day(one.anchor)}</td>
                    <td className="num">{count(lang, one.days)}</td>
                    <td>{day(one.since)}</td>
                    <td>{day(one.until)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
        <p className="sources">
          {t('common.sources')}: <code>{status.from}</code>
        </p>
      </section>

      <section className="block">
        <h2>{t('loop.queue.title')}</h2>
        <div className="kpis">
          <KpiCard
            label={t('header.threads')}
            value={count(lang, threads.read)}
            info={{ lines: [population], provenance: threads.from, label: t('common.info') }}
          />
          <KpiCard label={t('loop.queue.title')} value={count(lang, threads.queue)} />
          <KpiCard label={t('common.not_collected')} value={count(lang, threads.not_collected)} />
          <KpiCard label={t('common.all')} value={count(lang, threads.population)} />
          {/* the dictionary's own sentence is the only string that NAMES this figure, and its two
              digits arrive from the export through `count` — the label the brief asks for */}
          <KpiCard label={population} value={count(lang, threads.product_population)} />
        </div>
        <RowsTable t={t} lang={lang} caption={t('loop.tick.tables')} rows={status.table_rows} />
      </section>

      <section className="block">
        <h2>{t('loop.money.title')}</h2>
        <div className="kpis">
          <KpiCard
            label={t('loop.money.remaining')}
            value={money(status.money.remaining_usd)}
            info={{
              lines: [t('loop.money.display_only')],
              provenance: status.money.from,
              label: t('common.info'),
            }}
          />
        </div>
        <p className="pair">
          <span>
            <code>spent_usd</code> {money(status.money.spent_usd)}
          </span>
          <span>
            <code>cap_usd</code> {money(status.money.cap_usd)}
          </span>
          <span>
            <code>at</code> {day(status.money.at)} {hourMinute(status.money.at)}
          </span>
        </p>
        {/* the ledger's own sentence about its last line */}
        <p className="muted">{status.money.note}</p>
        <p className="note">{t('loop.money.display_only')}</p>
        <p className="sources">
          {t('common.sources')}: <code>{status.money.from}</code>
        </p>
      </section>

      <section className="block">
        <h2>{t('loop.schedule.title')}</h2>
        {scheduleMissing !== null && (
          <SourceMissingPanel
            t={t}
            file={scheduleMissing.file}
            {...(scheduleMissing.field === undefined ? {} : { field: scheduleMissing.field })}
            target={TARGET}
          />
        )}
        {served ? (
          <form className="schedule" onSubmit={save}>
            <label>
              {t('loop.schedule.min')}
              <input
                type="number"
                value={minHours}
                onChange={(event) => setMinHours(event.target.value)}
              />
            </label>
            <label>
              {t('loop.schedule.default')}
              <input
                type="number"
                value={defaultHours}
                onChange={(event) => setDefaultHours(event.target.value)}
              />
            </label>
            <p className="note">{t('loop.schedule.rule')}</p>
            <button type="submit">{t('loop.schedule.save')}</button>
          </form>
        ) : (
          /* No export carries the schedule — `data/schedule.json` is the daemon's file and the
             static build reads only what `make front` stages. The form used to render anyway, as
             two EMPTY number boxes: an empty input reads as «the interval is unset», which is a
             reading, and a false one (DESIGN-ship-1 §10 — an empty state names which of the three
             it is). The sentence says which, and no box invites an edit no API could take. */
          <>
            <p className="muted">{t('loop.schedule.not_in_build')}</p>
            <p className="note">{t('loop.schedule.readonly')}</p>
          </>
        )}
        {saved !== null &&
          (saved.ok ? (
            <p className="note">{t('loop.schedule.saved')}</p>
          ) : (
            <Refused text={saved.detail} />
          ))}
        {served && (
          <p className="sources">
            {t('common.sources')}: <code>{SCHEDULE_FILE}</code>
          </p>
        )}
      </section>

      <section className="block">
        {served ? (
          <button type="button" disabled={running} onClick={tickNow}>
            {running ? t('loop.tick.running') : t('loop.tick.now')}
          </button>
        ) : (
          // its own sentence: this section is about the tick, and the schedule's «read-only» stood
          // here too, so the static build printed one line twice under two different headings
          <p className="note">{t('loop.tick.no_api')}</p>
        )}
        {ran !== null &&
          (ran.ok ? (
            <TickResult t={t} lang={lang} run={ran.run} />
          ) : (
            <SourceMissingPanel
              t={t}
              file={ran.missing.file}
              {...(ran.missing.field === undefined ? {} : { field: ran.missing.field })}
              target={TARGET}
            />
          ))}
        <p className="note">{t('loop.paid.never')}</p>
      </section>

      <p className="sources">
        {t('common.sources')}: <code>{status.from}</code> · <code>{PROMO_FILE}</code> ·{' '}
        <code>{status.money.from}</code>
      </p>
    </>
  )
}

/**
 * The last tick's counters, table by table: what it inserted and what the table then held. A table
 * one map carries and the other does not says so — a zero there would claim the tick counted it.
 */
function TickCounters({
  t,
  lang,
  tick,
}: {
  t: Translate
  lang: Lang
  tick: TickReading
}): React.JSX.Element {
  const names = [
    ...new Set([...Object.keys(tick.new_rows ?? {}), ...Object.keys(tick.table_rows ?? {})]),
  ].sort()
  if (names.length === 0) return <p className="muted">{t('common.not_exported')}</p>
  return (
    <div className="scroll">
      <table>
        <caption>{t('common.rows')}</caption>
        <thead>
          <tr>
            <th scope="col">{t('common.table')}</th>
            <th scope="col" className="num">
              {t('loop.tick.new_rows')}
            </th>
            <th scope="col" className="num">
              {t('loop.tick.tables')}
            </th>
          </tr>
        </thead>
        <tbody>
          {names.map((name) => (
            <tr key={name}>
              <th scope="row">{name}</th>
              <td className="num">{counter(t, lang, tick.new_rows, name)}</td>
              <td className="num">{counter(t, lang, tick.table_rows, name)}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}

function counter(
  t: Translate,
  lang: Lang,
  rows: TableRows | undefined,
  name: string,
): React.ReactNode {
  const value = rows?.[name]
  return value === undefined ? <span className="muted">{t('common.absent')}</span> : count(lang, value)
}

/** One counter map as a table of table → rows, or the sentence that says why it is empty. */
function RowsTable({
  t,
  lang,
  caption,
  rows,
}: {
  t: Translate
  lang: Lang
  caption: string
  rows: TableRows
}): React.JSX.Element {
  const names = Object.keys(rows).sort()
  if (names.length === 0) return <p className="muted">{t('common.not_exported')}</p>
  return (
    <div className="scroll">
      <table>
        <caption>{caption}</caption>
        <thead>
          <tr>
            <th scope="col">{t('common.table')}</th>
            <th scope="col" className="num">
              {t('common.rows')}
            </th>
          </tr>
        </thead>
        <tbody>
          {names.map((name) => (
            <tr key={name}>
              <th scope="row">{name}</th>
              <td className="num">{counter(t, lang, rows, name)}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}

/**
 * What the tick answered: its exit code, the rows it inserted, and — only when it failed — its own
 * stderr. A tick that answered without writing its state file wrote no counters, which is absent
 * and not «nothing new».
 */
function TickResult({
  t,
  lang,
  run,
}: {
  t: Translate
  lang: Lang
  run: TickRun
}): React.JSX.Element {
  return (
    <>
      <p>{t('loop.tick.done', { code: run.exit_code })}</p>
      {run.state === null ? (
        <p className="muted">{t('common.absent')}</p>
      ) : run.state.new_rows === undefined ? (
        <p className="muted">{t('common.not_exported')}</p>
      ) : (
        <RowsTable t={t} lang={lang} caption={t('loop.tick.new_rows')} rows={run.state.new_rows} />
      )}
      {run.exit_code !== 0 && (
        <pre className="scroll">
          <code>{run.stderr}</code>
        </pre>
      )}
    </>
  )
}

/**
 * The server's refusal, verbatim. `PUT /api/schedule`'s 422 names the offending field and the rule
 * it broke; re-phrased here it would be a second, softer sentence beside the one the server meant.
 */
function Refused({ text }: { text: string }): React.JSX.Element {
  return (
    <section className="missing" role="alert">
      <p>{text}</p>
    </section>
  )
}

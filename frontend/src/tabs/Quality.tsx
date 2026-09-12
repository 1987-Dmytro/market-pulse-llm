/**
 * Промо · Якість — how far the numbers on these screens can be trusted (DESIGN-ship-1 §7).
 *
 * `front_data.json :: s1_reading`, `s2_readings` and `sources`, READ. The bars are the graders'
 * own: `data/front.ts :: barStatus` turns the file's `held` flag into the badge, and nothing here
 * compares a value against a bar. A bar the file publishes as not held is printed as not held,
 * beside its own reading and at the digits `format.ts :: ratio` gives it — never rounded toward
 * the bar, never re-graded.
 *
 * What the tab refuses to show: any figure the record does not carry (no verdict over the two bars
 * together, no share recomputed from `matched` and `gold`), and the record's `missed` list — those
 * rows are the frozen gold's own contents, so the screen shows the COUNT the record carries and
 * not the answer key.
 */

import { useApp } from '../app-state.ts'
import { KpiCard } from '../components/KpiCard.tsx'
import { S2Table } from '../components/S2Table.tsx'
import { SourceMissingPanel } from '../components/SourceMissingPanel.tsx'
import { barStatus, s1, s2, sources } from '../data/front.ts'
import { FRONT_FILE } from '../data/load.ts'
import { count, ratio } from '../format.ts'
import type { Lang } from '../i18n/t.ts'
import type { S1Reading } from '../types.ts'

/** How much of a digest a manifest row shows — enough to compare by eye, the full value is in the file. */
const SHA_PREFIX = 12

export function QualityTab(): React.JSX.Element {
  const { front, t } = useApp()
  const s2Rows = s2(front)

  return (
    <>
      <h2 className="question">{t('quality.question')}</h2>

      <section className="block">
        <h2>{t('quality.s1.title')}</h2>
        <S1Block reading={s1(front)} />
      </section>

      <section className="block">
        <h2>{t('quality.s2.title')}</h2>
        {s2Rows.length === 0 ? (
          <p className="note">
            {t('common.not_exported')} <code>{FRONT_FILE} :: s2_readings</code>
          </p>
        ) : (
          <S2Table t={t} rows={s2Rows} boundary={front.s2_boundary} />
        )}
      </section>

      <section className="block">
        <h2>{t('quality.limits.title')}</h2>
        <p className="note">{t('quality.limits.body')}</p>
      </section>

      <section className="block">
        <h2>{t('common.provenance')}</h2>
        <Manifest />
      </section>

      <p className="sources">
        {t('common.sources')}: <code>{FRONT_FILE} :: s1_reading</code> ·{' '}
        <code>{FRONT_FILE} :: s2_readings</code> · <code>{FRONT_FILE} :: sources</code>
      </p>
    </>
  )
}

/**
 * S1 as the grade file publishes it, or the red panel when this checkout has no grade file:
 * `reading === null` is the export's own «optional source absent», and the S2 block below still
 * renders because one missing grader does not hide the other's readings.
 */
function S1Block({ reading }: { reading: S1Reading }): React.JSX.Element {
  const { lang, t } = useApp()
  const record = reading.reading

  if (record === null) {
    return (
      <>
        <SourceMissingPanel t={t} file={reading.from} target="make front" />
        <p className="note">{t('quality.s1.absent')}</p>
        {reading.why !== undefined && <p className="note">{reading.why}</p>}
      </>
    )
  }

  const { completeness, price_accuracy } = record.bars
  const readings = record.readings
  const draw = reading.draw

  return (
    <>
      <div className="kpis">
        <KpiCard
          label={t('quality.s1.completeness')}
          value={ratio(completeness.value)}
          status={{
            kind: barStatus(completeness.held),
            label: `${t(completeness.held ? 'common.holds' : 'common.red')} · ${t('common.bar')} ${ratio(completeness.bar, 2)}`,
          }}
          {...(draw === undefined
            ? {}
            : {
                context: t('quality.s1.gold', {
                  rows: count(lang, completeness.gold),
                  pages: count(lang, draw.pages),
                }),
              })}
          info={{
            lines: [record.match_rule],
            provenance: `${reading.from} :: bars.completeness`,
            label: t('common.info'),
          }}
        />
        <KpiCard
          label={t('quality.s1.price')}
          value={ratio(price_accuracy.value)}
          status={{
            kind: barStatus(price_accuracy.held),
            label: `${t(price_accuracy.held ? 'common.holds' : 'common.red')} · ${t('common.bar')} ${ratio(price_accuracy.bar, 2)}`,
          }}
          context={`${count(lang, price_accuracy.right)} / ${count(lang, price_accuracy.scored)}`}
          info={{
            lines: [price_accuracy.denominator],
            provenance: `${reading.from} :: bars.price_accuracy`,
            label: t('common.info'),
          }}
        />
      </div>

      <div className="rows">
        <Reading
          label={t('quality.s1.unmatched')}
          value={count(lang, readings.predicted_rows_no_gold_row_claims)}
          field="readings.predicted_rows_no_gold_row_claims"
        />
        <Reading
          label={t('quality.s1.unreached')}
          value={count(lang, readings.gold_rows_no_prediction_reached)}
          field="readings.gold_rows_no_prediction_reached"
        />
        <Reading
          label={t('quality.s1.badge')}
          value={fraction(lang, readings.printed_badge)}
          note={readings.printed_badge.note}
          field="readings.printed_badge"
        />
        {/* uk.json carries no label for the old-price reading, so this row wears the field's own
            name rather than a Ukrainian label no file holds. `n === 0` is the producer carrying no
            such field — «not exported», not «0 agreed» — and the record's note says so in words */}
        <p className="pair">
          <span>
            <code>readings.price_old</code>
          </span>
          <span>
            <b>
              {readings.price_old.n === 0
                ? t('common.not_exported')
                : fraction(lang, readings.price_old)}
            </b>
          </span>
          <span className="muted">{readings.price_old.note}</span>
        </p>
      </div>

      {draw === undefined ? (
        <p className="note">
          {t('common.not_exported')} <code>{FRONT_FILE} :: s1_reading.draw</code>
        </p>
      ) : (
        <p className="note">
          {t('quality.s1.draw', {
            drawn: count(lang, draw.rows_drawn),
            population: count(lang, draw.population),
            // a seed is an identifier, not a magnitude: it is printed as the file spells it
            seed: draw.seed,
          })}{' '}
          <code>{draw.from}</code>
        </p>
      )}

      <p className="note">{t('quality.s1.limits')}</p>
      <p className="note">
        {t('quality.s1.match_rule')}: <code>{record.match_rule}</code>
      </p>
    </>
  )
}

/** «40/42» — the record's own two counts, formatted side by side and never divided. */
function fraction(lang: Lang, reading: { agree: number; n: number }): string {
  return `${count(lang, reading.agree)}/${count(lang, reading.n)}`
}

interface ReadingProps {
  label: string
  value: string
  field: string
  note?: string
}

function Reading({ label, value, field, note }: ReadingProps): React.JSX.Element {
  return (
    <p className="pair">
      <span>{label}</span>
      <span>
        <b>{value}</b>
      </span>
      {note !== undefined && <span className="muted">{note}</span>}
      <code>{field}</code>
    </p>
  )
}

/**
 * «which screen ← which file», in one table: the export's own manifest, sorted by file. The column
 * heads are the manifest's field names because uk.json has no label for a digest or for a byte
 * count — a head invented here would be a word no file holds.
 */
function Manifest(): React.JSX.Element {
  const { front, lang, t } = useApp()
  const rows = sources(front)

  if (rows.length === 0) {
    return (
      <p className="note">
        {t('common.not_exported')} <code>{FRONT_FILE} :: sources</code>
      </p>
    )
  }

  return (
    <div className="scroll">
      <table>
        <caption>{t('common.provenance')}</caption>
        <thead>
          <tr>
            <th scope="col">{t('common.file')}</th>
            <th scope="col">
              <code>sha256</code>
            </th>
            <th scope="col" className="num">
              <code>bytes</code>
            </th>
          </tr>
        </thead>
        <tbody>
          {rows.map((row) => (
            <tr key={row.file}>
              <th scope="row">
                <code>{row.file}</code>
              </th>
              <td>
                <code>{row.sha256.slice(0, SHA_PREFIX)}</code>
              </td>
              <td className="num">{count(lang, row.bytes)}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}

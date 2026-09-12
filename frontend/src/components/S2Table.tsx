/**
 * The S2 block, rendered ONCE and read by two tabs (Реакції and Якість).
 *
 * Every cell is the grader's own: the value, the bar, and the file's `held` flag — this component
 * compares nothing. The boundary sentence under the table comes from the export too
 * (`build_promo_screen.S2_BOUNDARY`), because a boundary explained two ways is two boundaries.
 */

import type { Translate } from '../i18n/t.ts'
import { ratio } from '../format.ts'
import { barStatus } from '../data/front.ts'
import type { S2Row } from '../types.ts'
import { StatusBadge } from './StatusBadge.tsx'

export interface S2TableProps {
  t: Translate
  rows: S2Row[]
  boundary: string
}

export function S2Table({ t, rows, boundary }: S2TableProps): React.JSX.Element {
  return (
    <>
      <div className="scroll">
        <table>
          <caption>{t('reactions.s2.title')}</caption>
          <thead>
            <tr>
              <th scope="col">{t('reactions.s2.col.reading')}</th>
              <th scope="col">{t('reactions.s2.col.subject')}</th>
              <th scope="col">{t('reactions.s2.col.signal')}</th>
              <th scope="col">{t('common.file')}</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((row) => {
              const subject = row.bars.subject_agreement
              const signal = row.bars.signal_type_agreement
              return (
                <tr key={row.label}>
                  <th scope="row">{row.label}</th>
                  <td className="num">
                    {ratio(subject.value)} ({row.agreed}/{row.comments}){' '}
                    <StatusBadge
                      kind={barStatus(subject.held)}
                      label={`${t(subject.held ? 'common.holds' : 'common.red')} · ${t('common.bar')} ${ratio(subject.bar, 2)}`}
                    />
                  </td>
                  <td className="num">
                    {ratio(signal.value)}{' '}
                    <StatusBadge
                      kind={barStatus(signal.held)}
                      label={`${t(signal.held ? 'common.holds' : 'common.red')} · ${t('common.bar')} ${ratio(signal.bar, 2)}`}
                    />
                  </td>
                  <td>
                    <code>
                      {row.file} :: {row.block}
                    </code>
                  </td>
                </tr>
              )
            })}
          </tbody>
        </table>
      </div>
      <p className="note">{boundary}</p>
      {rows
        .filter((row) => row.misses !== null)
        .map((row) => (
          <p className="note" key={`${row.label}-ties`}>
            <b>{t('quality.ties.title')}</b>: {row.label} — {row.misses?.total} / {row.misses?.gold_unsure}.{' '}
            {row.misses?.rule}
          </p>
        ))}
    </>
  )
}

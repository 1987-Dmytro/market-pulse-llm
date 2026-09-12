/**
 * ChartCard — title (the question), subtitle (unit + window), the chart, a legend, the ⓘ, and a
 * «таблиця» toggle that renders the SAME series as a table (DESIGN-ship-1 §5, §6).
 *
 * The table view is not a nicety: it is the accessibility fallback, the print fallback and the
 * place a reader checks a mark against a number. The CSV is the shown rows, written in the
 * browser — nothing leaves the page.
 */

import { useState } from 'react'

import type { Translate } from '../i18n/t.ts'
import { Info } from './Info.tsx'

export interface ChartTable {
  head: string[]
  rows: (string | number)[][]
}

export interface ChartCardProps {
  t: Translate
  title: string
  subtitle: string
  provenance: string
  info?: string[]
  legend?: { colour: string; label: string }[]
  table: ChartTable
  note?: string
  wide?: boolean
  children: React.ReactNode
}

function csvOf(table: ChartTable): string {
  const cell = (value: string | number): string => {
    const text = String(value)
    return /[",\n]/.test(text) ? `"${text.replaceAll('"', '""')}"` : text
  }
  return [table.head, ...table.rows].map((row) => row.map(cell).join(',')).join('\n')
}

export function ChartCard({
  t,
  title,
  subtitle,
  provenance,
  info,
  legend,
  table,
  note,
  wide,
  children,
}: ChartCardProps): React.JSX.Element {
  const [asTable, setAsTable] = useState(false)

  const download = (): void => {
    const blob = new Blob([csvOf(table)], { type: 'text/csv;charset=utf-8' })
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `${title.replaceAll(/[^\p{L}\p{N}]+/gu, '-').toLowerCase()}.csv`
    link.click()
    URL.revokeObjectURL(url)
  }

  return (
    <section className={wide === true ? 'card wide' : 'card'}>
      <div className="chart-head">
        <h3>{title}</h3>
        <span className="sub">{subtitle}</span>
        <Info
          lines={info ?? []}
          provenance={provenance}
          label={t('common.info')}
        />
        <span className="spacer" />
        <button type="button" aria-pressed={asTable} onClick={() => setAsTable(!asTable)}>
          {asTable ? t('common.chart') : t('common.table')}
        </button>
        <button type="button" onClick={download}>
          {t('common.csv')}
        </button>
      </div>

      {/* An empty series says WHY in `children` (the chart branch renders it). The table view used
          to replace that sentence with a head over an empty body — the one view of the two where
          «none in the data» became a blank (DESIGN-ship-1 §10), and the default view of Тренди
          opens on exactly such a series. With no rows there is no table to draw, so the sentence
          stands in both views and the reader is never shown a hole. */}
      {asTable && table.rows.length === 0 ? (
        children
      ) : asTable ? (
        <div className="scroll">
          <table>
            <caption>{subtitle}</caption>
            <thead>
              <tr>
                {table.head.map((head) => (
                  <th key={head} scope="col">
                    {head}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {table.rows.map((row, index) => (
                <tr key={`${String(row[0])}-${index}`}>
                  {row.map((value, column) => (
                    <td
                      key={table.head[column] ?? String(column)}
                      className={typeof value === 'number' ? 'num' : undefined}
                    >
                      {value}
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ) : (
        children
      )}

      {legend !== undefined && legend.length > 0 && (
        <div className="legend">
          {legend.map((entry) => (
            <span key={entry.label}>
              <i style={{ background: entry.colour }} />
              {entry.label}
            </span>
          ))}
        </div>
      )}
      {note !== undefined && <p className="note">{note}</p>}
    </section>
  )
}

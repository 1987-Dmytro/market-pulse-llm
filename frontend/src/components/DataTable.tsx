/**
 * DataTable — a real `<table>` with a sticky head, sortable headers, «показано N з M», paging by a
 * hundred rows and a row that expands to its provenance (DESIGN-ship-1 §5).
 *
 * No virtualisation library: a hundred rows a page is the whole of the performance question, and a
 * row the reader can expand to its channel and message id is the whole of the trust question.
 *
 * §11's staggered reveal is one CSS rule and one `--i` per row: the `<tbody>` is keyed on what is
 * being shown, so a filter, a sort or a page turn remounts the rows and the animation plays again.
 */

import { Fragment, useEffect, useState } from 'react'

import type { Translate } from '../i18n/t.ts'

export interface Column<T> {
  key: string
  label: string
  /** right-aligned, tabular — a number */
  num?: boolean
  sortable?: boolean
  render: (row: T) => React.ReactNode
  csv?: (row: T) => string | number
}

export interface Sorting {
  key: string
  direction: 'asc' | 'desc'
  onSort: (key: string) => void
}

export interface DataTableProps<T> {
  t: Translate
  caption: string
  columns: Column<T>[]
  rows: T[]
  total: number
  keyOf: (row: T) => string
  sort?: Sorting
  expand?: (row: T) => React.ReactNode
  pageSize?: number
}

const PAGE_SIZE = 100

export function DataTable<T>({
  t,
  caption,
  columns,
  rows,
  total,
  keyOf,
  sort,
  expand,
  pageSize = PAGE_SIZE,
}: DataTableProps<T>): React.JSX.Element {
  const [page, setPage] = useState(0)
  const [open, setOpen] = useState<string | null>(null)

  const pages = Math.max(1, Math.ceil(rows.length / pageSize))
  // a filter that shrinks the rows under a reader standing on page nine must not leave an empty
  // screen with no rows and no sentence
  useEffect(() => {
    setPage((current) => Math.min(current, pages - 1))
  }, [pages])

  const shown = rows.slice(page * pageSize, page * pageSize + pageSize)
  const ariaSort = (column: Column<T>): 'ascending' | 'descending' | 'none' | undefined => {
    if (sort === undefined || column.sortable !== true) return undefined
    if (sort.key !== column.key) return 'none'
    return sort.direction === 'asc' ? 'ascending' : 'descending'
  }

  return (
    <>
      <p className="count">{t('common.shown', { shown: rows.length, total })}</p>
      <div className="scroll">
        <table>
          <caption>{caption}</caption>
          <thead>
            <tr>
              {expand !== undefined && <th scope="col" aria-label={t('common.provenance')} />}
              {columns.map((column) => (
                <th
                  key={column.key}
                  scope="col"
                  className={column.num === true ? 'num' : undefined}
                  aria-sort={ariaSort(column)}
                >
                  {column.sortable === true && sort !== undefined ? (
                    <button type="button" onClick={() => sort.onSort(column.key)}>
                      {column.label}
                      {sort.key === column.key ? (sort.direction === 'asc' ? ' ↑' : ' ↓') : ''}
                    </button>
                  ) : (
                    column.label
                  )}
                </th>
              ))}
            </tr>
          </thead>
          <tbody key={`${String(page)}:${String(rows.length)}:${shown[0] === undefined ? '' : keyOf(shown[0])}`}>
            {shown.map((row, index) => {
              const id = keyOf(row)
              return (
                <Fragment key={id}>
                  <tr className="reveal" style={{ '--i': index } as React.CSSProperties}>
                    {expand !== undefined && (
                      <td>
                        <button
                          type="button"
                          aria-expanded={open === id}
                          aria-label={t('common.provenance')}
                          onClick={() => setOpen(open === id ? null : id)}
                        >
                          ⓘ
                        </button>
                      </td>
                    )}
                    {columns.map((column) => (
                      <td key={column.key} className={column.num === true ? 'num' : undefined}>
                        {column.render(row)}
                      </td>
                    ))}
                  </tr>
                  {expand !== undefined && open === id && (
                    <tr>
                      <td colSpan={columns.length + 1}>{expand(row)}</td>
                    </tr>
                  )}
                </Fragment>
              )
            })}
          </tbody>
        </table>
      </div>
      {pages > 1 && (
        <div className="pager">
          <button type="button" disabled={page === 0} onClick={() => setPage(page - 1)}>
            {t('common.prev')}
          </button>
          <span>
            {t('common.page')} {page + 1} / {pages}
          </span>
          <button type="button" disabled={page + 1 >= pages} onClick={() => setPage(page + 1)}>
            {t('common.next')}
          </button>
        </div>
      )}
    </>
  )
}

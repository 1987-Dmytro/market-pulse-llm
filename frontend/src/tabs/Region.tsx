/**
 * Промо · Регіон — the stage-2 regional baseline (DESIGN-ship-1 §13).
 *
 * The tab reads `front_data.json :: region`: a KEYWORD sentinel over the eighteen Poltava-oblast
 * channels, not the model. The model's reading of the region is stage 2's gated paid step, and the
 * ⓘ says so where the figures are rather than in a footnote.
 *
 * Its whole point is the honest ZERO. A zero renders as the producer's own sentence — «0 згадок за
 * <вікно> — точка відліку» — never as an empty state: a clean field IS the product, and the brand's
 * own activity is what will move the number. The comment population is a SAMPLE, and the coverage
 * table prints the sentence the export carries for it (ruling (hhh) 3).
 *
 * Not `regions` one letter over, rendered at the foot of Позиції: that is the operator's cut across
 * retail CHAINS. Two populations, two files, and nothing joins them.
 */

import { useApp } from '../app-state.ts'
import { type Column, DataTable } from '../components/DataTable.tsx'
import { Info } from '../components/Info.tsx'
import { KpiCard } from '../components/KpiCard.tsx'
import { REGION_PULSE_FIELD, regionPulse, saidText } from '../data/front.ts'
import { FRONT_FILE } from '../data/load.ts'
import { asDate, telegramLink } from '../data/promo.ts'
import { count } from '../format.ts'
import { hrefFor } from '../router.ts'
import type { MentionRow } from '../types.ts'

export function RegionTab(): React.JSX.Element {
  const { front, lang, t } = useApp()
  const block = regionPulse(front)

  // the producer sorts the brands own-first, and the sentinel refuses a dictionary that names no
  // brand at all — so the head of this list is the brand the instrument exists for
  const watched = block.brands[0]

  const columns: Column<MentionRow>[] = [
    { key: 'date', label: t('region.col.date'), render: (row) => asDate(row.date) },
    { key: 'channel', label: t('reactions.col.channel'), render: (row) => row.channel },
    {
      key: 'kind',
      label: t('region.col.kind'),
      // «post» / «comment» is the sentinel's own vocabulary: data, never a translation key
      render: (row) => <span className="badge">{row.kind}</span>,
    },
    {
      key: 'brand',
      label: t('region.col.brand'),
      render: (row) => <span className="badge">{row.brand}</span>,
    },
    { key: 'matched', label: t('region.col.matched'), render: (row) => <code>{row.matched}</code> },
    {
      key: 'quote',
      label: t('reactions.col.quote'),
      render: (row) => <span className="quote">{row.quote}</span>,
    },
  ]

  return (
    <>
      <h2 className="question">
        {t('region.question', { brand: watched === undefined ? '' : watched.name })}
      </h2>
      {/* a <div>, not a <p>: the ⓘ popover renders its own <p>s, which may not nest inside one */}
      <div className="population">
        {saidText(block.instrument, lang)}
        <Info
          lines={[block.reading, block.sample.from]}
          provenance={`${FRONT_FILE} :: ${REGION_PULSE_FIELD}`}
          label={t('common.info')}
        />
      </div>

      <section className="block">
        <h2>{t('region.baseline.title')}</h2>
        <p className="note">{saidText(block.baseline_says, lang)}</p>
        <div className="kpis">
          {block.brands.map((brand) => (
            <KpiCard
              key={brand.brand_id}
              label={brand.name}
              value={count(lang, brand.mentions)}
              context={`${
                brand.own === null
                  ? t('region.baseline.unlisted')
                  : brand.own
                    ? t('region.baseline.own')
                    : t('region.baseline.rival')
              } · ${
                brand.spellings.length === 0
                  ? t('common.absent')
                  : t('region.baseline.spellings', { spellings: brand.spellings.join(' · ') })
              }`}
              info={{
                lines: [saidText(block.baseline_says, lang), block.reading],
                provenance: `${FRONT_FILE} :: ${REGION_PULSE_FIELD}.brands`,
                label: t('common.info'),
              }}
            />
          ))}
        </div>
      </section>

      <section className="block">
        <h2>{t('region.feed.title')}</h2>
        {block.mentions.length === 0 ? (
          // §10's three states, and this one is «none in the data»: the scan ran over every channel
          // of the window and found nothing — not «not collected», not «rows not exported»
          <p className="note">
            {saidText(block.baseline_says, lang)} — {t('common.absent')}
          </p>
        ) : (
          <DataTable
            t={t}
            caption={t('region.feed.title')}
            columns={columns}
            rows={block.mentions}
            total={block.mentions.length}
            keyOf={(row) => `${row.channel}/${row.msg_id}/${row.brand}`}
            expand={(row) => <Evidence row={row} />}
          />
        )}
      </section>

      <section className="block">
        <h2>{t('region.coverage.title')}</h2>
        <p className="note">{saidText(block.sample.sentence, lang)}</p>
        <div className="scroll">
          <table>
            <caption>{t('region.coverage.title')}</caption>
            <thead>
              <tr>
                <th scope="col">{t('reactions.col.channel')}</th>
                <th scope="col" className="num">
                  {t('region.col.posts')}
                </th>
                <th scope="col" className="num">
                  {t('region.col.comments')}
                </th>
                <th scope="col">{t('region.col.window')}</th>
                <th scope="col" className="num">
                  {t('region.col.threads')}
                </th>
                <th scope="col" className="num">
                  {t('region.col.outstanding')}
                </th>
                <th scope="col" className="num">
                  {t('region.col.mentions')}
                </th>
              </tr>
            </thead>
            <tbody>
              {block.channels.map((row) => (
                <tr key={row.channel}>
                  <th scope="row">{row.channel}</th>
                  <td className="num">{count(lang, row.posts)}</td>
                  <td className="num">{count(lang, row.comments)}</td>
                  <td>
                    {row.first_date === null || row.last_date === null ? (
                      <span className="muted">{t('common.absent')}</span>
                    ) : (
                      `${asDate(row.first_date)} – ${asDate(row.last_date)}`
                    )}
                  </td>
                  <td className="num">
                    {row.threads_read === null || row.threads_total === null ? (
                      <span className="muted">{t('common.not_exported')}</span>
                    ) : (
                      `${count(lang, row.threads_read)} / ${count(lang, row.threads_total)}`
                    )}
                  </td>
                  <td className="num">
                    {row.outstanding === null ? (
                      <span className="muted">{t('common.not_exported')}</span>
                    ) : (
                      count(lang, row.outstanding)
                    )}
                  </td>
                  <td className="num">{count(lang, row.mentions)}</td>
                </tr>
              ))}
              <tr>
                <th scope="row">{t('reactions.matrix.total')}</th>
                <td className="num">
                  <b>{count(lang, block.totals.posts)}</b>
                </td>
                <td className="num">
                  <b>{count(lang, block.totals.comments)}</b>
                </td>
                <td>
                  {block.window.first_date === null || block.window.last_date === null ? (
                    <span className="muted">{t('common.absent')}</span>
                  ) : (
                    `${asDate(block.window.first_date)} – ${asDate(block.window.last_date)}`
                  )}
                </td>
                <td className="num">
                  <b>
                    {count(lang, block.sample.threads_read)} /{' '}
                    {count(lang, block.sample.threads_total)}
                  </b>
                </td>
                <td className="num">
                  <b>{count(lang, block.sample.outstanding)}</b>
                </td>
                <td className="num">
                  <b>{count(lang, block.totals.mentions)}</b>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>

      <section className="block">
        <h2>{t('region.link.title')}</h2>
        <p className="note">
          <a href={hrefFor('/promo/positions', new URLSearchParams({ chain: block.promo_link.chain }))}>
            {t('region.link.cta', { chain: block.promo_link.name })}
          </a>
        </p>
      </section>

      <p className="sources">
        {t('common.sources')}:{' '}
        <code>
          {FRONT_FILE} :: {REGION_PULSE_FIELD}
        </code>
      </p>
    </>
  )
}

function Evidence({ row }: { row: MentionRow }): React.JSX.Element {
  const { t } = useApp()
  const link = telegramLink(row.channel, row.msg_id)
  return (
    <p className="pair">
      <span>
        <code>
          {row.channel}/{row.msg_id}
        </code>
      </span>
      <span>
        {t('region.col.matched')}: <code>{row.matched}</code>
      </span>
      {link === null ? (
        <span className="muted">{t('positions.link.private')}</span>
      ) : (
        <a href={link} target="_blank" rel="noreferrer noopener">
          {t('positions.link')}
        </a>
      )}
    </p>
  )
}

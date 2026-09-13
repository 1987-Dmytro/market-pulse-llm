/**
 * Ціни промо за категоріями — the median a kilogram costs, and the two ends named.
 *
 * Every figure here is a field of `front_data.json :: category_prices`; this component formats and
 * links, and computes nothing (DESIGN-ship-1 §3). One card per category AND per unit, because the
 * producer cuts them that way: a category holding both gram and millilitre rows has no single
 * median, and ₴/kg added to ₴/L would be a sum with no unit.
 *
 * The median leads because it survives a misread size; the ends are shown because the operator has
 * to see WHICH pack is cheapest — and each of them carries its own leaflet page, one click away,
 * since S1 completeness is red and an extreme is exactly where a misread size lands.
 */

import { useState } from 'react'

import { useApp } from '../app-state.ts'
import { categoryPrices } from '../data/front.ts'
import { FRONT_FILE } from '../data/load.ts'
import { mediaOf, pageUrl } from '../data/media.ts'
import { telegramLink } from '../data/promo.ts'
import { count, price } from '../format.ts'
import type { CategoryBasis, CategoryPrices as Category, PriceCard } from '../types.ts'
import { ChartCard } from './ChartCard.tsx'
import { CorrectionInfo } from './CorrectionInfo.tsx'
import { Lightbox } from './Lightbox.tsx'

export const CATEGORY_FIELD = 'category_prices'

/** A card is one (category, unit) pair — or a category with nothing priced, which still gets one. */
interface Card {
  category: Category
  basis: CategoryBasis | undefined
}

function cardsOf(categories: Category[]): Card[] {
  const cards = categories.flatMap((category): Card[] =>
    category.bases.length === 0
      ? [{ category, basis: undefined }]
      : category.bases.map((basis) => ({ category, basis })),
  )
  // the fullest first: a director reads Морозиво and Сир твердий before Рослинні аналоги
  return cards.sort((left, right) => (right.basis?.n ?? 0) - (left.basis?.n ?? 0))
}

export function CategoryPrices(): React.JSX.Element {
  const { front, lang, t } = useApp()
  const [opened, setOpened] = useState<{ title: string; pages: string[] } | null>(null)
  const block = categoryPrices(front)
  const media = mediaOf(front)
  const cards = cardsOf(block.categories)

  const unitWord = (unit: string): string =>
    unit === 'uah_per_l' ? t('trends.prices.per_l') : t('trends.prices.per_kg')

  /** A price per unit, beside the unit it is per — «297,00 ₴/кг». */
  const perUnit = (value: number, unit: string): string =>
    `${price(lang, value)}/${unitWord(unit)}`

  const end = (card: PriceCard, unit: string, label: string): React.JSX.Element => {
    const link = telegramLink(card.channel, card.msg_id)
    return (
      <div className="extreme">
        {card.page === undefined ? (
          <span className="muted tiny">{t('media.no_page')}</span>
        ) : (
          <button
            type="button"
            className="thumb big"
            aria-label={t('media.open_page')}
            onClick={() => setOpened({ title: card.brand, pages: [card.page as string] })}
          >
            <img src={pageUrl(media, card.page)} alt="" loading="lazy" />
          </button>
        )}
        <span className="who">
          <span className="muted">
            {label}
            {card.unit_price !== undefined && (
              <b className="price"> {perUnit(card.unit_price, unit)}</b>
            )}
            <CorrectionInfo card={card} lang={lang} t={t} />
          </span>
          <b>{card.brand}</b>
          {card.line !== undefined && <span>{card.line}</span>}
          <span className="muted">
            {card.size_value !== undefined &&
              `${count(lang, card.size_value)} ${card.size_unit ?? ''} · `}
            {card.promo_price === undefined ? t('common.absent') : price(lang, card.promo_price)}
            {link !== null && (
              <>
                {' '}
                <a href={link} target="_blank" rel="noreferrer">
                  {t('positions.link')}
                </a>
              </>
            )}
          </span>
        </span>
      </div>
    )
  }

  return (
    <>
      <ChartCard
        t={t}
        wide
        title={t('trends.prices.title')}
        subtitle={t('trends.prices.subtitle')}
        provenance={`${FRONT_FILE} :: ${CATEGORY_FIELD}`}
        info={[t('trends.prices.rule')]}
        note={[
          t('trends.prices.window', { positions: count(lang, block.positions) }),
          t('trends.prices.without', { rows: count(lang, block.rows_without_a_unit_price) }),
          // the rows whose page prints no price at all: counted on the block that drops them,
          // because a population that shrank without a sentence is a claim
          ...(block.excluded.n > 0
            ? [t('trends.prices.excluded', { rows: count(lang, block.excluded.n) })]
            : []),
        ].join(' · ')}
        table={{
          head: [
            t('trends.prices.col.category'),
            t('trends.prices.col.unit'),
            t('common.rows'),
            t('trends.prices.col.min'),
            t('trends.prices.median'),
            t('trends.prices.col.max'),
            t('trends.prices.cheapest'),
            t('trends.prices.dearest'),
          ],
          rows: cards.map((card) => [
            card.category.name,
            card.basis === undefined ? t('common.absent') : unitWord(card.basis.unit),
            card.basis?.n ?? 0,
            card.basis?.min ?? '',
            card.basis?.median ?? '',
            card.basis?.max ?? '',
            card.basis === undefined ? '' : cardTitle(card.basis.cheapest),
            card.basis === undefined ? '' : cardTitle(card.basis.dearest),
          ]),
        }}
      >
        <div className="cards">
          {cards.map((card) => (
            <article
              key={`${card.category.category}:${card.basis?.unit ?? 'none'}`}
              className="card tile"
            >
              <h3>
                {card.category.name}
                {card.basis !== undefined && (
                  <span className="badge">{unitWord(card.basis.unit)}</span>
                )}
              </h3>
              {card.basis === undefined ? (
                <>
                  <p className="figure">{t('common.absent')}</p>
                  <p className="context">
                    {t('trends.prices.count', {
                      priced: count(lang, 0),
                      positions: count(lang, card.category.positions),
                    })}
                  </p>
                </>
              ) : (
                <>
                  <p className="figure">
                    {card.basis.median === null
                      ? t('common.absent')
                      : perUnit(card.basis.median, card.basis.unit)}
                  </p>
                  <p className="context">
                    {t('trends.prices.median')} ·{' '}
                    {t('trends.prices.count', {
                      priced: count(lang, card.basis.n),
                      positions: count(lang, card.category.positions),
                    })}
                  </p>
                  {card.category.is_group_key === true && (
                    <p className="muted">{t('trends.prices.group_hint')}</p>
                  )}
                  {end(card.basis.cheapest, card.basis.unit, t('trends.prices.cheapest'))}
                  {end(card.basis.dearest, card.basis.unit, t('trends.prices.dearest'))}
                </>
              )}
            </article>
          ))}
        </div>
      </ChartCard>

      {opened !== null && (
        <Lightbox
          t={t}
          title={opened.title}
          pages={opened.pages}
          start={0}
          urlOf={(name) => pageUrl(media, name)}
          onClose={() => setOpened(null)}
        />
      )}
    </>
  )
}

/** The table view's one-cell name for an end: the brand and what it is, nothing computed. */
function cardTitle(card: PriceCard): string {
  return card.line === undefined ? card.brand : `${card.brand} · ${card.line}`
}

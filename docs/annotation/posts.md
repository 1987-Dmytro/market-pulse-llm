# Annotation guideline — retailer posts (T2)

Task T2 of `docs/SPEC.md` §4: category relevance, post type and brand mentions for
posts from retail-chain and aggregator channels. Labels from this guideline feed
gates G1d (relevance + 3-class) and G1e (brand extraction).

Examples are verbatim from `data/raw/posts/`, left in the original UA/RU.

## Unit

One post = one row. An album is one post: its items were collapsed at collection, and
the caption of whichever item carried one is the text you see. Judge the text only —
you cannot see the images, and neither will the model at training time. A post whose
text is empty is not in the batch.

## Schema

Every row in `data/annotation/posts_batch.jsonl` carries the record fields (`id`,
`source_id`, `channel`, `msg_id`, `date`, `language`, `text`, `has_media`,
`reply_count`) plus the empty label fields:

| field | values |
|---|---|
| `relevant` | `true` \| `false` — does the post concern the tracked category |
| `post_type` | `"launch"` \| `"promo"` \| `"other"` |
| `brands` | list of `{"brand_id": <watchlist id or null>, "mention": "<as written>"}` |
| `unclear` | `true` \| `false` — excluded from every gate |
| `annotator` | your initials |
| `notes` | free text |

Label `post_type` and `brands` for every post, including irrelevant ones — the model
learns the three classes on the full stream, and relevance is a separate head.

## relevant

`true` when the post mentions, promotes or announces a product in a tracked group of
`config/registry.yaml` → `taxonomy.tracked_groups`:

- **dairy** — milk, kefir/ryazhanka, yogurt, curd and сирки, sour cream, butter,
  cheese, dairy desserts, plant-based analogs;
- **ice-cream** — any format.

One qualifying product in a list of many is enough:
`🔸 Ікра імітована зі смаком кети ТМ Caps Food 🔸 Морозиво 100% ТМ Рудь` → `true`
(the ice cream qualifies, the imitation caviar does not).

`false` for everything else — beer, household goods, McDonald's news in an aggregator
channel, channel housekeeping.

Borderline calls, decided once here:

- **Dairy as an ingredient** in a prepared dish (pizza with cheese, cheesecake,
  pampushky with a cream filling) → `false`. The tracked category is the dairy product
  on the shelf, not every recipe containing it.
- **Plant-based analogs** (oat/soy/almond drinks, vegan cheese) → `true`, the taxonomy
  lists them explicitly.
- **Eggs, mayonnaise, margarine, condensed milk, cheese-flavoured snacks** → `false`.
  They live next to dairy in the store, not in the taxonomy.
- **A generic mention with no product** (`знижки на молочку до 30%`) → `true`, group
  named, no brand.

## post_type

**`launch`** — first-time announcement of a NEW product, flavour, format or collection
in the channel. The claim must be about the product being new, not about its price:
`Дві новинки, які точно варті дегустації: 🔸 Peach Sunrise Berliner Weisse — ніжний
смак стиглого персика` → `launch` (and `relevant: false`, it is beer).

Not a launch:

- a repeated promo of something announced earlier — `re-promo`, label `promo`;
- a returning seasonal item (`Курочка повертається в МакДональдз`) → `promo`,
  a return is not a first appearance;
- a discount on an item merely described as new → `promo` wins when the post's
  subject is the price.

When both apply (a new product introduced *with* an opening discount), `launch` wins:
the announcement is the event, the discount is its packaging.

**`promo`** — discounts, price offers, giveaways, loyalty campaigns:
`❄️Цими морозними грудневими днями... знижки на улюблені продукти. Тільки з 12 по 18
грудня 2024 року: 🧈масло солодковершкове «Галичина» «Селянське» 72,6%` → `promo`,
`relevant: true`.

**`other`** — everything else: recipes, holidays, channel news, service notices,
polls. `За останній час у нас тут багато новеньких! Привіт-привіт, вітаємо в
корисно-вигідно-подарунковому каналі VARUS` → `other`, `relevant: false`.

## brands

Extract every brand mentioned **as the maker of a product in the tracked category**.
Brands of non-tracked products in the same post are not extracted — in the caviar +
ice cream example above, only `Рудь` is.

For each mention record what is written and, when it matches, the watchlist id:

```json
{"brand_id": "rud", "mention": "Рудь"}
{"brand_id": null, "mention": "Звени гора"}
```

- `brand_id` comes from `config/registry.yaml` → `watchlist`, matched against
  `display_names` in either UA or RU spelling. Match on meaning, not on characters:
  `Яготинское` → `yagotynske`.
- A dairy brand outside the watchlist still gets a row with `brand_id: null` and the
  mention as written. The watchlist prioritises, it never filters (SPEC §3).
- `ТМ X` markers, quotes and «» are stripped from the mention: `масло ТМ «Галичина»`
  → `Галичина`.
- **Private labels** count as brands: `Премія` (`premia`), `Своя Лінія`
  (`svoia-liniia`), `Varto` (`varto`). A bare chain name used as a product brand
  (`Морозиво VARUS`) → `varus-pl`; the same chain name used as the shop
  (`у магазинах VARUS`) is **not** a brand mention.
- The same brand named twice in one post → one entry.
- No qualifying brand → `brands: []`. This is the common case, including for relevant
  posts that only name a category.

## Decision rules for the cases that repeat

**Aggregator posts about other retailers.** `@msuaaaa` covers АТБ, Сільпо, METRO and
fast food alike. Label them exactly like chain posts — the source is provenance, not a
label.

**Multi-product promo lists.** Many posts are bullet lists of unrelated products. One
tracked item makes the post relevant; extract only the tracked items' brands.

**Post text without the offer.** Some captions describe a mood and leave the offer to
the image (`Вітаємо з першим днем канікул... об'їдатися кавуном і морозивом`). Label
what the text supports: ice cream is named, so `relevant: true`, `post_type: other`,
`brands: []`.

**Reposts and near-duplicates.** Chains repost the same weekly promo. Label each
occurrence identically; do not skip rows.

**Undecidable** — truncated text, a link with no description, a language you cannot
read → `unclear: true`.

## Quality control

Same rule as the comment guideline: self-agreement ≥ 90% on a re-labelled random 100
rows (SPEC §8). Relevance is the cheapest place to lose agreement — when a borderline
call takes more than a few seconds, write the rule into this file instead of deciding
it twice differently.

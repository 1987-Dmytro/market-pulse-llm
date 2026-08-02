# Annotation guideline — comments (T1)

> **Guideline v2 changelog — 2026-08-02** (`docs/SPEC.md` amendment 3.8). One field changes:
> `intents` gains a sixth class, **`service`**. `sentiment`, `sarcasm` and `unclear` are
> untouched, and so is every rule about them. What moved:
>
> - **§intents** — the `service` bullet; the `availability` boundary (the product, not the
>   process around it); and the promo-mechanic rule, which sent those rows to `[]` in v1 and
>   sends them to `service` now. Co-occurrence with a product intent is allowed.
> - **§sarcasm** — two of the five examples are giveaway comments that carried `[]` and
>   `["availability"]`; both are `["service"]` under v2. The second was wrong under v1 too:
>   a draw nobody won is not a product missing from a shelf.
> - **Decision rules** — "Off-topic replies" becomes a `service` rule instead of an `[]` rule;
>   a new giveaway rule; bot `+` spam stays `unclear: true` and is never `service`.
>
> **Why:** the blind audit (4.5a) had the operator rule 22 of 40 agreed `intents` rows wrong.
> His review found the old law right where it was challenged — 17 of the 19 disputed `[]` rows
> stand — and the *taxonomy* one class short: a reaction to the retailer as a service had
> nowhere to go but `[]`. v1 stays readable in git history.

Task T1 of `docs/SPEC.md` §4: sentiment, sarcasm and intents for comments collected
under retailer and aggregator posts. Labels from this guideline train the model and
feed gates G1a–G1c, so the rules below are the definition of those numbers.

Examples are verbatim from `data/raw/comments/`, left in the original UA/RU — do not
translate them, and do not fix their spelling. The few illustrations marked
*(constructed)* are shapes to recognise, not corpus strings.

## Unit

One comment = one row = one label set. Judge the comment on its own text, plus the
parent post only when the comment is meaningless without it (`Так`, `+`, *(constructed)*
`А коли?`). Never label from the thread's mood or from other comments.

The parent post is the row with `msg_id == parent_msg_id` in
`data/raw/posts/<channel>.jsonl` — the same channel as the comment. Every parent is
there, because comments were collected from the threads of stored posts.

## Schema

Every row in `data/annotation/comments_batch.jsonl` carries the record fields
(`id`, `source_id`, `channel`, `msg_id`, `parent_msg_id`, `date`, `language`, `text`)
plus the empty label fields to fill:

| field | values |
|---|---|
| `sentiment` | `"positive"` \| `"negative"` \| `"neutral"` |
| `sarcasm` | `true` \| `false` |
| `intents` | subset of `["taste","price","packaging","quality","availability","service"]`, may be empty |
| `unclear` | `true` \| `false` — excluded from every gate |
| `annotator` | your initials |
| `notes` | free text, only where the call was hard |

Fill `sentiment`, `sarcasm` and `intents` even when `unclear` is `true`, if you can —
the row is excluded from scoring either way, and the values still help error analysis.

## sentiment

The attitude the author expresses **towards the product, the price or the retailer**,
not their mood.

- `positive` — praise, thanks, satisfaction: `Блинчики, как всегда, отменные ❤️`
- `negative` — complaint, disappointment, accusation: `Макарони по 84.9грн, знижки в магазині немає`
- `neutral` — question, factual statement, request without an evaluation:
  `Цікавить ця кава. Як дізнатися наявність у магазинах?`

**Sarcasm outranks the surface wording**: the label is what the author *means*. A
sarcastic compliment is `negative`.

Mixed praise and complaint in one comment (`Дякую за відповідь, але ви виправили
ціну...`) → label the dominant one; if neither dominates, `neutral` plus a note.

## sarcasm

`sarcasm: true` when the literal reading contradicts the intended one — irony,
mock praise, bitter exaggeration. It is a flag, not a sentiment: a comment can be
`negative` + `sarcasm: true`, or `negative` + `sarcasm: false`.

Five real examples, all `sarcasm: true`:

1. `мабуть смачні млинці по 300-400 грн за кг.... таке враження, що вони не з муки, а з золота...`
   → `negative`, intents `["price"]`. Mock praise plus a price exaggeration.
2. `Знову виграв працівник компанії або хтось із їхньої родини👍`
   → `negative`, intents `["service"]`. The 👍 contradicts the accusation; the accusation is
   about how the draw is run.
3. `Софія,ми знову в прольоті,як фанера над Парижем😃😃😃`
   → `negative`, intents `["service"]`. Smileys carry resignation, not joy. The comment is under
   a giveaway post — nothing here is missing from a shelf.
4. `Это по "Акции" а до "акции" было 932 за килограмм 😂😂😂`
   → `negative`, intents `["price"]`. Quotation marks around the promo word are the marker.
5. `Перевіряю і в не одному немає, як завжди акція є товару немає`
   → `negative`, intents `["availability","price"]`. `як завжди` frames it as a recurring farce.

Counter-example — the same `как всегда` marker, no sarcasm:
`Блинчики, как всегда, отменные ❤️` → `positive`, `sarcasm: false`, intents `["taste"]`.

Emoji alone never decide. 😂 and 👍 appear in sincere comments as often as in sarcastic
ones; the contradiction must be in the text.

If you hesitate about sarcasm but the sentiment is clear, label the sentiment and set
`sarcasm: false` with a note. G1b is scored on a curated slice, so a missed flag costs
less than an invented one.

## intents

Multi-label, empty allowed. What the comment is *about*:

- `taste` — flavour, smell, texture: `Виглядають дуже смачно, поживно і корисно`
- `price` — cost, discount, promo value:
  `Чому в телеграм каналі ціна одна в додатку інша , а в магазині ще інша ?`
- `packaging` — package, volume, label, portion: `4- шт это и есть сто грамм 😂`
- `quality` — freshness, spoilage, composition, production: `В магазині Варус продається неякісний цукор`
- `availability` — presence in a store, stock, delivery of the product:
  `Перевіряю і в не одному немає`
- `service` — interaction with the retailer as a service: in-store and online service, the
  delivery process, the app and the checkout, the support hotline, staff, and how promos and
  giveaways are organised — mechanics, fairness, communication:
  `А головне що оператори на сайті варуса навіть не знали що е такий розіграш😂😂😂`

The first five are about the **product**; `service` is about the **retailer**. A comment can
carry several (`акція є товару немає` = `price` + `availability`) or none (`Дякую`), and a
product intent and `service` can be true at once — label both:
`Хотіла вчора купити шашлик "Кавказький", який зараз в акції,  але мені відмовили!!! Сказали в нашому магазині такої акції немає!😡 м.Кривий Ріг, вул. М.Світальського, 15`
= `price` + `service`. The promo is what she came for; being turned away at the shop is how the
retailer served her. The shashlik itself was there, so `availability` is not the label.

`availability` stays about the **product** — whether it is in the shop, in stock, or delivered at
all. The process around the order is `service`: a slot moved, a courier, an order that cannot be
cancelled.

`price` covers what the buyer pays. A question or a complaint about a *promo mechanic* — how a
discount is applied, whether a giveaway is fair, what the terms say — is `service`, not `price`:
`Підкажіть, будь ласка, як працює ця акція? Вона автоматично розраховується на касі коли скануєш додаток?`
(v1 sent these rows to `[]`.)

What still takes no intent: bare thanks (`Дякую за відповідь`), emoji-only rows, and jokes or
banter about neither the product nor the retailer (`А говорят мужиков в Украине мало уже 🤣`).

## Decision rules for the cases that repeat

**Price complaint phrased as a joke.** Label the meaning, not the register:
`negative`, `sarcasm: true`, `intents: ["price"]`. The joke is the delivery, the
complaint is the content. See example 1.

**Emoji-only comments.** `👍`, `❤️`, `😂😂😂` with no words: sentiment from the emoji
where it is unambiguous (`👍` `❤️` → `positive`), `intents: []`, `sarcasm: false`.
Ambiguous or mixed emoji (`🤦🤣🤣`, `🥲`) → `unclear: true`.

**Bot spam and giveaway noise.** `+`, `++++++`, `➕` — participation markers under
giveaway posts, the single most repeated string in the corpus. Always
`unclear: true`, `sentiment: neutral`, `intents: []`. They are not reactions — a ticket into a
draw says nothing about how the draw is run, so it is never `service`.

**Giveaways: the reaction, not the ticket.** Distrust of a draw, an accusation that it is rigged,
a complaint that the rules or the winners were never communicated → `service`:
`В Варусі роблю закупи з моменту його відкриття, через день! Гроші там зоставляю бешенні!!! НІКОЛИ НІЧОГО ЗА ЦІ РОКИ НЕ ВИГРАЛА! НЕ ВІРЮ в ці розіграші!`

**Service complaints with no product in them.** App failures, delivery slots, loyalty points,
the queue at the till: `Вже добу чекаю на доставку і знову перенесли на обід завтра`. These are
real reactions to the retailer: label `sentiment` normally, `intents: ["service"]`,
`unclear: false`. (v1 gave these rows `intents: []`.)
A reply aimed at another commenter rather than at the retailer (`Дурнів багато. Хто
хоче той і купує`) → `unclear: true`.

**Retailer's own replies.** The chains answer in their own comment threads:
`Дякуємо за ваш запит. Наші плани включають відкриття магазинів...`,
`Вже біжимо до вас у приватні повідомлення`. These are corporate support voice, not
consumer reaction — always `unclear: true`. Training on them would teach the model
that PR phrasing is customer sentiment. They are recognisable by the plural
`Дякуємо/Розуміємо/Передамо` and the 🧡 house style.

**Duplicates.** The same text appears many times (`+` 51×, boilerplate replies 13×).
Label each occurrence the same way; do not skip rows.

**Language other than UA/RU/EN**, or unreadable text → `unclear: true`.

## Quality control

SPEC §8 gates the label set on **self-agreement ≥ 90%**: re-label a random 100 rows
after a break, without looking at the first pass, and compare. Below 90%, the
guideline is the problem — fix the rule here first, then re-label, and say so in the
dataset card.

`unclear` rows are excluded from the gates, so they cost nothing but the time to mark
them. Prefer `unclear` over a guess; do not use it to avoid a decision you can make.

---
type: decision
status: accepted
date: 2026-08-08
tags: [decision, phase5, yield, taxonomy, discovery]
---

# 5c1 — the relevance floor: 66 channels were admitted without anyone measuring the category

The operator's question is what exposed the gap, and it is worth quoting in its own shape: the
registry had grown from 4 sources to 67 through a gate battery of four instruments, and **not one
of them had ever asked whether a channel contains the tracked category**. `entry_check` grades
capability — does it resolve, is it alive, is it a broadcast channel, does its group admit us.
`language_census_5c1` grades language. `market_screen_5c1` grades which market it sells into.
`theme_screen_5c1` grades "is this about food at all". A channel could pass all four while never
mentioning milk.

SPEC **amendment 3.12** (approved 2026-08-08) closes it in two halves: (1) the track-R entry gate
gains a mandatory relevance floor, the **yield screen**, run retroactively over the whole
registry, and (2) discovery becomes content-first. This record is the first half's execution and
the second half's price list.

## (1) The bars, and the order they were written in

`results/yield_bars_5c1.preregistration.json`, sha256 `1aa89818…`, committed in `0259939` —
**before** `scripts/yield_screen_5c1.py` existed in the tree:

| bar | value | currency |
|---|---|---|
| A | 4 relevant posts per 28 days | posts |
| B | 10 comments under relevant posts per 28 days | comments |

Ruled by the operator on 2026-08-08, in `docs/PROMPT-5c1-yield.md`, which is itself committed in
`e6926ca` before any yield number existed. Posts and comments are separate currencies and are
never blended into one: retail_official earns on posts, the audience segments earn on comments.
The script's constants are checked against that file on every run and the record cites its sha256
— the language-census discipline.

Ordering recorded honestly rather than smoothed over: the executor DID look at four channels'
relevance counts before the pre-registration file was committed — the four positive controls,
probed to find out whether the control was measurable at all. The bars are the operator's and did
not move. What the probe did inform is the WINDOW rule for those four (below), and the probe's
answer was that @atb_market_official reads 0 under both candidate rules, so no rule choice could
rescue the control.

## (2) What the screen measured — `results/yield_screen_5c1.json`, 66 sources, $0, offline

| | |
|---|---|
| cleared bar A | 29 |
| cleared bar B | 8 |
| below both | 36 |
| `verdicts_reportable` | **false** |

Per audience, `below_both` against `n`: health_fitness **14 / 17** · regional 9 / 17 · baby_food
6 / 8 · supermarket_deals 3 / 4 · mothers_kids 3 / 5 · retail_official 1 / 7 · cooking_recipes
**0 / 7** · food_quality 0 / 1.

The shape of that table is the finding. The segments the composition spent the whole phase
recruiting — health_fitness (17 channels) and the mothers/baby pair (13) — are where the taxonomy
is thinnest, and the recipe feeds nobody argued about clear bar A seven for seven.

## (3) The screen refuses to report, and the reason is a real measurement

The pre-registered positive control is the four original registry channels: if the instrument
cannot find the tracked category in the channels the project was BUILT on, no verdict it produces
about an unknown channel is worth reading. Three cleared. **@atb_market_official did not.**

In its own 28 days АТБ posted 25 times, **19 of them image-only**, and none of the six texted
posts names dairy, ice cream or a watchlist brand: Fairy dish soap, card-holder discounts,
own-label promos. The same instrument reads the same channel fine over a longer horizon — across
its whole 777-post store it finds the tracked category **34 times** («Хочете більше морозива?»,
«Печиво "Своя Лінія" з ароматом молока»). So the zero belongs to the window, not to the matcher,
and the refusal is the pre-registered rule firing rather than a bug.

That is also a finding about АТБ and not only about the screen: the project's anchor retail
channel publishes its assortment **inside images**. The registry already excludes two channels as
TEXT-FREE — «on topic and unreadable» (@ATB_FANatik, @discountua1) — and this says the biggest
chain in the country is the same shape in this window. Every row therefore carries
`posts.with_text` / `posts.without_text` beside its bar, because "off-category" and "unreadable"
are different operator rulings.

## (4) The terms the passes hang on — the screen's own headline

Neither instrument is law here: the lexicon ships `status: draft-not-law` and the watchlist is the
operator's list. So nothing was patched. What the record does instead is refuse to let a term hide
inside a total — every count breaks down to the term that produced it, each with one quoted line,
and each row carries `bar_A_sole_carriers`: strike one term at a time, does the row still clear?

| term | posts | channels | what it actually matched |
|---|---|---|---|
| `dairy:сир` | 318 | 27 | «🧀м'які сири» — real |
| `dairy:масл` | 138 | 20 | real, and «🔹Денис Маслов — міністр юстиції» |
| `brand:varto` | **89** | **24** | «Про що варто пам'ятати» — the ordinary Ukrainian adverb |
| `brand:varus-pl` | 56 | 1 | real, on Varus's own channel |
| `brand:president` | **33** | 8 | «Президент України Володимир Зеленський» |
| `brand:ferma` | 8 | 6 | «ферма морських коників» |

`варто` is АТБ's private label AND the word "it is worth"; it fires on more posts than any other
brand on the list, including Varus's own name on its own channel. Two rows clear bar A on an
ordinary word alone:
**@polyakova_fitness** on `brand:varto`, **@myrhorodtown** on `brand:president`. The pass list of
29 cannot be read as 29 channels that carry the category, and now it does not have to be taken on
trust — the operator can read the line each one fired on.

This is the third instance of the same class in the phase: a new kind of source meets an old term
list. There is no stop-word fix, and one is not attempted here.

## (5) The four originals are screened over their own 28 days

Amendment 3.12 says "a channel's **collected** 28-day window". The four originals' store is the
pinned raw v1 corpus (`results/raw_v1_baseline.sha256`), collected before `collect_5c1.json`'s
`since` existed and stopping 2026-07-23…27 — so the shared window covers 13 to 17 of their days
against everyone else's 28, while bar A counts absolutely. They are screened over their own last
28 days, every row says which rule it got, and because that rule is favourable to them the
shared-window reading is published beside each one:

| channel | own 28 d | shared window |
|---|---|---|
| @atb_market_official | 0 → FAIL | 0 → FAIL |
| @silposilpo | 11 → PASS | 7 → PASS |
| @VARUS_channel | 65 → PASS | 41 → PASS |
| @msuaaaa | 6 → PASS | **3 → FAIL** |

## (6) The 08.08 acceptance rulings

- **@dikankaa EXCLUDED** — `ru 1.00 on 20 decidable posts + RF oblasts in the channel's own
  description; UA-only policy`. The census reading is in `results/language_census_5c1_day2.json`
  (ua 0 / ru 20 of 30 posts); the RF geography is in the window too («По Волгоградской области
  ( Энгельс, Саратов тоже можем )», 2026-08-01). The channel's description is in NO artifact this
  repo holds — the gate stores a title, never a bio — and the removal comment says so. Registry
  **67 → 66**.
- **Three RF_FLAGs KEPT**, per-row ruling `war-news-explained (Wildberries warehouse strike
  report)` written onto the rows of `results/market_screen_5c1_day2.json` by a `--close` that
  re-measures nothing. All three are one story: Ukrainian drones hit a Wildberries hub, and the
  screen's `retailer` and `location` patterns read a war report as a market fact.
- **Four closed-group flags, option 1** — "the flag concerns a capability the assigned bucket does
  not use" (@gorishnie_plavni1, @zinkivnews, @tvorcha_matusyua, @educationwithloven).
  @KarlivkaLive carries the identical flag and is deliberately not in the four: it was ruled
  separately as «Дозаявка №9».
- **@KarlivkaLive, option 2** — the broadcast analogue instead of the supergroup. Already
  executed on day 2: gated 2026-08-08 10:48 (FLAG, cleared), in the registry, window collected
  (12 posts). Its yield row: 11 posts in window, **0 relevant**, below both bars.

## (7) Watchlist +3, and what a revision does to history

`zarih` (Заріг / Зарог) · `myrhorodska-korivka` (Миргородська корівка / Миргородская коровка) ·
`yahotynske-dlia-ditei` (Яготинське для дітей / Яготинское для детей). UA is the canon everywhere
operator-facing; the RU spellings are matching aliases only. In `config/registry.yaml` and
`docs/WATCHLIST.md`, in the same edit.

The third one arrived with a trap: its display name **contains** «Яготинське», so the shipped
matcher credits the parent brand with every mention of the child. The operator tracks them
separately (the Мгарське pattern), so the yield screen resolves the nesting — longest span wins —
and a test pins both the nesting and the shipped matcher's behaviour, since the two now differ by
exactly that case.

**G1e history is never re-scored on this revision.** The yield record names the registry's sha256
(`c82d0cff…`) so any future run's provenance says which watchlist it read.

## (8) Discovery: the price list, measured before anything was spent

Amendment 3.12 (2), and the numbers come from a **free** `checkSearchPostsFlood` probe on
2026-08-08 ~09:00 UTC that left the quota untouched at 10/10 (STATUS, amendment 3.12 block):

| item | price | note |
|---|---|---|
| Telegram Premium | €5.99 / month | must sit on the ACCOUNT behind `marketpulse.session` (id 1658562597, `premium: True`) |
| full-text queries | **10 / day free** | `channels.searchPosts`, live since 2025-07-31 |
| beyond the quota | **10 Stars ≈ €0.20** per query | returned by the API itself, before the first paid query |
| session cap | ≤ $5 in Stars | each discovery session individually authorised |
| TGStat | **ruled OUT** | an RF service, RUB payment |
| Telemetr.io free tier | permitted | catalog fallback |

Consequence, already computed: a pass of the brand lexicon (~20–25 queries, +3 for the new
brands) costs **$0 spread over two to three days**, or ~€2–3 in Stars in one day. The tempo is the
operator's choice in the discovery contract, which is a separate future session — nothing here
spends a Star.

## What this does not decide

Nothing entered or left the registry on the yield screen. Zero-yield members are surfaced with
their numbers; removal is an operator ruling. The registry diff of day 2 stays **PROVISIONAL**
until the operator reads `results/yield_screen_5c1.json` and signs — and the screen says
`verdicts_reportable: false`, so the first thing to rule on is whether an anchor channel that
publishes in images invalidates the exam, or is the exam working.

Related: [[5c1-day2-composition-and-search]]

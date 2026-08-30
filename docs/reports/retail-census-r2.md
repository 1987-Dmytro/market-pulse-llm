# retail-census r2+r3 (C1) — official chain channels, and what the Poltava chats actually carry, $0

**Which chains have an official Telegram we can collect, and where are comments open? — every one of the 36 rows was read; 17 of 36 rows have a channel and 7 of those have comments open.** The operator's ruling narrows what «comments» means: only threads under PRICE posts count, the rest is noise. Under that filter the collected corpus holds **4 718 comments in 678 price threads**, and they sit in two places — `msuaaaa` (3 407) and `@VARUS_channel` (1 210). **Varus is the only CHAIN with dairy in its posts and live comments under them.** Full 36 rows `results/retail_chains_table.md` · working set by purpose `results/working_set.md` · record `results/retail_chains.json` · promo-thread yield `results/promo_comment_yield.json` · brand probe `results/poltava_brand_probe.json` · category B `results/poltava_chats_b.md`.

| chain | channel | subs | n | price | comments | com/day | dairy | what it is |
|---|---|--:|--:|--:|---|--:|--:|---|
| **Varus** | @VARUS_channel | 121086 | 134 | 0.246 | **open** | 16.643 | **0.194** | the one chain source of promo reactions |
| Маркетопт | +Ejz6ubzm21IyMTQy | 42378 | 29 | 0.276 | closed | — | **0.241** | JOINED; prices are in the flyer IMAGES |
| Епіцентр | @epicentrk_sale | 52081 | 137 | 0.657 | closed | — | 0.051 | seed handle, not linked by the chain |
| ЕКО маркет | @ekomarket_shop | 1341 | 17 | **0.882** | closed | — | 0.412 | deepest promo of any chain |
| АТБ | @atb_market_official | 41858 | 31 | 0.000 | closed | — | 0.000 | official and CORPORATE — no promo at all |
| Фора | @foraINFO | 7506 | 10 | 0.600 | closed | — | 0.200 | found only inside the site's JS bundle |
| Сільпо | @silposilpo | 19714 | 33 | 0.212 | closed | — | 0.152 | |
| Близенько | @blyzenkoua | 4985 | 57 | 0.351 | closed | — | 0.018 | the chain's own, NOT linked from its site |
| METRO | @HRCNc | 3359 | 26 | 0.000 | open | 0.071 | 0.231 | «HoReCaНець» — B2B, ~2 comments a month |

**Block 1 — retail.** ATB's own channel exists (41 858 subs, reached via atbmarket.com → its official Instagram) and carries **no promo and no comments**; ATB's promo with comments open is unofficial — `@ATB_FANatik` at **0.25 comments/day**, about seven a month, a footnote and not a second source. Novus and Ашан have no channel at all: site links a bot, official Instagram links nothing, checked twice each. **19 rows have no channel** — 6 link a bot and nothing else, 7 were read and carry no `t.me`, 1 links another brand of its own group, 3 have no verifiable site, 2 aggregators screened out. For 16 of the 17 the deliverable is PRICES, not voice — and Маркетопт's and Епіцентр's prices live in flyer images, which is the 5c2 vision instrument's job, not the text matcher's.

**Block 2 — the Poltava chats: coverage is up, and the brand premise does not hold.** 61 chats across **21 of 24 district centres** after the operator lifted the language bar (language is a column now). The three still empty are three different states: Чутове found nothing at any bar; Диканька and Козельщина have chats that resolve, are OPEN and carry ZERO messages in 28 days — they exist and are silent, which no budget fixes. **The probe then read 4 507 messages from the four liveliest chats and found ZERO real dairy-brand mentions.** The watchlist fired four times and all four were false positives, hand-read: «третій **президент** України» and three job ads for «**Ферма** клубники» (Dv898). The 61 chats project **2.6 dairy-CATEGORY messages a day, ~78 a month** for the whole oblast, before any brand filter. Independently: across the 16 324 comments already in `data/raw/` the watchlist is named 228 times, **198 of them `varus-pl` inside Varus's own channel**, and **Гармонія 0** — reproducing SPEC v2 §0's own ≈40/0 from a different direction (Dv899).

**What this asks of the team lead.** These chats are classifieds and job boards: they carry CATEGORY voice, not BRAND voice. Whether ~78 category messages a month is worth collecting is a ruling, not an executor's call, and it is worth taking BEFORE the remaining **81 candidates** are scanned — they are the same kind of chat and the marginal yield will be the same. One thing the probe did not test: whether people discuss dairy without naming a brand («взяла молоко в АТБ, кисле»), which the category lexicon catches and the watchlist never will.

**Evidence.** Step 0 — `pytest tests/test_hooks.py -q` → `2 passed`, guard v2 refusing 16 spellings and accepting 10; the D1 witness green at HEAD from `cd7df0e`. Step 1 — four instruments, because the positive control showed curl alone rediscovering **1 of r1's 6 known handles**. Step 2 — **40 of 40**, the contract's cap, spent. Step 3 (operator-authorised, own ceiling) — 41 of 80. Probe — 52 of 60. Every budget counted by wrapping the client, min gap 3.0 s, no FloodWait; one join, the one the operator ordered, logged in `results/joins_5c1.jsonl` and reversible.

**Deviations Dv880–Dv899** (`implementation-notes.md`). The ones that move a number: a candidate costs 4–13 requests, not the contract's one history each (Dv881); `entry_check.PAUSE_SECONDS` is 2.0 against a 3 s floor (Dv882); site-reading and name-search are complementary, and treating one as the replacement hid Близенько's own channel (Dv892); the watchlist over-reports on a classifieds corpus (Dv898).

```
$ make check
FAILED tests/test_repair_phase4_ledger.py::test_the_silence_check_fires_on_the_LINE_ledger_too
1 failed, 4129 passed, 2 skipped in 671.58s (0:11:11)
```
The one red is the r3 ledger debt, not caused here; `make check` had 2 at session start and step 0 closed the other.

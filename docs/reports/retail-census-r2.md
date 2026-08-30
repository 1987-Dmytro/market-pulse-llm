# retail-census-r2 (C1) — official chain channels, read off the chains' own sites, $0

**Which Ukrainian retail chains and promo aggregators have an official Telegram channel we can collect, and where are comments open? — every one of the 36 rows was read; 13 of 36 rows have a channel and 7 of those have comments open. Three of the 7 also carry dairy, but METRO's `@HRCNc` resolves to «HoReCaНець», its B2B HoReCa channel, and Копійочка's .011 is an aggregator on r1's older clock — so the one consumer-facing chain channel with dairy AND live comments is Varus** (16.643 comments/day against METRO's 0.071). Full 36 rows `results/retail_chains_table.md` · record `results/retail_chains.json` · category B, r1's 47 Poltava chats, NOT re-measured, `results/poltava_chats_b.md`.

| chain | channel | subs | n | price | comments | com/day | dairy | lang |
|---|---|--:|--:|--:|---|--:|--:|---|
| **Varus** | @VARUS_channel | 121086 | 134 | 0.246 | **open** | 16.643 | **0.194** | ua 0.83 |
| METRO · B2B | @HRCNc «HoReCaНець» | 3359 | 26 | 0.000 | **open** | 0.071 | 0.231 | ua 1.00 |
| Сім23 | @sim23_simi | 5266 | 17 | 0.176 | **open** | 0.607 | 0.000 | ua 1.00 |
| Rozetka · marketplace | @rrozetka | 369535 | 167 | 0.521 | **open** | 304.429 | 0.000 | ua 0.99 |
| ЕКО маркет | @ekomarket_shop | 1341 | 17 | 0.882 | closed | 0.000 | 0.412 | ua 1.00 |
| Фора | @foraINFO | 7506 | 10 | 0.600 | closed | 0.000 | 0.200 | ua 1.00 |
| Сільпо | @silposilpo | 19714 | 33 | 0.212 | closed | 0.000 | 0.152 | ua 1.00 |
| Fozzy · cash&carry | @fozzyshopua | 518 | 11 | 0.182 | closed | 0.000 | 0.091 | ua 1.00 |

A resolved title is not the brand on the site: `@HRCNc` is METRO's HoReCa arm, `@fozzyshopua` is «FOZZY Cash&Сarry», `@rrozetka` is the marketplace and not its grocery vertical. `n` is the posts a share was computed over — ЕКО's .882 and Фора's .600 rest on 17 and 10 posts. Таврія В's channel is invite-only (`ChatInvitePeek`, «🔴 ТАВРІЯ В | Мережа супермаркетів»): its history needs a join, so it is `unmeasured`, not zero.

Aggregators, on r1's 27.08 clock, marked as such in the table: @znishkom price .762 n=168 open · @kop1chat 22.071 msgs/day (a group, so that column is messages) · @xochydeshevshe price 1.000 **over n=10** · @brovarysale closed. «MSUa» and «Skidka» have NO Ukrainian channel — r1's name search returned Moscow State University and Kazan, and the Ukraine screen (`ua >= 0.5`, r1's own bar) rejects them. Every r2 row keeps: its handle came off the chain's own verified site, which is why r1's 54 `ua 0.00` rows cannot recur. **23 rows have no channel** — 7 link a bot and nothing else, 9 were read and carry no `t.me`, 1 links another brand of its own group (Delikat's site offers only Bloom, its florist), 4 have no verifiable site, 2 aggregators screened out. **Nothing is left unread: `blocked`, `shell` and `dns` are all zero.** Of the four without a site the record says why, because «not found» hides very different things: **Барвінок stopped existing** (sold 2015, bought by ATB 2016, every store rebranded — which is why r1 found an ОСББ of that name); **Маркетопт is a live Poltava chain with no website at all** (Instagram @marketopt, Facebook @marketopt.official), so no footer can answer it; **Толока** matches no retail chain in any source — the word is Ukrainian for a community work-day; **Гурман** is an Instagram-only shop in Південне, and `gurman.ua` is a domain-for-sale page.

**Evidence.** Step 0 — `pytest tests/test_hooks.py -q` → `2 passed`: guard v2 refuses 16 spellings of the sweep (bare `ruff format` among them), accepts 10 targeted forms; the D1 witness `test_the_registration_rebuilds_except_where_step_0_moved_a_pin PASSED` is green at HEAD from `cd7df0e`. Step 1 — `scripts/retail_sites.py`, four instruments, because the positive control showed curl alone rediscovering **1 of r1's 6 known handles**: `curl` · `curl+bundle` (`@foraINFO` exists only inside Фора's JS) · `browser` (`@silposilpo`, `@HRCNc`, `@rrozetka`, and thrash.ua and zakaz.ua on the second pass) · web discovery for the names whose contract domain was dead. Step 2 — `scripts/retail_resolve_r2.py`: **40 of 40** MTProto requests, counted by wrapping the client, minimum gap **3.0 s**, derived from the rows' own `checked_at`, no joins.

**Deviations Dv880–Dv891** (`implementation-notes.md`). Moving a number: a candidate costs 4–9 requests, not one history each — r1's code kept so the columns compare (Dv881); `entry_check.PAUSE_SECONDS` is 2.0 against a 3 s floor (Dv882); `entry.suggest` answers a failed resolve with r1's discredited name search, disabled and counted at 0 (Dv883); four readings were written down before they were true and are now tested both ways (Dv888, Dv889); and a `t.me` link in a footer turned out not to prove whose channel it is (Dv890). Dv885 — two rows unread — is CLOSED by this pass (Dv891).

```
$ make check
FAILED tests/test_repair_phase4_ledger.py::test_the_silence_check_fires_on_the_LINE_ledger_too
1 failed, 4122 passed, 2 skipped in 670.56s (0:11:10)
```
The one red is the r3 ledger debt, not caused here. `make check` had **2** reds at session start (`25b9931`: 2 failed, 4101 passed); step 0 closed the other (`test_think_zero_shot`) and the pass count went 4102 → 4122 — this contract's 20 tests across four new files.

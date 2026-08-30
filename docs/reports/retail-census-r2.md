# retail-census-r2 (C1) — official chain channels, read off the chains' own sites, $0

**Which Ukrainian retail chains and promo aggregators have an official Telegram channel we can collect, and where are comments open? — 13 of 36 rows have a channel; 7 of those have comments open; 3 of those 7 also carry dairy (METRO .231, Varus .194, Копійочка .011), and only Varus carries dairy with comment traffic worth reading — 16.643/day against METRO's 0.071.** Six chains link a Telegram BOT and no channel (АТБ, Novus, Auchan, Велмарт, Рукавичка, Копійка): for them the answer is «no channel to collect», not «not found». Full 36 rows `results/retail_chains_table.md` · record `results/retail_chains.json` · category B, r1's 47 Poltava chats, NOT re-measured, `results/poltava_chats_b.md`.

| chain | channel | subs | n | price | comments | com/day | dairy | lang |
|---|---|--:|--:|--:|---|--:|--:|---|
| **Varus** | @VARUS_channel | 121086 | 134 | 0.246 | **open** | 16.643 | **0.194** | ua 0.83 |
| METRO | @HRCNc | 3359 | 26 | 0.000 | **open** | 0.071 | 0.231 | ua 1.00 |
| Сім23 | @sim23_simi | 5266 | 17 | 0.176 | **open** | 0.607 | 0.000 | ua 1.00 |
| Rozetka | @rrozetka | 369535 | 167 | 0.521 | **open** | 304.429 | 0.000 | ua 0.99 |
| ЕКО маркет | @ekomarket_shop | 1341 | 17 | 0.882 | closed | 0.000 | 0.412 | ua 1.00 |
| Фора | @foraINFO | 7506 | 10 | 0.600 | closed | 0.000 | 0.200 | ua 1.00 |
| Сільпо | @silposilpo | 19714 | 33 | 0.212 | closed | 0.000 | 0.152 | ua 1.00 |
| Fozzy | @fozzyshopua | 518 | 11 | 0.182 | closed | 0.000 | 0.091 | ua 1.00 |

`n` is the posts a share was computed over: ЕКО's price .882 and Фора's .600 rest on 17 and 10 posts. Таврія В's own channel is invite-only (`ChatInvitePeek`, title «🔴 ТАВРІЯ В | Мережа супермаркетів») — its history needs a join, so it is `unmeasured`, not zero.

Aggregators, from r1's window ending 27.08 — a different clock, marked as such in the table: @znishkom price .762 n=168 open · @kop1chat 22.071 msgs/day (a group, so that column is messages) · @xochydeshevshe price 1.000 **over n=10** · @brovarysale closed. «MSUa» and «Skidka» have NO Ukrainian channel: r1's name search returned Moscow State University and Kazan, and the Ukraine screen (`ua >= 0.5`, r1's own bar) rejects them. Every r2 row keeps — its handle came off the chain's own verified site, which is why r1's 54 `ua 0.00` rows cannot recur here. **23 rows have no channel**: 8 site READ and carrying no `t.me` (two instruments each), 6 bot-only, 2 sites never read (`zakaz.ua` Cloudflare + Chrome domain permission, `thrash.ua` a JS shell), 2 domains that do not resolve, 3 names with no verifiable site, 2 aggregators screened out.

**Evidence.** Step 0 — `pytest tests/test_hooks.py -q` → `2 passed`: guard v2 refuses 16 spellings of the sweep (bare `ruff format` among them) and accepts 10 targeted forms; the D1 witness `test_the_registration_rebuilds_except_where_step_0_moved_a_pin PASSED` is green at HEAD from `cd7df0e`. Step 1 — `scripts/retail_sites.py`, three instruments because one is not enough: the positive control showed curl alone rediscovering **1 of r1's 6 known handles**, `@foraINFO` exists only inside Фора's JS bundle, and `@silposilpo`/`@HRCNc`/`@rrozetka` only in a browser past Cloudflare. Step 2 — `scripts/retail_resolve_r2.py`: **40 of 40** MTProto requests, counted by wrapping the client, minimum gap **3.0 s measured**, no joins.

**Deviations Dv880–Dv888** (`implementation-notes.md`). The ones that move a number: a candidate costs 4–9 requests, not the contract's one history each — r1's code kept so the columns still compare (Dv881); `entry_check.PAUSE_SECONDS` is 2.0 against the contract's 3 s floor (Dv882); `entry.suggest` answers a failed resolve with r1's own discredited name search, disabled here and counted at 0 (Dv883); three readings were written down before they were true — a support phone read as a group invite, a domain-squatter's parking page read as Гурман's site, a null title on `ChatInvitePeek` — each now tested both ways (Dv888). The contract's ≤40-row table and `/report`'s ≤30 lines do not both fit, so the 36 rows are a linked file and this report carries the ones that answer the question (Dv887).

```
$ make check
FAILED tests/test_repair_phase4_ledger.py::test_the_silence_check_fires_on_the_LINE_ledger_too
1 failed, 4117 passed, 2 skipped in 705.24s (0:11:45)
```
The one red is the r3 ledger debt, not caused here. `make check` had **2** reds at session start (`25b9931`: 2 failed, 4101 passed); step 0 closed the other (`test_think_zero_shot`) and the pass count went 4102 → 4117 — the 15 tests this contract added, across three new files.

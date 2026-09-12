# PROGRESS — ship-1 (ruling 03.09 (e): the executor's one file — done / next / open stop, ≤60 lines)

## Done — 12.09 s51 «design-pass» ($0, PHASE-ship-1 §2 item 7, ruling (vv)): the approved look on the accepted app
Start ritual: no team-lead file modified or new, so none was committed by path first. Commits `f783af4` (producer), `a44cad6`
(app), `a1bdb46` (screens). **Dark is the DEFAULT**: `index.html` carries `data-theme="dark"` so the FIRST PAINT is dark and
`rememberedTheme()` answers dark when nothing is stored — the system preference no longer picks it; toggle, light theme and
`?theme=system` unchanged. §11's tonality is in the tokens (deeper page under a lit card, ONE soft shadow in dark, `--sp-*` =
§3's scale ×1.25), written from ONE string into both dark blocks, so the toggle and the system query cannot drift.
**The photos** (`export_front_data.py`, +199/-6): `media`, joined out of `results/post_media_*.json :: entries[].images[]`
(by GLOB, not the five that exist today) into `screen.positions[].evidence` on `(channel, msg_id)` — **402 pages · 11 flyer
sets · 25 rows with no photo**, read from the RECORDS and never from the disk, so a clone writes the same export: two runs
byte-identical, sha256 `aaf9f792…`, and beside `media` the diff moves only `sources`. `--stage` copies exactly `media.files`
into `dashboard/app/media/` and REPORTS **referenced 402 · staged 402 · missing 0 · 90.9 MB** into `data/manifest.json` (a size for `firebase deploy` to know);
pointed at a tree with no photos it stages 0, refuses nothing and writes nothing — measured, so `make front` stays green on
the clone `e2e-ship` runs. **The screen** carries §11's grammar (chips, four counted-up cards, «Свіжі
листівки» one card per chain with the real cover, a 40 px photo per row, the price large, the printed badge as a bar, one
`<dialog>` lightbox for both, «фото немає» where a file did not arrive) and **the four animations**: count-up ≤600 ms in
script; lift 200 ms (measured: `translateY(-4px)` + `--lift` on the hovered card, `0` on its neighbours); reveal 30 ms/step
capped at 20 over 100 rows; crossfade 200 ms.
**Якість**: `promoTabs(mode)` builds the nav and `servedOnly(path, mode)` answers the route from ONE rule — measured in both
builds: static shows four promo tabs and answers `#/promo/quality` with «вкладка живе на сервері», no `0.2333` anywhere on
the page; served shows five and the tab is unchanged (0.2333 · 0.9524). **Checks:** `make front` green · `npm run check` clean
· `npx vitest run` **21 passed** (19 + the two the check names) · no console message from the app (all 33 were the MetaMask
extension) · four screens in `docs/reports/screens/` · `make check` GREEN: ruff clean, **4340 passed / 2 skipped** in five
slices whose union is PROVEN equal to `ls tests/test_*.py` (231 files, no gap, no overlap, asserted before a slice ran);
735+1005+803+956+841 = 4340 = s48's count — this item adds no pytest. **$0; no cloud call this session.**

## Ten defects fixed before the commit — five measured in the browser, five from a read-only review (27 findings, 8
verified adversarially); each is named in full in `a44cad6` / `f783af4`. The two the review CONFIRMED both changed what the
screen SAYS: «без фото» now states what the join established («без фото: 25 з 1 301 — жоден запис медіа не містить знімка
для цих дописів»), and a photo-less checkout paints «фото немає» (`onError` in row, card and lightbox) — not 402 broken images.

## Next — «front-2» ($0, §2 item 8: the command centre T0–T8). Then «e2e-ship» → the gate.

## Open stop — NONE. Cloud empty: no pod, endpoint or volume; cycle-3 $8.8398 of $10.00, REMAINING $1.1602. $0 this session.

## Deviations (each a §4.2 fork: the simplest reading that keeps every number on its file)
- §11 says «`positions[].media`»; the positions are rows of `promo_screen_data.json`, which this producer must not rewrite (its
  sha is read by tests), so the field arrives as `media.pages`, keyed by the row's own `(channel, msg_id)`. §11's «old price
  struck through» is NOT rendered: no file carries `price_old`, and a promo price beside an arithmetic depth returns the old
  price to the kopiyka (SPEC 3.21 (4)) — the tab's own sentence says so already, and it stays.
- «CURRENT week» is per CHAIN — the newest week that chain has pages in — because the newest over ALL chains is Маркетопт's
  alone (W36) while the grammar asks one card per chain; each card prints its own dates (W33…W36 over the eleven), and a set's
  pages are the ones a position was read off, not the whole issue, so the card counts «N стор. з позиціями». A row's photo opens
  THAT page; a card walks its set. Screenshots are NEW files; front-1's four stay as its own report's evidence.
- `prefers-reduced-motion` was NOT toggled at the OS level — no devtools media emulation here. Measured instead: the rule is live
  in the CSSOM (`* { transition: none; animation: none }`, both `!important`), with its declarations applied every reveal is at
  rest and every card opaque, and the count-up asks the query itself, in script, where no stylesheet reaches.

## Named, not built (the phase file forbids adding what it did not ask for)
- **A served page can come up as the STATIC build**: one cold load did, seconds after `make serve` started, while `/api/status`
  answered 200 in 43 ms — `load.ts`'s 1 s guard is the only path to that null, and the latched mode re-points BOTH exports at
  `./data/` (the last BUILD's copy) instead of live `results/` via `/api/exports/`: the screen then reads a stale file and says
  nothing. Not reproduced in three further loads; §11's gate makes it visible. A fix changes DESIGN §2's boot contract — named.
- `status.money.from` names `sessions[-1]` for a block whose `cap_usd` is a ROOT key; and the two id spaces (`rollup`/
  `depth_by_chain_and_brand` key on a CHANNEL, `positions[].chain.id` on a folded id) — both ruled to front-2 planning by
  (uu) 6. The English `from`/`note` sentences still render verbatim in the UA UI. Carried from s48: the S1 loss is in `product`.
- Carried: no test for `loop_daemon.py`, `promote_signals.py`, `thread_population`, the gate's third state; `promote_signals.py`
  never clears its output dir; the fold map has no guard ((pp) 2(a)); `spend_promo_c3.json` says `"tolerance": 0.05` where the
  FLOOR closed it; `promo_projection_c2.json` not reproducible; no test asserts `cap_from`/`{leg}`/`{STEP}-s4`, `graded()`'s rows.

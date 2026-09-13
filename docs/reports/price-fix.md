# price-fix — the eight misread rows are page-true on the screen, and nothing else moved

**Question (PHASE-ship-1 §2, ruling (yy) option (c)):** the reading found eight rows on six pages
whose figure the leaflet page contradicts, and the defect is the model's, not the pipeline's — does
the screen now publish what the page prints, without a corridor, a re-read, or a moved population?

**Answer: yes, on six corrections and two exclusions, at $0.** `config/price_corrections.yaml`
carries the eight entries a human verified; `export_front_data.page_true()` applies them ONCE,
between the screen export and every block that shows a price. `results/front_data.json` (sha256
`5a6f5750…`, byte-identical over two runs) moves three blocks and no others: `category_prices`,
`regions`, `sources`. The four evidence cards the operator was shown are page-true — йогурти
cheapest 12.2571 → 49.75, сир твердий dearest 4993.3333 → 1247.92, морозиво dearest 2006.6667 →
1073.913, сир кисломолочний cheapest 100.0 → 162.5714 — and the eight rows land exactly on the
readings: 122.8286 (×3) · 499.3333 · 200.6667 · 345.3333, plus the two rows off pages that print no
price. The window stays 311 positions with 8 rows carrying no unit price; the two excluded rows are
counted, not dropped: the block prints «вилучено 2: сторінка без ціни». No threshold, no corridor,
no re-read; `promo_screen_data.json`, `grade_positions_50.json` and every sealed record untouched.

## The category table, before → after (`results/front_data.json :: category_prices`, both readings from the file)

| категорія × одиниця | n | min | median | max |
|---|---|---|---|---|
| Морозиво ₴/кг | 95 | 106.0 | **299.0 → 287.0** | **2006.6667 → 1073.913** |
| Сир твердий ₴/кг | 62 | 253.3333 | 390.4216 | **4993.3333 → 1247.92** |
| Йогурти ₴/кг | 39 | **12.2571 → 49.75** | **99.6429 → 103.4783** | 213.6364 |
| Сир кисломолочний та сирки ₴/кг | **23 → 22** | **100.0 → 162.5714** | 298.3333 | 766.6667 |
| Молочні десерти ₴/кг | 18 | 113.0 | 160.7692 | 277.7222 |
| Сметана ₴/кг | 15 | 69.75 | 134.8649 | 399.9714 |
| Масло ₴/кг | 13 | 277.2222 | 366.1111 | 474.375 |
| Молоко ₴/кг | 13 | 40.6484 | 48.1609 | 177.25 |
| Кефір та ряжанка ₴/кг | 6 | 45.7647 | 54.7543 | 71.1905 |
| Молочні продукти ₴/л | **7 → 6** | 53.9 | 379.6667 | 569.5 |
| Молочні продукти ₴/кг | 6 | 133.8 | 199.9714 | 503.96 |
| Морозиво ₴/л | 4 | 94.5 | 106.0 | 210.0 |
| Рослинні аналоги молочних продуктів ₴/л | 2 | 135.99 | 135.99 | 135.99 |

Nine of the thirteen bases do not move at all; the two `n` that move are the two exclusions, one in
each of their categories. The moved numbers are published here per (dd), never silently.

## Evidence

- `PYTHONPATH=src python3.11 scripts/export_front_data.py` twice → `5a6f5750be0053bc…` both times,
  `git status --porcelain results` empty after the second (`media` referenced 402 · staged 402 ·
  missing 0 — the gallery did not move).
- `pytest tests/test_export_front_data.py -q` → 1 passed. Both ways in one test: the correction
  lands on its ONE row with `was`, `page` and `verified_by` and reaches `position_card`; the twin
  row of a repeated `row_id` (the id names two products) is untouched; a record naming a row the
  data lacks raises `SystemExit` naming `config/price_corrections.yaml`. Negative control run
  by hand: with `page_true` replaced by the identity, the test reds.
- `python3.11 scripts/read_price_plausibility.py` → **13 of 303 priced rows**, unchanged: the
  accepted diagnostic reads the screen export, so ruling (yy)'s own number still reproduces.
- `env -u NODE_ENV make front` → green; `npm run check` (tsc) clean; `npx vitest run` 21/21.
- Own browser, served at `localhost:8000`: Позиції UA — the Полтавщина АТБ card reads «ice-cream ·
  750 г · 150,50 грн −41% · 200,67 грн/кг» and its ⓘ opens complete («виправлено вручну за
  сторінкою листівки» · «було: 75 г → 750 г» · «сторінку прочитали: reader-1, reader-2» ·
  `config/price_corrections.yaml :: atb_market_official_4767.jpg`); Тренди UA — «…311 позицій ·
  без ціни за одиницю: 8 … · вилучено 2: сторінка без ціни»; EN the same. No console error
  from the app.
- Corroboration found in the data, not assumed: on BOTH copies of the same leaflet tile the model
  wrote row `:1` = сендвіч 75 г at 25.90 and row `:2` at 150.50 — the readers' verdict (the 150⁵⁰
  tag is the 750 г tub's, the сендвіч's own tag is 25⁹⁰) is what the two pages already say twice.

## Deviations

- `Dv1 [cause: contract-gap]` — `verified_by` names the readers of THAT page, so `team-lead` stands
  on the two pages ruling (yy) 1 says the team lead opened, not on all eight. The check's list is
  the template; claiming a reading nobody made would be the defect the record exists to close.
- `Dv2 [cause: spec-gap]` — the one test landed in `tests/test_export_front_data.py`, the file
  «data-shape» is authorized to land. Only this item's test is in it; data-shape's three named
  cases are NOT written here.
- `Dv3 [cause: verify-gap]` — one CSS rule beyond the item: inside a card at the page's right edge
  the new ⓘ opened off-screen, and a provenance that cannot be read is the defect the ⓘ exists to
  close. `.sku .popover`/`.extreme .popover` open leftwards; measured both ways in the browser.

## Debts (named, not built — all mine to carry into planning, none fixed here)

- The Позиції **table** reads `promo_screen_data.json` directly (DESIGN §7), so it still shows
  4,29 ₴ for the three Млековіта rows while the price cards show the page-true figure. Correcting
  that export would move a K10-pinned committed artifact — a §4.1 stop, not this item's.
- `@ATB_FANatik:4657:1` and `:2` become identical rows (Хрещатик, 75 г, 25.90) once `:2` carries
  its page-true price: one offer counted twice in морозиво ₴/кг n=95. Same class as the page+post
  double count (yy) 5 ruled POST-GATE; de-duplicating moves a published population.
- `media.flyers[].positions` still counts the two excluded rows: the gallery joins pages, not
  figures, and the cover in the page population is POST-GATE.
- The regional cut drops an excluded row from its cards; **no excluded row falls in the cut this
  week (0)**, so nothing is printed there and no count was added.

`make check` on `f655e9f` (one run, backgrounded to a log): `ruff check .` → **All checks passed!**;
`pytest -q` → **4341 passed, 2 skipped in 728.82s (0:12:08)**, exit 0 — the tree's 4340 plus this
item's one test. Stop 2's four guard families were re-run separately BEFORE the item's commits, at
`5ce9499`: **156 passed**; their evidence on the final tree is this full run, which carries them.
Money: **$0**; cloud `[]`; REMAINING $1.1602 unmoved; nothing was created anywhere.

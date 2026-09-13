# DATASETS — what this repository collects, derives and ships

Written for the operator's future models (price forecasting, competitor promo prediction). Three
layers, one line per dataset: its KEY · its WEEK · the PROVENANCE columns that say where a row came
from · the model that would read it. `data/**` is gitignored and local; `results/**` and `config/**`
are committed. Nothing here is typed by hand: every figure is written by the script named beside it.

## The week, once, for every layer

A row's week is the ISO week of its own MESSAGE date — `market_pulse.trends.iso_week`, the one
spelling. A post's date comes from the raw store; a leaflet page IS a message with its own `msg_id`,
so its date lives in `results/post_media_*.json` and nowhere else (`export_front_data.media_index`).
A message no record dates is COUNTED and dropped, never bucketed: an unknown week is not a week.

## 1. Raw — what Telegram gave us (collector output, one file per channel)

| dataset | key | week | provenance | read by |
|---|---|---|---|---|
| `data/raw/posts/<channel>.jsonl` (archive, 75 ch.) · `data/raw_r2/posts/` (live, 18) | `(channel, msg_id)` | `date` | `record_type`, `source_id`, `provenance`, `grouped_id`, `has_media` | every week join; post-text price rows |
| `data/raw/comments/`, `comments_v2/`, `data/raw_r2/comments/` | `(channel, msg_id)`, thread `parent_msg_id` | `date` | as above + `sender_anon_id` (anonymised author) | comment labelling (Gemma-4 + QLoRA adapter) |

## 2. Derived — what a model already read (one record per answer, never edited)

| dataset | key | week | provenance | read by |
|---|---|---|---|---|
| `data/derived{,_w2}/leaflet_pages/`, `position_rows/`, `post_position_rows/`, `post_texts/`, `inferences/` | `(channel, msg_id)` + `ordinal` / `row_id` | joined, none stored | `at`, `task`, `prompt_sha256`, `model_revision`, `served_by`, `image_sha256`, `rendering` | re-scoring a reading without paying for it again |
| `data/derived/pulse.db` — the aggregate layer (`scripts/build_aggregates.py`) | `positions(window_id, carrier, row_id)`; the promo tables are keyed by `uuid5` over the row's own fields | **none** — joined at query time | `window_id`, `channel`, `msg_id`, `tier`, `carrier`, `presence_*` | the screen, the trends, the rollup |
| `results/weekly/positions_<ISO-week>.jsonl` (`scripts/weekly_positions.py`, every `make tick`) — **committed**, so a tick that collects a new week dirties `results/` until the operator commits it | `(carrier, row_id)` inside the file | **`week`**, on every row | `window_id`, `channel`, `msg_id`, `row_id`, `carrier`, `tier`, `presence_*`, `price_qualifier` | **price forecasting · competitor promo prediction** |

**Why the weekly files exist.** The store is REBUILT, not extended: a second
`build_aggregates.py` into the same path unlinks the database and backs a freshly built one over it,
so it holds exactly the windows the run's own record files describe (measured — a planted window and
a sentinel table do not survive). Week N+1's collection would leave week N nowhere on disk. The
weekly files are written from the store's own rows, one per ISO week; a week a later run no longer
carries is left exactly where it is, and a week it does carry is rewritten from the store.
Today: **1 301 rows, 10 weeks, 2026-W27 … 2026-W36**, every row dated.

They live in `results/weekly/`, which git carries (ruling (ccc) 4, 13.09). Their first home was
`data/derived/weekly/`, beside the store and gitignored, and the claim that stood here — that the
ten weeks were still reconstructible on a clean clone — is TOO STRONG, measured: the committed
`results/promo_screen_data.json` and `results/post_media_*.json` restore each row's identity, its
week and 15 of its 28 columns (some under other names), and **13 of them nothing committed carries**
— `price_old` · `pack_count` · `price_qualifier` · `discount_footnote` ·
`depth_disagrees_with_printed` · the five `presence_*` · `brand_raw` · `ordinal` · `window_id`.
Those live in `data/derived/`, which no clone has. A history for a model has to survive the laptop
it was collected on, so it is committed as it is written.

Fields are the store's, so the figures are the MODEL's reading: `price_promo`, `price_old`, `depth`,
`discount_pct_printed`, `size_value`/`size_unit`/`pack_count` (a unit price is
`price_promo / (size_value × pack_count) × 1000`), `brand_id`, `category`, `line`. The extraction's
own completeness bar is RED (0.2333, `results/grade_positions_50.json`) — a model trained here is
trained on a reading with holes, and the six hand-verified corrections of
`config/price_corrections.yaml` (identity `(row_id, carrier)`) are an overlay the weekly files do
NOT carry: they are applied at export time, by `export_front_data.page_true()`.

## 3. Exports — what ships (committed, the app and the README read nothing else)

| dataset | key | week | provenance | read by |
|---|---|---|---|---|
| `results/promo_screen_data.json` (`make tick`) | `screen.positions[].row_id` + `carrier` (1 301 rows) | `screen.weeks`, `screen.rollup[].week` | `windows[]` with anchors, `not_collected`, `evidence.channel/msg_id` | the promo screen; the front export's own source |
| `results/front_data.json` (`make front`, $0) | as above, page-true (1 299 + 2 excluded) | `reporting_week`, `media.flyers[].week` | every block carries `from` (file :: path) and `reading` (the rule in words) | the React app — it formats, filters and links, and computes no figure |
| `results/dashboard_data_w1.json` | window 1's command centre | w1 only | sealed, byte-pinned | T0–T8 by reference |
| `results/grade_*.json` | the graded set's own ids | the set's window | the gold file, the grader, the bar | S1/S2 quality, published as measured |

## 4. Labelled and frozen (never rewritten, never grown)

`docs/labels-positions-50.jsonl` (180 gold position rows over the 46-page draw of
`results/positions_draw_50.json`; 44 of those pages carry a row — the S1 bar) ·
`docs/labels-*.jsonl` (comment gold) · `data/frozen/comments_{train,test}*.jsonl` and
`posts_{train,test}*.jsonl` (the comment model's frozen splits) · `data/annotation/**` (the
annotation rounds that produced them). A frozen set is a RECORD: it is re-read, never re-cut.

## Not a dataset

`data/derived/pulse.db` (rebuilt in a second; holds no fact its inputs lack) ·
`dashboard/app/data/**` (a staged copy of the two exports, with a manifest of their shas) ·
`results/promo_tick.json` (the tick's own clock, untracked).

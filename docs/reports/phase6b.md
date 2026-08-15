# phase6b — the command centre: nine tabs, one figure source, rows under every number

**Contract:** `docs/PROMPT-phase6b.md` · **Design authority:** `docs/PLAN-phase6-command-center.md`
§3 §7 §11 · SPEC block `amendment-3.20` · **Class:** $0, build script + one artifact
**Baseline:** `make check` 2 370 passed / 2 skipped @ `bc71d0d` → **2 392 passed / 2 skipped**
**Spend:** $0.00 · no GPU, no network, no collection · `data/loop_cursor.json` unchanged
(`9b59aa5f…` before and after) · not one byte moved under `results/`.

---

## 0. Step 0 — the tail

`ac1d840` commits the standing vault tail and this contract's prompt, staged by path. Live
`git status` at the start held exactly four entries and all four went in:

```
 M knowledge/daily_logs/2026-08-15.md
 M knowledge/hot.md
 M knowledge/index.md
?? docs/PROMPT-phase6b.md
```

The expected list in the contract named the three vault files; `docs/PROMPT-phase6b.md` is the
untracked fourth, and `git add -A` was never used — a queued prompt file claims its own bytes.

---

## 1. The deliverable

`scripts/build_dashboard.py` → `dashboard/index.html`, one self-contained file: inline CSS, inline
JS, inline SVG, no external request of any kind, UA/EN and light/dark both switchable, nine tabs
T0–T8, and the export embedded byte for byte so the page can be audited without the repository.

| | |
|---|---|
| `dashboard/index.html` | `c526b3211f7c7304…`, 502 765 bytes |
| `scripts/build_dashboard.py` | `1c694758749bcebf…`, 82 618 bytes |
| `config/ui_strings.yaml` | `650aa1064ca2eaac…`, 31 934 bytes |
| drill-down expanders | 27, carrying 196 drawn rows and 196 t.me links |

### 1.1 The honesty seam, as built

**Python at build time** reads `results/dashboard_data_w1.json`, `config/metrics.yaml` and
`config/ui_strings.yaml`, and computes every string, number, percent and SVG coordinate. **JS at
view time** switches tabs, switches language, switches theme, shows and hides the tooltip and sorts
the table. It never touches the embedded record: `export-data`, `JSON.parse`, `toFixed` and
`parseFloat` appear nowhere in the script, `Number(` appears twice — both inside the sort
comparator — and the one `Math.max` clamps a tooltip to the viewport, not a figure. Both languages
of every label and tooltip are in the document before the script loads.

### 1.2 Where a figure may come from — and the two stub classes

A digit reaches the page from the export, or from an arithmetic derivation of the export's own
values made in the build where a test can see it (a per-segment NSR out of the segment's
sentiment counts; a share of a column's maximum for a micro-bar's width). Nothing is recomputed
from rows. Where the export has no figure the surface renders a stub — and there are **two kinds,
deliberately not merged**:

* **The export's own** `NOT_COMPUTABLE` entries — seven, each with the reason and the unlock
  condition the export carries. They answer «this cannot be computed yet».
* **`GAPS`** — four surfaces this contract names for which the aggregate layer emits no field at
  all. They answer «6a never exported this», carry the field that would fill them, and render with
  their own border and their own words. **This list is 6a's backlog** (§4), and folding it into the
  first class would have buried a debt inside a passing test. **Dv342.**

### 1.3 The drill-down: the rows under a figure are that figure's rows

Rows come through the ONE reader — `scripts/window_summary_5c2.py`'s reading path, the same one
`scripts/build_aggregates.py` imports — and every file it opens is checked against the export's own
`provenance` sha before a line of it is parsed: `config/registry.yaml`,
`results/prereg_5c2_run.json` and all 38 evidence files. A page showing rows from evidence the
figures were not built on would be worse than a page with no rows.

Each of the 27 expanders **declares the export field that holds its population size**, and the
build refuses when the rows it found do not number what the export says:

```
drill-down `t2_price`: the store holds 553 rows and
`metrics.aspect_share.by_sample.payable.labels.price` says 554 — the sample under a figure must be
drawn from the population that figure was computed over. Stop and report.
```

That refusal is the seam of the whole page and it has a test with a poisoned export. Every one of
the 27 populations agreed on the first build, including the six per-brand ones whose count is
`cuts.brand_by_sentiment.rows.<brand>` summed over its sentiments.

The draw is seeded **per expander** — `random.Random(f"42:{key}")`, never one generator across
strata (`.claude/rules/registrations-and-draws.md`, Dv323) — ≤10 rows, and each expander names its
population: «ціна · 10 з 553, seed 42». The test measures the drawn RANKS, not the ids: every wide
expander draws ten distinct ranks inside its own population, no two expanders draw the same rank
vector, and no rank is shared by all of them.

### 1.4 D4 — `config/ui_strings.yaml`

Every rendered chrome string with `ua` and `en`; the build refuses on a missing key or a missing
language rather than rendering an empty span (negative control in the tests, both ways). No digits:
the only ones that survive the check are citations — a law by its number, the gate range G1a–G1e,
`sha256`, and the ordinal «вікна-2» — and the pattern that recognises them is deliberately tight,
so a bare decimal like a median matches nothing and reddens. Each key allowed to cite is enumerated
with its reason, so a new exemption cannot arrive unseen.

No duplication with `config/metrics.yaml`: the test compares the two files, and it **caught two
real collisions** — T5's section heading «Глибина знижки / Promo depth» and T4's column head
«Промо-тиск / Promo pressure» were second homes for names the dictionary already owns. Both now
render the metric's own name from the dictionary.

---

## 2. What is on each tab

| tab | PRODUCT.md question | what it renders |
|---|---|---|
| **T0** | owner's screen | 6 KPI tiles (value · beside · context · Δ-slot · status), three code-generated insights, the trend stub |
| **T1** | q1 | diverging sentiment by sample and by brand, the sarcasm badge, SoV in one hue, four expanders |
| **T2** | q2 | aspect bars in one hue, the no-aspect count, the price-origin note, six expanders, two gap stubs |
| **T3** | q5 | eight registry cards in three states, per-card NSR mini-bar, the `retail_official` reading, eight expanders |
| **T4** | q3 | 23 brands, sortable, micro-bars for SoV / NSR / promo pressure, the private-label gap stub |
| **T5** | q7 | depth as two quartile bands, promo pressure by chain and by brand, the leaflet stub, two expanders |
| **T6** | q4 | the category-layer and sidecar stubs |
| **T7** | q6 | the watermarked alert mock, the baseline and trend stubs |
| **T8** | — | glossary, the data layer's gates, provenance manifest, honest limits, all seven stubs |

Four points where the contract and the data met each other:

* **T0 carries no trend and no arrow.** The Δ slot on every tile reads «з вікна-2», which is the
  export's `trend_vs_previous_window` stub said in one line. The status slot reads «порогу не
  зареєстровано» on all six: no threshold is registered for any of these metrics anywhere, and
  inventing one on the screen an owner reads in ten seconds would have been a bar with no
  producer. **Dv348.**
* **T3 renders eight cards in three states** — talked · evidence but no conversation
  (`regional`) · silent (`food_quality`, zero rows, `registry_channels: 1`). A rate over no rows
  renders «не вимірюється», never `0.0`. This is 6a's Dv341 arriving on a screen: the export made
  the eighth card possible and the page shows it.
* **T5 keys all four chains** the amendment names, each with its carrier, and the test greps
  `@marketopt_promo` out of the SPEC block itself so the producer's list cannot drift from the law
  that put it there.
* **T7's mock is the one non-data surface** and says so on its face, across both languages.

---

## 3. Verify

### 3.1 `make check`

```
2392 passed, 2 skipped in 77.69s (0:01:17)
```

Baseline 2 370 / 2 → **+22 tests** (`tests/test_build_dashboard.py` 17,
`tests/test_ui_strings.py` 5). `ruff check .` and `ruff format --check .` both clean — the
formatter is not part of `make check` and was run separately.

### 3.2 Guard 4 — the poisoned build

`metrics.promo_depth.readings.from_price_pair.median` set to `0.1234` in a copy of the export, both
pages built, every digit-bearing text node compared in document order. The target was chosen
because it surfaces on two screens and anchors NO drill-down population — poisoning an aspect count
would have hit the population check first and masked the result.

```
digit-bearing text nodes      585 (identical count in both builds)
moved                         22
of them, the poisoned figure  2  -> [('42.06%', '12.34%'), ('42.06%', '12.34%')]
of them, the export's own sha 20  (the banner on 9 tabs + footer, ×2 languages)
moved for any other reason    0
```

Changed everywhere it surfaces, nowhere else. The 20 sha nodes are the banner: the export's own
digest is a figure ABOUT the export and moves with it by construction.

### 3.3 Read from the built file

Not printed by the build script — parsed out of `dashboard/index.html` after the suite. UA side
only, for legibility.

**The footer:**

```
вікно 28 днів · якір 2026-08-09 · 2026-07-12 — 2026-08-09 · експорт e93673749b840bfe…
· усі числа зібрані з цього файлу
Жодне число на цій сторінці не введене руками: сторінку зібрано скриптом із файлу експорту,
і сам файл вкладено нижче байт у байт.
```

**The T0 KPI row:**

```
Обсяг ⓘ                                  3 714    beside=1 361 · 159 · 44
    context: поруч: безтекстові коментарі · сторінки листівок · тексти постів
    status : Δ з вікна-2   порогу не зареєстровано
Чиста тональність (NSR) ⓘ                +10.53%  beside=bought +7.70%
Частка негативу з поправкою на сарказм ⓘ 7.35%    beside=7.27% без поправки
Частка голосу (SoV) ⓘ                    7.69%    beside=Гармонія
Глибина промо ⓘ                          42.06%   beside=31.4% – 47.0%
Покриття ⓘ                               28/66    beside=7/8
```

**The `retail_official` card:**

```
Офіційні канали мереж · розмова є · 234 рядків · 242 куплено ·
канали (дали рядок / у реєстрі): 7/7 · NSR -11.11% · 23.1% / 12.0% ·
Топ-аспекти: смак 33 · наявність 28 · сервіс 28 · сарказм: 6.41%
@VARUS_channel · @atb_market_official · @ekomarket_shop · @epicentrk_sale · @forainfo ·
@marketopt_promo · @silposilpo

Мінус тут — функція каналу: скаржаться там, де мережа слухає. Сприйняття брендів живе в
інших сегментах, і переносити цю оцінку на категорію не можна.
```

### 3.4 The other five guards (the contract's numbering; 4 is §3.2 above)

1. **Determinism** — two builds byte-identical (`diff` empty), and the committed
   `dashboard/index.html` IS that build, compared as bytes.
2. **Embedded == committed** — the blob between the script tags equals `results/dashboard_data_w1.json`
   byte for byte, and the export's sha appears in the banner of every tab and in the footer.
3. **No external resources** — no `<script src`, `<link`, `@import`, `@font-face`, `<img`,
   `fetch(`, `XMLHttpRequest`, `WebSocket` or `<iframe>`; every one of the 196 `href`s starts
   `https://t.me/`.
5. **Stub coverage** — seven `NOT_COMPUTABLE` entries each rendered with their unlock, four gap
   stubs, eight segment cards across the three states, four promo chains keyed, the T7 watermark
   present in both languages.
6. **Strings closure** — the set of keys the document asked for equals the set the file declares,
   both directions, and every key carries both languages with matching placeholders.

Plus the palette: `PALETTE` and `RAMP` are compared against a hand-copy of the contract's table,
and both hexes of every role are asserted present in the page. There is no colour validator on this
machine, so a drifted hex must fail in a test instead of shipping unvalidated.

---

## 4. The backlog this contract hands back to 6a

Four surfaces the contract names have no export field. Each renders as a gap stub naming what it
needs; none of them was recomputed or zeroed.

| surface | the field it needs | note |
|---|---|---|
| T2 brand × aspect heatmap | `cuts.brand_by_aspect` | the export crosses neither pair |
| T2 negative profile by aspect | `cuts.aspect_by_sentiment` | same |
| T4 private-label badge | a registry field first | **Dv343** — see below |
| T8 model gates with figures and ceilings | `gates.model` | the export carries the DATA layer's gates only |

A fifth, smaller one, which cost T5 its per-chain drill-down (**Dv344**): the export keys chains by
source id (`promo_pressure.by_chain.marketopt_promo`) and channels by handle
(`cuts.legs.post_text.per_channel.@marketopt_promo`) and carries no join between the two spaces, so
a position row read from the store cannot be resolved to a chain from the export alone.

**Dv343 is not a 6a omission at all.** `docs/PLAN-phase6-command-center.md` §2's data table names
`config/lexicon.yaml` as the home of «watchlist 23 бренда, private-label флаги». That file is the
CATEGORY vocabulary (SPEC 3.17 (8)) and holds no brand. The watchlist lives in
`config/registry.yaml`; `market_pulse.registry.WatchlistBrand` carries `brand_id`, `display_names`
and `own`; and the four chain labels are separated from the competitors by a YAML **comment**.
Nothing in the repository knows which brands are private labels — the fix is a registry field and
an operator's word, not a dashboard heuristic.

---

## 5. What the browser found that a text check did not

The page was opened and driven in a real browser (locally served, no network), which found two
defects no string-level assertion would have:

* **The first sentiment chart was empty.** `metrics.nsr.by_sample.<sample>` holds `negative` /
  `neutral` / `positive` at the TOP of the block, while `cuts.comment_by_segment.*.payable` holds
  them under `sentiment`. One shared helper guessed the shape, and for the metric blocks it read
  zeros — a chart with all bars at zero width, no error, no test failure. The helper now takes the
  counts and the denominator as separate arguments and the docstring says why.
* **A 100 %-negative bar ran through its own label column.** The diverging layout scaled shares to
  the plot width and centred them, so a row whose mass is all on one side reaches half a plot past
  the midpoint. It now scales by the row that reaches furthest, with a gutter for the value labels.

Both are in the deliverable commit. This is the second contract where an artifact-level check
(6a's re-derivation script, 6b's browser) found what the test suite was not shaped to see.

---

## 6. Deviations

**Dv342–Dv352**, in `implementation-notes.md`:

* **Dv342** the two stub classes, kept apart · **Dv343** the private-label flag exists nowhere ·
  **Dv344** no chain↔handle join, so no per-chain drill-down · **Dv345** a comment links to its POST
  (`msg_id` is the discussion group's id space) · **Dv346** one numeric format for both languages
  and the export's English readings quoted untranslated · **Dv347** a value label on every bar of a
  comparison chart · **Dv348** «порогу не зареєстровано» on every status slot · **Dv349** «28 днів»
  rather than «4 тижні» · **Dv350** Гармонія emphasised typographically where the hues are the
  scale · **Dv351** the registry read for aliases and display names, pinned, never for a figure ·
  **Dv352** self-review: a claim the rule never counted, and a blob that could end its own script
  block.

## 7. Process signals

* Opening the artifact in a browser is now a step, not a nicety: it found a silently empty chart and
  a bar drawn through its own labels, and neither had a shape a text assertion would catch.
* Four of eleven deviations are one shape again — the contract names a surface, the export has no
  field. That seam between two contracts is what the backlog table in §4 exists for.
* Dv343 is the keeper: the brief named a file as the home of a flag. Grepping that file before
  writing the note was the difference between «6a forgot to export it» and «nobody has ever
  recorded it».
* The duplication test between the two config files earned its place immediately — two headings
  were already second homes for names the dictionary owns.
* A code-generated insight will happily state something its rule never computed. «Єдиний сегмент»
  was true and guaranteed by nothing; the rule now counts what it claims.

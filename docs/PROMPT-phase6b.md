# PROMPT — phase6b (the command centre: one HTML file, built from the export; $0)

**Contract class:** zero-cost, build script + one artifact. No GPU, no network, no collection, no spend.
**Issued:** 2026-08-15 (team lead). **Baseline:** `make check` 2 370 passed / 2 skipped (6a accepted);
record your starting HEAD in the report.
**Design authority:** `docs/PLAN-phase6-command-center.md` §3 (the nine tabs), §7 (design rules),
§11 (rulings) · SPEC block `amendment-3.20` (the law) · `results/dashboard_data_w1.json` (the ONLY
figure source) · `config/metrics.yaml` (tooltips + glossary).

## Step 0 — tail

Commit the standing vault tail by path (expected: `knowledge/hot.md`,
`knowledge/daily_logs/2026-08-15.md`, `knowledge/index.md` — verify against live `git status`, list
the actuals in the report) and this prompt file.

## Deliverable — `scripts/build_dashboard.py` → `dashboard/index.html` (committed)

One self-contained file: inline CSS, inline JS, inline SVG charts. **Zero external requests** — no
CDN, no webfonts, no remote images; the only `http` hrefs allowed are t.me row links (links, not
resources). System sans everywhere: `system-ui, -apple-system, "Segoe UI", sans-serif`; tabular
figures only where columns align.

**Division of labour (the honesty seam):**
- Python (build time): reads the export + `config/metrics.yaml` + `config/ui_strings.yaml` (new,
  D4) — computes NOTHING from rows. Every displayed string, number, percent and SVG geometry is
  derived from the EXPORT's values at build time, where tests can see it. The export's figures pass
  through; if a surface needs a figure the export lacks → it renders that surface's
  `NOT_COMPUTABLE` stub, never a recomputation and never a zero.
- JS (view time): tabs, UA/EN toggle, light/dark toggle, tooltip show/hide, drill-down expanders,
  table sort. **No arithmetic on data** — tooltip and label texts are prebuilt into data-attributes
  in both languages at build time.

## The visual law (pre-validated palette — do not alter any hex without telling the team lead;
## you have no validator on this machine, so a changed color is an unvalidated color)

CSS custom properties, both modes (media query for OS + `data-theme` toggle that wins both ways):

| role | light | dark |
|---|---|---|
| chart surface | `#fcfcfb` | `#1a1a19` |
| page plane | `#f9f9f7` | `#0d0d0d` |
| primary ink | `#0b0b0b` | `#ffffff` |
| secondary ink | `#52514e` | `#c3c2b7` |
| muted (axis/labels) | `#898781` | `#898781` |
| gridline | `#e1e0d9` | `#2c2c2a` |
| baseline/axis | `#c3c2b7` | `#383835` |
| series-1 blue | `#2a78d6` | `#3987e5` |
| series-2 orange | `#eb6834` | `#d95926` |
| series-3 aqua | `#1baf7a` | `#199e70` |
| diverging pole − | red `#e34948` | `#e66767` |
| diverging midpoint | `#f0efec` | `#383835` |
| status good/warn/serious/critical | `#0ca30c` `#fab219` `#ec835a` `#d03b3b` | same hexes |
| delta-good text | `#006300` | `#0ca30c` |

Sequential ramp (magnitude, one hue, blue): `#cde2fb #9ec5f4 #6da7ec #3987e5 #2a78d6 #1c5cab #104281`
(light→dark; for discrete ordinal marks start no lighter than `#86b6ef` on light / no darker than
`#184f95` on dark).

Rules that are NOT negotiable: one axis per chart, never dual-scale; categorical hues in fixed slot
order, never cycled, and color follows the entity, never its rank; more than 3 series in
scatter-like forms or more than ~7 anywhere → fold to "Other" or use a table; sequential = one hue;
diverging = the pair above with a GRAY midpoint; status colors are reserved for status (always icon
+ label, never color alone); text wears ink tokens, never series colors; thin marks, 4px rounded
data-ends anchored to the baseline, 2px surface gap between adjacent fills and stacked segments;
recessive grid; every multi-series chart carries a legend, ≤4 series also direct-labeled; numbers
never on every point — selective labels only; every chart hover-tooltips (per-mark), hit target
larger than the mark; every tab shows the data window («вікно 4 тижні, якір 09.08» /
"4-week window, anchor 2026-08-09") and the export sha it renders.

## Form per surface (the data's job picks the form)

- **T0:** KPI row of stat tiles (value + context line + status where defined); NO sparklines and NO
  delta arrows in window-1 — the slot renders «з вікна-2» until a second window exists. The three
  code-generated insights (3.20 (4)) each cite their figures. The headline NSR is the PAYABLE
  sample, with bought beside it and the ⓘ explaining why (the 1 361 finding).
- **T1 tonality:** diverging stacked bars centered on neutral (sentiment is an ordered scale);
  Гармонія via EMPHASIS — accent hue for her, de-emphasis gray for context brands; SoV as a
  horizontal bar in ONE sequential hue with its n=11/5 075 sample line visibly beside it.
- **T2 aspects:** horizontal bars, one hue; brand × aspect as a sequential heatmap; the negative
  profile in the diverging pair.
- **T3 segments:** all EIGHT registry cards (the export's three states: talked / evidence-no-talk /
  silent — zeros and nulls render as their own honest labels, never as blank). Per-card NSR as a
  diverging mini-bar. The `retail_official` card carries the reading (D4 strings, no digits):
  «мінус тут — функція каналу: скаржаться там, де мережа слухає; сприйняття брендів живе в інших
  сегментах» + EN twin.
- **T4 competitors:** a TABLE (23 brands > 7 classes) with inline micro-bars for SoV/NSR,
  private-label badge, sortable; zero-mention brands present as zeros (the dimension-table point).
- **T5 promo:** depth as median + quartile band per reading (`from_price_pair` and
  `from_printed_badge` labelled as two instruments); promo pressure by chain — АТБ, Сільпо, Varus,
  Маркетопт all four keyed (3.20 (6)), empty chains as honest stubs naming prep-b; comment-origin
  prices appear ONLY as the price-aspect note (3.20 (5)).
- **T6, T7:** stubs from the export's `NOT_COMPUTABLE` entries — each names its unlock (5c3 /
  window-2); T7 additionally renders the alert-rule preview mock CLEARLY WATERMARKED «макет — не
  дані» / "mock — not data" (the one legal non-data surface, and it must say so on its face).
- **T8 methodology:** glossary rendered from `config/metrics.yaml` (both languages), the provenance
  manifest (which screen ← which export path ← which anchors, with shas from the export's
  provenance block), the gates-of-the-model table (from export/dictionary fields, not typed), and
  the honest-limits list.

## Drill-down — the trust feature

Under every headline figure of T1–T5: an expander with SEED-DRAWN sample rows (seed **42**, recorded
in the build's provenance; never hand-picked). Per row: the original text as collected (UA/RU as
is), the model's verdict fields, channel + segment, and a t.me link where one is honestly derivable
from the row's fields (a leg whose link cannot be built renders none — say so in the report). Cap:
≤10 rows per expander; each expander names its population («10 из 553, seed 42» class — the sitting
pattern 3.18 (6), now in UI). Rows come through the ONE reader (`window_summary_5c2` path) at build
time; the full corpus is never embedded.

## D4 — `config/ui_strings.yaml`

Every rendered chrome string (tab titles, section heads, stub texts, the retail_official reading,
banners, toggles) lives here with `ua` and `en`; the build refuses on a missing key or a missing
language. No digits in strings (the 6a Dv339 law); identities that can go stale point at data
fields instead. Metric names/definitions stay in `config/metrics.yaml` — no duplication between
the two files (test it).

## Guards (tests, in `make check`)

1. **Determinism:** two builds byte-identical; the committed `dashboard/index.html` equals a fresh
   build.
2. **Embedded == committed:** the JSON blob embedded in the HTML is byte-equal to
   `results/dashboard_data_w1.json`, and the page footer carries that file's sha256.
3. **No external resources:** no `<script src=`, `<link href=`, `<img src="http`, no `fetch(` of
   remote URLs, no `@import`; t.me anchors are the only external hrefs.
4. **No hand-typed figures:** every digit-bearing text node in the HTML traces to the export, the
   build's derivations of it, or a `data-` attribute the build wrote — enforce by building with a
   poisoned export (one figure changed) and asserting the rendered HTML changed everywhere that
   figure surfaces and nowhere else.
5. **Coverage of the honest stubs:** all seven `NOT_COMPUTABLE` entries render as stubs; all eight
   segment cards render; all four promo chains keyed; the mock watermark present on T7.
6. **Strings closure:** every rendered string key exists in both languages; no orphan keys.

## DO NOT

- Do not edit team-lead files (`docs/STATUS.md`, `docs/SPEC.md`, `docs/PRODUCT.md`,
  `docs/PROMPT-*.md`, `docs/PLAN-*.md`).
- Do not move a byte under `results/` — the export is READ; a defect found in it is a STOP-and-
  report (the fix belongs to 6a's producer, re-accepted, never patched in the dashboard).
- Do not recompute any aggregate from rows in the dashboard build (rows are read ONLY for the
  drill-down samples, through the one reader); do not put arithmetic on data into JS.
- Do not alter palette hexes or introduce new colors; do not add dependencies (stdlib + what the
  repo already carries); no network at build or view time.
- `data/loop_cursor.json`, `data/raw`, Telegram — untouched. Never `git add -A`.

## Autonomy

Layout free within the visual law and plan §3; where the plan and this contract are silent, match
the export's structure rather than inventing content. Anything requiring a NEW figure → the stub
path, plus a note in the report for 6a's backlog. A surface that would need a palette change or a
new external asset → STOP and report.

## Verify (evidence, not assertions)

`make check` green (baseline 2 370/2 — expect growth); paste the tail. Paste guard-4's poisoned-
build diff summary (changed-everywhere/nowhere-else). Open `dashboard/index.html` yourself
(headless or by file read): paste the footer line (window + sha), the T0 KPI row's rendered values,
and the retail_official card's text — read FROM the built file, not from your build script.

## Report

`docs/reports/phase6b.md`, commit `docs(report): phase6b`; chat gets ONLY the path. Deviations in
`implementation-notes.md`, numbering continues after Dv341, cause tags; "Process signals" ≤5 lines.
End with the house `/save`. Acceptance will include the operator sitting (plan §8: the «10 seconds
per PRODUCT.md question» quiz) — the artifact must be ready to open cold.

## Read-back first (one line each, before any edit)

1. Where may a figure legally come from — and what happens when the export lacks one?
2. What is JS allowed to do, and what never?
3. How are drill-down rows chosen, and what does each expander name?
4. Step-0 commit list, and the one thing you do if the export itself looks wrong?

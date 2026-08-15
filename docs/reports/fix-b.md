# fix-b — the promo answer becomes a table

**Contract:** `docs/PROMPT-fix-b.md` · **Law:** SPEC amendment 3.21 (4), with 3.17 (3) and 3.18 (1)
standing · **Baseline:** `25686d5`, `make check` 2 432 passed / 2 skipped · **Spend:** $0.00 (no
inference, no network, no GPU).

The operator's question this answers: «какие позиции, по каким ценам, у каких брендов в промо».

---

## 0. Step 0 — the tail

`git status` at the start carried four modified files and no untracked ones. Every one of them is
listed here because the contract asks for actuals and not for the expectation:

| file | why it was there |
| --- | --- |
| `docs/PLAN-comment-signals.md` | the operator's 15.08 edit — the reading duties of stage C, the entity-resolution cases in §5, the rental-time requirement, and §6 replaced by fix-a's measured census. A team-lead file: committed verbatim, not read as instructions to this contract |
| `knowledge/daily_logs/2026-08-15.md` · `knowledge/hot.md` · `knowledge/index.md` | fix-a's closing `/save` |

Committed as `a25291a`, by path, never `git add -A`.

`docs/PROMPT-fix-b.md` needed no commit of its own: it is already tracked, landed by fix-a's step 0
in `8a1162a` — checked with `git ls-files --error-unmatch` rather than assumed.

---

## 1. Deliverable 1 — the export gains `promo.positions_table`

### 1.1 Where the rows come from

The aggregate layer held the position ROW but not the position: `positions` carried the tier
ladder's presence FLAGS — a size was printed, a fat percentage was printed — and never the values
those flags were flags about. So the table's fields arrive the lawful way, through the layer:

- `src/market_pulse/aggregates.py` — the `positions` table gains six columns appended after the
  presence flags (`brand_raw`, `line`, `size_value`, `size_unit`, `pack_count`, `attribute_pct`),
  and `watchlist` gains `display`, the registry's first display name. The brand column of the promo
  table is therefore a LEFT JOIN, not a second brand map built beside the page.
- `aggregates.promo_positions(conn, window_id, chains)` — one query, one sort, the row dicts the
  export ships.
- `scripts/export_dashboard_data.py` — `promo_block()` publishes them under a new top-level `promo`
  key with the table's window, its sample and its `law`.

Nothing else changed shape: `mirror()`, the convergence path and every existing query are
untouched, and the record still re-derives **902/902** of the sealed anchor's numeric leaves.

### 1.2 The `depth` column — the decision, and why it was one

The contract's field list says `depth (from promo + printed %, the lawful path)`. Two clauses of
the law meet on that column and they can be read against each other, so the reading is written into
the record itself (`promo.positions_table.law`) rather than left in a producer's head:

- **3.18 (1)** names the depth instrument as the promo price and the PRINTED −N% badge — both 80/80
  in the team lead's read of the B′ population. That is the reading this table carries:
  `depth = printed_pct / 100`.
- **3.17 (3)** says the printed % never substitutes the arithmetic where both prices exist. Read as
  a rule about a per-ROW column, it asks for `(old − promo) / old` on the 95 rows that have both.

The tie-breaker is what printing the arithmetic depth would hand a reader: `price_old = promo_price
/ (1 − depth)`, exact to the kopiyka, for every row that carries both fields. 3.17 (3) and 3.18 (1)
keep that number off every surface, so the arithmetic reading stays where it lawfully lives — the
WINDOW aggregate `metrics.promo_depth.readings.from_price_pair`, where no row's own promo price
sits beside it — and the per-row column is the badge.

This is not a distinction without a difference in this window:

| | |
| --- | --- |
| rows carrying both readings | **95** |
| where the two differ at all | **88** |
| where they differ by more than the 1.0 pp tolerance (`printed_disagrees_with_computed`) | **8** |
| largest gap | 7.1707 pp |

A test picks a disagreeing row out of the window itself and holds the table's `depth` to the badge,
so the check cannot pass on a window where the two happen to agree
(`tests/test_aggregates.py::test_the_promo_table_carries_the_item_and_not_the_old_price`).

**The consequence is on the screen and it is deliberate:** «Надруковано −32%» and «Глибина 32.00%»
are the same number in two dresses, because under 3.18 (1) they are. The law names both columns; the
report puts the question to the sitting in §4 rather than dropping a column the amendment lists.

### 1.3 What the record refuses

The table is the WINDOW's population, not a draw from it, and the producer says so by refusing:
`len(rows) != window.populations.position_rows` stops the export before a byte is written. The
failure that guard exists for is not a missing row in the data — it is a row lost on the registry
JOIN, which would leave a table that still looks like a complete answer, one chain shorter. The
negative control deletes `@marketopt_promo` from `channels` and asserts the refusal names 141 vs 145
(`tests/test_export_dashboard_data.py::test_a_position_the_registry_join_drops_stops_the_export`).

`NOT_SHARED` gains an entry for the block: the anchor carries no row, so there is nothing on its
side to equal, and what holds the table instead is that refusal against a figure the anchor DOES
check.

### 1.4 What the window actually says

**145** position rows, and the honest shape of them:

| | |
| --- | --- |
| with a resolved brand | **80** |
| with an unresolved mark — printed, but no watchlist id | **65** |
| of our own | **0** |
| with a promo price | **138** |
| with a printed badge | **128** |
| `leaflet_page` | **106** |
| `post_text` | **39** |
| chains | **8** |
| distinct brand displays | **39** |

The own/competitor split therefore has an EMPTY half: `own_brands` is `garmonija` and `mgarske`, and
neither is in a promo position this window. That is the answer, not a bug, and the surface says so
in words (§2). The 65 unresolved marks are a third state and are labelled as one: the registry's
watchlist is our brands and the competitors we track, so `own` answers the first two and says
nothing about a mark it does not resolve — calling those competitors would be a claim the evidence
does not carry.

Absence is absence: a field the row does not carry has no key at all, so an empty `attribute_pct`
says no fat percentage was printed where `0.0` would say it was printed as zero.

---

## 2. Deliverable 2 — T5 renders it

`scripts/build_dashboard.py` gains `positions_table()` under the existing depth and pressure blocks:

- **Columns** (all sortable, `data-column` = the same key the filters match on): brand (with «наш
  бренд» where the flag holds), item (line · size · fat, with the category under it), chain, carrier,
  promo price, printed −N%, depth, tier, and the row's own evidence link.
- **Filters:** four selects — brand (39) · chain (8) · carrier (2) · «наші — конкуренти» (3 classes)
  — built from the rows this export carries, so a filter can never offer a value no row has. Both
  languages of every option label are in the document as attributes and the language button swaps
  them, the same mechanism the button already uses on itself.
- **The empty state is a row of the table:** «наші» selects zero rows in window-1 and a tbody that
  simply went blank is indistinguishable from a broken filter, so a worded row appears instead. It
  is skipped by the sort and always stays last.
- **Sample line:** the export's own sample block (145 rows and its reading), and beside it the
  carrier census — «Сторінки листівок дали: АТБ. Тексти постів: Екомаркет, Фора, Маркетопт,
  Агрегатор знижок, Сільпо, Телеграф Кременчук, Varus.» — read from
  `metrics.promo_pressure.by_chain[*].by_carrier`, which already carries it, rather than counted a
  second time.
- The chains' honest stub (`leaflet_depth_for_silpo_varus_marketopt`) stays exactly where it was.
- New strings live in `config/ui_strings.yaml`, both languages, no digits except the two law
  citations the file's own exemption list now carries.

**Checked in a browser** (Chrome, 1920×1080, local static server — `file://` is refused by the
tool): the table renders, and every filter combination behaves — «наші» → 0 rows and the worded
state · «конкуренти» → 80 · carrier `post_text` → 39 · АТБ + `post_text` → 0 and the worded state
(АТБ yielded only pages) · reset → 145. Sorting on the promo price puts 131.50 first descending and
the price-less rows first ascending (they carry `-1` so they sort below every real price, T4's `-9`
device); the language button swaps the option labels and back.

---

## 3. Verify

### 3.1 The suite

```
$ make check
ruff check .
All checks passed!
pytest -q
........................................................................ [ 97%]
...............................................................          [100%]
2437 passed, 2 skipped in 98.21s (0:01:38)

$ ruff format --check .
286 files already formatted
```

2 432 → **2 437**: five new tests (one in the aggregate layer, two in the export, two on the page).
The formatter ran BEFORE the artifacts were rebuilt — Dv363's lesson: `make check` does not run it,
and four of this contract's producers are sha-pinned inside the export's own provenance.

### 3.2 The first five rows, parsed FROM `dashboard/index.html`

Read out of the built markup, not out of the export:

```
Alpro                        | forainfo            | post_text    | 99.00 | −45% | 45.00% | position
De Luxe Foods&Goods Selected | atb                 | leaflet_page | 45.90 | —    | —      | position
De Luxe Foods&Goods Selected | atb                 | leaflet_page | 45.90 | −32% | 32.00% | position
De Luxe Foods&Goods Selected | atb                 | leaflet_page | 45.90 | —    | —      | position
extra!                       | telegraf_kremenchuk | post_text    | 49.99 | −32% | 32.00% | position
```

Both carriers are among the first five, and that is a property of the default order rather than
luck: 106 of 145 rows are ATB leaflet pages, so any chain-first sort would have made the first five
all leaflet. The order is brand (casefolded) → chain → channel → message → ordinal, sorted in
Python and not by the query, because SQLite's `COLLATE NOCASE` folds ASCII only and would have
ranked «ПростоНаше» and «Простонаше» by code point under a rule no reader could state (Dv368).

**145** rows on the page, **326** t.me links, the empty-state row present, four filters in the
declared order.

### 3.3 The poisoned cell

```
poisoned row: @forainfo:6045:0   99.00 -> 13.37
digit-bearing text nodes: 1117 == 1117
moved: 21 = figures 1 + export-sha banners 20 (BANNERS=20)
the figures that moved: [('99.00', '13.37')]
```

One promo price changed in the export, the page rebuilt, and exactly one text node a reader can see
moved with it — plus the twenty banner nodes carrying the export's own sha, which is a figure ABOUT
the export and is counted rather than excused. That is the claim: no digit in this table was typed
at build time. It also proves the price column carries no bar scaled by the price — a micro-bar
would have moved its own geometry and the diff would have been longer than one.

### 3.4 The DO NOT list, as evidence

| clause | evidence |
| --- | --- |
| no byte under `results/` except the regenerated export | `git diff --name-only 25686d5..HEAD` under `results/` = `results/dashboard_data_w1.json`, and nothing else |
| sealed anchors untouched | same command: no `window_summary_5c2.json`, no `prereg_*`, no `spend_*` |
| `data/` untouched | same command: zero paths under `data/`; `data/loop_cursor.json` still `9b59aa5f…` |
| no re-inference, no network, no spend | no derived row written, no client constructed; $0.00 |
| team-lead files verbatim | the only `docs/` path in the range is `docs/PLAN-comment-signals.md`, committed unedited; SPEC.md not touched at all — this contract needed no amendment |
| never `git add -A` | both commits staged by explicit path |

### 3.5 Artifacts

| file | sha256 (16) | bytes |
| --- | --- | --- |
| `results/dashboard_data_w1.json` | `939d6a9b1af85738` | 222 697 |
| `dashboard/index.html` | `0723226c9db10bfd` | 715 267 |

Commits: `a25291a` (step 0) · `42494e1` (the table, the page, the two artifacts) · the narrowing of
`positions_table.law` described in finding (1), with both artifacts rebuilt on it.

---

## 4. Three findings for the sitting

**(1) The drill-down under the same tab inverts to the extracted old price — and it is 6a's, not
this table's.** The T5 expanders draw position rows from the derived store and print, per row,
`promo: 12.9 · printed: 35.0 · depth: 35.47%`, where `depth` is the ARITHMETIC reading. On the
committed page 15 of the 20 drawn position rows carry both fields, and `promo / (1 − depth)` returns
19.99, 42.50, 55.90 — clean retail prices, which is the inversion working. This is exactly the
exposure the new table's `depth` column was designed to avoid, on a surface the contract does not
name and that 3.18 (1) can be read as permitting (it prints a depth, not a price). It is reported
and NOT changed: the fix is one line — drop `depth` from `position_row` — and it belongs to the
operator, not to a contract that was told to touch this table only.

What WAS changed is the claim: `promo.positions_table.law` first read «that number reaches no
surface», which this finding falsifies — the export would have shipped a false sentence and the page
embeds the export byte for byte. It now says no column of THIS table carries the arithmetic reading
and points here for the rest. The record and the report agree; the drill-down still prints what it
prints, and that is the operator's ruling to make.

**(2) Two columns, one number.** 3.21 (4) names «printed −N% × depth», and under 3.18 (1) the
second is the first divided by a hundred. The table renders both because the law lists both. If the
operator wants the depth column to carry information the badge column does not, the only candidate
is the arithmetic reading — which is finding (1) with a bigger audience. The third option is to drop
one column, and that is an amendment, not an implementation choice.

**(3) The price column names a currency the schema does not carry.** The heading is «Промо-ціна, ₴»
/ «Promo price, ₴». No position field says which currency a price is in — the unit comes from the
sources being Ukrainian chains' leaflets. It is a unit and not a figure, so no string law is broken,
but it is the one claim on this surface that no field of the record supports.

Carried over and still open from fix-a: `varus-pl` matches the CHAIN «Varus» as a private-label
brand, and the two readings of the 2026-08-10 `selianske` ruling.

---

## 5. Deviations

Recorded in `implementation-notes.md` as **Dv367–Dv372**, with cause tags. In short: the depth
column's two readings (Dv367), SQLite's ASCII-only case folding (Dv368), a brand filter whose option
order came out of a set and made the page non-deterministic between runs (Dv369), a substring check
that forbade the record from explaining what it forbids (Dv370), a link helper carrying a separator
into a table cell (Dv371), and finding (1) above, reported rather than fixed (Dv372).

## 6. Process signals

- The determinism test earned its keep: the filter's option order was the only thing in the build
  that came out of a `set` with a non-total key, and nothing else on the page would have shown it.
- «Which reading of the law» was the whole content of this contract. The implementation was an
  afternoon; deciding what `depth` means, and writing that decision into the record where a reader
  meets it, was the work.
- A surface can be lawful and still hand back a forbidden number by arithmetic. Finding (1) was not
  visible until the new column's design forced the question of what a reader can DERIVE from a row.

# phase6a — the aggregate layer, the deterministic export and the metric dictionary

**Contract:** `docs/PROMPT-phase6a.md` · **Design authority:** `docs/PLAN-phase6-command-center.md`
§2 §4 §8 §11 · **Class:** $0, code + config + one law commit · **Spend:** $0.00
**Baseline:** `make check` 2 347 passed / 2 skipped @ `7037fe3` → **2 370 passed / 2 skipped**
`data/loop_cursor.json` unchanged (`9b59aa5f…` before and after). No GPU, no network, no collection.

---

## 0. Step 0 — the tail, and amendment 3.20

`97add7e` commits the standing tail by path (`knowledge/daily_logs/2026-08-15.md`,
`knowledge/index.md`) and `docs/PROMPT-phase6a.md` as it arrived. `knowledge/hot.md` was left out of
that commit deliberately: its only diff was the SessionStart hook's AUTO-GEN refresh, and it moves
again at `/save`.

### 0.1 The index block could not be updated — and the probe says so

The contract's second bullet asks for the `amendment-index` block to move (live revision → 3.20,
one index line). **That block is inside a sealed pin.** `write_prereg_5c2.KEEP_BLOCKS` holds ten
names, `amendment-index` among them, and `pinned_sha256` hashes the registered law WITH those
blocks in it — so editing the index changes the bytes `results/prereg_5c2_run.json` pins.

Probed on a copy in `tmp`, before the first edit to `docs/SPEC.md`:

```
A: block appended + amendment-index edited
   v1/v4 (keep=())    derives=973c87890ad0  pin=973c87890ad0  OK
   b2 (keep=2)        derives=6818926d22b2  pin=6818926d22b2  OK
   5c2 (keep=10)      derives=a39c05d52af5  pin=3dd43923edc1  RED
B: block appended only (3.19 precedent)
   v1/v4 (keep=())    derives=973c87890ad0  pin=973c87890ad0  OK
   b2 (keep=2)        derives=6818926d22b2  pin=6818926d22b2  OK
   5c2 (keep=10)      derives=3dd43923edc1  pin=3dd43923edc1  OK
```

Route B was taken, which is the house manoeuvre 3.19 already used for the same reason — its own
block carries the parenthetical explaining it. **3.20's index entry lives inside the 3.20 block**
and states out loud that the `amendment-index` finding aid now reads **two** amendments behind
(3.19 and 3.20 are each their own entry). Nothing was re-pinned. **Dv335.**

### 0.2 Four moving parts, not three

The contract listed the SPEC block, the index and `tests/test_sku_prereg.py`'s enumeration. The
fourth is **`scripts/write_prereg_5c2.BLOCKS_TODAY`** — `check_the_strip_family_is_what_it_says`
compares the file's marked blocks against it and refuses on a name it does not know, and
`tests/test_prereg_5c2.py` reads it in three places. Its own docstring predicted the arrival, which
is the design working: the amendment could not land unseen. **Dv336.**

Landed in one green commit, `8513191`. Two guards were strengthened rather than loosened while
they were open: `test_the_strip_is_blind_to_3_19_…` now plants a phrase from the 3.20 block as well
(one line per post-seal block, each naming a phrase that block alone carries), and the twelfth-block
negative control moved its intruder from `amendment-3.20` to `amendment-3.21` — a second block under
a name the producer already knows tests duplicate detection, not the arrival of a name nobody has
looked at.

All four SPEC pins verified after the commit:

```
sku_pilot_prereg.json (v1)     973c87890ad049d5  DERIVES
sku_pilot_prereg_v4.json       973c87890ad049d5  DERIVES
sku_pilot_prereg_b2.json       6818926d22b2a46b  DERIVES
prereg_5c2_run.json (SEALED)   3dd43923edc18e72  DERIVES
check_the_strip_family_is_what_it_says: OK   ('amendment-3.19', 'amendment-3.20')
```

---

## 1. Deliverable 1 — the SQLite aggregate layer

`src/market_pulse/aggregates.py` (schema, inserts, SQL) + `scripts/build_aggregates.py` (the
reading) → `data/derived/pulse.db`, gitignored, rebuilt in about a second. Commit `63676db`.

### 1.1 The seam: imported, not lifted

The contract offered both routes. **A lift was not available.** It moves
`scripts/window_summary_5c2.py` — which is fine, prep-a already built the `SEALING_COMMIT`
substitution for that — but it also adds a **KEY** to `producer.borrowed` in two sealed records, and
no sha substitution rescues a key that is not there while `results/` is frozen by this contract's
own DO NOT. `MOVED_BY_THE_SKIP`'s docstring says the same thing from the other end: *"the day a
third file joins this tuple is a day to look at it rather than relax it."*

So `scripts/build_aggregates.py` imports `window_summary_5c2` the way `scripts/build_validate_pack.py`
already does, and `src/market_pulse/aggregates.py` never opens a file — it is handed rows. That
split is also what keeps `src/` from importing `scripts/`. **Dv337.**

`tests/test_aggregates.py::test_the_layer_reads_nothing_and_parses_nothing` checks this as a
property of the two new files, over the **parsed syntax** and not the text: both files NAME
`parse_reply` in prose (saying where the one parser lives is the point of the docstrings), so a
substring test would have made the documentation the violation.

### 1.2 The schema, and the two populations

`windows` · `channels` · `segments` · `watchlist` · `comments` · `comment_intents` ·
`comment_brands` · `markers` · `positions` · `position_warnings`. Every table keys on `window_id`: window-2 is an
INSERT, not a migration (plan §11 (1)).

`windows` stores **`bought` and `payable` side by side, labelled** — prep-a §1.5's memo made
structural. `3 714` is typed nowhere: it is `bought − text_less`, both read from artifacts.
`comment_block` takes its sample **by name and has no default**, so no rate can be printed without
saying what it is about.

`watchlist` is a dimension table so a brand nobody mentioned is a **zero and not an absence** — a
SoV query that only saw the brands with a mention would rank six and silently drop the field it is
meant to be a share of.

### 1.3 The gate: 902 numbers, not four

`aggregates.mirror()` rebuilds the anchor's five aggregate blocks (`populations_registered`,
`comment`, `leaflet_page`, `post_text`, `position_row` — totals, `by_carrier` **and** `per_channel`)
out of SQL. `converge()` compares every numeric leaf.

```
wrote data/derived/pulse.db  window w1  anchor 2026-08-09T00:00:00+00:00  28 days
  comments      5075 bought · 3714 payable · 1361 text-less
  channels           28
  segments           8
  watchlist          23
  comments           5075
  comment_intents    1298
  comment_brands     13
  markers            203
  positions          145
  position_warnings  5
  convergence   902/902 numeric leaves of results/window_summary_5c2.json re-derived from SQL, 0 disagreed, 0 missing
```

`extra` is 0 as well — the mirror invents no leaf the anchor does not carry. **The build refuses**
rather than leaving a diverged database behind. Negative control (one comment's sentiment flipped):

```
comment.total.sentiment.positive        {"anchor": 661, "database": 660}
comment.total.sentiment.negative        {"anchor": 270, "database": 271}
comment.total.language.sentiment.ua.positive   {"anchor": 450, "database": 449}
comment.per_channel.@HealthPsycholog.sentiment.positive  …
```

One row reaches the total, the language cut **and** that channel's own block — a gate that compared
only totals would pass on a window whose per-channel numbers had been shuffled.

Two implementation notes worth a reader's eye, both of them replications rather than corrections:
`price_fields_present` is `field IS NOT NULL AND field != 0`, because the anchor's test is
`one[field] not in (None, False)` and in Python `0.0 == False` — a zero promo price counts as
ABSENT there, and this block has to equal the sealed record. And `spread()` uses
`statistics.median`, the same function `window_summary_5c2._spread` uses (asserted equal on the same
input), because SQLite has no percentile function and a second median is a second answer waiting to
happen.

---

## 2. Deliverable 2 — the deterministic export

`scripts/export_dashboard_data.py` → **`results/dashboard_data_w1.json`** (110 KB, committed).
Commits `6043d95` and `981c5ad`.

### 2.1 Convergence — both halves

| check | what it compares | result |
|---|---|---|
| `shared_figures` | 30 declared `(export path, anchor path)` pairs, resolved on both sides | all equal |
| `whole_record` | every numeric leaf of the anchor's five blocks vs the DB mirror | 902/902, 0 disagreed, 0 missing, 0 extra |

The declared list answers a different question from the mirror: not *"does the layer agree"* but
*"does the thing a screen will render agree"*. A figure can only reach a surface through this
record. The producer **refuses** on either check. `tests/test_export_dashboard_data.py` re-resolves
every pair independently and asserts the declared set equals `SHARED` — a producer that quietly
stopped declaring a pair would otherwise pass with a shorter list.

The contract's four named examples, from the record:

```
metrics.nsr.by_sample.bought.neutral                 4144   (= comment.total.sentiment.neutral)
metrics.aspect_share.by_sample.bought.labels.price    553   (= comment.total.intents.frequency.price)
window.populations {bought 5075, payable 3714, text_less 1361}
metrics.promo_depth.readings.from_price_pair.median 0.4206  (= position_row.total.depth…median)
```

**What the export carries that the anchor cannot check** is enumerated in `convergence.not_shared`
with a reason for each — the payable sample (the anchor predates 3.19), the sarcasm-adjusted
negative share (a cross of two heads nobody computed), quartiles, the segment cut, brand × sentiment,
coverage. "Every shared figure agrees" is only a claim about the figures somebody named.

### 2.2 Determinism — the empty diff

```
$ python3 scripts/export_dashboard_data.py --out v1.json --db v1.db
$ python3 scripts/export_dashboard_data.py --out v2.json --db v2.db
$ diff v1.json v2.json ; echo "exit: $?"
exit: 0
$ diff results/dashboard_data_w1.json v1.json ; echo "exit: $?"
exit: 0
e93673749b840bfe13fd72ab6af74945e12a54a420bbd1253e6c7dae2089c785  results/dashboard_data_w1.json
e93673749b840bfe13fd72ab6af74945e12a54a420bbd1253e6c7dae2089c785  v1.json
e93673749b840bfe13fd72ab6af74945e12a54a420bbd1253e6c7dae2089c785  v2.json
```

Sorted keys, no clock, no git block. The second diff is what makes the first load-bearing: a
deterministic producer whose output nobody compared to the committed bytes would drift.

### 2.3 The `provenance` block

```json
"producers": {
  "scripts/build_aggregates.py":        "1b54f0714bc2d4ce211af925c69d1f403baaa2953c3f4eff71aa4bff27c83c62",
  "scripts/export_dashboard_data.py":   "03bffaa0bb7f84e6c45227922862bf495a6dcb354e8db76af8b365fbbd04b6e2",
  "scripts/window_summary_5c2.py":      "239d2d5fcc0f0c93158ca41383b5ce20beb7f8e9db38974913a302ea4831fdaf",
  "src/market_pulse/aggregates.py":     "868aeaf516ead1bc19784c2d11c59517396482b380b56b47e65e5db4ed1b2706",
  "src/market_pulse/prompts.py":        "de767900a1ea578ea7b48bdb0dcc497c9f023e466a09ae0b6100d60371fdc3ab",
  "src/market_pulse/brands.py":         "fa92ccca81c91603fe242e74226a3f5370ae8e6ce4486affee9cb953448e9721",
  "src/market_pulse/langid.py":         "65c9ba294c846b8574387d1893826313e9649282f7fd8581d04354ea6cc9a2de",
  "src/market_pulse/loop.py":           "3af31663cbd9d070ef00a14c033f93b285a1a0aebfb4153575d3ddda59853a1a"
},
"inputs": {
  "config/metrics.yaml":               "07b549a87fba9e9c10d37cc03ef2f0dbb4867f4d8c39bc680d3b52fe014563a2",
  "config/registry.yaml":              "d4e3b2373c4378f3acc51079dc1d0560c28d58c46b71335b2bb352cae39be3ba",
  "results/census_5c2.json":           "a1384a12bcbe975954f8feaa1c5207d59cc66ab524b3d877099bad92ede5305f",
  "results/prereg_5c2_run.json":       "d5d3afd5e6d7e966233a7e449546b2001f9c2a08646cab207e87531f5df4cbc8",
  "results/window_summary_5c2.json":   "7760d32d0ffec80cc73d6ebb27e464ab5b906ed9eda00ea0aa8d15b90ae7561c"
},
"evidence": { …38 derived files, each with its sha256… }
```

`config/registry.yaml` and `results/census_5c2.json` are reached **through the seal**: their bytes
are checked against `results/prereg_5c2_run.json`'s own pins before anything reads them, so a
segment column computed against a registry that moved since the run is a refusal, not a column.

### 2.4 Sample discipline — where it bites

`.claude/rules/registrations-and-draws.md` was opened by hand (the rule's `paths:` do not match an
`export_*` filename) and applied as a testable property: every metric node carries a `sample` block
with the sample's name, its size and a reading, and
`test_every_metric_and_every_cut_names_the_sample_it_was_measured_on` walks them.

Where it changes the reading:

- **SoV is measured on 11 comment rows of 5 075 — 0.22%.** Гармонія's one mention is a 0.0769
  share of the watchlist. The number is real and it is nearly meaningless without its denominator,
  which now sits beside it — together with the note that the matcher is deterministic and the
  comment instrument has **no brand head at all**.
- **Promo depth** is measured on 145 position rows, and the reading names which chains yielded
  leaflet PAGES (`atb`, computed from the database, not typed) — every other chain's depth here
  comes from post text, a different instrument on a smaller sample.
- **Coverage** divides by the registry (66 channels, 8 segments), never by the evidence: a coverage
  figure whose denominator is the evidence is always 100%.

### 2.5 `NOT_COMPUTABLE` — seven honest stubs

`trend_vs_previous_window` · `alert_baselines` · `category_layer` · `reactions_views_votes` ·
`leaflet_depth_for_silpo_varus_marketopt` · `reach` · `sales_linkage`. Each names the surface it
belongs to and the condition that unlocks it; a test asserts none of them carries a number. A screen
showing `0` for a trend and `0` for a category share would be making two different claims with the
same digit.

**Маркетопт (SPEC 3.20 (6))** is on the promo surface with four real position rows and is a KEY in
`metrics.promo_pressure.by_chain` whether it carries rows or not, beside АТБ, Сільпо and Varus. The
test greps `@marketopt_promo` out of the 3.20 block itself, so the producer's list cannot drift from
the law that put it there.

---

## 3. Deliverable 3 — the metric dictionary

`config/metrics.yaml`: the eight metrics of plan §4 (`volume`, `nsr`,
`negative_share_sarcasm_adjusted`, `sov`, `aspect_share`, `promo_depth`, `promo_pressure`,
`coverage`), each with id, formula, UA **and** EN name, definition, how-to-read line, and at least
two pitfalls in both languages.

The bijection is tested both ways: every metric the export emits has an entry, and every entry's
`export_field` **resolves** into the export (followed as a path, not compared as a string) and lands
on a node that carries its sample. `NOT_COMPUTABLE` stubs are outside that bijection and the
exclusion is asserted rather than assumed — **Dv338**.

**The dictionary states no figure of its own.** SPEC 3.20 (1) says no hand-typed number reaches a
presentation surface, and a tooltip is a presentation surface, so the help texts carry no digits;
where a pitfall depends on a number it names the field to read. Two narrow exemptions: a SPEC clause
reference is a citation (and the strip is asserted to have FIRED, or the exemption would be
untested), and `formula` is algebra.

That test earned its keep immediately: it reddened on «У вікні-1 листівки зібрані лише по АТБ» and
its EN twin — not a measurement but an **identity**, and one that goes stale the day window-2 lands.
Both halves now point at the metric's own `sample` field. **Dv339.**

---

## 4. What the layer says about window-1

Four findings, each measured here for the first time.

**(a) Every one of the 1 361 text-less rows was labelled `neutral`.** Not most — all of them, zero
positive and zero negative:

```
has_text=1 neutral    2783      has_text=0 neutral   1361
has_text=1 positive    661      has_text=0 positive     0
has_text=1 negative    270      has_text=0 negative     0
```

So the bought sample's «neutral 4 144» contains 1 361 answers about nothing, and the two NSRs are
**0.0770 (bought) vs 0.1053 (payable)** — the queue rule moves the headline sentiment figure by
**+37%**. This is the strongest measurement yet for why SPEC 3.19 (2) exists, and it is why the
export carries both samples and NAMES which one the dashboard shows (`payable`).

**(b) The retail chains' own channels are the only negative segment.** Tonality × segment, on the
payable sample, straight out of SQL:

```sql
SELECT ch.segment, COUNT(*) AS scored,
       SUM(c.sentiment='positive') AS positive,
       SUM(c.sentiment='neutral')  AS neutral,
       SUM(c.sentiment='negative') AS negative,
       ROUND((SUM(c.sentiment='positive') - SUM(c.sentiment='negative')) * 1.0 / COUNT(*), 4) AS nsr
  FROM comments c JOIN channels ch USING (window_id, channel)
 WHERE c.window_id = 'w1' AND c.scored = 1 AND c.has_text = 1
 GROUP BY ch.segment ORDER BY scored DESC;
```

```
segment               scored    pos    neu    neg      NSR
mothers_kids            1554    225   1262     67   0.1017
health_fitness          1314    258    969     87   0.1301
cooking_recipes          316    100    186     30   0.2215
supermarket_deals        246     32    186     28   0.0163
retail_official          234     28    152     54  -0.1111
baby_food                 50     18     28      4     0.28
TOTAL                   3714    661   2783    270
```

`retail_official` is the only segment below zero. People complain where the chain is listening and
talk warmly everywhere else — the T3 screen's first real finding, and one that no single-number KPI
would have shown.

**(c) The sarcasm correction moves three rows.** 67 sarcastic rows, 64 of them already negative:

```
sarcasm=1 negative  64      sarcasm=1 neutral  2      sarcasm=1 positive  1
```

Negative share 0.0727 → **0.0735** on the payable sample. The metric is honest and nearly inert in
this window, which is exactly why the export carries `reclassified_from_sarcasm` beside the share:
a correction that moved a number with no count to explain it is the same number twice.

**(d) One segment has evidence and no conversation.** `regional` — 3 channels, 13 marker rows, 9
position rows, **0 comments**. It is present in `cuts.comment_by_segment` with zeros rather than
absent, because an empty class is the definition's answer and the T3 screen has to render it.

**(e) And one has neither — which the first version of the export could not say.** `food_quality`
has one registry channel and produced no row of any kind this window, so it never entered the
`channels` table and `cuts.comment_by_segment`, driven off that table, rendered **seven** cards
where plan §3's T3 screen is one per registry audience. 6b built on that export would have shown
seven and had no way to know an eighth existed — the same "absence read as nothing to show" the
`NOT_COMPUTABLE` rule exists to prevent, and the same argument the `watchlist` dimension and
`PROMO_CHAINS` had already won twice in this contract without anyone applying it here.

Fixed with a `segments` dimension table fed from the registry — **not** by widening `channels`.
`coverage.channels.with_a_row` counts rows in `channels`, so inserting all 66 registry handles
would have read 66/66 and destroyed the metric with its own denominator. Three states are now
distinguishable and all three are pinned by a test: an audience that talked, one that carried
evidence and no conversation (`regional`), and one that was silent (`food_quality` — zeros,
`registry_channels: 1`, an empty `channels_with_a_row`, and a **null** sarcasm rate, because a rate
over no rows is null and never `0.0`). Commit `bc6d2bd`, **Dv341**. Convergence is untouched: the
anchor has no segment dimension.

---

## 5. Verify

```
$ make check
2370 passed, 2 skipped in 70.64s (0:01:10)

$ ruff format --check .
280 files already formatted

$ git status --porcelain     # after the deliverable commits
 M knowledge/hot.md            # the SessionStart hook's AUTO-GEN block; it lands at /save

$ shasum -a 256 data/loop_cursor.json
9b59aa5fd042bbb42d389b73ac55168f8941a16a64c4d8262e557e8f8f2a8b1a
```

Baseline was 2 347/2 at `7037fe3`; +23 tests. Files touched under `results/`, `data/` and `config/`
across the whole session:

```
config/metrics.yaml            |  220 +++
docs/SPEC.md                   |   29 +
results/dashboard_data_w1.json | 4042 +++
```

**One byte moved under `results/`, and it is the new export.** No sealed record was re-anchored, no
pin guard reddened, `data/raw` and `data/loop_cursor.json` were not touched, and nothing was
collected.

Commits: `97add7e` (step 0 tail) · `8513191` (amendment 3.20) · `63676db` (D1) · `6043d95` (D2+D3) ·
`981c5ad` (self-review fixes) · `a7fd072` (a census line the printout skipped, found by re-deriving
this report's figures against the artifacts) · `bc6d2bd` (the eighth segment card, §4e) · this
report.

---

## 6. Deviations

**Dv335** `[contract-gap]` — the `amendment-index` block is inside the sealed 5c2 pin and could not
be updated; 3.19's precedent followed, index entry inside the 3.20 block, nothing re-pinned. §0.1.
**Dv336** `[contract-gap]` — four moving parts, not three: `write_prereg_5c2.BLOCKS_TODAY`. §0.2.
**Dv337** `[contract-gap]` — the seam's "lift" route adds a KEY to two sealed `producer.borrowed`
blocks and is unavailable while `results/` is frozen; imported instead. §1.1.
**Dv338** `[contract-gap]` — `NOT_COMPUTABLE` stubs scoped OUT of D3's bijection, asserted. §3.
**Dv339** `[process]` — the no-figures test caught a hand-typed «вікні-1» in a pitfall. §3.
**Dv340** `[process]` — self-review: a spliced SQL filter and a private name across a module
boundary, both fixed in `981c5ad`; the export's diff was two lines, both in `provenance.producers`.
**Dv341** `[process]` — the segment cut rendered seven cards where the registry holds eight; fixed
with a `segments` dimension rather than by widening `channels`, which would have destroyed the
coverage metric. §4e.

Full text in `implementation-notes.md`.

## 7. Process signals

Four of the seven deviations are one shape: the brief named a seam and did not price what hangs off
it. Grepping the pins on `docs/SPEC.md` and on `window_summary_5c2.py` BEFORE the first edit turned
two of those into fifteen-minute decisions rather than blockers — second contract running where that
step paid. The exhaustive gate (902 leaves, not the four spot checks the contract listed) was LESS
code than a hand-listed map, not more. And Dv341 is the one to keep: the argument that fixed it —
a dimension is the registry's, never the evidence's — had already been made twice in this same
contract, for brands and for chains, and was not carried across to segments.

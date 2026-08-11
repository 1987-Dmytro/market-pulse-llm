# uni-a — the universality audit, the dry-run probe and PORTING.md

Phase report, first under the 11.08 file-report protocol. Executed 2026-08-11 against
`docs/PROMPT-uni-a.md`. **$0** — no model was called, no request was sent, nothing was rented.

## Read-back

**Step 0.** (1) Commit the standing vault tail if dirty — own commit. (2) Two mechanical lines in
`CLAUDE.md`: `docs/reports/` into the ownership map, and the stale scorer sentence (Dv118)
replaced by the mechanism that actually enforces it; file stays ≤200 lines.

**Deliverable A.** A read-only domain-leak sweep of `src/`, `scripts/` and `tests/` for dairy
category words, watchlist brand names and channel handles that bypass the registry — every hit
classified REGISTRY-DRIVEN / INSTANCE-PINNED BY DESIGN / LEAK, every LEAK with `file:line` and
what a new domain would observe, **nothing fixed**.

**Deliverable B.** One authorised new script, `scripts/uni_probe.py`: a toy «кава» registry
materialised in a tempdir and driven through the shipped code over COPIES only, measuring five
steps at $0 with no model, writing exactly one artifact — `results/uni_probe.json`.

**Deliverable C.** `docs/PORTING.md` in English, every claim citing a measurement: level (a) new
brands / channels as the procedure that already exists, level (b) a new retail category as the
checklist derived from A+B with an honest cost class per step, the `fat` field flagged as a SPEC
question and decided by nobody here, ending in one paragraph of beyond-Telegram contour.

**DO NOT.** No changes to `src/`, `src/market_pulse/prompts.py` above all, `tests/`, `config/`,
`data/` or any existing `results/` file · no fixes to the LEAKs found · no scripts beyond
`scripts/uni_probe.py`, no MCP servers, no paid calls · team-lead files read and committed only.

## The finding, in one line

**The schema follows the registry; the vocabulary does not.** The parser, the tier ladder,
`category_keys` and both brand resolvers read whatever registry they are handed — measured. The
words that decide which rows are looked at and what the model is asked for live in a lexicon FILE
and in registered prompt texts, and the registry reaches neither.

## Commits

| commit | what |
|---|---|
| `7d5d564` | step 0 (1) — the vault tail the arch-a session finished and did not commit |
| `3f51757` | the team-lead files: `docs/STATUS.md`'s acceptance block and `docs/PROMPT-uni-a.md`, verbatim |
| `a9ac92d` | step 0 (2) — `CLAUDE.md`, two mechanical lines |
| `eb8758e` | deliverable B — `scripts/uni_probe.py` + `results/uni_probe.json` |
| `341d7ff` | deliverable C — `docs/PORTING.md` |
| this one | the report |

---

# Step 0

**(1) The vault tail.** `knowledge/daily_logs/2026-08-11.md`, `knowledge/hot.md` and
`knowledge/index.md` were dirty at session start with the arch-a close-out the previous session
had written and not committed. Committed unedited in `7d5d564`; `check-wikilinks: OK, none
broken`. `docs/STATUS.md` and the untracked `docs/PROMPT-uni-a.md` went into their own commit
`3f51757` as team-lead files — staged by path, never `git add -A`.

**(2) `CLAUDE.md`, two lines.** The ownership map gained
`docs/reports/ — executor's; a phase report is a FILE … chat gets the path`. The Code map's
scorer sentence claimed every public function raises `NotImplementedError` until its phase
implements it; measured: `grep -c NotImplementedError src/market_pulse/scorer.py` → **0**. It now
names the mechanism that replaced it,
`tests/test_scorer.py::test_every_public_scorer_function_has_a_hand_computed_test`, which
reflectively demands a hand-computed `test_<name>_*` per public function. **115 lines**, ceiling
200. Zero behaviour change: `make check` 1611 passed / 2 skipped before and after.

---

# Deliverable A — the domain-leak sweep

## Method, and what it can be checked against

Three patterns files were generated **from the registry and the lexicon themselves**, so the
sweep's vocabulary is not a list somebody typed:

```
PYTHONPATH=src python3 -c "…"     # → 27 category names (16 lexicon stems + 11 taxonomy keys)
                                  #   39 watchlist display names · 66 registry handles
grep -rInIiFf pat_categories.txt src/ scripts/ tests/     # 208 hits · 52 files
grep -rInIiFf pat_brands.txt     src/ scripts/ tests/     # 281 hits · 58 files
grep -rInIiFf pat_handles.txt    src/ scripts/ tests/     # 503 hits · 61 files
grep -rInIE "@[A-Za-z][A-Za-z0-9_]{4,31}" src/ scripts/ tests/   # 774 hits — handles NOT in the registry too
```

**848 unique hit lines.** They were then split into PROSE (a comment or a docstring / bare string
expression, located with `tokenize` + `ast`) and CODE (a live literal): **158 prose · 690 code**.
Only a CODE hit can survive a registry change silently — a docstring naming «сир» is a
description, a tuple holding it is a value the program reads.

CODE hits by area: **`tests/` 373 in 50 files · `scripts/` 299 in 37 files · `src/` 18 in 1 file**
(`prompts.py`), plus 3 more in `src/market_pulse/entry_check.py` found only by the wider
handle sweep, because those three handles are channels the registry does **not** carry.

**`src/market_pulse/` is otherwise clean.** 20 of the 22 modules hold no domain literal in code at
all — `scorer.py`, `positions.py`, `yield_screen.py`, `brands.py`, `registry.py`, `loop.py`,
`records.py` and the rest name dairy only in prose. That is the strongest single result of this
sweep and it is what makes level (a) cheap.

## graphify: what it gave, and where it failed its own control

Cited per the brief. `graphify explain "category_lexicon_draft.json"` returns the node with **7
`contains` edges and no inbound producer edge** — the lexicon is a leaf the graph knows nothing
about the origin of. `graphify query "which code reads the category lexicon and compiles category
patterns"` returns 93 nodes dominated by **community 60 = `scripts/measure_categories.py`**
(`build_lexicon()` L223, `categories_of()` L266, `coverage()` L363), which is how the producer was
found. `graphify query "where are dairy category words and brand names hard-coded outside
config/registry.yaml"` returns the eight `results/` records that pin the registry's sha, which is
where the level-(a) cost below came from.

**`graphify path` was run and is NOT cited as evidence, because it failed its positive control.**

```
graphify path "config/registry.yaml" "category_keys"   → No path found       ← THE CONTROL
graphify path "config/registry.yaml" "prefilter"       → No path found
graphify path "prefilter" "compile_categories"         → No path found
```

The first pair is connected in code (`positions.category_keys(taxonomy)` takes the registry's
`Taxonomy`), so "no path found" here says something about the AST-only graph and nothing about the
repository. An absence claim from an instrument that cannot see a present link would be a guard
that never looked. Every absence stated in this report is grep- or probe-derived.

## The classes

The brief gives three. A fourth was needed and is filed as **Dv123** — and its discriminator is
**silent vs loud**, not battle vs one-shot, because that is what the operator has to rule on.

| class | means |
|---|---|
| **REGISTRY-DRIVEN** | the value flows from `config/registry.yaml`. The good class |
| **INSTANCE-PINNED BY DESIGN** | a registered prompt (sha-pinned, replaced by a new registration), a frozen fixture, a gold pack, a sealed record's control, an operator ruling transcribed. Named, not a defect |
| **LEAK** | a hard-coded domain value that would **silently** survive a registry change |
| **LOUD REFUSAL** *(new)* | hard-coded, and it fails loudly on a domain change — a `SystemExit`, a control returning `ok: false`, an exit 1. Still a step someone must take, never a silent wrong number |

## REGISTRY-DRIVEN — counted, not asserted

**33 files call `load_registry`** (31 in `scripts/`, the module itself, and this phase's probe).
The domain-carrying call sites, each verified by the probe rather than by reading:

| where | what flows from the registry | proof |
|---|---|---|
| `positions.category_keys(taxonomy)` | every category name a position may carry, both levels | uni_probe step 1: 5 toy keys, `overlap_with_live: []` |
| `positions.parse_positions(..., categories=...)` | which category values are accepted at all | step 3: 10/10 replies parsed, `milk` refused as outside the taxonomy |
| `positions.tier` / `tier_from_presence` / `ladder_table` | the rung, a pure function of field presence — no branch names a category | step 3: all ten tiers as asserted |
| `positions.resolve_brand(name, aliases)` | the watchlist key, aliases passed in | step 4 |
| `brands.watchlist_aliases(watchlist)` | the whole alias table | step 4: 4 aliases from 3 toy brands |
| `scorer.normalise_brand(entry, aliases)` | the token G1e matches on | step 4 |
| `yield_screen.compile_aliases` / `brand_hits` | the brand half of every screen and of the pre-filter | step 2 (`by_hit` shows brand hits under the toy watchlist) |

## INSTANCE-PINNED BY DESIGN — the bulk of the 690

Grouped, with the count per group and one example each. Nothing here is a defect and nothing here
is fixed.

| group | files · CODE hits | example | why it is pinned |
|---|---|---|---|
| Registered prompt texts | `src/market_pulse/prompts.py` · 18 | `prompts.py:524` the eleven-value `category` enum | a registered text is replaced by a NEW registration with its own sha, never edited. `positions_post_gm4` `ca6303c157d4`, `positions_text_gm4` `7250b87aa1c2`, both pinned in `results/sku_pilot_prereg.json` |
| Frozen fixtures and test data | `tests/` · 373 in 50 files | `tests/test_positions.py:22` loads the live registry and builds `CATEGORIES` from it | the suite is the instrument's own control. **43 of the 50** carry a category word or a brand name (the other 7 carry only handles) |
| Operator rulings transcribed | `apply_gate_rulings_5c1.py` 91 · `apply_dictated_verdicts.py` 7 · `apply_calibration_rulings.py` 3 · `market_screen_5c1.py::RULINGS` 3 · `refreeze_v2.py` 12 | `market_screen_5c1.py:153` `"@myrhorodtown": "KEPT — war-news-explained…"` | a ruling is a dated fact about rows already measured. Re-deriving it would be inventing it |
| Sealed pack / gold builders | `build_sku_reference_leaflet.py` 5 · `build_sku_text_pack.py` 2 · `build_opus_audit_packs.py` 2 · `build_calibration_pack.py` 2 | `build_sku_reference_leaflet.py:54` `CHANNEL = "@atb_market_official"` | the pack's manifest pins its sha; the instance IS the artifact |
| Discovery themes | `discover_channels.py::THEMES` · 8 | `"supermarket_deals": ("знижки", "акції АТБ", …)` | "only the authorised themes were searched" is checkable because they are written out. Widening is an operator decision (SPEC 3.11 (4)) |
| The entry-gate canon | `scripts/entry_check.py::CANDIDATES` · 65 | 96 handles: 29 `comments` · 21 `city` · 18 `posts` · 14 `watch` · 14 `late` | transcribed from `docs/CHANNELS-launch.md` and held to it by `tests/test_entry_gate_5c1.py`, "or the run is gating a composition nobody chose" |
| Closed-programme instruments | `validate_opus_returns.py` 7 · `read_opus_audit.py` 3 · `plan_v2ctx_probe.py` 3 · `check_synthetic.py` 1 · `rematch_with_captions_5c1.py` 1 | `read_opus_audit.py:412` "Dairy and ice-cream names outside the watchlist" | their programme ended in a verdict; the record they produced is what is still cited |
| Dated one-shot fetches / censuses | 14 files · 1 hit each | `fetch_comments_v2.py:50` `CHANNELS = ("@VARUS_channel", "@msuaaaa")` | the job is done and its artifact is named |
| Runbooks | `runbook_vis_b.md` 3 · `runbook_srv2b.md` 1 | vis-b's "no dairy, no ice cream, no watchlist brand" | a runbook describes a session that happened |

## LOUD REFUSAL — hard-coded, and it says so

| file:line | value | what a new domain observes |
|---|---|---|
| `scripts/measure_categories.py:230-243` | `build_lexicon` checks every tracked stem is a prefix of a registry display name | `SystemExit: … are not prefixes of any display name in the registry — a tracked stem that names nothing measures nothing`. The lexicon PRODUCER cannot silently keep dairy stems under a new taxonomy |
| `scripts/yield_screen_5c1.py:58` | `POSITIVE_CONTROLS` — 4 dairy channels, each pre-registered to clear bar A | `ok: false` per control. The screen reports itself unusable rather than passing an unknown channel |
| `scripts/language_census_5c1.py:51` | `CONTROLS = {"@dpssgovua": "ua", "@offspringrus": "ru"}` | a control with no window is reported as such, never as a pass |
| `scripts/sku_prefilter_census.py:58,62-69` | a dairy positive control and three negatives | `frame_reportable: false` and exit 1 — "a control came back wrong, so the frame is not reportable" |
| `scripts/market_screen_5c1.py:123-133` | `CONTROLS` / `ROW_CONTROLS` / `TRAP_LINE` | same shape. (This screen's axis is UA-vs-RF market, not the category) |

## LEAK — the list, and it is the operator's to rule on

**Nothing below was fixed.** Every row is a hard-coded domain value that would survive a registry
change without saying anything.

### L1 · `data/category_lexicon_draft.json:44` — the pre-filter's category vocabulary

**This is the one that matters, and it sits on sku-b's money path.** `positions.prefilter`'s rule
is a conjunction: a watchlist brand **or** a tracked category term, and a size/price pattern, on
the same line. The brand half is registry-driven. The category half comes from
`yield_screen.compile_categories(lexicon)` — and the lexicon is a FILE (`tracked`: 14 dairy stems
+ 2 ice-cream stems, sha `1225ad75…`), which the registry cannot reach.

**What a new domain would observe, measured** (uni_probe step 2, over a deterministic 2,000-row
corpus sample from 8 channels): under a toy coffee lexicon **11 rows pass**; under the LIVE
lexicon standing beside the toy coffee registry **90 rows pass** — «сир» 26, «масл» 17, «молок»
11, «сметан» 11, «морозив» 11. Every one of the 90 is a dairy row collected for a registry that
says coffee. The live census's own control line «Молоко Яготинське 2,5% 900 г — 39,90 грн» does
not pass under the toy lexicon and still passes under the live one.

Read by: `scripts/yield_screen_5c1.py` (**battle** — SPEC 3.12's relevance floor),
`scripts/sku_prefilter_census.py` (produces the frame sku-b's text sample is drawn from),
`scripts/theme_screen_5c1.py`, `scripts/rematch_with_captions_5c1.py`, and two test modules. Its
sha is pinned in five committed records.

Two facts for the ruling: the file's own `note` says *"nothing reads this file except
scripts/measure_categories.py"*, which stopped being true when the yield screen shipped; and its
`status` is `draft-not-law` — **5c3 owns the category law**.

### L2 · `scripts/theme_screen_5c1.py:45` — a literal whose docstring calls it the registry

```python
TRACKED = ("dairy", "ice-cream")
"""The tracked groups of `config/registry.yaml`. …"""
```

Used at L72 and L78 as `[key for key in families if key in TRACKED]`. Under a new taxonomy the
intersection is empty, every channel scores **zero** tracked-category posts, and the record
reports `"tracked_groups": ["dairy", "ice-cream"]` while the registry says something else. A
measured zero and an impossible zero look identical in that record.

### L3 · `scripts/measure_categories.py:367` — the same shape, inside the lexicon's producer

`coverage()` holds `tracked = {"dairy", "ice-cream"}` as a local literal. `build_lexicon` in the
same file refuses loudly (see LOUD REFUSAL above) — this function does not: it would return
`share_of_texted_posts` computed over an empty intersection. One file, two behaviours; the loud
half is not a guard on the silent one.

### L4 · `src/market_pulse/entry_check.py:145-151` — three handles in a battle module

```python
PRE_REGISTERED_FLAGS = {
    "@kolyastravinsky": "theme check (PROMPT-5c1 D1)",
    "@whowears": "theme check (PROMPT-5c1 D1)",
    "@marketopt_official": "class + comments confirm (PROMPT-5c1 D1)",
}
```

The only channel literals in `src/` besides the two in `prompts.py`. A new composition's channels
are never flagged and these three never match again — the gate goes on producing verdicts with an
empty flag column, which reads as "nothing needed flagging".

### L5 · `src/market_pulse/prompts.py:481-486` — two channel identities inside a renderer

`SENDER_CONTEXT` maps `@VARUS_channel` and `@msuaaaa` to the sentence rendered beside a row for
the `WITH_CONTEXT` task. The task it serves (`precheck_v2ctx_with_post`) is a **closed** probe
whose verdict was KILL, so nothing live renders it today; under a new composition the mapping
silently matches nothing. Listed for completeness, and because `prompts.py` is a battle module.

### L6 · `src/market_pulse/positions.py:475` — a closed unit list (documented, still a constraint)

`SIZE_PRICE_UNITS = ("кг", "мл", "грн", "г", "л", "%")`. Coffee survives it; a category sold by
the piece («6 шт») does not — the pre-filter's second half never fires and the yield reads zero.
The module names this itself as a named revision rather than a tweak, which is why it is last:
it is a documented domain assumption, not a hidden one.

### Out of both levels, recorded once

Currency is Ukrainian throughout (`positions.parse_price` strips `грн|₴|uah`,
`market_screen_5c1.py` compiles `грн / ₴ / гривня / UAH`). Neither level (a) nor level (b) changes
the country, so this is noted and not counted as a leak.

---

# Deliverable B — the dry-run probe

`scripts/uni_probe.py` → `results/uni_probe.json`. A toy registry (category «кава», four
subcategories, three real coffee brands, **the live `sources` block carried over unchanged**) and
a toy lexicon are materialised in a tempdir and deleted at exit. `data/raw/` is read, never
written. No live file is modified. $0, no model.

```
follows-registry         1 · positions.category_keys over the toy taxonomy
hard-coded               2 · the deterministic pre-filter over the corpus
follows-registry         3 · the strict parser and the tier ladder
follows-registry         4 · brand resolution over the toy watchlist
needs-new-registration   5 · prompt instantiation

step 2 controls: OK
wrote results/uni_probe.json
```

**Step 1 — `follows-registry`.** Handed the toy taxonomy, `category_keys` returns
`coffee · coffee-beans · coffee-capsules · ground-coffee · instant-coffee` and **`overlap_with_live:
[]`**. The docstring's claim is now a measurement.

**Step 2 — `hard-coded`, split by half.** Brand half `follows-registry`, category half
`hard-coded`. The 11-vs-90 measurement is above under L1. The probe **had to write a second toy
file** for this step to run at all (Dv121). Controls: the toy positive line passes, all four
negatives fail to pass, including the live census's dairy control.

**Step 3 — `follows-registry`.** Ten synthetic coffee replies through `parse_positions` and the
ladder: 0 parse failures, and all ten tier lists equal to what was asserted. Negative control: the
dairy reply is refused — `entry 0 category 'milk' is outside the taxonomy`. `ladder_sha256` is
recorded in the artifact. *(Worth stating: the probe's own first fixture was wrong — a hedged
price beside a category was expected to be a `position` and the ladder returned `product_mention`,
correctly, because a price is not a differentiating attribute. The assert caught it. A step that
printed tiers instead of asserting them would have printed a plausible wrong list.)*

**Step 4 — `follows-registry`, with a priced caveat.** 3 toy brands → 4 aliases. Of 12 spellings,
**8 resolve, 4 do not**: «Nescafe» without its diacritic, the inflected «Галку», «Lavazza» (outside
the watchlist, kept as `brand_raw` — correct), «Яготинське» (a dairy brand, correctly unresolved
under a coffee registry). The two real losses price the exactness of a casefolded table with no
stemming, no diacritic folding and no transliteration.

**Step 5 — `needs-new-registration`.** There is **no generator**: measured by walking every public
callable in `market_pulse.prompts` for a `taxonomy` / `registry` / `categories` / `watchlist` /
`aliases` parameter — **the list is empty**. `PROMPTS` is 16 literal strings; the position prompts
are concatenation and a `_swap` at import time. What a new domain must write anew, by line class:
the category paragraph, the eleven-value enum, the shape example («Рудь · Пломбір · ice-cream»).
Reusable as written: both intros (they name the LEG) and the 12 schema rules.

**Steps 1 and 5 are one finding.** The registered page prompt says, verbatim and grepped back out
of the imported module:

> chocolate, sausage, coffee, nappies and cheese-flavoured snacks are not dairy

The parser would accept a coffee category; this prompt would never produce one. Step 1 reported
alone reads as a green light for level (b), and that reading is wrong.

---

# Deliverable C — `docs/PORTING.md`

269 lines, English, every claim citing `results/uni_probe.json` or the sweep, every quote grepped
back into its source. Level (a) writes down the existing procedure (the 08.08 +3-brands precedent
in its own words) and adds the three costs the ruling did not name: the lexicon has no brand
section to receive anything (Dv6, re-measured); `entry_check.py::CANDIDATES` is 96 hand-transcribed
handles beside the registry edit; and of the **8 `results/` files pinning the registry sha, 3 still
hold the live `920c7f20…`** — `sku_pilot_prereg.json`, `sku_prefilter_census.json`,
`sku_reference_leaflet.json` — so a level-(a) edit during phase B would move a sha its own
pre-registration pins. The other 5 already hold the pre-signature `c82d0cff…` and refuse to run,
which is correct and documented.

Level (b) is ordered by what blocks what: lexicon → taxonomy block → two new registered prompts →
the unit list → the watchlist → the `fat` ruling → new gold and re-earned gates → the adapter.

**The `fat` SPEC question, flagged and not decided.** `fat` ∈ `positions.PRESENCE_FIELDS` →
`ladder_table()` → `ladder_sha256()` = `b497c072…`, **pinned in `results/sku_pilot_prereg.json`**
(line 68, whole 32-row table at line 125, with the prereg's own "the ladder is an INPUT to the
bar"). Generalising `fat` to an `attribute` is therefore not a rename: it moves a sha a live
pre-registration holds. It is possible **before sku-b starts or after B closes, never between.**
This phase takes no position on which.

---

# Verify

| the brief asks | measured |
|---|---|
| `make check` green, 1611 / 2 skipped, no new fast-suite tests | green at each of five points — session start, after the `CLAUDE.md` edit, after the probe, after `PORTING.md`, and after this report; last quoted: `1611 passed, 2 skipped in 47.45s` |
| ruff clean | `All checks passed!` · `ruff format --check .` → **212 files already formatted** (211 + `uni_probe.py`) |
| live `config/registry.yaml` sha unchanged | `920c7f203b9f0e38fd8df9e893d9b15705a6b19b297bd9d14b14258ae38ac3be` — the literal the brief names, recorded in `results/uni_probe.json` beside the toy `34723b80…` |
| `prompts.PROMPTS` still 16 entries, shas unchanged | **16 entries, 15 distinct shas** (the RENDER_ONLY twin shares one); `positions_post_gm4` `ca6303c157d4` and `positions_text_gm4` `7250b87aa1c2` both still match their pins in `results/sku_pilot_prereg.json` |
| the only new `results/` file is `results/uni_probe.json` | `git status` after the probe: `?? results/uni_probe.json`, `?? scripts/uni_probe.py`, nothing else |
| nothing immutable moved | all **267** files that were under `results/` before this phase, `config/registry.yaml`, `config/qlora.yaml`, `data/category_lexicon_draft.json`, `src/market_pulse/prompts.py` and all **110** files under `data/raw` + `data/frozen` hash to their pre-phase values — **0 mismatches**, baselined before the first write-capable action and re-checked AFTER the suite ran. The directory now holds 268: the 268th is `results/uni_probe.json`, this phase's only new file, which by construction has no baseline |
| wikilinks green | `check-wikilinks: OK, none broken` (re-run after `PORTING.md` landed) |
| Deviations Dv119+ | filed as **Dv121–Dv124** — see below |
| report at `docs/reports/uni-a.md` | this file |
| $0 | no model loaded, no request sent. The probe is a deterministic function of the repository |

Reproducibility of the artifact: two consecutive runs are **byte-identical apart from
`generated_at` and the `git` block**, checked by comparing the two records with those fields
removed.

---

# Deviations

Numbering note, not a deviation: the brief says "continue at Dv119", and arch-a filed **Dv112–
Dv120**. uni-a starts at **Dv121** rather than colliding or renumbering another phase's history.

**Dv121 — the probe needed a SECOND toy file, and that necessity is the phase's main finding.**
The brief anticipates "a TOY registry materialized at runtime in a tempdir". Step 2 cannot run
against a registry alone: `positions.prefilter` takes `compiled`, which comes from
`yield_screen.compile_categories(lexicon)` — a lexicon, never a `Taxonomy`. So
`scripts/uni_probe.py` also writes a toy lexicon in the tempdir, in the shipped shape, reusing the
live `endings` so the matcher is unchanged. Both toy files are recorded with their shas in the
artifact and both are deleted at exit. Without the second file the step would have been
UNMEASURED; with it, the leak is a number (11 vs 90).

**Dv122 — the brief's deliverable-C line "pre-filter category words (registry)" is not what the
code does.** Measured: the pre-filter's category half reads `data/category_lexicon_draft.json`
and the registry cannot reach it. The brief was committed unedited (`3f51757`) and `PORTING.md` is
written against the measurement, with the gap flagged here rather than silently reconciled. The
brand half of the same conjunction IS registry-driven, so the line is half right — which is
exactly why it needed measuring instead of reading.

**Dv123 — the sweep needed a fourth class, and its discriminator is silent vs loud.** The brief's
three classes have no home for a hard-coded value that refuses LOUDLY: `build_lexicon`'s
`SystemExit`, the yield screen's `ok: false` controls, the census's exit 1. Calling those LEAKs
would put a `SystemExit` beside a silently wrong number, and calling them
INSTANCE-PINNED-BY-DESIGN would hide that someone must act on a domain change. They are filed as
**LOUD REFUSAL**, and the instrument class from arch-a's inventory (battle / pilot-pending /
closed / one-shot) is carried as its own column instead of being folded into the verdict.

**Dv124 — `graphify path` failed its positive control and is cited nowhere as evidence.** The
brief says "use graphify queries + grep; cite the query per finding". `graphify query` and
`graphify explain` were used and are cited. `graphify path "config/registry.yaml"
"category_keys"` returns "No path found" for a link that exists in code, so the tool cannot
support an absence claim in this repository — an AST-only graph does not connect a YAML file to
the function that reads its parsed form. Recorded rather than quietly dropped, because a "no path
found" screenshot would have been the most persuasive-looking evidence in this report and it would
have been worthless.

---

# What the operator is being asked to rule on

1. **The six LEAKs** (L1–L6), unfixed by contract. L1 is the only one on a money path: sku-b's
   text leg draws from a frame the lexicon defines. Nothing in sku-b's scope needs it changed —
   the dairy lexicon is correct for the dairy pilot — but the ruling on whether the category
   vocabulary belongs in the registry, in the lexicon, or in both with a generator, is the shape
   of level (b)'s first step.
2. **The `fat` field** — a SPEC question with an ordering constraint (before sku-b or after B,
   never between). This phase decides nothing.
3. **`docs/PORTING.md`** as the standing procedure for both levels, or amendments to it.

Operator budget at acceptance, per the brief: ~20–30 min.

# Porting — what it costs to change the domain

How this system moves when `config/registry.yaml` changes. Two levels, ruled by the operator on
2026-08-11: **(a)** new brands or new channels inside the tracked category, and **(b)** a new
retail category. Beyond-Telegram is one paragraph of contour at the end and nothing more.

Every claim here cites a measurement. The measurements are `results/uni_probe.json` (the uni-a dry
run: a toy «кава» registry driven through the shipped code, $0, no model), its re-run
`results/uni_probe_v2.json` (uni-b, the same probe under the changed code) and the domain-leak
sweep recorded in `docs/reports/uni-a.md`. Where this document and the code disagree, the code is
right and this document is stale — say so and fix the document.

**uni-b (2026-08-11, SPEC 3.17 (8)) closed four of the leaks this document was written around.**
The category vocabulary is law in `config/lexicon.yaml` and follows a registry edit; the unit list
moved into it; the schema's fifth presence field is `attribute`, not `fat`; and the two silent
zeros (L2, L3) are loud refusals. What did NOT change is the expensive half — the registered
prompt texts, the gold, the bars. Sections marked **[uni-b]** below are the ones whose cost moved.

## The one-line answer

The **schema** follows the registry. The **vocabulary** does now too — the prompts still do not.

*(Before uni-b this line ended at "does not", and the file it pointed at was
`data/category_lexicon_draft.json`. That half is fixed; the sentence is kept in its corrected form
rather than deleted, because the SHAPE of the finding is what the cost model below rests on.)*

`positions.category_keys`, the parser, the tier ladder and both brand resolvers read whatever
registry they are handed — measured, not asserted (uni_probe steps 1, 3, 4). The words that decide
which rows are looked at and what the model is asked for lived in two places the registry could not
reach: `data/category_lexicon_draft.json` and the registered prompt texts in
`src/market_pulse/prompts.py`. The first is now `config/lexicon.yaml`, a law file with a guard
tying its stems to the registry's display names; the second is unchanged and unchangeable — a
registered text is replaced by a NEW registration, never edited (SPEC 3.17 (5)). That split is
still the whole cost model below, with one side of it now cheap.

---

# Level (a) — new brands, new channels, same category

This procedure already exists and has been executed. It is written down here, not invented.

## (a.1) A new watchlist brand

**Precedent:** the operator's ruling of 2026-08-08, `docs/STATUS.md`: watchlist **+3 brands** — ТМ
«Заріг», ТМ «Миргородська корівка» and «Яготинське для дітей» as its own row. The ruling's own
words for the path are «WATCHLIST → реестр → лексикон, $0, офлайн», the executor enters it inside
the yield-screen contract, the discovery plan gains +3 queries, and **old G1e numbers are not
re-computed — the watchlist revision goes into provenance instead**.

| # | step | owner | cost |
|---|---|---|---|
| 1 | The ruling: which brand, which display names, why it is tracked | operator | — |
| 2 | `docs/WATCHLIST.md` / `docs/CHANNELS-launch.md` — the canon gains the row | operator's canon, executor transcribes | $0 |
| 3 | `config/registry.yaml` → one `watchlist` entry: `brand_id` + every `display_names` spelling | executor | $0 |
| 4 | The lexicon is NOT touched | — | $0 |
| 5 | Re-run the yield screen / the censuses that read the watchlist, with an explicit `--out` | executor | $0, offline |
| 6 | Name the revision in provenance; do not re-score history | executor | $0 |

**Step 4 is a correction of the ruling's own text.** The ruling names three files, and the third
has nothing to receive a brand: `data/category_lexicon_draft.json` has **no brand section at all**
— its `tracked` half is 14 dairy stems and 2 ice-cream stems, seeded from the taxonomy's display
names. This was recorded as Dv6 when the +3 landed and it is still true (uni-a re-measured it).

**Step 3 is strict on purpose.** `registry.load_registry` refuses a duplicate `brand_id` and a
brand with no `display_names`, naming the defect. What it cannot refuse is a MISSING spelling, and
that is the real cost of this step: `brands.watchlist_aliases` is a casefolded exact lookup with
no stemming, no diacritic folding and no transliteration. uni_probe step 4 measured it on twelve
strings against a three-brand toy watchlist: **8 resolved, 4 did not** — and two of the four are
the honest cost of exactness rather than a bug: «Nescafe» written without its diacritic does not
resolve to the registered «Nescafé», and the accusative «Галку» does not resolve to «Галка». Every
spelling a source actually uses has to be a registered `display_name`.

**What step 6 costs, precisely.** Nine files under `results/` pin the registry's sha256. Five of
them already hold pre-signature bytes (`c82d0cff…`) and refuse to re-run, which is correct and
documented. **Four hold the live `920c7f20…`** (re-measured after uni-b, which added the fourth):

- `results/sku_pilot_prereg.json` — sku-b's pre-registration as first registered, now sealed
- `results/sku_pilot_prereg_v2.json` — its uni-b re-registration, the LIVE one
- `results/sku_prefilter_census.json` — the frame the sku-b text sample is drawn from
- `results/sku_reference_leaflet.json` — the leaflet gold

(`results/uni_probe.json` and `results/uni_probe_v2.json` carry the same string, but as a
MEASUREMENT — "the live registry was untouched while a toy one was driven through the code" — not
as a pin. Counting them here would inflate the cost of a registry edit by two files that judge
nothing.)

A level-(a) edit moves all four to stale. **Two of them are inputs to the paid attempt that has
not run yet**, so a watchlist edit *during* phase B is a collision, not a chore: it would move the
sha a live pre-registration pins. The window for a level-(a) edit is before sku-b starts or after
B closes.

## (a.2) A new channel

The entry path is the track-R gate with its mandatory relevance floor (SPEC amendment 3.12 (1)).

| # | step | owner | cost |
|---|---|---|---|
| 1 | Discovery: `scripts/discover_channels.py` over the AUTHORISED themes, or Telegram's content-first post search (3.12 (2)) | executor, themes are the operator's | $0 (+ Premium/Stars for search) |
| 2 | The candidate list reaches `docs/CHANNELS-launch.md` — the canon | operator | — |
| 3 | `scripts/entry_check.py`'s `CANDIDATES` tuple gains the handle and its bucket | executor | $0 |
| 4 | The gate runs: resolve, comments, traffic, script mix, pre-registered verdict | executor | $0, Telegram only |
| 5 | The yield screen's bars A/B over the channel's own 28-day window | executor | $0, offline |
| 6 | The operator rules PASS / FAIL / FLAG; `apply_gate_rulings_5c1.py` writes the registry | operator, then executor | $0 |

**Step 3 is the step the registry does not cover.** `CANDIDATES` is **96 handles** — 29
`comments`, 21 `city`, 18 `posts`, 14 `watch`, 14 `late` — transcribed handle-for-handle from the
canon and held to it by `tests/test_entry_gate_5c1.py`: a battle script, edited by hand, beside
the registry edit. Its own comment says why: "this tuple and the
canon's tables must name the same channels in the same buckets, or the run is gating a composition
nobody chose."

**Two instruments re-register with the composition, and they fail LOUDLY if they do not** —
which is the behaviour wanted, and it is still a step someone has to take:

- `scripts/yield_screen_5c1.py`'s `POSITIVE_CONTROLS` — four dairy channels the project was built
  on, each pre-registered to clear bar A on its own window. A composition without them reports
  `ok: false`, not a silent pass.
- `scripts/language_census_5c1.py`'s `CONTROLS` — `@dpssgovua` (ua) and `@offspringrus` (ru), one
  of which is deliberately outside the registry.

**Two footguns on this path, both already recorded:** `apply_gate_rulings_5c1.remove_sources`
stamps `removed 2026-08-07` from a hardcoded literal, so the next channel to leave gets
yesterday's date on its tombstone; and `language_census_5c1.py` / `market_screen_5c1.py` refuse
their own default `--out`, because their shipped records are dated measurements a ruling cites.

## (a.3) What level (a) does NOT cost

No prompt is rewritten, no gold is rebuilt, no gate is re-earned, and no model is retrained.
`positions.resolve_brand` keeps an unregistered brand as `brand_raw` with its own identity rather
than dropping it (uni_probe step 4: «Lavazza» outside the toy watchlist resolves to `None` and is
kept), so a brand that is not yet on the watchlist is still collected — it simply does not
aggregate under a watchlist id. **Cost: ≈ $0.**

---

# Level (b) — a new retail category

Ordered by what blocks what, not by cost. Nothing downstream measures anything until step 1 and
step 2 exist.

## The headline, measured

**The parser accepts a vocabulary the prompt forbids.** Handed a toy taxonomy of coffee,
`positions.category_keys` returns the five coffee keys and none of the eleven dairy ones
(uni_probe step 1, `overlap_with_live: []`), and the strict parser accepts all ten synthetic
coffee replies while refusing `milk` as outside the taxonomy (step 3). The registered page prompt,
meanwhile, instructs the model to refuse coffee **by name**:

> chocolate, sausage, coffee, nappies and cheese-flavoured snacks are not dairy

(`src/market_pulse/prompts.POSITIONS_BODY`, grepped back out of the imported module by the probe.)
Step 1 read alone says "the schema is universal, ship it". Step 5 read beside it says what that is
worth without a new registered prompt: nothing. **They are one finding.**

And the pre-filter, measured over a deterministic 2,000-row corpus sample (8 channels, sorted file
order, texted rows only): **11 rows pass under a toy coffee lexicon; 90 rows pass under the LIVE
lexicon standing beside the toy registry** — every one of the 90 on a dairy stem («сир» 26, «масл»
17, «молок» 11, «сметан» 11, «морозив» 11). The registry said coffee and the filter kept reading
dairy. That is the silent failure this checklist exists to prevent.

## The checklist

### 1 · The category lexicon — FIRST, and it is LAW now **[uni-b]**

`config/lexicon.yaml` needs a new `tracked` family: the stems of the new category under the
lexicon's own matcher (`stem + one of endings, bounded by non-word characters`). Nothing
downstream can measure the new category until it exists — the uni-a probe itself had to write a
toy lexicon in a tempdir before step 2 could run at all.

The guard moved onto the law with it. `market_pulse.lexicon.load_lexicon(path, taxonomy=…)` checks
every tracked stem against the registry's display names and **raises loudly** when they do not
match (`… are not prefixes of any display name in the registry`), which is
`scripts/measure_categories.py::build_lexicon`'s own rule with ONE implementation, now called by
both. Swapping the taxonomy without swapping the stems is refused rather than measured as zero.

`data/category_lexicon_draft.json` stays on disk, frozen, `status: draft-not-law`: five committed
records pin its sha `1225ad75…` and the law's header names it as source with that sha. It is still
read as shipped by the 5c1 SCREEN instruments — `scripts/yield_screen_5c1.py` (battle),
`scripts/theme_screen_5c1.py` (through the producer) and `scripts/rematch_with_captions_5c1.py` —
which sealed their records against it; the pre-filter path (`scripts/sku_prefilter_census.py`,
`market_pulse.positions`) reads the law.

### 2 · The registry taxonomy block (cheap, registry edit only)

One `tracked_groups` entry with a display `name` and its `subcategories`. `load_registry` requires
a non-empty mapping and nothing else; `positions.category_keys` picks up both levels with no code
change — that is the property uni_probe step 1 proves rather than assumes.

### 3 · Two NEW registered prompts (cheap in money, manual in effort)

There is **no generator**. `prompts.PROMPTS` is a dict of literal strings, the page prompt is
`POSITIONS_PAGE_INTRO + POSITIONS_BODY` concatenated at import time and the text prompt is
`_swap`ped from it. The probe measured this by walking every public callable in the module for a
`taxonomy` / `registry` / `categories` / `watchlist` / `aliases` parameter: **the list is empty**.

What has to be written anew, by line class, measured off the live text:

| part | domain-bound? |
|---|---|
| page intro / text intro | No — they name the LEG (a leaflet page, a text row). Reusable as written |
| the category paragraph | **Yes** — names the eleven dairy kinds and excludes coffee by name. Rewritten in full |
| the category enum | **Yes** — eleven literal values the model may answer. A registry offering new keys changes nothing here |
| the shape example | **Yes** — «Рудь · Пломбір · ice-cream». A format illustration, written in the live domain |
| the schema rules (12 lines: OMIT-a-key, COMPUTE-NOTHING, the two-price rule, the empty array) | No — domain-free. Reusable as written |

Registration discipline, unchanged: the new prompts are added **beside** the dairy ones with their
own shas, never by editing a registered text. Today's two are `positions_post_gm4` `ca6303c157d4`
and `positions_text_gm4` `7250b87aa1c2`, both pinned — unchanged — in
`results/sku_pilot_prereg.json` and its uni-b re-registration `results/sku_pilot_prereg_v2.json`.

### 4 · The pre-filter's second half — the unit list (cheap, but a NAMED revision) **[uni-b]**

The six units `кг · мл · грн · г · л · %` are `units:` in `config/lexicon.yaml` and
`positions.SIZE_PRICE_UNITS` reads them from there. Coffee survives the list (a pack is grams), but
a category sold by the piece does not — «6 шт» is not a match, and widening the list moves the
sample frame the text bar of SPEC 3.17 (6) is measured over. It is a named revision and not a
tweak, and it is now pinned by sha in `results/sku_pilot_prereg_v2.json` like the registry is.

**The order is load-bearing.** Longest-first: a regex alternation takes the first branch that
matches, so «г» before «грн» reads "90 грн" as a size. `tests/test_lexicon.py` asserts the exact
sequence, not the set — an alphabetical tidy-up of that list is a silent breakage.

### 5 · The watchlist for the new category (cheap, with a structural caveat)

As level (a.1), with one difference that is structural rather than marginal: for a category whose
brands are Latin-script, the exact casefolded table costs more. «Nescafé» and «Nescafe» are two
keys, measured (uni_probe step 4). A Latin-brand category needs every spelling registered, or a
normalization decision — and normalization is a re-scoring decision with a plan, not a fix (the
homoglyph gap found on the 4.5a brands stratum is deferred for exactly this reason).

### 6 · The attribute field — RULED, and the ceremony it cost **[uni-b]**

`Position.attribute_pct` was `fat_pct` until SPEC 3.17 (8). A coffee position has roast and grind;
a detergent position has concentration — the ladder is a function of PRESENCE, and «жирність» was
only what a dairy source happens to differentiate a SKU by. The operator ruled the generalization
on 2026-08-11, before sku-b, which is the only window it had:

`attribute` is one of `positions.PRESENCE_FIELDS` → `PRESENCE_FIELDS` builds `ladder_table()` →
`ladder_table()` is hashed by `ladder_sha256()` → that hash is pinned inside the pilot's
pre-registration, whose own words are: "bar 3's gold is computed from the operator's ticks by this
ladder and the model's tier by the same function, so the ladder is an INPUT to the bar."

So it was never a rename. `b497c072…` → `6a257e04…`, and the price was a ceremony: SPEC 3.17 (8),
`results/sku_pilot_prereg_v2.json` registered BESIDE the sealed v1, the pack manifest rebuilt over
the new ladder. What did NOT move: any rung (the renamed table is a bijection onto the old one),
any threshold, the $0.35 cap, the one-attempt clause, the R1–R5 readings, the adjudicated
`text30.csv` or its `given_sha256`.

**Two things a new domain inherits from this.** The field is still percent-only —
`attribute_pct > 100` is refused and `parse_fat` takes «2,5%» — so a coffee attribute that is not a
percentage needs a schema decision, not just a registry edit. And the WIRE keeps the domain word:
the dairy prompts ask for `"fat"` and `positions.WIRE_KEYS` maps it to the schema, because a
registered prompt text is replaced by a new registration, never edited.

**Registering a new instrument family is TWO edits, not one:** a row in `positions.WIRE_KEYS`
(`{"coffee": {"attribute": "<the key that family's prompt asks for>"}}`) **and** that key in
`positions.REPLY_KEYS`, which is the closed vocabulary a reply may use. Do only the first and the
parser refuses the family by name — `family 'coffee' reads its attribute from …, which is not a key
the prompts ask for` — which is deliberate: before that guard existed, a coffee reply carrying
`"fat"` passed the key check and was then dropped in silence, and a reply carrying `"attribute"`
was refused as an unasked key. Two silent halves, both now loud.

**The window rule still stands for anything else of this shape:** a change that moves a pinned sha
happens **before sku-b starts or after B closes — never between.**

### 7 · New gold, new frozen sets, gates re-earned — THE IRREDUCIBLE COST

Numbers never transfer. Every bar in SPEC §5 and amendment 3.17 (6) is a number about the dairy
corpus, the dairy gold and the dairy prompts:

- a leaflet gold pack for the new category (today: `results/sku_reference_leaflet.json`, 19 ATB
  posts read by a reviewer)
- a text pack drawn from a **new** pre-filter census over the new lexicon (today:
  `results/sku_text_pack_manifest.json`, 30 rows at seed 42), adjudicated by the operator
- frozen test sets, if the classification family is to be re-gated at all
- the bars themselves pre-registered before any number is seen

There is no shortcut and no discount here. Everything cheap above is cheap because this step is
not.

### 8 · The adapter — reuse and MEASURE first, retrain only on measured failure

The serving adapter (4.5h2-arm-A, sha `b3ca6308…`) was trained on dairy comments for the
classification family; the position layer runs the NF4 base with the **adapter off**. The
discipline that governs this is the project's own ablation rule: score the artifact in the exact
configuration production will serve, compare arms on pre-registered criteria, and let the
measurement decide. A new category does not authorise a retrain — a measured failure does.

### 9 · The instruments that must be re-pointed, or they answer about dairy **[uni-b]**

Found by the uni-a sweep; the full table with classes is in `docs/reports/uni-a.md`. uni-b closed
or made loud everything above the line; what is left below it is what a new domain still pays.

**Closed:**

| was | now |
|---|---|
| `data/category_lexicon_draft.json` — the pre-filter kept passing dairy rows: 90 of 2,000 sampled, measured (L1) | `config/lexicon.yaml`, law, guarded against the registry's display names |
| `positions.SIZE_PRICE_UNITS` — a closed literal (L6) | `units:` in the same law file |
| `scripts/theme_screen_5c1.py::TRACKED = ("dairy", "ice-cream")` — a literal whose docstring called it the registry's (L2) | `tracked_groups(registry, compiled)`; an empty intersection is `SystemExit`, never a table of zeros |
| `scripts/measure_categories.py::coverage()` — `tracked = {"dairy", "ice-cream"}` (L3) | the same, in the script that produces the draft |
| `src/market_pulse/entry_check.py::PRE_REGISTERED_FLAGS` — three 5c1 handles (L4) | the keys stay (transcribed ruling, provenance); the gate record now carries `flags_unmatched` naming any key the composition no longer holds |
| `src/market_pulse/prompts.py::SENDER_CONTEXT` — two channel identities inside `src/` (L5) | unchanged BY LAW — a registered text file is not edited — but fenced: the lines render only for `precheck_v2ctx_with_post`, a closed 4.5g4 revision in no live task set, and `tests/test_prompts.py` holds that reach. A new domain inherits an unreachable dictionary, not two channel identities in its prompts |

**Still open:**

| instrument | what a new domain would observe |
|---|---|
| the registered prompt texts (`positions_post_gm4`, `positions_text_gm4`) | the model is asked about eleven dairy kinds and told to exclude coffee by name. Two NEW registrations — step 3 above |
| the nine `results/` files pinning the registry sha | five already stale, the rest go stale on the first edit |
| every gold pack, frozen set and bar | step 7 — the irreducible cost |

---

## Beyond Telegram — the contour, not a design

SPEC §1 fixes the MVP constraint in the operator's own terms: **Telegram-only, $0 data budget. "X
API, FB/IG scrapers, and website monitoring are future extensions behind a source-agnostic
connector interface — out of MVP scope, no code for them."** §6 states the same shape from the
pipeline's side: the connector interface is source-agnostic so X/FB/IG/web can be added later
without touching the core, and track R in §11 carries them as deferred with a decision record per
source. What the uni-a measurements add to that contour is only this: the parts of the core that
would sit behind such a connector — the schema, the parser, the ladder, brand resolution — already
take their domain as an argument, and the parts that would not — the lexicon file, the registered
prompts, the gold — are the same parts level (b) pays for. **Nothing is designed here, no
interface is sketched, and no code exists for any non-Telegram source.**

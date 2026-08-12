# skub2-prep — instrument v2 and the B′ registration, before the re-measurement ($0)

`docs/PROMPT-skub2-prep.md` · authority SPEC §3.17 (13), ratified 2026-08-12 · executor, $0, no
paid calls · 2026-08-12.

Five deliverables, sixteen commits, `d3fa574..<the vault tail>`. Four of the five landed as files
on disk.
The fifth — the B′ pre-registration — **is a producer that refuses**, because four decomposition
pairs are still `PENDING_TEAM_LEAD` and each of them can still leave the denominator it would
register.

> **This section is skub2-prep's record and its numbers are that session's.** SPEC 3.17 (14) landed
> after it: the four pairs are read, the registration writes, the gold is 37 pairs over 10 posts and
> the cap is $0.65. The **§Fix** section at the foot of this file is the current state; where the
> two disagree, Fix is later.

---

## What the session produced

| # | Deliverable | Where it landed |
| --- | --- | --- |
| 1 | The decomposition verdicts applied | `results/sku_miss_decomposition.json` |
| 2 | Instrument v2 — the parser family and the ceiling | `src/market_pulse/positions.py`, `src/market_pulse/local_llm.py`, `results/sku_pilot_serving_v2.json` |
| 3 | The three evidenced Latin aliases | `config/registry.yaml`, `src/market_pulse/registry.py` |
| 4 | The B′ pre-registration | `scripts/write_sku_prereg_b2.py` — **refuses; no record** |
| 5 | The projection against $0.40 | `results/sku_projection_b2.json` |

`make check` after the last commit:

```
$ python3 -m pytest -q
1969 passed, 2 skipped in 58.89s
$ ruff check . && ruff format --check .
All checks passed!
244 files already formatted
```

1854 tests at the start of the day, 1869 after the miss-pack contract, **1969** now.

---

## Deliverable 1 — the 29 misses, decomposed

`results/sku_miss_decomposition.json`, written by `scripts/apply_miss_decomposition.py`. The team
lead's 25 dictated rulings joined to the pack's own rows, and four deferred:

```
$ PYTHONPATH=src python3 scripts/apply_miss_decomposition.py
results/sku_miss_pack.json — 29 missed pairs, each ruled on or deferred exactly once
  a 11 · b 12 · c 2 · pending_team_lead 4 (#4, #9, #28, #29)
  11 mechanism(s) checked against the instrument's own refusal reasons
     5  non-dairy watchlist item
     5  refusal:token-ceiling
     4  PENDING_TEAM_LEAD
     3  refusal:multipack
     2  SKU-name-vs-TM
     2  maker-logo
     2  refusal:asterisk
     1  alias:latin-form
     1  dairy-adjacent, reviewer's own caveat
     1  gold-key artifact — brand was found
     1  non-dairy
     1  non-dairy, by-pattern
     1  two-brands-one-box
wrote results/sku_miss_decomposition.json
```

The counts are the contract's own sentence, transcribed, never computed from the table they check.
Both halves of the pack are pinned by sha — the **markdown** as well as the JSON, because the row
numbers 1..29 the dictation speaks in are printed in the markdown, so it is the markdown that has
to be unmoved for a row number to mean what the team lead meant.

**The one check here that is not a transcription.** Every `refusal:*` ruling is held against the
reason the extractor itself wrote on that post's refused page:

| mechanism | the page the read blames | what the extractor recorded |
| --- | --- | --- |
| `refusal:asterisk` | 4340 p3, 4467 p1 | `printed discount '-50%*' is not a percentage` |
| `refusal:token-ceiling` | 4401 p5 | `malformed JSON` |
| `refusal:multipack` | 4446 p1 | `size '6х100 г' is a multipack — a pack count is not a size` |

Eleven of the 25 carry that evidence (ten refusals and the one alias gap, which is held against
that post's unmatched extraction instead). The classes themselves are not checkable from here and
are not checked: only the images can say whether a brand carried a price box.

`b_prime_denominator.final` is `null` while any pair is pending. That field is what deliverable 4
refuses on.

---

## Deliverable 3 — the three Latin aliases, and the eight pins they moved

Taken before deliverable 2 in this report because its blast radius is what shaped the session.

`config/registry.yaml`, aliases only — no row added, none removed, no `own` flag moved, asserted as
an entity diff rather than claimed. The evidence sits **on each row**:

| brand | alias | evidence |
| --- | --- | --- |
| `rud` | `Rud` | reviewer, `results/opus_audit_5c1.json` @ekomarket_shop:1450 — «Морозиво «Ескімос Панкейк» Rud, 60 г»; «Latin-script Rud is the brand's own logo form … but the canon table lists only Cyrillic «Рудь»» |
| `try-vedmedi` | `Three Bears` | reviewer, `results/sku_reference_leaflet.json` @atb_market_official:4340 — «Page 4341 headline reads ТМ «Три Ведмеді» while the caption renders it as «Three Bears» -- a Latin form the canon table has no alias for»; extracted and unmatched, decomposition row 2 |
| `limo` | `LIMO` | **no reviewer note names it.** The evidence is the instrument's own: two positions read off `atb_market_official_4360` page 1 as «Limo» with `brand_id: null` (`results/sku_b_positions_v4.jsonl`) |

The negative half is why this is three named forms and not a transliteration rule: juice ТМ
«Galicia» on `atb_market_official_4510` must **not** reach `halychyna`. Tested both ways, plus a
closed-list test that «Yagotynske», «Selianske», «Prostokvashino», «Premia» and «Harmonia» are
absent — the table grows by named row, never by pattern.

### Dv196 — the edit moves a sha that eight sealed records pin

`config/registry.yaml` is pinned by `sku_pilot_prereg{,_v2,_v3,_v4}.json`,
`sku_reference_leaflet.json`, `sku_prefilter_census.json`, `uni_probe{,_v2}.json` and cited by
`yield_screen_5c1.json`. **None of them is re-pinned.** The chain is written down instead:

* `market_pulse.registry.registry_before_the_latin_aliases(path)` — drops every line carrying the
  `# (13)(b)` prefix and undoes the three enumerated `display_names` lists. It reproduces
  `920c7f20…` exactly, which is what v1–v4 pin.
* `market_pulse.registry.load_registry_as_pinned(pin, path)` — today's file when it hashes to the
  pin, that reconstruction when it does not, and a **refusal** otherwise. `sku_bar_verdicts` and
  `build_sku_miss_pack` now take their alias table from the pre-registration through this call
  rather than from disk.
* `tests/test_registry.py` grows a second link in the signed-screen chain: the stamp strip alone no
  longer reaches `c82d0cff…` and that is asserted, the composed reconstruction does, and the middle
  sha `920c7f20…` is nailed down too.

The enumeration in `LATIN_ALIASES_13B` is literal, with a negative control: a fourth alias added to
one of those three rows without a line here makes the reconstruction refuse rather than silently
produce bytes nobody registered.

Proof that nothing sealed moved:

```
$ PYTHONPATH=src python3 scripts/sku_bar_verdicts.py --out <tmp>/verdicts.json
  leaflet_brand_recall       0.3603 vs 0.75   FAIL
  price_pair_accuracy        0.3279 vs 0.80   FAIL
  text_tier_accuracy         0.8621 vs 0.85   PASS
rebuilds identically: True
```

### Dv197 — the key space moved with it, and a test had already said so

`gold_key` returns the brand_id when a name resolves and `raw:` + the name when it does not. «Rud»
and «LIMO» casefold onto their **own brand_ids**, so `gold_key("rud")` now answers `rud` where the
sealed reference stores `raw:rud`. «Three Bears» does not — it is not `try-vedmedi` — so that key
is unmoved. The result is a gold key space whose shape depends on whether a brand's Latin form
happens to equal its id.

This was found by `test_bar_one_puts_a_resolved_watchlist_brand_in_the_reviewers_key_space`, whose
docstring already read: *«if either changed, one of these two posts would silently read 0.5 instead
of 1.0»*. It changed. The standing hazard is now written into that test: **bar 1 holds its gold
half STORED and recomputes its prediction half**, so the two agree only while the stored keys came
from the same alias table. Which is why the sealed v4 bar is recomputed through the table its
pre-registration pins, and why the B′ gold is REBUILT rather than filtered.

---

## Deliverable 2 — instrument v2

### The parser family ((13)(a))

Three strings that used to cost a whole leaflet page are read now and recorded as **warnings** on
the position. `Position` gains two required fields and a `warnings()` method:

| input | before | now |
| --- | --- | --- |
| `-50%*` | page refused | `50.0` + `discount_footnote: true` |
| `6х100 г` | page refused | `size 100 г` + `pack_count: 6` — never multiplied into 600 |
| `від 39,90` | page refused | `39.9` + `price_qualifier: "from"` |

`QUALIFIERS` gains `"from"` with a **stated precedence** — `from` > `approx` > `exact` — because a
floor is a bound rather than a noisy point estimate and one record can carry both hedges in two
price fields. Before this the winner was whichever price the loop read first.

`warnings` is in `assert_no_imputation`'s list of things that must not be storable, and
`pack_count` / `discount_footnote` / `warnings` are in `DECIDED_BY_CODE` so a reply cannot claim
its own.

**The widening is not salvage.** A truncated tail is still a parse refusal — the ceiling and the
parser are the two separate halves of (13)(a), and a parser that repaired truncation would hide
whether the ceiling did anything.

### The ceiling ((13)(a)): 800 → 1200

`local_llm.POSITIONS_MAX_NEW_TOKENS`. It is what bar 1 lost its densest page to: 4401 page 5 came
back `malformed JSON` — a reply that used its whole budget — and that one page carried **five** of
the 29 missed gold pairs.

`results/sku_pilot_serving_v2.json` registers the move BESIDE the sealed v1 pin:

```
$ PYTHONPATH=src python3 scripts/write_sku_serving_pin_v2.py
wrote results/sku_pilot_serving_v2.json  (beside results/sku_pilot_serving.json, which stays sealed)
  config        POSITIONS / base-no-adapter
  revision      842da3794eaa0b77d5f08bae87a17459d91ff475
  generation    greedy, batch 1, max_new_tokens 1200 (v1: 800)
  moved         ['max_new_tokens'] — every other expected_worker field is v1's
  positions_post_gm4   ca6303c157d46e70…
  positions_text_gm4   7250b87aa1c2de40…
```

The producer refuses if a second knob moves, and refuses if the ceiling ever goes **down** — a
lower one would truncate exactly the pages the amendment exists to keep. Both driven with controls.

v1's pin and v1's projection now transcribe 800 as their own historical constant instead of reading
the live one. And v1's identity stop now **refuses this checkout's worker by name**
(`max_new_tokens: worker says 1200, expected 800`), which is the guard working across a revision
rather than in spite of one; the same block passes once the one moved knob is put back.

### Dv199 — the warnings do not reach the dump, and that is asserted

The dump's columns are DERIVED from the registered `price_pair_accuracy.procedure` sentence, which
B′ keeps byte-equal to v4. So `pack_count` and `discount_footnote` are on the `Position` and in the
preflight, and **not** in the dump. Carrying them into the run record's per-page outcome is
skub2-run's step. `test_a_row_carries_every_registered_column_in_order` now asserts their absence,
so the sealed column list is shown not to have moved under the amendment rather than assumed.

### The preflight, re-driven

```
$ PYTHONPATH=src <peftvenv>/bin/python scripts/preflight_serving_guards.py
EXIT=0    PASS 40    FAIL 0
local   transformers 5.14.1 · peft 0.20.0 · torch 2.13.0
volume  transformers 5.14.1 · peft 0.20.0
```

30 checks before, 40 now, every existing control kept. The new section verbatim:

```
--- SPEC 3.17 (13)(a): the parser family, warnings instead of page refusals ---
   -50%* (atb_market_official 4340 p3, 4467 p1)   ACCEPT     discount_footnote · discount_pct_printed=50.0
   6х100 г (atb_market_official 4446 p1)          ACCEPT     multipack · pack_count=6
   від 39,90 (the one-sided range)                ACCEPT     price_from · price_qualifier=from
   the multipack's size is the UNIT size          100.0 г  (not 600)
   still refused, so the widening is not salvage:
     2х0,5 л х 3 — not one count and one unit size  REFUSE
     1х100 г — a pack starts at two                 REFUSE
     80-90 — a written-out range is two prices      REFUSE
     -50%*** — three asterisks is not a footnote    REFUSE
     39,90 від Рудь — «від» is not leading          REFUSE
   the control: an unremarkable position          warnings ()
```

The three accepted strings are the **actual** strings v4 pages were refused on, read out of the
decomposition's refusal reasons rather than invented.

**Dv200:** the peft venv the earlier sessions used no longer exists on this machine. It was rebuilt
at the pinned versions before the preflight ran; an unrunnable preflight is a finding, not a pass.

---

## Deliverable 4 — the B′ pre-registration, which does not exist yet

```
$ PYTHONPATH=src python3 scripts/write_sku_prereg_b2.py
refused: 4 missed pair(s) are still PENDING_TEAM_LEAD: [4, 9, 28, 29]. SPEC 3.17 (13)(c)
builds the B′ gold out of these verdicts and each of these rows can still leave the
denominator, so registering now would register a denominator that moves afterwards. The team
lead reads them at the B′-prep acceptance and this producer runs then.
EXIT=1
```

**Dv201.** `results/sku_pilot_prereg_b2.json` is not on disk and must not be. Nothing was inferred
about #4, #9, #28 or #29 — three of the four are `svoia-liniia` rows and the team lead ruled five
of those separately anyway, so the pattern is exactly the wrong thing to extrapolate from.

The build is exercised regardless: `tests/test_sku_prereg_b2.py` resolves the four inside a fixture
(class `a`, the reading that moves the denominator **least**, so nothing passes because the fixture
removed the hard cases) and drives the whole producer. Under that fixture:

| | |
| --- | --- |
| gold | **41** pairs of 55, minus the 14 ruled b or c |
| posts in the macro mean | **11**, not v4's 15 |
| asymmetry | **9** pairs kept on a key ruled out elsewhere |

### Dv202 — the rescope empties four posts

`@atb_market_official:4377`, `:4411`, `:4421` and `:4498` each carried exactly one gold key —
`raw:svoia-liniia`, all four ruled class b. Removing it empties their gold, so under R3's own rule
(*an empty gold set is a precision probe*) they leave the recall average. **Bar 1's macro mean is
over 11 posts.** Registered as B5 rather than decided.

### Dv203 — the rescope can only remove misses, and that moves recall up on both sides

A class exists only for a pair the instrument **missed**. So (13)(c) can never remove a pair the
instrument found — and **9** pairs sit on a gold key the same team lead ruled out of the
denominator on another post:

| what the pair was | n |
| --- | --- |
| found by v1 | 6 |
| class a | 3 |

All nine are `raw:svoia-liniia` or `raw:каштан`. The six found ones are pairs instrument v2 will
very likely find again, and they stay in a 41-pair denominator while their twins leave. The
rescope therefore lifts recall from both directions. Reported in the record, gating nothing, and
put to the team lead as **B4**: whether a brand ruled «non-dairy watchlist item» or «maker logo» is
out of scope EVERYWHERE is not the executor's ruling, and the two readings move the bar in opposite
directions.

### Two things the producer does that v4's does not

**It pins a law that contains its own authority.** `registered_law` strips every marked
ratification block; v1–v4 predate all of them and B′ does not — it is registered UNDER (13). So the
function grows a `keep` parameter (one implementation, two callers) and B′ keeps `-7` while
stripping the six before it. Asserted three ways: the pin is not the live file, not v4's pin, and
`800 → **1200**` is inside the pinned law.

**It rebuilds the gold instead of filtering it.** Every reviewer name is keyed **twice** — once
under v4's alias table, which is the space the decomposition's rows are written in and the only
space the join happens in, and once under today's, which is what goes into the gold. The `raw:rud`
→ `rud` migration happens by re-keying and never by stripping a prefix, which would also have
matched `raw:try-vedmedi` to `try-vedmedi`. A pair that matches no reviewer name is a refusal.

**`config/registry.yaml` is pinned LIVE** here — the opposite of every earlier registration —
because (13)(b) is part of the instrument being registered. The three halves of instrument v2 are
each pinned where they can actually be read: the parser module sha, serving pin v2, the registry.

The bars' **verbatim texts and thresholds** are byte-equal to v4, with a negative control on both.

### Dv209 — the three readings that were still counting v4's posts

Found in review, after the first build. Bar 1 was assembled as *v4's bar with the gold replaced*,
so three leaves stayed v4's while the gold said something else:

| leaf | said | should say |
| --- | --- | --- |
| `excluded.posts` | 4 empty-gold posts | 8 |
| `denominator` | «the 15 posts … all 55 pairs» | 11 posts, 41 pairs |
| `reachable` | «15 of 19 posts … 55 pairs» | 11 of 19, 41 pairs |

The record answered the same question two ways, and **B5 asked the team lead to ratify 11 while the
machine-readable field said 15**.

It is not cosmetic. `sku_bar_verdicts.bar_one` opens by comparing `excluded.posts` against the
reference's own empty-gold list and refuses if they differ. With v4's four inherited, that
comparison **matches** the sealed reference and waves a 15-post scoring through — reading gold from
the sealed reference in the **v4 key space** while instrument v2's extractions key as `rud` and
`limo`. Guaranteed misses on exactly the two brands (13)(b) exists to fix, silently, at the one
paid attempt.

Recomputed, the same guard **refuses**, so skub2-run cannot begin without pointing the scorer at
this record's own `gold.per_post`. `check_the_bars_did_not_move` now names all four moved leaves
literally — the contract holds the bars' *verbatim texts and thresholds* byte-equal and those are
untouched; these four are the registration's **reading**, and every one of them counts posts or
pairs. The equality `bar_one` depends on is asserted with a control that fires.

**Dv210 — the scorer's gold source is skub2-run's first step.** `bar_one` reads gold from
`reference["posts"][…]["brands_visible"]["gold_keys"]`. B′'s gold lives in
`bars.leaflet_brand_recall.gold.per_post` and is in a different key space. Same shape as Dv199:
this contract registers the denominator, and wiring the scorer to it is the run's step — now
guarded by a refusal rather than left to be noticed.

### Dv207 — (13)(d) against (11)(a), stated out loud

(11)(a) says each element is bought exactly once **across the program**; (13)(d) authorises «one
re-measurement of instrument v2 over the same 138 elements». A re-measurement of a changed
instrument cannot reuse the old instrument's answers — the 17 first-session pages and the 121 v4
pages were extracted at an 800-token ceiling by a parser that refused four of them. The registered
reading is that (13)(d) supersedes (11)(a) **for this registration only**, all 138 are re-asked, and
v1's answers stay on disk as v1's measurement. Registered as **B1**. There is no `resume` block.

---

## Deliverable 5 — the projection against $0.40

```
$ PYTHONPATH=src python3 scripts/write_sku_projection_b2.py
  measured      4.0161 s/page (n=91) · 2.8188 s/row (n=30) · boot 205.518–402.586 s
  boot low · decode none                      802.2 s  $0.2460  $0.2534 with drift
  boot low · decode the whole ceiling        1070.6 s  $0.3283  $0.3382 with drift
  boot high · decode none                     999.3 s  $0.3065  $0.3157 with drift
  boot high · decode the whole ceiling       1267.6 s  $0.3888  $0.4004 with drift
  vs the $0.40 cap: DOES NOT FIT — dearest $0.4004, headroom $-0.0004
  job timeout   900 s vs 2x181 s conservative — ok
```

This is the first sku-b projection with a completed session behind it: every rate is read off
`results/sku_b_positions_v4.json`. The text marginal is the one number no single field holds — the
in-run gates report one marginal across both legs, so it is the billed total less the page leg, and
the test re-derives it by hand rather than by calling the producer.

The boot is a **range** and is never averaged: the same configuration booted in 205.518 s once and
402.586 s once, 1.96x apart with n=1 on each side. An average would be a number neither session
measured — and it would sit under the cap while the high corner does not.

**None of those seconds is a rate at the new ceiling.** They were all billed at 800 tokens, so
4.0161 s/page is a **floor** at 1200. The pessimistic corner scales every call by 1200/800, a hard
upper bound since no reply can generate past the ceiling; the optimistic corner leaves the rates
alone, which is what happens if the single page v4 recorded as `malformed JSON` was the only one
truncated.

### Dv204 — the dearest corner grazes the cap

$0.4004 against $0.40: over by four hundredths of a cent, and **only** once the 3% drift term is
applied on top of a bound that is already a bound. Without it the same corner fits with $0.0112 to
spare, and the corner the measurement actually supports costs $0.2534. The record states both
readings; the executor chooses neither. What the cap admits is (13)(d)'s.

Three ways out, none of them taken here: accept the corner as a bound the in-run (10)(a) gate
protects the middle of; drop the drift term where the corner is already an upper bound; or move the
cap by a cent. What must not happen is discovering it in flight — the gate would refuse the session
after the boot is already billed, which is the outcome (12)(b) prices.

**Re-checked because a ceiling change could have broken it quietly:** the 900 s job timeout still
exceeds twice the longest job even at the conservative bound the driver's own test uses (2×181 s),
so one wedged worker still cannot out-bill the cap.

**Dv208:** `scripts/positions_gm4_skub.py` still carries v4's `CAP_USD`, `PHASE` and `LEDGER`.
Moving them to the B′ three (`$0.40`, `skub2`, `results/spend_skub2.json`) is skub2-run's step; this
contract prices the run and does not configure it.

---

## The checkout table

`python3 -m pytest -q` at every commit, in a detached worktree, with `724d65c` — the commit before
this contract — as the checker's own control.

```
724d65c  chore(vault): the review tail                      1 failed, 1868 passed, 2 skipped
d3fa574  chore(docs): SPEC 3.17 (13), the B' prep contract  2 failed, 1867 passed, 2 skipped
2b8a35d  test(sku-prereg): the seventh ratification block   1 failed, 1868 passed, 2 skipped
c951e8f  feat: the decomposition of bar 1's 29 misses       1 failed, 1891 passed, 2 skipped
c6f7774  feat: the three evidenced Latin aliases            1 failed, 1899 passed, 2 skipped
3492d70  feat: instrument v2 -- parser family and ceiling   1 failed, 1932 passed, 2 skipped
61369e4  feat: the B' pre-registration                      1 failed, 1953 passed, 2 skipped
7342e10  feat: the B' projection                            1 failed, 1965 passed, 2 skipped
d7f240f  data: the decomposition re-stamped                 1 failed, 1965 passed, 2 skipped
2b6ee3f  data: serving pin v2 re-stamped                    1 failed, 1965 passed, 2 skipped
0c4dfe1  data: the B' projection re-stamped                 1 failed, 1965 passed, 2 skipped
b39b55e  data: serving pin v2, the last sibling             1 failed, 1965 passed, 2 skipped
79eaccb  docs(report): skub2-prep                           1 failed, 1965 passed, 2 skipped
10bcc3a  chore(vault): the skub2-prep tail                  1 failed, 1965 passed, 2 skipped
300a338  fix: the three readings that counted v4's posts    1 failed, 1968 passed, 2 skipped
```

The last three rows were run after the review pass that found Dv209; the report and vault commits
below them carry no code.

**Dv206 — the one failure on every row is the checker's, not the tree's.** `data/` is gitignored,
so the worktree is given a symlink to the repo's copy, and
`test_collect_5c1.py::test_the_guard_reads_the_pinned_paths_off_the_pin_file` then resolves a pinned
path outside the worktree root (`'…/market-pulse-llm/data/raw/posts/VARUS_channel.jsonl' is not in
the subpath of '…/wt'`). It fires on the **control commit** too, which is what says it is the
checker's artifact. Same as Dv193. In the repo itself the suite is 1966 passed / 2 skipped, and
1965 + 1 = 1966 on every row.

**`d3fa574` carries a SECOND failure and that one is by design** — the contract announced it. The
team-lead docs commit lands SPEC's seventh ratification block with
`tests/test_sku_prereg.py`'s enumeration one name short, which is the point of that enumeration:
an amendment cannot arrive unnoticed. Green again at `2b8a35d`.

---

## Deviations

**Dv195.** The contract says «Deviations **Dv189+**». Dv189–Dv194 were spent earlier on 2026-08-12
by the sku-b-close and sku-miss-pack contracts, so numbering continues at **Dv195** rather than
colliding with entries already in the day's log.

**Dv196.** The (13)(b) registry edit moves a sha eight sealed records pin. Reconstruction, not
re-pinning — `registry_before_the_latin_aliases` + `load_registry_as_pinned`, with the enumeration
literal and a negative control. §Deliverable 3.

**Dv197.** «Rud» and «LIMO» casefold onto their own brand_ids, so two gold keys change shape.
Consequence: the B′ gold is rebuilt, not filtered. §Deliverable 3.

**Dv198.** `parse_size` and `parse_percent` change arity (2→3 and 1→2 return values) rather than
gaining sibling functions, so a caller that ignores the new element gets a `TypeError` instead of
silently dropping a warning.

**Dv199.** The two new `Position` fields do not reach the dump; the registered column sentence is
byte-equal in B′. Asserted. §Deliverable 2.

**Dv200.** The peft venv was rebuilt (transformers 5.14.1 · peft 0.20.0 · torch 2.13.0) before the
preflight could be driven.

**Dv201.** `results/sku_pilot_prereg_b2.json` does not land this session. The producer refuses; the
tests drive the build against a resolved fixture. §Deliverable 4.

**Dv202.** The rescope empties four posts' gold; bar 1's macro mean is over 11 posts, not 15.
Registered as B5.

**Dv203.** The rescope can only remove misses; 9 pairs are kept on a key ruled out elsewhere (6
found by v1, 3 class a). Registered as B4.

**Dv204.** The dearest projection corner is $0.4004 against the $0.40 cap. Both readings in the
record; no choice made. §Deliverable 5.

**Dv205.** `write_sku_serving_pin_v2.py --force` was used to re-stamp the pin from a clean tree. The
condition the producer's own message names holds: the pin has genuinely not been read — no skub2
session has run, there is no `results/spend_skub2.json` and no skub2 run record.

**Dv206.** The checkout table's one failure per row is the symlinked-`data/` artifact and fires on
the control commit too. §The checkout table.

**Dv207.** (13)(d) against (11)(a): 138 elements, all re-asked. Registered as B1.

**Dv208.** The driver still carries v4's cap, phase and ledger; moving them is skub2-run's step.

**Dv209.** Found in review: bar 1's `excluded`, `denominator` and `reachable` were still v4's and
still counting 15 posts and 55 pairs beside a gold of 11 and 41 — and `bar_one`'s own guard would
have matched the sealed reference and scored 15 posts in the v4 key space. Recomputed; the guard
now refuses. §Deliverable 4.

**Dv210.** `bar_one` still reads gold from the sealed reference. Pointing it at
`bars.leaflet_brand_recall.gold.per_post` is skub2-run's first step, and Dv209's fix makes it a
stop rather than a silent wrong number.

---

## What the acceptance has to decide

1. **The four pending pairs** — #4 (4360 `svoia-liniia`), #9 (4391 `svoia-liniia`), #28 (4508
   `svoia-liniia`), #29 (4508 `try-vedmedi`). Their pages, files and shas are listed in
   `results/sku_miss_decomposition.json :: rows[].pages`. Until they land, `write_sku_prereg_b2.py`
   refuses and there is no B′ registration.
2. **B4** — is a brand ruled class b out of the denominator everywhere, or only on the pair it was
   ruled on? Nine pairs, six of them free correct answers, and the two readings move bar 1 in
   opposite directions.
3. **B1** — 138 re-asked, or something narrower.
4. **B5** — 11 posts in the macro mean.
5. **The $0.40 cap against a $0.4004 upper bound** — accept, drop the drift term on a corner that
   is already a bound, or move the cap.
6. **The scorer's gold source** (Dv210) — `sku_bar_verdicts.bar_one` reads the sealed reference's
   `gold_keys`, which are the v4 key space. skub2-run has to point it at the B′ registration's own
   `gold.per_post` before the first paid call; until then the run refuses at `bar_one`'s
   empty-gold check, which is where Dv209's fix put the stop.

Nothing above is a number this session chose.

---

## Fix

`docs/PROMPT-skub2-fix.md` · authority SPEC §3.17 (14), ratified 2026-08-12 · executor, $0, no paid
calls · 2026-08-12, 16:30–17:39. **Twelve** commits, `2621d6f..6a20671`, and a thirteenth that
corrects two numbers in this section — see §Corrections at its foot.

The four pending pairs land, the B′ registration writes, and the driver's constants move with it.

| step | what | where it landed |
| --- | --- | --- |
| 1 | the team-lead docs, unedited, and the enumeration | `2621d6f` · `56b2214` |
| 2 | the four verdicts applied, `final` = 37 | `results/sku_miss_decomposition.json` |
| 3 | the B′ pre-registration, **written** | `results/sku_pilot_prereg_b2.json` |
| 4 | the driver's constants — Dv208 paid | `scripts/positions_gm4_skub.py` |
| 5 | the projection against $0.65, the preflight re-driven | `results/sku_projection_b2.json`, `scripts/preflight_serving_guards.py` |

```
$ python3 -m pytest -q
1985 passed, 2 skipped in 58.28s
$ ruff check . && ruff format --check .
All checks passed!
244 files already formatted
```

1969 tests at the end of skub2-prep, **1985** now.

---

### Step 2 — the four verdicts

`#4`, `#9`, `#28` and `#29` are all class b. The applier's table gains four rows and `PENDING`
becomes empty; `EXPECTED` is transcribed from the contract's own line, never computed from the table
it checks.

```
$ PYTHONPATH=src python3 scripts/apply_miss_decomposition.py
results/sku_miss_pack.json — 29 missed pairs, each ruled on or deferred exactly once
  a 11 · b 16 · c 2 · pending_team_lead 0
  11 mechanism(s) checked against the instrument's own refusal reasons
  4 page-read citation(s) checked against the pages that could be read
     9  non-dairy watchlist item
     5  refusal:token-ceiling
     3  refusal:multipack
     2  SKU-name-vs-TM
     2  maker-logo
     2  refusal:asterisk
     1  alias:latin-form
     1  dairy-adjacent, reviewer's own caveat
     1  gold-key artifact — brand was found
     1  non-dairy
     1  non-dairy, by-pattern
     1  two-brands-one-box
wrote results/sku_miss_decomposition.json
```

`b_prime_denominator.final` is **37** for the first time — 55 gold pairs less the 18 ruled b or c —
and that field is what `write_sku_prereg_b2.py` refused on.

#### Dv211 — a page citation is checkable, so it is checked

(14)(a) does not only rule the four; it says which pages each verdict was read on («fish p2, tea p3,
zefir p4, oil p5, pate p6 — every page read»). Those citations are the evidence that replaces the
guess the first read refused to make, so the applier holds them against the pack.
`check_the_page_reads_land_on_readable_pages` refuses a page number that is not on that post, a page
the extractor returned as unreadable, a `PAGE_READS` key the table does not rule on, and a citation
on a row that is still `PENDING_TEAM_LEAD`. Four citations checked, four negative controls.

The refused-page branch is the one that matters. Row 14 is ruled «non-dairy, **by-pattern**» because
its own page came back refused and the verdict came from the rows beside it — a full-page read that
cited a refused page would be that same thing wearing the other words.

#### Dv212 — the mechanism vocabulary is not the page reads

The four wear `non-dairy watchlist item`, the string the first read already used for five other
rows. Put into `mechanism`, the parenthetical page lists would have split one bucket of nine into
five plus four buckets of one, and `by_mechanism` would stop counting anything. The page reads live
in a sibling `pages_read` field on those four rows.

#### Dv224 — «16 images» against 18 sent pages

The contract's heading says «full-page reads on 16 images», and STATUS.md repeats it. The four rows
sit on three posts — 4360, 4391 and 4508 — and the pack records **six sent pages each**, 18 in
total. Every page number the verdicts cite (p1–p6) is inside that range and none is unreadable, so
the new check passes and no verdict is affected. Reported because it is the team lead's own count
and not the executor's to correct.

---

### Step 3 — the B′ pre-registration, written

```
$ PYTHONPATH=src python3 scripts/write_sku_prereg_b2.py
wrote results/sku_pilot_prereg_b2.json  (beside results/sku_pilot_prereg_v4.json, which stays sealed)
  bar 1 gold    37 pairs over 10 posts (55 - 18 removed by (13)(c))
  population    138 elements, cap $0.65
  instrument    parser 0b058e800244…
```

**37 pairs · 10 posts · 5 emptied**, each computed by the producer and each equal to what (14)(c)
states. The three are independent in the code — the pairs are summed over the kept gold keys, the
posts counted from the non-empty sets, the emptied list diffed against v4's — so their agreement
with the law is a check rather than a transcription. Dv201 is closed.

Nine posts now sit outside bar 1's recall average: v4's four plus the five (13)(c) empties. 4391 is
the fifth, and it is 4391 because (14)(a) ruled its `svoia-liniia` pair class b.

#### Dv213 — the pin keeps (14) too, not only (13)

The contract's step 1 says the enumeration gains `sku-b-ratification-8`; it does not say what the B′
pin keeps. It has to keep it. The cap this record enforces is (14)(e)'s, its gold is (14)(a)'s and
its B1/B4/B5 readings are (14)(b)–(d) — a SPEC pin over a law stripped of (14) would not contain the
sentence authorising the run it registers. `KEEP_BLOCK` becomes
`KEEP_BLOCKS = ("sku-b-ratification-7", "sku-b-ratification-8")`, and the test asserts that a pin
over (13) alone is a **different hash**, which is the control saying the eighth block counts.

#### Dv215 — the open lines are ruled, not deleted

All five of B1–B5 are answered. The block keeps its name and all five entries, each gaining a
`ruled_by` carrying the law's own sentence, because a registration records the question as well as
the answer: B4's losing reading is what makes the ruling mean something, and `sku_bar_verdicts.py`
copies the block into the verdicts record verbatim.

Every quoted ruling is held against the file by `check_the_quoted_rulings_are_the_law` — the rule
`write_sku_prereg.check_the_bars_are_the_laws` already applies to the bars. Its negative control
paraphrases B5 and the producer refuses.

#### Dv216 — (13)(d)'s sentence still says $0.40

`attempts.verbatim` is (13)(d) quoted unedited, «cap $0.40» included, because a law with its number
swapped is not the law. Beside it sit `cap_verbatim` — (14)(e)'s superseding sentence — and
`cap_verbatim_source`; `cap_usd` follows (14)(e). A reader sees which clause the run is under and
which one it supersedes without opening SPEC.

#### Dv214 — Dv209's shape, a second time

`excluded.why_this_list_grew` said «the **four** new ones each carried exactly one gold key» beside
a computed `len(empty)`. (14)(a) made it five, and «exactly one» stopped being a fact anybody had
checked. It is a function now, with every number computed from the gold it describes — including the
per-post key count — and a test that drives it on a fake where those numbers differ. A count in
prose next to a count in code is a record that answers the same question twice.

---

### Step 4 — the driver's constants (Dv208 paid)

`PHASE` / `CAP_USD` / `LEDGER` / `PREREG` become `skub2` / `$0.65` / `results/spend_skub2.json` /
`results/sku_pilot_prereg_b2.json`.

**Which triple.** Dv208 was written as «the driver still carries **v4's** cap, phase and ledger»,
which points at `RESUME_*`. What skub2 actually reads is the PRIMARY set: B′ has no resume block, so
`resume_plan` refuses it and skub2 is forced onto the non-resume path. The primary set moved; v4's
triple stays v4's, because that session completed and the preflight's block 9b is its control.

Three things step 4 does not name and the money path did.

#### Dv217 — the coherence guard was wired where it could not fire

`check_the_constants_are_the_registrations` was **called inside `if args.resume:`**. Re-pointing the
test while leaving the call there would have given a green suite and an unguarded paid run: the one
path that now carries a fresh cap, a fresh anchor and a fresh registration was the one path nothing
checked. Moved out of the branch, with `test_the_constants_check_runs_on_the_non_resume_path_too`
driving it through `main --dry-run` — the wiring, not the function — and three refusals in the
preflight.

#### Dv218 — the serving pin is a money constant

`assert_serving` compares **every** field of `expected_worker`, `max_new_tokens` among them. v1's pin
says 800 and instrument v2 serves 1200, so a run left on the old pin refuses at the identity stop —
**after the boot has been billed**, the one refusal (12)(b) prices. `PIN` moves to
`results/sku_pilot_serving_v2.json`, `--pin` follows the mode like `--prereg` and `--ledger`
(`PIN_RESUME` keeps v1's for the resumed path, which (11)(b) freezes), and a new guard,
`check_the_serving_pin_is_the_registered_one`, holds it against the registration that names it.
Skipped rather than failed for a registration with no `instruments.instrument_v2` block, since v1–v4
pin their serving config elsewhere.

#### Dv219 — the output pair was still the first session's

`DUMP` / `RECORD` defaulted to `results/sku_b_positions.jsonl` / `.json`, the artifacts pinned in
`sku_pilot_prereg_v4.json :: resume.bought_already`. The overwrite guard would have stopped the run
at $0, but with a message about a paid artifact rather than about a registration. They become
`sku_b_positions_skub2.*`, named for their own session the way the v4 pair is.

#### Dv225 — the run record's contract string named the wrong contract

`head["contract"]`'s non-resume branch said `docs/PROMPT-sku-b-prep.md` + 3.17 (6), (9), (10) — the
FIRST session's contract. That branch is skub2's since the constants moved, so a completed run would
have recorded a contract it was not under. Moved with the rest, to
`docs/PROMPT-skub2-prep.md + docs/PROMPT-skub2-fix.md; docs/SPEC.md amendment 3.17 (9), (10), (13),
(14)`. The resume branch is untouched, **including the (12) it omits: that is Dv176 and it stays
open.**

#### Dv226 — the new guard had this contract's own defect

`check_the_serving_pin_is_the_registered_one` was proved three ways as a function and driven by the
preflight as a function, and nothing asserted `main` calls it — Dv217's shape, on code added here.
Closed by a `main --dry-run` test. Two test docstrings that described the live constants were
falsified by the same move and are corrected in the same commit.

#### Three tests were reading live constants for sealed facts

Re-pointed, not re-fitted:

- **Dv220.** `scripts/write_sku_projection.py` read `driver.CAP_USD` for the SEALED v1 projection's
  corners. With the live cap at $0.65 that record would have re-priced itself into a comfortable fit
  against a cap it never had. It carries its own `CAP_USD = 0.35` now, exactly as it already carries
  its own `POSITIONS_CEILING = 800`.
- **Dv221.** `test_the_two_records_the_two_caps_and_the_two_anchors_never_cross` told the two
  constant sets apart **by the cap**. (14)(e) put skub2's at $0.65, which is what (12)(a) gave v4:
  the caps are equal now and separate nothing. The test asserts that equality out loud and
  discriminates on the six names that do differ — phase, ledger, registration, dump, record, pin.
- **Dv222.** The three (10)(a)-refusal tests anchored `10.30` against a $0.35 cap to leave $0.05 for
  the run. At $0.65 the projection fits and they stopped refusing — silently, in the direction of
  passing. The anchor is derived from the cap now (`SPENT_LEAVING_FIVE_CENTS`).

#### Dv223 — two models of the job-timeout margin, and they disagree by 3x

`tests/test_positions_driver.py` asserts `JOB_TIMEOUT_S >= 2 * (30 * 4.262 * (800 / 256))` — v1's
uplift model, srv-2d's measured 4.262 s/row scaled by the ratio of registered ceilings. Re-typed at
the 1200 ceiling the same expression gives 1199 s against a 900 s timeout and **would fail**. The
measured re-check disagrees: `results/sku_projection_b2.json :: job_timeout_headroom` prices the
same job from the v4 session's own seconds at 181 s, twice that is 362 s, and the property holds
with 2.5x to spare.

The literal is **left at 800** with a comment naming both models, because a literal moved to keep a
test green is not a re-check. It gates nothing either way: the money guard is
`JOB_TIMEOUT_S * rate < CAP_USD` — $0.276 against $0.65 — and one wedged worker cannot out-bill the
cap under either model.

---

### Step 5 — the projection, and the preflight

Not one corner moved. Every rate was measured before the cap was ruled on and the arithmetic is the
same arithmetic; what changed is the line it is compared to.

```
$ PYTHONPATH=src python3 scripts/write_sku_projection_b2.py
  measured      4.0161 s/page (n=91) · 2.8188 s/row (n=30) · boot 205.518–402.586 s
  boot low · decode none                      802.2 s  $0.2460  $0.2534 with drift
  boot low · decode the whole ceiling        1070.6 s  $0.3283  $0.3382 with drift
  boot high · decode none                     999.3 s  $0.3065  $0.3157 with drift
  boot high · decode the whole ceiling       1267.6 s  $0.3888  $0.4004 with drift
  vs the $0.65 cap: FITS — dearest $0.4004, headroom $0.2496
  job timeout   900 s vs 2x181 s conservative — ok
```

**Dv204 is closed, and closed on the arithmetic it reported:** the hard upper bound is still
$0.4004, still over (13)(d)'s $0.40, and now $0.2496 under the cap that supersedes it.

The preflight gains blocks **9c** (the live session's three constants against B′) and **9d** (the
serving pin against the registration that names it), and its resume block reads `PIN_RESUME` — with
`PIN` it would have failed on the pin before reaching any of its own subjects.

```
9c. the live session         skub2 against results/sku_pilot_prereg_b2.json
    the registered set         ACCEPT   <- the control ($0.65 · skub2 · results/spend_skub2.json)
    the FIRST session's ledger REFUSE — … ledger: the run would use 'spend_sku_b.json' …
    (13)(d)'s superseded cap   REFUSE — … cap_usd: the run would use 0.4 and the registration names 0.65 …
    the FIRST session's phase  REFUSE — … phase: the run would use 'sku-b' and the registration names 'skub2' …

9d. the registered instrument the serving pin B′ names, by name and by sha
    serving pin v2             ACCEPT   <- the control
    v1's pin (800 ceiling)     REFUSE — the run would serve against sku_pilot_serving.json (5f900beb555f12f5…) …
    v4, which names no pin     ACCEPT   <- skipped, not failed
```

`EXIT=0`, **PASS 47 · FAIL 0** (was 40), driven under the rebuilt peft venv (transformers 5.14.1 ·
peft 0.20.0 · torch 2.13.0).

---

### The checkout table

`PYTHONPATH=src python3 -m pytest -q` at every commit, in a detached worktree, with `c85d595` — the
commit before this contract — as the checker's own control.

```
c85d595  chore(vault): the review tail                       1 failed, 1968 passed, 2 skipped
2621d6f  chore(docs): SPEC 3.17 (14), the skub2-fix contract 2 failed, 1967 passed, 2 skipped
56b2214  test(sku-prereg): the eighth ratification block     1 failed, 1968 passed, 2 skipped
e59016c  feat: the four verdicts land -- a=11 . b=16 . c=2   1 failed, 1978 passed, 2 skipped
881f816  data: the decomposition re-stamped                  1 failed, 1978 passed, 2 skipped
ada5afe  data: the projection re-stamped                     1 failed, 1978 passed, 2 skipped
c2fc096  data: the B' pre-registration, written              1 failed, 1980 passed, 2 skipped
b30cb0d  feat: the driver's constants move to skub2          1 failed, 1983 passed, 2 skipped
40042c5  data: the projection re-stamped after Dv208 landed  1 failed, 1983 passed, 2 skipped
30673be  fix: the run record's contract string follows       1 failed, 1983 passed, 2 skipped
53d59ba  test: the pin guard's wiring, two docstrings        1 failed, 1984 passed, 2 skipped
```

The report and vault commits below the last row carry no code.

**Dv206 again — the one failure on every row is the checker's, not the tree's.** `data/` is
gitignored, so the worktree is given a symlink FARM (one link per missing entry, two levels deep —
not one link over the directory, which would show the tracked files under `data/` as deleted and
make the next `git checkout` refuse). `test_collect_5c1.py::test_the_guard_reads_the_pinned_paths_off_the_pin_file`
then resolves a pinned path outside the worktree root. It fires on the **control commit** too, which
is what says it is the checker's artifact. In the repo itself the suite is 1985 passed / 2 skipped,
and 1984 + 1 = 1985 on the last row.

**`2621d6f` carries a SECOND failure and that one is by design** — its own commit message announced
it. The team-lead docs commit lands SPEC's eighth ratification block with `tests/test_sku_prereg.py`'s
enumeration one name short, which is the point of that enumeration: an amendment cannot arrive
unnoticed. Green again at `56b2214`.

---

### Reported, gating nothing

**The B′ gold is scored against a 0.75 bar, and the team lead's own figure for v1 on it is 0.703.**
`docs/STATUS.md` records «голд v2 = 37 пар / 10 постів; v1 на нём = 0.703 — планка честная»;
`bars.leaflet_brand_recall.threshold` is `0.75`. Not re-derived here — SPEC §10 — and quoted with
its source. The reading it forces is worth stating before the spend rather than after it:

- the re-scope **alone does not pass bar 1**. Instrument v2 has to supply roughly **4.7 pp** on top
  of what v1's extractions already score on this gold;
- and 0.703 is already the double-lifted number. The exclusion was distilled from an error analysis,
  so it can only ever remove failures: 18 guaranteed misses left the denominator while nine pairs on
  keys ruled out elsewhere stayed, six of them pairs v1 had already found (Dv203, ruled per pair by
  (14)(b)). The 4.7 pp gap is what remains after both lifts.

This is not a new measurement and it changes nothing in the registration; it is what $0.65 is
buying, said out loud.

**Dv227 — the artifacts' `git.dirty` names three `knowledge/` files.** The /save checkpoint from
before this contract is uncommitted by the contract's own ordering (vault tail last), so
`sku_miss_decomposition.json`, `sku_projection_b2.json` and `sku_pilot_prereg_b2.json` each record
three dirty vault paths. Nothing under `src/`, `scripts/`, `config/` or `results/` was dirty when any
of them was written.

---

### What this leaves for skub2-run

1. **Dv210, still first.** `sku_bar_verdicts.bar_one` reads gold from the sealed reference's
   `gold_keys`, which are the v4 key space. It has to be pointed at
   `results/sku_pilot_prereg_b2.json :: bars.leaflet_brand_recall.gold.per_post` before the first
   paid call. Until then the run refuses at `bar_one`'s empty-gold check — B′ excludes nine posts
   and the reference four — which is exactly where Dv209's fix put the stop.
2. **Dv199, carried.** Instrument v2's `pack_count` and `discount_footnote` reach no artifact. The
   dump's columns are derived from bar 2's `procedure` sentence, which (13) and (14) keep byte-equal,
   so the team lead scoring bar 2 sees `size: 100 г` for a `6х100 г` multipack with nothing saying it
   is a six-pack. Carrying the warnings into the run RECORD, beside the dump rather than inside it,
   is skub2-run's to decide.
3. **Dv176, still open.** `head["contract"]`'s resume branch omits 3.17 (12). Untouched here — that
   branch is v4's.
4. **Dv223, carried.** The driver's job-timeout margin literal is v1's model at v1's ceiling.


---

### Corrections

Two numbers in this section were wrong when it was committed at `4f59132`, and both are the same
mistake — a count taken from the nearest thing that looked like it, instead of from `git log`.

1. **«Eleven commits»** was the checkout table's ROW count, which includes `c85d595` — the control,
   which is not a commit of this contract. Twelve: `2621d6f 56b2214 e59016c 881f816 ada5afe c2fc096
   b30cb0d 40042c5 30673be 53d59ba 4f59132 6a20671`. The vault commit's own message and hot.md
   repeated the eleven; hot.md is corrected, a commit message cannot be.
2. **The session's wall clock.** The day's log header said «16:20–18:05» and hot.md's
   `**Last update:**` said 18:05. `git log --date=format:'%H:%M'` says **16:30** for the first
   commit and **17:39** for the last. Corrected in both.

This is the second time in one day: the 16:16 checkpoint corrected «14:20–17:40 / 17:40–18:20» to
14:18–15:58 and wrote down the rule it broke — the wall clock of a session comes from `git log`, not
from a sense of how long the work felt. It broke again in the same file within five hours, which is
what says the rule needs a command and not a resolution:

```
git log --reverse --format='%h %ad %s' --date=format:'%H:%M' <first>^..HEAD
```

# skub2-prep — instrument v2 and the B′ registration, before the re-measurement ($0)

`docs/PROMPT-skub2-prep.md` · authority SPEC §3.17 (13), ratified 2026-08-12 · executor, $0, no
paid calls · 2026-08-12.

Five deliverables, eleven commits, `d3fa574..b39b55e`. Four of the five landed as files on disk.
The fifth — the B′ pre-registration — **is a producer that refuses**, because four decomposition
pairs are still `PENDING_TEAM_LEAD` and each of them can still leave the denominator it would
register.

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
1966 passed, 2 skipped in 58.17s
$ ruff check . && ruff format --check .
All checks passed!
244 files already formatted
```

1854 tests at the start of the day, 1869 after the miss-pack contract, **1966** now.

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

The bars are byte-equal to v4 leaf by leaf except `leaflet_brand_recall.gold`, with a negative
control on both the text and the threshold.

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
```

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

Nothing above is a number this session chose.

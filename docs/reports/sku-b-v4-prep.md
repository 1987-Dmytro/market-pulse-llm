# sku-b-v4-prep — the fresh-ledger re-registration ($0)

## Read-back

**The four deliverables:**

1. **Pre-registration v4** — `results/sku_pilot_prereg_v4.json` via the producer, BESIDE v3,
   committed before any v4-run artifact; `supersedes` names v3's sha and pins the (10)(a) refusal
   record; `moved` enumerates only the cap, the ledger/phase names and the supersede metadata;
   everything the measurement is made of is byte-equal to v3, asserted row by row.
2. **Driver: the v4 constants, set together** — `RESUME_CAP_USD = 0.65`,
   `RESUME_LEDGER = results/spend_sku_b_v4.json`, `RESUME_PHASE = "sku-b-v4"` and the registration
   path pointed at v4, one block, one commit, with a test asserting the three name one phase; plus
   the Dv163 debt — BOTH exits write the `jobs_planned` / `jobs_submitted` split from one shared
   cost-block builder, driven by a test through both.
3. **Projection v4** — `results/sku_projection_v4.json`, BESIDE v3's: both marginals as corners,
   the gate-pessimistic 14.808 s/page and the population-drawn 5.0772 s/page, text at 3.862 s
   measured, the idle tail, and the headroom per corner with the 3% drift.
4. **Preflight pins** — the resume guards re-driven against the v4 registration: it accepts the
   honest v4, refuses a moved v3-refusal-record pin, refuses the OLD ledger name, and every
   existing control is kept.

**SPEC 3.17 (12), the four readings:**

- **(a)** ONE more resumed session under a v4 re-registration BESIDE v3, cap **$0.65** — sized to
  admit the gate's own pessimistic projection (~$0.60), whose probe is structurally a deep leaflet
  page and prices above the first-six-page population's drawn marginal; the in-run gate still
  protects the middle.
- **(b)** A session refused at the (10)(a) gate charges the PHASE ledger, never the next attempt's
  cap: each registered attempt runs under its own fresh anchor and its own cap/ledger/phase
  constants, **set together** — the Dv167 finding.
- **(c)** The warm-up inputs remain the REGISTERED ones of v3 — the same unsent page and the same
  non-pack row, re-verified by hash, never re-picked.
- **(d)** Every reading of (10) and (11) otherwise applies unchanged; the population is still the 121
  unbought elements, each of the 138 bought exactly once across the program.

**No paid calls in this contract.** No pod, no endpoint, no template, no `/run`. The only network
this session touched was `runpodctl`'s four read-only listings below and one `pip install` into a
scratch venv outside the repo (Dv173).

---

## Deliverable 1 — pre-registration v4

`results/sku_pilot_prereg_v4.json`, sha `22fd7d9cc363ac93…`, commit `4905295`, its own commit and
before any v4-run artifact exists.

### The byte-equality run

```
$ PYTHONPATH=src python3 - <<'PY'   # leaf-by-leaf, v3 against v4
bars                     45 leaves   byte-equal: True
ratification_required    20 leaves   byte-equal: True
not_in_scope              4 leaves   byte-equal: True
instruments               3 leaves   byte-equal: True
ladder                   34 leaves   byte-equal: True
pinned_inputs             6 leaves   byte-equal: True
resume                  195 leaves   byte-equal: True
attempts added           ['attempts.authority', 'attempts.ledger', 'attempts.phase']
attempts lost            []
attempts moved           ['attempts.cap_usd'] 0.45 -> 0.65
top-level sections       identical
supersedes.moved         3 entries
```

307 leaves compared as a mapping rather than as a key set — a pin whose VALUE moved is the only way
a pinned input can betray a bar, and a key-set assertion would pass it. `resume` is in the frozen
list this time, which is what makes v3 → v4 a smaller move than v2 → v3: the refused session
measured nothing a bar can read, so the population, the (11)(c) warm-up pins and `bought_already`'s
17 of 138 are the same bytes v3 carried. The same comparison runs as
`tests/test_sku_prereg.py::test_v4_carries_v3s_whole_measurement_and_moves_only_the_cap_and_the_two_names`.

### What moved, and the three entries `supersedes.moved` names

| moved | from → to | authority |
|---|---|---|
| `attempts.cap_usd` | 0.45 → **0.65** | (12)(a) |
| `attempts.phase`, `attempts.ledger` (new) | — → `sku-b-v4`, `results/spend_sku_b_v4.json` | (12)(b) |
| `supersedes` | v2 → **v3** by sha, plus (12)(a)–(d) verbatim and the refusal record pinned | (12) |

`attempts.authority` is the third new field and it rides with the second entry: it is where the
record says that the clause it sits under is still (11)'s and that $0.65 comes from (12)(a). See
Dv169.

### The refusal record is read, not merely hashed

```
refused       results/sku_b_positions_v3.json 7196abfbf488168d… (stopped_before_gold, 0 asked, $0.1416 to the phase)
```

v4 inherits its population from v3 rather than re-deriving it, and what makes that legal is one
fact about the CONTENTS of that file: the refused session bought nothing. A sha proves the bytes
have not moved and says nothing about what is in them, so `refused_nothing_bought()` reads
`stopped_before_gold` and `population.asked` and refuses the write otherwise. Both halves are
asserted, and the negative control is a doctored v3 record whose session reached the gold:

```
$ PYTHONPATH=src python3 -m pytest tests/test_sku_prereg.py -k "refused or v4 or bought_something" -v
tests/test_sku_prereg.py::test_a_paraphrased_v4_reading_stops_the_write PASSED                        [ 20%]
tests/test_sku_prereg.py::test_v4_was_committed_before_the_v4_session_and_over_all_three_artifacts PASSED [ 40%]
tests/test_sku_prereg.py::test_v4_carries_v3s_whole_measurement_and_moves_only_the_cap_and_the_two_names PASSED [ 60%]
tests/test_sku_prereg.py::test_the_refused_session_is_pinned_and_read_not_merely_quoted PASSED        [ 80%]
tests/test_sku_prereg.py::test_a_v3_record_that_had_bought_something_stops_the_write PASSED           [100%]
5 passed, 26 deselected in 0.22s
```

### The ordering rule, widened

`test_v4_was_committed_before_the_v4_session_and_over_all_three_artifacts` is not v3's check with a
new constant. At the commit that added v4 the tree holds **three** sku-b run artifacts — the first
session's record and dump, and now the v3 refusal record — and all three are asserted to be exactly
what the registration pins, by `git show`ing the blobs at that commit. A copy of v3's two-file
assertion would have failed here for the honest reason that the tree grew; widening it turned the
breakage into the check that matters. There is no `sku_b_positions_v3.jsonl`: a session refused
before the first gold call writes no dump, and the expected set is three rather than four.

v3 is now sealed at `a80e8e55488439372244715f24f7bbfb56cf46a3a2586d38fa75a14c4c643656`, beside v1 and
v2, and the chain v1 ← v2 ← v3 ← v4 is asserted link by link.

---

## Deliverable 2 — the driver's v4 constants and the shared cost block

Commit `20b9436`.

### The three constants, and the test that binds them

```
RESUME_PHASE = "sku-b-v4"
RESUME_CAP_USD = 0.65
RESUME_LEDGER = REPO_ROOT / "results" / "spend_sku_b_v4.json"
```

with `PREREG_RESUME`, `RESUME_RECORD` and `RESUME_DUMP` following to v4. The coherence test asserts
the registration signs all three and that a half-update cannot look tidy:

```
$ PYTHONPATH=src python3 -m pytest -k "three_constants_name_one_phase or both_exits_write" -v
tests/test_positions_driver.py::test_the_three_constants_name_one_phase_and_the_registration_signs_all_three PASSED [ 50%]
tests/test_positions_driver.py::test_both_exits_write_the_same_cost_fields PASSED [100%]
2 passed, 1823 deselected in 1.31s
```

The test reads `attempts.{phase,cap_usd,ledger}` out of `results/sku_pilot_prereg_v4.json` and
compares them to the module constants, then drives `check_the_constants_are_the_registrations` with
its control (the registered set, accepted) and two negative controls (the v3 ledger name, the $0.45
cap). Dv167 cannot recur half-updated because the registration is now a party to it.

`check_the_constants_are_the_registrations` runs in `main` **after** `resume_plan` — which is the
function that recognises a registration with no `resume` block at all, so a wrong file is reported
as one wrong file rather than as three missing fields — and **before** any balance is read, so
`--dry-run` proves it too:

```
$ PYTHONPATH=src python3 scripts/positions_gm4_skub.py --resume --dry-run
page leg   91 pages sent (of 159 available, 19 posts) in 6 job(s), largest 7.99 MB
text leg   30 rows in 1 job(s)
dump       18 columns: item, page, file, sha256, brand_raw, brand_id, line, category, size, fat, price_promo, price_old, discount_pct_printed, price_qualifier, tier, depth, depth_disagrees_with_printed, bought_by
resume     SPEC 3.17 (11) under results/sku_pilot_prereg_v4.json
  bought    17 of 138 by results/sku_b_positions.json, never re-asked
  to buy    91 page(s) + 30 row(s) = 121 of 121 registered
  cap       $0.65 (12)(a) · phase sku-b-v4 · anchor results/spend_sku_b_v4.json
```

91 + 30 in 6 + 1 jobs, unchanged from v3 — the population is (12)(d)'s, not a new one.

### Dv163: one cost block, both exits

`cost_block()` builds `jobs_planned` / `jobs_submitted` / `jobs_reading` / `usd` / `cap_usd` /
`anchor` / `read_failed` / `reading` for the completion path and the (10)(a) refusal path alike;
only `reading` differs, because the two exits really do price different things. The refusal exit
used to write `jobs: 0` — the ambiguous name Dv153 found — on the record a reader opens first when
a session refused. Driven through both:

| field | refusal exit | completion exit |
|---|---|---|
| `jobs_planned` | 1 | 1 |
| `jobs_submitted` | 3 — the handshake and the two warm-up calls | 4 — and the gold job on top |
| `jobs` | absent | absent |
| `jobs_reading` | identical string | identical string |

`jobs_planned` is 1 and not 0 on the refusal exit, which is the finding: the packing had already
happened when the gate fired, so the number reports the size of the run that did not happen rather
than reading as "nothing was planned".

### resume_plan's fourth refusal

The pinned (10)(a) refusal record. Named in the docstring beside the other three and driven in the
preflight below.

---

## Deliverable 3 — projection v4

`results/sku_projection_v4.json`, sha `88c45e5c1e472370…`, commit `6369123`, beside v3's.

```
$ PYTHONPATH=src python3 scripts/write_sku_projection_v4.py
wrote results/sku_projection_v4.json
  population   91 pages + 30 rows = 121 calls
  boot         402.586 s ($0.1235) · idle tail 60 s ($0.0184) · text 3.862 s/row (n=1)
  the registered probe, a deep unsent page             14.808 s/page (n=1)   $0.5964 → $0.6143 with drift  headroom $+0.0357  fits
  the population's drawn marginal, 17 first-six pages   5.0772 s/page (n=17)  $0.3218 → $0.3315 with drift  headroom $+0.3185  fits
  cap          $0.65 · fits at every corner with drift: True
```

**The pessimistic corner is the number the gate refused.** $0.5964 is exactly
`results/sku_b_positions_v3.json :: projection.go_no_go.projected_usd` — same marginals, same 121
elements — and the producer asserts the equality when it builds, refusing to write a projection
whose own positive control has failed. The control for the control: a 10% slower boot moves this
record's corner and not the gate's recorded figure, and the producer stops
(`test_arithmetic_that_disagrees_with_the_gate_stops_the_write`).

**What each number is made of, said out loud.** The probe is n=1 and structurally DEEP — the sent
set is the first six pages of each leaflet, so the 51 unsent ones are the dense grids. The drawn
marginal is n=17 but 10 of those 17 answered `[]`, and an empty answer decodes early, so a mean over
a 59%-empty sample prices the non-empty pages at less than they cost. The text rate is the FIRST
positions call ever made on text and it is one row, not a rate over the pack — v3's projection had
to bound the text leg by the page marginal because no such measurement existed.

**The 3% is a contract term.** It is `docs/PROMPT-sku-b-v4-prep.md` deliverable 3's requirement, and
the record says so: nothing in this repository measures how far a serverless worker's seconds move
between two runs of the same job, and presenting 3% as an observed spread would be inventing a
number. It is applied to the whole billed second count, because what it stands in for is the
endpoint being slower on the day.

**The verdict is an inequality.** At this boot the page marginal would have to reach **16.0366
s/call — 1.083× the registered probe's own 14.808** — before $0.65 is exhausted with the drift on.
A test substitutes that rate back into the corner and lands on the cap, because a break-even nobody
can put back is arithmetic nobody checked.

```
$ PYTHONPATH=src python3 -m pytest tests/test_sku_projection_v4.py -q
10 passed in 0.13s
```

---

## Deliverable 4 — the preflight, re-driven against v4

```
$ PYTHONPATH=src <peftvenv>/bin/python scripts/preflight_serving_guards.py
EXIT=0    PASS 30    FAIL 0
local   transformers 5.14.1 · peft 0.20.0 · torch 2.13.0
volume  transformers 5.14.1 · peft 0.20.0
```

24 checks before, 30 now; every existing control kept. The resume half, verbatim:

```
--- SPEC 3.17 (11)/(12): the resume ---

9. the registration          121 to buy, 17 already bought   <- the control: it ACCEPTS
   a moved dump pin                   REFUSE — the per-position dump hashes 4178ce5e53559c84… and results/sku_pilot_prereg_v4.json pins 0000000000000000… — the resume
   a moved serving pin                REFUSE — the serving pin hashes 5f900beb555f12f5… and the registration pins 0000000000000000… — SPEC 3.17 (11)(b) freezes the ins
   an unbought id with an answer      REFUSE — 1 id(s) the registration lists as UNBOUGHT already carry an answer in results/sku_b_positions.json — data/annotation/cap
   a moved (10)(a) refusal-record pin REFUSE — results/sku_b_positions_v3.json hashes 7196abfbf488168d… and results/sku_pilot_prereg_v4.json pins 0000000000000000…. Th

9b. the (12)(b) constants    cap, ledger and phase against the registration
    the registered set         ACCEPT   <- the control ($0.65 · sku-b-v4 · results/spend_sku_b_v4.json)
    the OLD ledger name        REFUSE — the run's constants do not match the registration — ledger: the run would use 'spend_sku_b_v3.json' and the registration
    the OLD cap                REFUSE — the run's constants do not match the registration — cap_usd: the run would use 0.45 and the registration names 0.65. SPE
    the OLD phase key          REFUSE — the run's constants do not match the registration — phase: the run would use 'sku-b-v3' and the registration names 'sku-
    read_ledger, for contrast  REFUSE — spend_sku_b_v3.json carries no runpod_balance_at_sku-b-v4_start — it is another phase's anchor. Spending against it woul

10. the selection            a bought id     REFUSE — the page leg selected 1 id(s) the first session already bought — data/annotation/captions_5c1/posts_media/atb_market_off
    an unbought id           1 kept   <- the control

11. the (11)(c) warm-up      atb_market_official_4476.jpg 0.32 MB · row @silposilpo:3370 (548 chars)   <- the control: ACCEPT
    a page inside the sent 108 REFUSE — data/annotation/captions_5c1/posts_media/atb_market_official_4340.jpg is one of the 108 SENT pages: the registered warm-
    a row inside the 30      REFUSE — @VARUS_channel:7119 is one of the 30 adjudicated rows: the registered warm-up row is inside bar 3's gold and 3.17 (9) op

12. the merged bar input     a source bought twice  REFUSE — 1 source(s) carry an answer from BOTH sessions — data/annotation/captions_5c1/posts_media/atb_market_official_4340.jpg….
    an unbought source       18 outcomes   <- the control
```

The full PASS list:

```
PASS  the fixed guard ACCEPTS a bare real model
PASS  the fixed guard REFUSES an adapter-carrying one
PASS  the control fires: the vis-a guard refuses the bare model
PASS  POSITIONS serves the base with no adapter directory
PASS  POSITIONS refuses ADAPTER_DIR
PASS  POSITIONS refuses MERGED_DIR
PASS  POSITIONS refuses an unpinned base
PASS  the adapter refusal reaches the POSITIONS config too
PASS  every config x op cell behaves as CONFIG_OPS says
PASS  a job exactly at the payload budget passes
PASS  a job one byte over it refuses rather than shortening the album
PASS  a truncated tail is a parse REFUSAL, never an empty answer
PASS  the control: an empty array is an ANSWER and is accepted
PASS  the honest registration is accepted and names 121 elements to buy
PASS  the resume refuses a moved dump pin
PASS  the resume refuses a moved serving pin
PASS  the resume refuses an unbought id with an answer
PASS  the resume refuses a moved (10)(a) refusal-record pin
PASS  the control: the registered cap/ledger/phase are accepted together
PASS  the run refuses the OLD ledger name
PASS  the run refuses the OLD cap
PASS  the run refuses the OLD phase key
PASS  read_ledger refuses the v3 anchor too, and for its own reason
PASS  a bought id that reaches the selection is refused
PASS  the control: an unbought id passes the same selection
PASS  the registered warm-up inputs are real, full-size and accepted
PASS  the warm-up refuses a page inside the sent 108
PASS  the warm-up refuses a row inside the 30
PASS  a source answered by both sessions is refused in the merge
PASS  the control: the merged record carries 17 + what this session bought
```

**Which guard fires.** `read_ledger` would also have stopped a v3 anchor — by its missing key, after
a balance had been read, and with a message about anchor keys rather than about a registration. Both
are driven side by side above so the two refusals are visibly different reasons rather than one
guard standing in for another, which is a guard nobody has located.

---

## Verify

```
$ make check
1823 passed, 2 skipped in 54.53s

$ ruff format --check .
230 files already formatted
```

The formatter is not in `make check`, so it is run separately.

The account, unchanged because this contract created nothing — with a POSITIVE CONTROL, because two
empty arrays are also what an unauthenticated or broken CLI returns:

```
$ runpodctl pod list -a
[]
$ runpodctl serverless list
[]
$ runpodctl template list --type user      ← the control: the tool can see things
unfcr3ja0t | market-pulse-5b-a
0g6zg73ptq | mp-5b-diag
$ runpodctl network-volume list
qw4nwleanc mp-srv2 EU-RO-1 100
```

The two 5b-era templates and the volume are the same rows the sku-b-v3-run teardown left standing.
Nothing here bills but the volume.

### The per-commit checkout table

Stashed first (4 dirty vault paths), each commit checked out and running its OWN suite, HEAD printed
from `git rev-parse` rather than from the loop variable, stderr never swallowed. The parent is the
control for the checker's own bias.

| # | commit | what | fact at that commit | `make check` |
|---|---|---|---|---|
| — | `91d83ef` | CONTROL (parent) | `chore(vault): the sku-b-v3-run tail` | 1806 passed, 2 skipped |
| 1 | `f721115` | team-lead docs | `sku-b-ratification-6` × 2 in `docs/SPEC.md` | **exit=2 — RED BY DESIGN**, see Dv172 |
| 2 | `7e6e528` | the enumeration | `sku-b-ratification-6` × 1 in the test's list | 1806 passed, 2 skipped |
| 3 | `4905295` | prereg v4 | `0.65 sku-b-v4 results/spend_sku_b_v4.json 3` | 1811 passed, 2 skipped |
| 4 | `20b9436` | the v4 constants | `RESUME_PHASE = "sku-b-v4" · RESUME_CAP_USD = 0.65 · RESUME_LEDGER = …/spend_sku_b_v4.json` | 1813 passed, 2 skipped |
| 5 | `6369123` | projection v4 | `0.5964 0.6143 16.0366` | 1823 passed, 2 skipped |
| 6 | `87c2240` | the preflight | 2 hits for the two new subjects | 1823 passed, 2 skipped |
| 7 | `bb6b96e` | the ADR | 1 row in `knowledge/decisions/INDEX.md` | 1823 passed, 2 skipped |

Restored at `bb6b96e` with the same 4 dirty vault paths.

The table covers commits 1–7. Commit 8 (this report) was checked out separately after it landed —
`HEAD 8f4a7ed`, **1823 passed, 2 skipped** — and commit 9 is the vault tail, whose `make check` is
the one printed above under Verify. A report cannot check out the commit that carries it, so the
last two rows are stated here rather than left implied.

Row 1's single failure is
`tests/test_sku_prereg.py::test_every_pinned_input_still_hashes_to_what_it_says` — exactly the test
the contract names: *"On checkout, ONE test is red BY DESIGN (the sixth marker); step 0.2 adds
`sku-b-ratification-6` to the enumeration and greens it."* Row 2 is that step.

---

## Deviations

**Dv169 — v4's `attempts.verbatim` is still (11)'s clause, and its parenthetical names v3.**
(11)'s sentence reads "…under a re-registration (results/sku_pilot_prereg_v3.json, registered BESIDE
v2 before the resumed session)", and v4 carries it unchanged. Moving it to (12)(a)'s sentence would
be a FOURTH entry in `supersedes.moved`, and the contract says the list enumerates only three. Not
fixed: instead `attempts.authority` is added beside the clause and says which reading each number
comes from, and `supersedes.readings` carries (12)(a)–(d) verbatim as the law this file runs under.
The same shape applies to `resume.readings.d`'s "$0.45" — it is what v3 was registered under, it is
superseded by (12)(a) and it is not overwritten, and a test asserts both halves of that sentence are
in the record. Named rather than tidied, because tidying a registered clause is how a registration
stops being the thing that was signed.

**Dv170 — `scripts/sku_bar_verdicts.py` still names v3 in three places, and one of them is not
guarded.** `PREREG` and `RECORD` default to `results/sku_pilot_prereg_v3.json` and
`results/sku_b_positions_v3.json` — those two are loud, because the producer takes `--record` and
`--prereg` and already refuses a mismatch by name (`the record was bought under X, not Y`). The
third is not: line 395 writes `"contract": "docs/PROMPT-sku-b-v3-run.md step 6; docs/SPEC.md
amendment 3.17 (6), (11)"` INTO the verdict record — the artifact the team lead opens at acceptance
— and nothing checks a provenance string. Scored after the v4 run it would claim the verdicts were
produced under the v3-run contract and cite (6) and (11) without (12). Not moved in this contract:
it is the bar producer's own work and the record it names will exist in the v4-run contract, which
is where all three belong. Named here so that contract inherits a complete list rather than a
partial one. Checked and clear: nothing in that file keys on the `bought_by` VALUE — the
`RESUME_PHASE` rename to `sku-b-v4` reaches every dump row, and the producer reads
`record["resume"]["sessions"]` as data without comparing it to a literal.

**Dv171 — the ledger guard compares the file NAME, not the path.** The trap (12)(b) names is reading
another session's anchor, and `spend_sku_b_v3.json` against `spend_sku_b_v4.json` is what separates
those; a deliberate redirect into another directory still passes, creating a fresh anchor at today's
balance and charging no previous session. Marked `ponytail:` with its upgrade path. The other half
of this: the test harness drives `main` into a tmp directory, so `run_resume` and `ledgered` now use
the REGISTERED file name there — a harness that renamed the anchor would be driving a run the
registration does not describe, which is the thing the guard exists to stop.

**Dv172 — commit 1 is red by design and the checkout table shows it.** The contract pre-authorises
it and step 0.2 greens it in the next commit. Kept as two commits rather than merged: merging them
would hide, inside one green commit, the fact that a SPEC amendment landed with the strip's
enumeration not yet extended — and that enumeration being loud is the whole reason it is a literal
list. The row is annotated rather than omitted.

**Dv173 — the peft venv was rebuilt again.** Dv160's scratch venv did not survive; rebuilt with
`python3 -m venv --system-site-packages` + `pip install peft==0.20.0` in this session's scratchpad.
`transformers` 5.14.1 and `torch` 2.13.0 were already present and are the volume's versions. No repo
dependency moved; `pyproject.toml` is untouched. This is the third time a scratch venv has had to be
rebuilt to run the preflight, which is a small recurring tax on the one check that exercises the real
libraries.

**Dv174 — the ADR commit landed after the four deliverables, not at Step 0's listed position.** Step
0 lists it third of four with the vault tail fourth, and the vault tail is unambiguously last — so
the list is a set of pre-authorised commits rather than a sequence. The ADR quotes the cap arithmetic
of deliverable 3, so writing it before that record existed would have meant quoting numbers not yet
produced. Ordering chosen on that ground and named here.
**Dv175 — the vault tail is its own commit but not the last one.** The contract says "vault tail →
its own final commit", and it is commit 9 of 10: this report needed one more commit to record the
`make check` of the commit that carries it, which by construction can only be written after that
commit exists. The vault tail is not mixed into any other change, which is what the rule protects;
what moved is the word "final". Named rather than repaired by a rebase — rewriting a published
commit to make an ordering claim true is a worse trade than saying it plainly.

---

## Assumptions

1. **"The supersede metadata" covers the new `supersedes` sub-blocks.** The contract's `moved` list
   names three entries, and (12)(a)–(d)'s verbatim transcription plus the refusal-record pin are
   read as part of the third. They live INSIDE `supersedes` rather than beside it, so the entry is
   literally true of where they sit. If the team lead meant `supersedes` to gain only a record and a
   sha, this record carries two blocks more than intended — and none of them touches a bar.
2. **The v4 run's artifact paths** (`results/sku_b_positions_v4.{json,jsonl}`,
   `results/spend_sku_b_v4.json`) are the executor's naming, following v3's pattern. The contract
   specified the ledger name; the record and dump names follow it so the refusal record of v3 is not
   overwritten by a session that succeeds.
3. **The 3% drift multiplies the whole billed second count**, not one leg. The contract names the
   term and the corner it must fit, not where it applies; applying it to everything is the
   conservative reading and it is stated in the record.
4. **$0.00030669/s is still the rate.** Read from `results/srv2d_cost.json :: rate.usd_per_second`,
   settled, and not re-derived — there has been no completed run to re-derive it from.
5. **402.586 s is the boot to price.** It is the only same-configuration reading and it is the
   refused session's own. Whether the volume is warmer now is not something this record can know, so
   the full figure is priced rather than a discounted one.
6. **The two warm-up marginals are n=1 each.** They are used as rates because the alternative for
   the page is a sample of the wrong kind of page and the alternative for text is a bound with no
   measurement behind it at all. Both n's are carried beside their numbers in the record.

---

## Commits

| # | commit | subject |
|---|---|---|
| 1 | `f721115` | `docs(team-lead)`: SPEC 3.17 (12), the v4-prep contract and STATUS — committed unedited |
| 2 | `7e6e528` | `test(sku-b-v4-prep)`: the strip's enumeration gains `sku-b-ratification-6` |
| 3 | `4905295` | `feat(sku-b-v4-prep)`: pre-registration v4, registered BESIDE v3 on a fresh ledger |
| 4 | `20b9436` | `feat(sku-b-v4-prep)`: the v4 constants set together, and one cost block for both exits |
| 5 | `6369123` | `feat(sku-b-v4-prep)`: projection v4 — both measured marginals as corners |
| 6 | `87c2240` | `feat(sku-b-v4-prep)`: the preflight re-driven against the v4 registration |
| 7 | `bb6b96e` | `docs(decision)`: the v3 refusal and the v4 ruling |

| 8 | `8f4a7ed` | `docs(report)`: sku-b-v4-prep |
| 9 | `7b9caa4` | `chore(vault)`: the sku-b-v4-prep tail — the day's log, hot.md, the index |
| 10 | — | `docs(report)`: sku-b-v4-prep — the checkout table's own tail, and Dv175 |

Ten commits. The vault tail is commit 9 rather than the last; Dv175 says why.

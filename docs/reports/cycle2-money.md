# cycle2-money — the ledger closes, the line opens, and the step meter stops running forever

**Contract:** `docs/PROMPT-cycle2-money.md` · **class:** zero-GPU, cloud READ-ONLY · **spend:** $0.00
**Baseline:** `make check` **2 562 passed / 2 skipped**, HEAD `48c974a` with the standing tail
**Close:** **2 583 passed / 2 skipped** (+21 tests), HEAD `c86d3fd`
**Law:** SPEC amendment **3.23**, landed by this contract — operator ruling 2026-08-16 (the reader
sitting). Two ADR debts paid, Phase 4 CLOSED, probe-b's step SETTLED.

**Precondition confirmed with the operator before the first `git add`:** the parallel session that
wrote today's vault files is closed.

---

## Read-back, before any edit

**The six landing parts** (fix-c's table, all six moved again):

| # | part | forced by |
| --- | --- | --- |
| 1 | the marked block in `docs/SPEC.md`, index note inside it | the contract |
| 2 | the literal enumeration in `tests/test_sku_prereg.py` | a red test |
| 3 | `write_prereg_5c2.BLOCKS_TODAY` (+ its docstring paragraph) | the producer's own refusal |
| 4 | `make check` green, one commit | the contract |
| 5 | the literal tail `BLOCKS_TODAY[10:]` in `tests/test_prereg_5c2.py` | a red test (Dv336) |
| 6 | the negative control's intruder, `amendment-3.23` → `amendment-3.24` | **a red test, for the first time** — fix-c's Dv374 assertion did its job |

**The anchor threshold** — the cycle-2 anchor is the first guard balance reading of **$40.00 or
more** after the operator's top-up, written verbatim with its timestamp; below it, anchoring is
REFUSED.

**The two step readings** — `step anchor − balance now` AND `billing walk since the step's anchor
time`; the verdict is the pessimistic **maximum where both exist**, and where the walk cannot answer
the figure is printed as a **LOWER BOUND**, never as a one-sided number.

---

## 0. Step 0 and Step 0.5

### 0.1 The standing tail — `c43a312`, `f0ac23b`

Live `git status --porcelain` before staging matched the contract's expectation exactly, and every
path was staged by name. Nothing was dirty outside the two classes, so there was no STOP condition.

| commit | paths |
| --- | --- |
| `c43a312` | `knowledge/daily_logs/2026-08-15.md`, `…/2026-08-16.md`, `knowledge/hot.md`, `knowledge/index.md`, `knowledge/decisions/INDEX.md`, `knowledge/decisions/reader-probe-card-and-interface.md` |
| `f0ac23b` | `docs/STATUS.md`, `docs/PROMPT-cycle2-money.md` — team-lead files, committed unedited |

`knowledge/daily_logs/2026-08-16.md` is the «further `knowledge/**` file» the contract anticipated.
The probe-b ADR was already written and was **not** duplicated.

### 0.2 The two ADR debts — `49cfe35`

`knowledge/decisions/serving-latency-deferred.md` and `knowledge/decisions/reader-sitting-16-08.md`,
English long form, translated from the two «День 16.08» sections of `docs/STATUS.md` without
reinterpretation, each with its row in `knowledge/decisions/INDEX.md`.

The first carries the decomposition (~239 s cold start, ~214 s of it the 62 GB bf16 load with
on-the-fly NF4; `idleTimeout: 60`; ~5 tok/s decode off the research stack), the warm-row parity that
acquits both runtime and card (**4.07 s pod vs 4.10 s serverless**), the two priced-and-unbought
cures, and the operator's deferral to «готовим прод» with the accepted price written down.

The second carries probe-b's acceptance and the four rulings — the $20 line with its three clauses,
the A+B v3 registration with the container ruling («two disagreeing top-level objects = REFUSE,
never last-wins»), the varto silencer off for the reader path alone with the new census cell
**measured and never derived**, and the «категория» ≡ «категория_личное» adjudication that re-derives
gold as a named r2 without editing the reference.

---

## 1. D1 — the Phase-4 ledger closes

Written by the guard, not by hand: `python3 scripts/runpod_guard.py --close --note "…"`. **No figure
in the entry was typed**, and every one of them re-derives from the `billing_by_kind` lines published
beside it.

```json
{
  "at": "2026-08-16T11:09:48+00:00",
  "closed": true,
  "balance": 22.519483661,
  "window_start": "2026-08-01T08:34:09+00:00",
  "balance_delta_usd": 12.470794,
  "billing_since_usd": 32.470794,
  "billing_by_kind": {"pods": 17.692135, "network-volume": 3.227778, "serverless": 11.550881},
  "spent_usd": 32.4708,
  "remaining_usd": 0.5292
}
```

**Both readings are carried BECAUSE they disagree, and the gap is exactly $20.00.** The operator
topped the account up on 2026-08-15, after this ledger's anchor was taken, so the balance delta
under-counts by that top-up and the billing walk is the binding number — as it has been since the
top-up landed. A closing entry that carried only `spent_usd` would have hidden the one fact a reader
needs to know about this ledger.

**Append-only, checked rather than asserted.** Against `HEAD~`: `sessions` 40 → 41, the prior 40
entries byte-identical, `runpod_balance_at_phase4_start`, `anchored_at`, `phase4_cap_usd` and the
file's own note untouched, and no new top-level key. The two tests that read the real file and select
their row by timestamp are green; so are `test_repair_phase4_ledger` and `test_witness_phase_ledger`,
which build fixtures from it.

**The guard says it.** Closure is a typed field (`closed: true`) that `closing_entry()` looks for
from the end of `sessions` — never a phrase grepped out of `note`, because a ledger whose state is
inferred from prose has a state nobody can test.

---

## 2. D2 — SPEC amendment 3.23 — `b3db748`

The block was written into `docs/SPEC.md` by a script through Bash: `.claude/settings.json` denies
every file-editing tool on that path, and this is the manoeuvre 3.20, 3.21 and 3.22 landed by. The
script derives all three pin families with the producers' **own** `registered_law()` before and after,
and rolls the file back if any of them moves.

```
v1-v4  973c87890ad049d5… unmoved
B'     6818926d22b2a46b… unmoved
5c2    3dd43923edc18e72… unmoved
blocks: 15 — amendment-3.23 is last
80,452 → 82,195 bytes live; registered law unmoved (50,135 == 50,135 bytes)
```

**Every strip family that names today's blocks, enumerated** — both producers grepped, not assumed:

| site | what it holds | moved |
| --- | --- | --- |
| `scripts/write_sku_prereg.RATIFICATION_NAME` | the regex `amendment-(?:index\|3\.\d+)` | **no** — it already matches `amendment-3.23`; the single point of change was not one this time |
| `scripts/write_prereg_5c2.KEEP_BLOCKS` | the sealed 5c2 pin's TEN names | **no** — Dv335; growing it would re-pin a sealed record |
| `scripts/write_prereg_5c2.BLOCKS_TODAY` | every block the file carries now | **yes**, + its docstring paragraph |
| `scripts/write_sku_prereg_b2.KEEP_BLOCKS` | `('sku-b-ratification-7', '-8')` | **no** — B′ keeps two and strips the rest, so a new block is stripped and its pin survives |
| `tests/test_sku_prereg.py:217–283` | the literal enumeration | **yes** |
| `tests/test_prereg_5c2.py:242` | the literal tail `BLOCKS_TODAY[10:]` | **yes** |
| `tests/test_prereg_5c2.py:316` | the negative control's intruder | **yes**, 3.23 → 3.24 |
| `amendment-index` | the index block inside the sealed pin | **no** — the note lives inside 3.23's own block, as 3.19–3.22 did; it is now FIVE amendments behind |

### 2.1 The negative controls

```
(1) the intruder control had to move, and the suite FORCED it this time
    'amendment-3.23' in BLOCKS_TODAY  -> True   <- fix-c's assertion `intruder not in writer.BLOCKS_TODAY` fails on exactly this
    'amendment-3.24' in BLOCKS_TODAY  -> False   <- the new intruder is a name nobody has looked at

(2) the producer refuses an unknown block; the live file passes
    refused: ... would be stripped of without a reader ever seeing it — add its name here and look at it
    live docs/SPEC.md: passes

(3) the enumeration and the literal tail are red without the new name
    findall(SPEC) == BLOCKS_TODAY            -> True   (15 blocks)
    findall(SPEC) == BLOCKS_TODAY[:-1]       -> False
    BLOCKS_TODAY[10:] -> ('amendment-3.19', 'amendment-3.20', 'amendment-3.21', 'amendment-3.22', 'amendment-3.23')
    block appears exactly once: begin 1 / end 1
    KEEP_BLOCKS still TEN and amendment-index untouched: True

(4) the six sealed pins, re-derived by the producers' OWN registered_law()
    v1  973c87890ad049d5...  unmoved
    v2  973c87890ad049d5...  unmoved
    v3  973c87890ad049d5...  unmoved
    v4  973c87890ad049d5...  unmoved
    B'  6818926d22b2a46b...  unmoved
    5c2 3dd43923edc18e72...  unmoved
    live SPEC 82,195 bytes (was 80,452) - registered law 50,135 bytes, unmoved
```

**Part 6 was forced for the first time.** fix-c's finding (5) called the intruder «a control with a
shelf life» and added `assert intruder not in writer.BLOCKS_TODAY` so the next omission would be red
instead of silent. The next landing is this one, and the assertion fired on the name it had planted.
A control that predicts its own next failure and then catches it is worth more than the four lines it
cost.

---

## 3. D3 — the guard — `27eba42`

Pins grepped before the first edit. `results/prereg_5c2_run.json` is the **only** record in the repo
that pins `scripts/runpod_guard.py` by sha (its `producer.borrows`); the other five files that name
the path do so in prose. Treatment: the house manoeuvre, never a re-pin — see Dv414.

### (a) The cycle-2 line

`CYCLE2_CAP_USD = 20.00` and `CYCLE2_ANCHOR_MIN_USD = 40.00` sit beside `PHASE_CAP_USD = 33.00`; the
ledger is `results/spend_cycle2.json`. Once Phase 4 is closed the line becomes the live ledger and is
read by the **same** `enforce()` the phase used — one implementation, two constants, so the
pessimistic rule of Dv33 has one home rather than two places to be half-applied. That is precisely how
`--step` came to have one reading where the phase had two.

**The anchor is DEFERRED and it is a named debt: «anchor deferred, awaiting funds».** The balance
reads **$22.52**, under the $40.00 threshold, so the guard refuses. The refusal path is shipped
TESTED in both directions — $39.99 refuses and writes nothing, $40.00 anchors and records the balance
verbatim with its timestamp — and nothing was polled or waited on.

### (b) Dv411 — three states, and none of them collapses

| state | verdict | what prints |
| --- | --- | --- |
| both readings | the pessimistic **maximum** | the delta, the walk, the decomposition, the step's own resources |
| a window, but «no rows yet» / unreadable | the delta **alone** | `UNAVAILABLE (…)` and «the delta stands alone as a **LOWER BOUND**» |
| no anchor time on the ledger at all | the delta **alone** | «this ledger **records no anchor time**, so the billing walk has no window to ask for» |

The third is a different sentence from the second on purpose: a walk that was never asked is not a
walk that answered nothing, and collapsing them rebuilds the defect one layer up. New step anchors
now record `anchored_at`, so the third state empties out — the driver of a step already wrote that key
under the same name and the same meaning, so `read_step` uses `setdefault` and never gives a ledger a
later time it did not happen at.

### (c) Attribution by kind

`billing_since` becomes **`billing_by_kind`** and returns the three kinds APART instead of summed;
`own_resources()` is that dictionary with `ALWAYS_ON_KINDS = ("network-volume",)` left out. The split
is by KIND and not by arithmetic — subtracting an hourly rate would be a second model of the bill
sitting beside the bill.

On probe-b's own settled lines the two answers **straddle the cap they were judged by**:

| | |
| --- | --- |
| pods + serverless — the step's own resources | **$0.313162** |
| network volume `qw4nwleanc`, standing | $0.136111 |
| everything the walk returned | $0.449273 |
| the balance delta at this session's reading | $0.449000 |

$0.3132 is inside $0.35 and $0.4493 is not. That is the distance between «overrun» and «inside», and
it was never about probe-b.

### (d) A step can be CLOSED

`--close` appends a settled entry — the walk, its decomposition, both readings — and **refuses to
write one over a walk that did not answer**, because closing on «no billing rows yet» would freeze a
zero into a record that is never re-derived. A closed ledger is priced by that entry forever after,
and the growth stops: the test drives the guard twice with the balance $0.05 lower on the second call
and the printed figure is identical.

Closing is **not an amnesty** — a closed step whose settled figure breaches its cap still refuses, and
that is a test.

**A closed phase refuses with the GAP, never with a cap breach.** Phase 4 is at $32.4708 of $33.00 and
the volume alone carries it past the line within days; a closed ledger that still shouted «the cap is
reached» would be Dv412 one layer up — a refusal about a charge nobody started. The refusal now names
3.23 (3) and says «this is not a cap breach» in as many words.

### (e) Two structural changes the contract implies

**Refusals are collected, not returned on.** «One-sided prints are the bug»: a guard that returned on
the first refusal could not show the step figure the refusal was about. Every leg now runs and prints,
and the exit code is decided once at the end. The consequence had to be handled — the step ANCHOR
write is now gated on the verdict rather than on the order of the code, with its own test
(`test_a_refused_start_leaves_no_step_anchor_behind`), because a counter must exist only for a step
that was allowed to begin.

**`tests/test_prereg_5c2.MOVED_BORROWS` carries a token PER MOVE.** As a single string it went on
passing after the guard moved a second time — `live != digest` was already true, the recovered blob
still lacked `step_ledger_path`, the disk still carried it — so it had stopped being a statement about
what moved. It is now `("step_ledger_path", "billing_by_kind")`, each read both ways. Nothing this
sealed registration states follows either move: it borrows the guard as the instrument that enforces
the cap and reads `PHASE_CAP_USD`, which neither move touched, and 3.18 (7)(b) already forbids
re-scoring what it priced.

---

## Verify

### The suite

```
$ make check
ruff check .
All checks passed!
pytest -q
2583 passed, 2 skipped in 177.65s (0:02:57)

$ ruff format --check .
306 files already formatted
```

2 562 → **2 583**, +21 tests. The formatter was run before any sha was computed or any artifact
written (Dv363/Dv410's lesson).

**Per commit, as a rule rather than a list** — an enumeration cannot name the commit that carries it.
`make check` ran on the exact tree of every commit that moves code, a test or a result artifact:
`b3db748` (2 562 / 2), `27eba42` (2 580 / 2), `c86d3fd` (2 583 / 2). The other three differ from a
verified tree in prose only — `c43a312` and `49cfe35` move `knowledge/**`, `f0ac23b` moves
`docs/STATUS.md` and this contract — and checked rather than assumed: the only vault path any test
opens is `knowledge/templates/daily-log.md` (`tests/test_templates.py`), untouched, and every
occurrence of `docs/reports/` under `tests/` is inside a docstring.

### The guard

```
$ python3 scripts/runpod_guard.py
balance now       $22.52
PHASE 4 CLOSED    $32.4708 of $33.00  (final reading 2026-08-16T11:09:48+00:00)
  pods            $17.6921
  network-volume  $3.2278   <- always on, beside the run and never inside it
  serverless      $11.5509
CYCLE 2           NOT ANCHORED — the line is $20.00 and its anchor needs a balance of $40.00 or more

REFUSED: Phase 4 is CLOSED at $32.4708 and the cycle-2 line is not anchored — the balance reads
$22.52, under the $40.00 of SPEC 3.23 (2). This is the INTER-LEDGER GAP: unbudgeted BY DESIGN
(3.23 (3)) and nothing may run in it. The standing network volume is the only thing that bills
here. This is not a cap breach.
                                                                        # exit 1 — see Dv417
```

```
$ python3 scripts/runpod_guard.py --step probe-b --step-cap 0.35
  … the same phase-closed and gap lines …
PROBE-B CLOSED     $0.3132 of $0.35  (settled at 2026-08-16T11:09:46+00:00, window from 2026-08-15T20:31:00+00:00)
  pods            $0.0287
  network-volume  $0.1361   <- always on, beside the run and never inside it
  serverless      $0.2845
                                # closed at $0.3132, decomposed by kind, NO breach of the step cap
```

**The step no longer shouts a false cap breach.** Yesterday's reading of this same command was
`REFUSED: probe-b's $0.35 cap is reached ($0.4493 spent)`, exit 1.

### The tests are not vacuous

The new suite was run against the **pre-fix guard**, with a walk adapter appended so every test
REACHES the old behaviour instead of dying on an `AttributeError` about a function that had not been
written:

```
17 failed, 17 passed in 0.41s
```

Fifteen of the sixteen older tests pass on the old guard; the sixteenth,
`test_the_billing_walk_asks_for_serverless_too`, fails because it now also asserts the kinds arrive
apart. Every one of the seventeen failures is a behavioural claim about this fix. Two of the
twenty-one new tests pass on the old guard and are named as such: `test_the_closing_flags_refuse_to_be_used_half` passes there only because
argparse rejects `--close` as unknown, and `test_a_refused_start_leaves_no_step_anchor_behind` passes
because the old control flow made it true by accident — it is a regression guard for the restructure,
which is why it exists.

### Artifacts

| file | sha256 (16) | bytes |
| --- | --- | --- |
| `results/spend_phase4.json` | `8b4b041603ff9326` | 14 532 |
| `results/spend_probe_b.json` | `30c629e34f855997` | 1 794 |
| `docs/SPEC.md` | `6c57df087de49f48` | 82 195 |
| `scripts/runpod_guard.py` | `ccedbddd114f1e89` | 34 335 |

### The DO NOT list, as evidence

| clause | evidence |
| --- | --- |
| team-lead files never edited | `docs/STATUS.md` and `docs/PROMPT-cycle2-money.md` committed verbatim in `f0ac23b`; `docs/SPEC.md` gained one marked block and nothing else — its registered law is unmoved at 50 135 bytes |
| no cloud resource created | only `runpodctl user` and `runpodctl billing <kind>` were run, both read-only. Measured, not asserted: the walk from `2026-08-16T00:00:00Z` returns **0 pod rows and 0 serverless rows** beside one network-volume row ($0.106944), so the standing volume is the day's only charge and this contract spent **$0.00** |
| no sealed record re-pinned | six SPEC pins re-derive; `MOVED_BORROWS` grew a token instead of the record growing a hash; `KEEP_BLOCKS` still ten |
| `spend_*.json` anchors untouched | both writes are appends — prior entries byte-identical, no new top-level key, anchors and `anchored_at` unchanged |
| no reader / r1 / census / dashboard / collection change | `git diff --name-only 48c974a..HEAD` returns eighteen paths (this report is the nineteenth), none of them under `src/`, `config/`, `data/` or `dashboard/` |
| never `git add -A` | all six commits staged by explicit path |

---

## Deviations

Numbering continues the programme's; probe-b's last was Dv412, so this report opens at **Dv413**.

- **Dv413** — the contract names `results/prereg_5c2.json` as the record that borrows the guard
  LIVE. There is no such file; the record is `results/prereg_5c2_run.json`, and a walk over every
  file under `results/` confirms it is the only one pinning `scripts/runpod_guard.py` by sha. Worked
  against the file on disk. [cause: brief-vs-disk]
- **Dv414** — the contract says the guard's sha move «takes the third `MOVED_BORROWS` entry … done
  twice already». The constant on disk had **one** key and **one** token. The counting is a
  labelling question — the manoeuvre has been applied twice if the producer's own `amendment-3.19`
  move counts, and this is the second entry in the dict either way — but the mechanical finding
  underneath it is real and worse: **as a single string the constant stayed GREEN through my move**,
  because every one of its four assertions was still true of the FIRST move. Fixed by making the
  value a tuple, one token per move, each read both ways. [cause: brief-vs-disk / control-decay]
- **Dv415** — **the closing record's headline did not re-derive from its own decomposition.**
  `settled_usd` came from the full-precision walk ($0.313161) while `billing_by_kind` published the
  lines rounded to six places, which add to $0.313162. One micro-dollar, and the difference between
  a record and a record that can be checked. Caught by the test that reads the shipped artifact —
  not by any of the fixture-driven ones, because a fixture's numbers are already round. Every figure
  is now derived from the ROUNDED lines, and the seam has its own unit test on the exact numbers
  that exposed it. Both ledgers were rewritten from a restored `HEAD` before either was committed.
  [cause: rounding-seam]
- **Dv416** — the first pair of closing entries carried dollar figures **inside the note** that
  disagreed with the fields written beside them: the note said «the balance delta of $0.4493»,
  copied from probe-b's report, while `balance_delta_usd` recorded this session's $0.4590. Both
  entries were rewritten (guard-written again, from a restored `HEAD`, nothing hand-edited) and the
  notes now carry provenance and law and **no figure a field already holds** — verified by grepping
  every `$n.nn` out of both notes and finding none. [cause: hand-typed-number]
- **Dv417** — **both guard commands in the Verify block exit 1**, and that is the correct answer.
  The contract's comments describe what they SAY — «phase 4 closed», «closed at X, decomposition by
  kind, no breach» — and all of that prints. The non-zero exit is the inter-ledger gap of 3.23 (3)
  refusing a start, which is the clause working. Named here so a future reader does not read the
  exit code as a failure of this contract. [cause: brief-vs-instrument]
- **Dv418** — `docs/STATUS.md` says the vocabulary ruling «живёт отдельной записью» (its own
  record), while the contract puts it inside `reader-sitting-16-08` as ruling (4). Followed the
  contract — two ADRs, not three — and the ruling has its own titled section inside that record, so
  both readings are served without a third file. [cause: brief-vs-status]
- **Dv419** — **the second step reading needs an anchor TIME and no step ledger carried one.**
  `read_step` wrote a balance and no clock, so the walk had no window to ask for; that is why Dv411
  could only ever have been half-fixed without a schema change. New anchors record `anchored_at`.
  probe-b's window came from `--since`, sourced from its own report's timeline (20:31 UTC), and the
  reading is invariant across 20:25 / 20:31 / 20:33 — all three return the same three lines, and the
  same three the report published. [cause: schema-gap]
- **Dv420** — the phase's billing figure is **$32.4708** here against the **$32.4513** `docs/STATUS.md`
  read this morning. Not a discrepancy: the volume accrues ~$0.0092/h and four hours passed. It is
  also the standing demonstration of why the phase had to close — a closed ledger stops moving, an
  open one does not. [cause: always-on-drift]
- **Dv421** — collecting refusals instead of returning on the first one changed WHO reaches the step
  leg: a refused phase used to return before a step anchor could be written. The property was
  preserved deliberately rather than by luck — the anchor write is gated on the verdict and has its
  own test, which passes on the old guard too and is a regression guard, not a discovery.
  [cause: control-flow]
- **Dv422** — `billing_since` was **removed** rather than kept as a two-line wrapper over
  `billing_by_kind`. Two names for one walk is exactly the drift this module keeps being bitten by,
  and the grep says nothing else in the repo calls it. The consequence: the by-hand command in
  the Verify block of `docs/reports/probe-b.md` (`… g.billing_since(...)`) no longer
  runs. That report is a historical record and was not edited; the replacement is
  `g.billing_by_kind(...)`. [cause: api-rename]

**Named debt, as the contract asks:** **anchor deferred, awaiting funds.** The cycle-2 line has its
law, its constants, its ledger shape and its refusal, all tested — but no anchor, because the balance
is $22.52 and 3.23 (2) puts the floor at $40.00. The first guard run after the operator's top-up
writes it; nothing else is owed.

---

## Findings

**(1) The inter-ledger gap has a cost and no owner.** The volume bills ~$0.0092/h — about $0.22 a day
— and 3.23 (3) says nothing may run in the gap. Every day between the close and the top-up is
therefore money spent against no line at all, and it is spent on a 100 GB volume whose contents
(`repo/` plus a 467 MB adapter) exist to make the next reader run cheap. Deleting it is not free
either. This is a team-lead ruling, not a script's, and it is the only clause of 3.23 with an
arithmetic consequence nobody has priced.

**(2) `results/spend_cycle2.json` will be written by the first run after the top-up, unreviewed.**
`read_cycle2` anchors on sight, exactly as `read_ledger` has always done for the phase — and that is
the house pattern. But the phase's anchor was taken once, in 2026, by a person who was watching. The
next cycle-2 anchor will be taken by whatever command happens to run first, which may be a `--step`
invocation whose author is thinking about something else. The threshold protects the number; nothing
protects the moment.

**(3) Twenty-two other step ledgers are in state three.** `results/` holds 23 `spend_*.json` step
ledgers beside the phase's, **none** of them carries an anchor time, and only `probe-b`'s has been
closed. Every one of the other 22, if asked today, reports a balance delta that has been growing at
the volume's rate since the day it ran — and now says so out loud («records no anchor time … LOWER
BOUND») instead of printing a number that looks settled. Closing them is cheap — one
`--close --since` each, with the window sourced from that step's own report — and it is not this
contract's scope.

---

## Process signals

- The contract named six landing parts and the tree held six. The part that fix-c could not enforce
  is the one that fired first: an assertion added *because* a control had decayed caught the very
  next landing. Controls that predict their own next failure are worth writing.
- The two defects that mattered were both found by a test that reads a **shipped artifact** rather
  than a fixture — the rounding seam (Dv415) and, one contract earlier, the guard bugs found by
  USING the guard. Fixtures carry round numbers, and round numbers hide arithmetic.
- Three of the four D3 sub-deliverables were one function each; deciding that a closed step's verdict
  moves to the settled figure rather than disappearing took longer than writing any of them, and it
  is the part a future reader will want.
- «Read the pins before the first edit» paid twice: once by finding that the brief's record path does
  not exist (Dv413), once by finding that the constant it sent me to would not have noticed my change
  (Dv414). Neither would have gone red.
- This is the third consecutive morning a guard defect was found by running the guard rather than by
  reading it. The money path gets its bugs from use, and the report that publishes a finding it
  refuses to fix mid-session (probe-b's Dv411, Dv412) is what makes the next contract cheap.

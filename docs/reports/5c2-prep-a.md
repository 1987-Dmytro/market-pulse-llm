# 5c2-prep-a — the law can grow again, the phase cap moves 25 → 30, the phase ledger is repaired

**Contract:** `docs/PROMPT-5c2-prep-a.md` · **Authority:** `docs/SPEC.md` amendment 3.18 (3),
operator ruling 2026-08-13 · **Session:** 2026-08-13, **$0 spent** (the only RunPod contact was the
guard's read-only `runpodctl` calls).

`docs/SPEC.md` can grow again without breaking a sealed pre-registration: the strip that produces
the registered law now knows the amendment family, and both sealed pins re-derive exactly from the
amended file. The Phase 4 cap is $30.00 everywhere it lives — in the constant the guard enforces, in
the ledger field that documents it, and in the fixtures that would otherwise have gone on passing
while measuring the old line. And `results/spend_phase4.json` is no longer two days and three paid
sessions behind reality: the missing entries are appended from the step ledgers that recorded them,
today's reading is in by the guard's own hand, and a permanent test now refuses to let a paid
session leave that file silent again.

---

## Deliverable 1 — a law that can grow without breaking a sealed pin

**The failure, reproduced before it was fixed.** Amendment 3.18 and the repaired amendment index are
new text in `docs/SPEC.md`, and `results/sku_pilot_prereg_v4.json` / `results/sku_pilot_prereg_b2.json`
pin the whole file with the marked blocks stripped off. Three tests went red on the working tree:

```
FAILED tests/test_sku_prereg.py::test_every_pinned_input_still_hashes_to_what_it_says
FAILED tests/test_sku_prereg.py::test_the_record_rebuilds_identically_apart_from_its_timestamp
FAILED tests/test_sku_prereg_b2.py::test_the_shipped_registration_is_the_one_this_script_writes
3 failed, 2010 passed, 2 skipped in 57.57s
```

**What was built.** `scripts/write_sku_prereg.py :: RATIFICATION_NAME` learns the second family:

```python
RATIFICATION_NAME = re.compile(
    r"^<!-- (sku-b-ratification(?:-\d+)?|amendment-(?:index|3\.\d+)) begin", re.MULTILINE
)
```

One expression, one implementation — `write_sku_prereg_b2.py` and both test modules reach
`registered_law` through this module, so the b2 record greened from this single change and **neither
b2 file was touched**. The docstring beside it now says what the family is for and that a block
whose name the expression does not know is *not* stripped, so the pin stops re-deriving and the test
goes red rather than passing quietly.

`tests/test_sku_prereg.py`'s literal `blocks` enumeration gains both names in **document order** —
`amendment-index` first, `amendment-3.18` last — so an amendment still cannot arrive unnoticed. The
loop below it was the trap the contract named: `for name in blocks[1:]` skipped the first name
because `sku-b-ratification` is a prefix of `-2` … `-8`, and in document order `blocks[0]` is now
`amendment-index`. The skip is keyed on the **name**:

```python
    for name in blocks:
        if name == "sku-b-ratification":
            continue
        assert name not in law
```

A `[1:]` slice would have stayed green while quietly ceasing to check that `amendment-index` came
off.

### The gate — reproduced, not trusted

Both directions on both records. A live hash equal to a pin would mean 3.18 never landed.

```
live docs/SPEC.md            sha256 273e9dae9e37ba1a4721877a3b471b8f56583e5b404887556d23bd035a833bcd
blocks the strip now knows   ['amendment-index', 'sku-b-ratification', 'sku-b-ratification-2',
                              'sku-b-ratification-3', 'sku-b-ratification-4', 'sku-b-ratification-5',
                              'sku-b-ratification-6', 'sku-b-ratification-7', 'sku-b-ratification-8',
                              'amendment-3.18']

results/sku_pilot_prereg_v4.json   (keep=())
  pinned                     973c87890ad049d5fa09879de148794f171994fac64437128bcecbaeade36604
  registered_law(SPEC)       973c87890ad049d5fa09879de148794f171994fac64437128bcecbaeade36604
  re-derives (stripped==pin) True
  live differs (live!=pin)   True

results/sku_pilot_prereg_b2.json   (keep=('sku-b-ratification-7', 'sku-b-ratification-8'))
  pinned                     6818926d22b2a46b594ed417689347bbfbc8069c17fdbb11d35b40ec996b27b3
  registered_law(SPEC)       6818926d22b2a46b594ed417689347bbfbc8069c17fdbb11d35b40ec996b27b3
  re-derives (stripped==pin) True
  live differs (live!=pin)   True
```

**Neither record was re-pinned.** `results/sku_pilot_prereg_v4.json` and
`results/sku_pilot_prereg_b2.json` are byte-identical to what was committed before this session.

### The negative control

`test_a_line_outside_every_marked_block_breaks_both_sealed_pins` copies the spec into `tmp_path`,
appends one line **outside every marked block**, and asserts neither pin re-derives from the copy —
with the live file checked first as the positive control, because an inequality nobody has seen
equal is not evidence. `docs/SPEC.md` is never written by a test.

**Commit:** `81855de` — `docs/SPEC.md` + `scripts/write_sku_prereg.py` + `tests/test_sku_prereg.py`
together. **This is the only commit in the session that carries `docs/SPEC.md`**; committing it
alone would have put a red commit in the history.

---

## Deliverable 2 — the phase cap moves 25 → 30, in every home it has

SPEC 3.18 (3), operator ruling 2026-08-13.

| home | before | after |
|---|---|---|
| `scripts/runpod_guard.py :: PHASE_CAP_USD` — what the guard ENFORCES | 25.00 | **30.00** |
| `results/spend_phase4.json :: phase4_cap_usd` — documentation | 25.0 | **30.0** |
| `tests/test_runpod_guard.py` — six cap-coupled sites, see below | 25.0 | **30.0** |
| `runpod_balance_at_phase4_start`, `anchored_at`, the 31 logged sessions | 35.0 / 2026-08-01T08:34:09Z / 31 | **untouched** |

`read_ledger` returns the ledger file untouched when it exists, so the constant is the enforced
number and the field is documentation — moved together in one commit or one of them is a lie waiting
to be quoted.

**Three numbers, and they are not the same number.** The contract names **three** literals (lines 26,
112 and 186 as the file stood). The file carries **six** cap-coupled sites. Moving the constant first
reddened **three** of them — and only ONE of those three is a literal the contract names. The other
three were found by reading, because a fixture can be coupled to the cap and still pass. The method
was to move the constant first and let pytest name what it could, then read for what it could not:

- `test_the_cap_refuses_the_next_start` (**reddened**) — **flipped.** Balance 9.99 is $25.01 spent: over the old
  cap, *under* the new one, so the test would have asserted a refusal that no longer happens. The
  fixture balance moved to 4.99 ($30.01), the same one cent over.
- `test_the_volume_keeps_billing_while_the_pod_is_stopped` (**reddened**) — `remaining_usd == 24.6`
  (= 25.0 − 0.4) → **29.6**. The spend the volume bills is unchanged.
- `test_the_first_run_anchors_and_says_so` (**reddened**) — `written["phase4_cap_usd"] ==
  guard.PHASE_CAP_USD == 25.00` → `30.00`. The only one of the contract's three literals that
  reddens by itself.
- `test_a_session_note_is_only_logged_when_the_start_is_allowed` (**silent**) — balance 5.00 is
  exactly $30.00 spent. It still refuses, but on the boundary rather than on margin; moved to 4.00
  ($31.00).
- The two ledger fixtures the contract names (`"phase4_cap_usd": 25.0`, twice) are **silent** —
  they are documentation inside a fixture and `read_ledger` returns the file untouched — and moved
  anyway.

`scripts/eval_zero_shot.py :: PHASE_CAP_USD = 8.00` was checked and is **not** a fourth home: it is
the Phase 3b OpenRouter cap, a different phase and a different account. Nothing else in `scripts/`,
`tests/`, `src/`, `results/` or `config/` names either constant.

**A finding, not a file this contract fixes:** `docs/ARCHITECTURE.md:324` describes the module in the
present tense as «The $25 Phase-4 GPU cap». It is now stale. Left alone deliberately — the contract
closes three homes and forbids widening scope, and ARCHITECTURE.md is a document prep-b or prep-c
should re-derive rather than have this session hand-patch. The `$25` in `scripts/runbook_4a.md`,
`4b`, `4c`, `45h2`, `srv2b` and the `docs/PROMPT-4*.md` files is **correct as history** — those are
records of sessions that ran under the old cap.

**Commit:** `3cfd792`.

---

## Deliverable 3 — the phase ledger tells the truth again

`results/spend_phase4.json` had not been appended since `2026-08-11T18:16:30Z` (sku-b-run). Three
paid sessions ran after it and lived only in their own step ledgers.

`scripts/repair_phase4_ledger.py` appends them in time order, **every number read from the step
ledger** (`runs[-1].balance` and its `at`), `spent_usd` = anchor − balance in the guard's own shape
and rounding, `remaining_usd` against **$25.00** — the cap in force when that money was spent. The
$25.00 literal is the module's own and is asserted *different* from `runpod_guard.PHASE_CAP_USD`:
importing that constant for the sake of DRY is precisely how a repaired history quietly re-scores
itself under a cap that did not exist when the money was billed.

```
anchor            $35.0000 at 2026-08-01T08:34:09+00:00
cap in force      $25.00 (SPEC 3.4 (4); 3.18 (3) raises it AFTER these)
at                              balance      spent  remaining  source
2026-08-11T20:48:07+00:00  12.0609061756    22.9391     2.0609  results/spend_sku_b_v3.json
2026-08-12T09:14:58+00:00  11.6919336398    23.3081     1.6919  results/spend_sku_b_v4.json
2026-08-12T16:45:21+00:00  11.3347237899    23.6653     1.3347  results/spend_skub2.json
appended 3 entries to results/spend_phase4.json (34 total)
```

**Cross-check the repair did not produce:** SPEC 3.18 (3) states independently that phase spend at
the ruling was **23.6653 by the anchor arithmetic**. That is skub2's row above, derived here from
`results/spend_skub2.json :: runs[-1].balance` and the anchor, with nothing typed.

**An append, never a regeneration.** `git diff` on the repair's write: **21 insertions, 0
deletions**. The anchor, `anchored_at` and all 31 existing entries are byte-identical, and a test
asserts every non-`sessions` field survives the write unchanged.

**Refusals, not guesses.** A missing step ledger, a step ledger with no paid run, a timestamp not
strictly after the last existing entry, a timestamp the ledger already carries — each exits
non-zero and writes nothing. The last rule is what makes the script idempotent, and it is asserted
against the **committed** ledger, not only against a copy:

```
tests/test_repair_phase4_ledger.py::test_the_repair_is_done_and_a_re_run_on_the_committed_ledger_refuses
  SystemExit: results/spend_sku_b_v3.json: results/spend_phase4.json already carries an entry at
  2026-08-11T20:48:07+00:00. Each session is appended exactly once and none is rewritten — if this
  is a re-run, the repair is already done. Nothing written.
```

### The permanent guard

`test_no_paid_step_ledger_is_silent_in_the_phase_ledger`: every run in every `results/spend_*.json`
step ledger that carries a `balance` — which is what separates a paid RunPod run from an OpenRouter
`runs` row, whose fields are `model`/`usd`/`requests` — must be witnessed by a phase entry with that
balance.

**One direction only.** The converse is not an invariant and asserting it would redden immediately:
the guard's own `--note` readings and the phase close-out entries have no step ledger behind them.

Three historical runs are excused **by name, one row each**, and each row names the phase entry that
witnesses it. The reason is not "no phase entry" — they all have one — but that the step ledger's
balance was read while the session ran and the phase entry was written minutes later, after
teardown, when the account had absorbed more of the bill:

| step ledger | run `at` | run balance | witnessed by | witness balance |
|---|---|---|---|---|
| `results/spend_5c1_vis.json` | 2026-08-09T11:28:50Z | 13.6119897968 | 2026-08-09T11:31:48Z | 13.4995549857 |
| `results/spend_5c1_vis.json` | 2026-08-09T13:03:50Z | 13.0358114078 | 2026-08-09T13:06:47Z | 12.9337324634 |
| `results/spend_sku_b.json` | 2026-08-11T18:14:10Z | 12.3242157645 | 2026-08-11T18:16:30Z | 12.2324512089 |

The test asserts each witness exists, is **later**, and reads **lower** — so an excuse that is not a
teardown reading of the same session fails — and that every row of the list was used, so an excuse
that stops applying is an excuse nobody looks at. Keyed per RUN and not per FILE: `spend_5c1_vis.json`
has three runs that match exactly and two that do not, and excusing the file would have blinded the
check to the one ledger that has already gone quiet twice. A tolerance on the match would have
swallowed exactly the three sessions this repair had to find.

**Negative control.** `test_the_silence_check_fires_when_a_phase_entry_goes_missing` drops skub2's
entry and asserts the check names that ledger, that timestamp and that balance — not merely that it
found something.

**Why the balances match at all, and what that means for the next session.** When
`runpod_guard.main` runs with `--step … --note`, it reads the balance ONCE and writes that one value
into both the step ledger's `gpu_sessions` and the phase ledger's `sessions` — matched by
construction. The step entries that do not match were written by a driver's own appending call
(`positions_gm4_skub.log_run`, `caption_gm4_5c1`'s `gpu_sessions.append`), which reads the balance at
its own moment; the phase entry for those sessions came later, from a separate guard invocation
after teardown, and reads lower. That is the whole of the excuse list.

The consequence is worth naming because it is the guard working, not failing: **the three repaired
rows match today only because the repair copied their balances out of the step ledgers.** A future
paid session whose step ledger is driver-written and whose phase entry is a separate later reading
will redden `test_no_paid_step_ledger_is_silent_in_the_phase_ledger` until someone appends the phase
entry — and `scripts/repair_phase4_ledger.py :: MISSING` is a literal three-tuple that cannot take a
fourth session without an edit. Both halves are deliberate: the check is meant to be looked at, and
the repair is meant to be a record of what it repaired rather than a standing job.

### The live guard run

One read-only run, bare `runpodctl` reads, nothing created:

```
$ python3.11 scripts/runpod_guard.py --note "5c2-prep-a: cap 25 → 30 per SPEC 3.18 (3); phase ledger repaired"
anchor            $35.00 at 2026-08-01T08:34:09+00:00
balance now       $11.17
  balance delta   $23.8310
  billing since   $23.8212 (read)
PHASE 4 SPENT     $23.8310 of $30.00
REMAINING         $6.1690
logged: 5c2-prep-a: cap 25 → 30 per SPEC 3.18 (3); phase ledger repaired
EXIT=0
```

It did not refuse. The entry it wrote with its own hand:

```json
{
  "at": "2026-08-13T07:59:22+00:00",
  "balance": 11.1690436569,
  "spent_usd": 23.831,
  "remaining_usd": 6.169,
  "note": "5c2-prep-a: cap 25 → 30 per SPEC 3.18 (3); phase ledger repaired"
}
```

The balance sits **below** skub2's 11.3347237899, as the contract expected: 0.1657 over 15.23 h =
**$0.01088/h** of volume drip on `qw4nwleanc`, against the ~$0.012/h projected. The billing reading
corroborates at $23.8212; the balance delta is the binding pessimistic reading at $23.8310.

**Commits:** `a00240c` (the script and its tests) and `dff9fc2` (the repaired ledger, the guard's own
entry, and the permanent guard).

---

## Verify gate

### 1. The checkout table

Every commit checked out for real into a worktree, running **its own** suite; `HEAD` printed from
`git rev-parse`, never from the loop variable. **`aecdd22` is the parent and the control** — the old
values must read there, or the table is measuring the working tree.

| commit | SPEC 3.18 | strip knows the family | `PHASE_CAP_USD` | repair script | permanent guard | phase entries | suite |
|---|---|---|---|---|---|---|---|
| `aecdd22` **control** | absent | no | 25.00 | no | no | 31 | 1 failed, 2012 passed ✅ |
| `5ac33b6` | absent | no | 25.00 | no | no | 31 | 1 failed, 2012 passed ✅ |
| `b31d2eb` | absent | no | 25.00 | no | no | 31 | 1 failed, 2012 passed ✅ |
| `81855de` | **present** | **yes** | 25.00 | no | no | 31 | 1 failed, **2013** passed ✅ |
| `3cfd792` | present | yes | **30.00** | no | no | 31 | 1 failed, 2013 passed ✅ |
| `a00240c` | present | yes | 30.00 | **yes** | no | 31 | 1 failed, **2021** passed ✅ |
| `dff9fc2` | present | yes | 30.00 | yes | **yes** | **35** | 1 failed, **2024** passed ✅ |

Seven rows: the control and the six commits of this contract. The report commit and the vault tail
postdate the table and are not in it. The passing count moves exactly where the commits put it —
+1 at `81855de` (the strip's negative control), +8 at `a00240c` (the repair's own tests), +3 at
`dff9fc2` (the permanent guard, its negative control and the committed-ledger idempotency check).
**No row is red beyond the one failure the control also carries.**

**Dv193/Dv206 again — the one failure on every row is the checker's, not the tree's.** `data/` is
gitignored apart from curated files, so the worktree's copy is replaced by a symlink to the repo's,
and the pinned-path guard then resolves a path outside the worktree root. Measured on the **control**
commit, where nothing of this contract exists:

```
$ cd "$WT" && python3 -m pytest -q -p no:cacheprovider --tb=no   # worktree at aecdd22
FAILED tests/test_collect_5c1.py::test_the_guard_reads_the_pinned_paths_off_the_pin_file
1 failed, 2012 passed, 2 skipped in 60.79s
```

That it fires on the control is what says it is the checker's artifact. In the repo itself
`make check` is green:

```
$ make check
2025 passed, 2 skipped in 58.59s
```

`ruff format --check .` — `250 files already formatted` (the formatter is not in `make check`).

### 2. The pin re-derivation

Both records, both directions — the block under Deliverable 1 above.

### 3. The guard's printed table

Under Deliverable 3 above: anchor $35.00, balance $11.17, delta $23.8310, billing $23.8212, spent
$23.8310 of $30.00, remaining $6.1690.

### 4. The session's history

```
$ git log --reverse --format='%h %ad %s' --date=format:'%H:%M' aecdd22..HEAD
5ac33b6 09:47 docs: 5c2 opened -- STATUS pointer of 12.08, PROMPT-5c2-prep-a
b31d2eb 09:47 docs(vault): the 12.08 tail
81855de 09:51 feat(5c2-prep-a): the strip learns the amendment family -- both sealed pins re-derive
3cfd792 09:55 feat(5c2-prep-a): the Phase 4 cap moves 25 -> 30 in every home it has
a00240c 09:59 feat(5c2-prep-a): the phase-ledger repair -- numbers read from the step ledgers, refusals instead of guesses
dff9fc2 10:02 data(5c2-prep-a): the phase ledger tells the truth again -- three repaired entries, today's reading, and a guard against the next silence

$ git rev-list --count aecdd22..HEAD
6
```

**Six commits, 09:47–10:02 local**, and this report and the vault tail after this line make eight.
`git status --short` is clean apart from the pre-authorised session output.

---

## Deviations

**Dv242 — the contract names three cap-coupled literals; the file carries six.** Moving the constant
first reddened three of the six, and only ONE of those was a literal the contract names
(`test_the_first_run_anchors_and_says_so`). Two sites the contract does not name reddened:
`test_the_cap_refuses_the_next_start`, which **flips** (balance 9.99 = $25.01 spent, which is under
the raised cap and allowed, so the test would have asserted a refusal that no longer happens), and
`test_the_volume_keeps_billing_while_the_pod_is_stopped` (`remaining_usd == 24.6`). Three were
silent and were found by reading: the two `"phase4_cap_usd": 25.0` ledger fixtures the contract
names, and `test_a_session_note_is_only_logged_when_the_start_is_allowed`, whose balance 5.00 lands
exactly on the new $30.00. **The suite enumerates what reddens, not what is coupled** — the count in
the contract, the count in the file and the count pytest names are three different numbers.
§Deliverable 2.

**Dv243 — `results/spend_phase4.json :: note` was amended, and the contract's list of homes does not
name it.** Its sentence «the $25 cap of SPEC amendment 3.4 (4) is enforced against that difference»
is exactly the documentation-contradicting-the-enforced-constant the contract forbids. The original
sentence is left **byte-intact** as what was written when the phase opened, and an appended one
supersedes its number and names the authority — the repo's own «superseded, not overwritten»
pattern (v4's $0.45 still stands in `resume.readings.d`). The anchor, `anchored_at` and every logged
session are untouched, and no test anywhere reads this field.

**Dv244 — the exclusion list's reason is not the one the contract's escape hatch anticipates.** The
contract says «If a historical ledger legitimately has no phase entry, name it in a literal
exclusion list with the reason». All three excused runs **do** have phase entries; what differs is
the balance, because the step ledger read during the session and the phase entry read minutes later
after teardown. Writing «no phase entry» would have been false. Each row therefore names its
witnessing entry and the test asserts that entry exists, is later and reads lower — a checkable
excuse rather than prose. Keyed per RUN rather than per FILE, because `spend_5c1_vis.json` has three
matching runs and two excused ones. §Deliverable 3.

**Dv245 — the permanent guard rides with the repaired ledger, not with the script.** The contract
says «Two commits at most: the script + its tests, then the repaired ledger with the guard's own
entry». In the script's commit the three step ledgers are still silent, so a repo-state guard placed
there would be red at that commit. It is in `dff9fc2` with the artifact it reads — Dv240's rule,
which this contract itself cites for Deliverable 1. Still two commits.

**Dv246 — the repair's `ledger` fixture rebuilds the PRE-repair state instead of copying the live
file.** A one-shot repair that has been shot can only ever reach its re-run refusal, and every
assertion about what it *appends* would stop running. The fixture drops every session from the first
repaired timestamp onwards and asserts the last remaining entry is sku-b-run's
`2026-08-11T18:16:30+00:00`, so the tests keep reading the real anchor and the real step ledgers
rather than a hand-written stub. Idempotency on the committed artifact is asserted separately.

**Dv247 — two flags on `scripts/repair_phase4_ledger.py` the contract does not name.** `--ledger`,
without which the tests would have to write the committed artifact to exercise anything; and
`--dry-run`, used to print and check the three entries against the step ledgers before the one real
write.

**Dv248 — commit subjects use ASCII `--` where the contract writes `—`.** No commit subject in this
repository's history carries an em dash; the bodies carry the contract's full text, including the
`cap 25 → 30` of the guard's session note, which is quoted verbatim.

---

## Assumptions stated

1. **«The cap in force when that money was spent» is $25.00 for all three repaired entries.** SPEC
   3.18 (3) is dated 2026-08-13 and the three sessions ran on 2026-08-11 and 2026-08-12, so no part
   of that money was billed under $30.00.
2. **«Every number read from the step ledger» is read as a rule about numbers.** The label prose in
   each repaired entry's `note` is typed (`sku-b-v3-run: REFUSED by the (10)(a) go/no-go …`); every
   figure — `at`, `balance`, `spent_usd`, `remaining_usd` — comes from `runs[-1]` and the anchor.
   Nothing downstream reads the prose.
3. **A «paid run» in a step ledger is an entry carrying a `balance`.** That is the field the RunPod
   readings have and the OpenRouter rows (`model`/`usd`/`requests`) do not, so the permanent guard
   discriminates on it rather than on the ledger's filename or its key name.

## What this contract did not touch

`results/sku_pilot_prereg_v4.json`, `results/sku_pilot_prereg_b2.json` and every sealed sku artifact
are byte-identical to their committed state — nothing was re-pinned. `scripts/write_sku_prereg_b2.py`
and `tests/test_sku_prereg_b2.py` were not edited: the b2 record greened from the single change to
`RATIFICATION_NAME`. The anchor of `results/spend_phase4.json` and its 31 pre-existing entries are
unchanged. No pod, endpoint, template, serverless job or OpenRouter call — **$0**. The loop core,
the census and the 5c2 pre-registration are prep-b and prep-c and were not entered.

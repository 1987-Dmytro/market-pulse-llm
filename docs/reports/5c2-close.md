# 5c2-close — the sitting's returns, amendment 3.19's consumers, the phase retro

The operator sitting SPEC 3.18 (6) makes phase 5c2 conditional on was held on 2026-08-14 and
ratified both halves — 6 leaflet posts with the 36 position rows under them, and 5 comments of 5 —
with nothing disputed and no REVIEW-class order issued. Its one ruling became SPEC amendment 3.19,
whose arrival reddened six tests that were designed to redden, and greening them cost one split
constant, four reformulated assertions and a seventh red test the contract's table did not predict.
The phase closes with `results/validate_5c2_returns.json` on disk, `witness_phase_ledger` wired into
the driver so no future paid exit can leave the phase ledger silent, and a retro over the program's
45 tagged deviations whose largest cluster now has a rule and a home.

**$0 session.** No paid call was made and nothing under `data/derived/`, no sealed record and no
cap-30 record was touched.

---

## 0. The tail, and the block whose bytes could not move

Committed by path, two commits, no `git add -A`:

* `2bfd172` `docs:` — `docs/SPEC.md` (amendment 3.19), `docs/STATUS.md`, `docs/PROMPT-5c2-close.md`
* `c7d1d57` `docs(vault):` — `knowledge/daily_logs/2026-08-14.md`, `knowledge/index.md`,
  `knowledge/hot.md`

Both landed on a RED tree by design: they are docs-only and the six failures below are what step 0.5
exists to fix.

**The amendment-index block is byte-identical to `50c5727`** — verified before committing, because
it is one of the TEN blocks the sealed 5c2 registration's pin KEEPS, and a single newline inside it
would break a pin that is never re-taken. That is why 3.19 carries its own index note instead of
being added to the list above it.

```
$ git show 50c5727:docs/SPEC.md  → extract <!-- amendment-index --> → sha256
amendment-index  identical: True  sha 568649d6cfe0a7fa  1169 bytes  (both sides)
amendment-3.18   identical: True  sha 277795ff03ebc6a5  10080 bytes (both sides)
```

## 0.5 — amendment 3.19's consumers: six predicted, one not

`e8205b6`. The root is one block; the seven consumers are one defect wearing different clothes — an
assertion whose truth had a shelf life of one amendment.

**The constant that did NOT grow.** `write_prereg_5c2.KEEP_BLOCKS` answered two questions with one
tuple: *what does the strip keep before hashing* and *what does the file carry today*. Only the
second one moves. Growing the keep to eleven would have made `pinned_sha256` strip 3.19 out of the
registered law — and the sealed record's own `check_the_inputs_have_not_moved` would then have
refused with «is not re-pinned to make it green», the producer's strongest refusal, turned on
itself. So the tuple is split: `BLOCKS_TODAY = (*KEEP_BLOCKS, "amendment-3.19")` is what the refusal
compares against, and `KEEP_BLOCKS` stays at TEN.

| # | consumer | what changed | the other direction, planted |
|---|---|---|---|
| 1 | `write_prereg_5c2.check_the_strip_family_is_what_it_says` | compares `found` to `BLOCKS_TODAY` (eleven); `pinned_sha256` still strips with `KEEP_BLOCKS` (ten) | `test_a_twelfth_marked_block_is_refused_rather_than_stripped` plants an `amendment-3.20` and the refusal fires; the live file must still PASS on the next line |
| 2 | `test_the_registered_law_is_the_spec_with_every_block_it_carries_today` | renamed `test_the_sealed_pin_still_derives_through_the_ten_block_keep`; the raw-identity line is gone and the pair `test_sku_prereg` uses is in its place — `live != pin` **and** `sha256(registered_law(spec, keep=KEEP_BLOCKS)) == pin` | either leg alone passes for the wrong reason: a live hash equal to the pin would mean 3.19 never landed |
| 3 | `test_an_eleventh_marked_block_is_refused_rather_than_stripped` | the intruder is a TWELFTH now — `amendment-3.20` — because the eleventh became real | see #1 |
| 4 | `tests/test_sku_prereg.py:248` | the literal enumeration learns `amendment-3.19`, with the comment saying why v1–v4 strip it | the same test re-derives all four sku pins through `registered_law(SPEC)` with an empty keep, and asserts every stripped block's name is absent from the law |
| 5 | `run_5c2.preflight` / `test_every_pinned_input_is_byte_identical_today` | new `pinned_today` routes `docs/SPEC.md` through the strip **the RECORD names** (`prereg["strip"]["keep"]`), and labels it apart from the eight files that really are byte-identical; test renamed `test_every_pinned_input_still_reads_as_the_seal_pinned_it` | `test_a_spec_that_stopped_deriving_is_the_same_stop_as_a_moved_file` sets the SPEC pin to `0…0` and the run still STOPS — the strip is not a way past the guard |
| 6 | `test_a_refused_handshake_…` + `test_the_registration_refuses_while_the_suite_is_red` | **nothing.** Both were downstream of #1 and #5 and went green with no edit of their own — measured, not assumed (`tests/test_run_5c2.py` 23 passed at that point) | the first one IS edited later, by deliverable 2, and that is stated there |
| **7** | `test_the_record_carries_no_clock_and_names_its_producer` — **not in the contract's table** | fixing #1 moved `scripts/write_prereg_5c2.py`, and the sealed registration pins `producer.sha256` over exactly those bytes. The record is NOT touched: the test recovers the sealed bytes with `git show 0e390ff:scripts/write_prereg_5c2.py` and asserts the live file has MOVED | `b"amendment-3.19" not in sealed` — a recovery that already carried the name would mean the test is checking the wrong commit |

**A new both-directions test for the strip itself**,
`test_the_strip_is_blind_to_3_19_and_to_nothing_the_keep_holds`: on a copy in `tmp_path`, editing
3.19's own words leaves the pin deriving, and editing either of two KEPT blocks (`**Amendment 3.18`,
`amendment 3.15 (the vis program moves`) breaks it. Without that leg, #2's reformulation would have
been satisfied by a strip that hid the whole file.

## Deliverable 1 — the sitting's returns

`4e839b9`. `scripts/write_validate_returns.py` → `results/validate_5c2_returns.json`.

| | on the table | verdict |
|---|---|---|
| leaflet half | 6 posts · 36 position rows | **ratified** |
| comment half | 5 of 5 | **ratified** |
| | disputed **0** · orders issued **0** · slots resolved **47 of 47** | |

The operator's words on the leaflet half are kept as DATA, in Russian and untranslated —
**«распознавание SKU идеальное»** — and grepped back at their source (`docs/PROMPT-5c2-close.md`,
whitespace normalised because the line wraps there) before the producer will write them. The one
RULING the sitting produced is amendment 3.19, referenced and never restated: the test asserts two
of its clauses appear in `docs/SPEC.md` and appear in the record **nowhere**.

**The refusal that does the real work is not the sha.** The pack sha (`2fad5339…`) catches a redraw
wearing the same filename, and it is necessary. But the guard that can fire on a self-consistent
pack is the JOIN: the `findings` slots are compared against the rows the pack PRINTED, so a slot
with no row (a verdict on something nobody saw) and a row with no slot (a row he had no way to rule
on) are both stops. And the group SIZES are the sitting's own — the operator ratified a HALF, not a
list of ids, so a 37th position row is refused rather than covered.

Six refusals, each exercised: a moved pack, a slot the pack never printed, a group larger than the
sitting ruled on, a skeleton already filled in, a verdict form the pack does not carry, and a
dispute on a row that does not exist. The dispute map is empty and is tested in **both** directions
— a planted dispute lands on its row and leaves the other 46 ratified — so its emptiness is a fact
about the sitting rather than about a producer that can only ratify.

**The determinism pair** (two writes to scratch paths, and the shipped file):

```
52564bf3440f20e0521afd4b5a81a78c64ca7556d01864fc1a1679db39e384cd  r1.json
52564bf3440f20e0521afd4b5a81a78c64ca7556d01864fc1a1679db39e384cd  r2.json
52564bf3440f20e0521afd4b5a81a78c64ca7556d01864fc1a1679db39e384cd  results/validate_5c2_returns.json
```

House hygiene: `producer.sha256` + an explicitly empty `borrows` with its reason, no clock, no git
block.

**`sitting.operator_minutes` is `null`.** See Dv326 — the contract asked for it «as relayed» and
nothing relayed one.

## Deliverable 2 — `witness_phase_ledger` wired into `finalise`

`1fc50b8`. The team lead's ruling after 5c2-run, and this was the next code-touching contract.

`finalise` runs on both arms of `main`'s try, so a completed leg and a dead one now leave the same
THREE artifacts. The call sits after `log_run`, because it reads the row `log_run` has just
appended — before it, the entry would witness the previous leg.

**The hazard the wiring creates, which the ruling did not name.** `finalise` is called from the
exception arm and the ORIGINAL exception is re-raised after it. A `SystemExit` escaping the witness
would have become the exception the operator sees, the re-raise would never happen, and a session
killed by a wrong serving configuration would have been reported as a bookkeeping failure. So
`witness_the_phase` never raises: it records its refusal in the run record's notes. That is not
hypothetical hygiene — `witness_phase_ledger` REFUSES on a timestamp the phase ledger already
carries, and that refusal is what makes it idempotent.

Four tests, and the negative control was run rather than asserted — the call was deleted from
`finalise` and the suite re-run:

```
$ (witness call removed)  python3 -m pytest tests/test_run_5c2.py -q
FAILED test_finalise_witnesses_the_phase_ledger_from_the_runs_own_numbers
FAILED test_a_witness_that_refuses_costs_the_run_record_nothing
FAILED test_a_refused_handshake_writes_the_ledger_row_and_the_record
FAILED test_a_witness_failure_never_replaces_the_exception_that_killed_the_run
4 failed, 22 passed
$ (restored)                                                    26 passed
```

* a completed exit appends one anchor-relative entry carrying the step ledger's OWN balance reading
  — asserted against each other, not against literals, because that identity is what the permanent
  silence guard matches on and a re-read minutes later is a different number;
* a refused witness writes nothing (`phase.read_bytes()` unchanged) and costs the record nothing;
* the exception arm witnesses too, and its note is now the second entry of `written["notes"]` — the
  equality that deliverable 0.5 left green and this deliverable changed on purpose;
* with the phase ledger absent entirely, the exception raised is still the handshake's.

**No test reads or writes `results/spend_phase4.json`.** Every one of them patches
`driver.PHASE_LEDGER` at a `tmp_path` fixture, and the helper's docstring says why: a suite that
appended to the live ledger would write sessions that never happened into the record every later
contract prices against. `git status` after the run confirms it untouched.

---

## Retro — the whole 5c2 program

### What the tags cover, and what they do not

The contract asks for Dv249–Dv324. **Only Dv280–Dv324 carry `[cause:]` tags** — 45 of them, every
number in that range. The convention began at 5c2-prep-c3a, «the first contract on the audit
template», so the 31 numbers Dv249–Dv279 predate it and are not silently counted as untagged
findings (Dv328).

Re-derivable, from the reports and `implementation-notes.md`:

```python
import re, pathlib, collections
SRC = [f"docs/reports/{n}.md" for n in ("5c2-prep-a","5c2-prep-b","5c2-prep-c1","5c2-prep-c2",
       "5c2-prep-c3a","5c2-prep-c3b","5c2-run","5c2-validate-prep")] + ["implementation-notes.md"]
tag = {}
for src in SRC:
    flat = " ".join(pathlib.Path(src).read_text(encoding="utf-8").split())
    for chunk in re.split(r"(?=\*\*Dv\d+)", flat):
        if (m := re.match(r"\*\*Dv(\d+)", chunk)) and (t := re.findall(r"\[cause:\s*([a-z-]+)\]", chunk)):
            tag.setdefault(int(m.group(1)), t[0])
inr = {d: t for d, t in tag.items() if 249 <= d <= 324}
print(len(inr), dict(collections.Counter(inr.values()).most_common()))
# 45 {'contract-gap': 11, 'model': 10, 'process': 9, 'tooling': 8, 'spec-gap': 6, 'env': 1}
```

| tag | n | the deviations |
|---|---|---|
| `contract-gap` | **11** | Dv280 281 282 295 303 304 307 312 316 317 318 |
| `model` | **10** | Dv284 287 289 308 309 310 320 322 323 324 |
| `process` | **9** | Dv283 292 293 298 299 302 311 314 319 |
| `tooling` | **8** | Dv288 291 294 301 306 313 315 321 |
| `spec-gap` | **6** | Dv285 286 290 296 297 300 |
| `env` | **1** | Dv305 |

Cross-checked against `docs/STATUS.md`'s own two-session tally, which the team lead kept
independently: run c-gap 4 · model 3 · tooling 3 · process 2 · env 1 (Dv303–315) and validate c-gap
3 · model 4 · process 1 · tooling 1 (Dv316–324). Both reproduce exactly.

### `[model]` — 10, the largest cluster: routed

Three shapes, one rule:

* **price vs sample** — Dv308: the leaflet page rate came from skub2's sparse PREFIX of the corpus
  and was **2.43×** under the truth on the 159-page population; the comment rate, measured on a
  population, landed within **−0.4%**. Same session, same record;
* **the warm-up as a sample of one** — Dv310: the go/no-go warmed up on a page that happened to be
  EMPTY and under-priced the leg **2.4×** across two independent boots (Dv180's 3.54× is the
  precedent it inherits);
* **the correlated draw** — Dv323: five comments from five strata under one `Random(42)` put three
  of them on **rank 163** of their pools. Reproducible and not representative.

> **Beside every price, name what it was measured ON. Beside every draw, measure a rank.**

**Home: `.claude/rules/registrations-and-draws.md`**, path-scoped to the registration, projection
and pack producers — 0 tokens at startup, loaded exactly when one of those files is touched.
CLAUDE.md was declined (200-line cap, and `scripts/context-census.py` reads 13.4K against a 9.0K
target — a rule binding on two kinds of file would be paid for in every session that edits neither);
a producer docstring was declined (it reaches whoever opens that one file, and the next cycle writes
a new producer). Routed in this session — Dv327 records the deviation from the contract's two
options.

### `[contract-gap]` — 11: the two lines the next cycle's contracts inherit

1. **A fake must model the transport's LIMITS, not only its answers.** Dv309: 126 base64 pages in
   one body, RunPod's 10 MiB ceiling, an HTTP 400 before any worker saw it, and the boot already
   paid for. Every stub in the suite modelled what the worker would REPLY.
2. **A verify-gate number is re-measured when its artifact moves.** Dv281 / Dv293 / the c3a session
   header — three instances in one day, each a true sentence about a moment left standing after the
   moment moved. The re-measurement belongs to the gate, not to a later reader's correction.

Both are recorded in the ADR, which is where a contract author can lift them; `docs/PROMPT-*.md` is
the team lead's file and is not edited here.

### `[tooling]` — 8: fixed in code, or honestly not

| Dv | what | commit |
|---|---|---|
| Dv306 | two id-hash conventions, one nearly-shared helper (comma vs newline) — the comment leg calls `census.leg` itself rather than restate it | `9bf2c93` |
| Dv301 | the registration's `verifier` block cannot carry pytest's last line (it holds the run's DURATION and the record's gate is byte-identity) | `0e390ff` |
| Dv288 | `ruff format` invalidated a shipped record's `producer.sha256`; the record was regenerated and the determinism pair re-measured after the formatter | `9c723a7` |
| Dv321 | the mirrored-root positive control could not use the committed aggregates; rebuilt over the mirror, name-mismatch refusal exercised separately | `8b6cbf4` |
| Dv291 | the worktree checkout linker landed `data/data` inside a partly-tracked `data/`, silently — every row read `1 error in 0.9s` | **no commit**: a shell procedure in the report, not committed code |
| Dv313 | `make check \| tail -3 && git commit` takes `tail`'s exit code; two commits landed on a red tree. `set -o pipefail` since | **no commit**: a shell idiom, and it is the habit this session used throughout |
| Dv315 | the same instrument again — the suite also reads gitignored content under `results/`, and without it every row read a uniform `46 failed`, the CONTROL included | **no commit**, same reason |
| Dv294 | the c3a census anchor guard has a hole on a fresh `--out`: it reads the OUT file's own anchor, so a new path skips it entirely | **still open, deliberately** — `git log -S refuse_to_move_the_anchor -- scripts/census_c3a_posts.py` shows one commit, `a39a8ad`, its own. The guard is c3a's shipped code and its record is sealed |

Three of the eight are shell procedure rather than code, which is itself the finding: the tools that
audit this repo are less versioned than the repo.

### `[process]` — 9: the shelf-life redesign is now a named house pattern

The cluster's dominant shape is a green assertion whose truth was fixed to a MOMENT, going red
because the world moved legitimately. Named once in the ADR so the next flip cites it instead of
rediscovering it, with four instances in four subsystems:

| form | was | became |
|---|---|---|
| freeze the constant | `PHASE_CAP_USD` live, 25 → 30 → 33 | `repair_phase4_ledger.CAP_IN_FORCE_USD = 25.00` |
| snapshot instead of absence | «`data/derived/` does not exist» | a before/after snapshot of every file and its sha |
| strip instead of identity | «the pin equals sha256 of `docs/SPEC.md`» | «the pin equals the STRIP of today's file», with `live != pin` beside it |
| recover instead of re-pin | «`producer.sha256` equals the live producer» | «those bytes are still fetchable at `git show 0e390ff:`, and the live file has moved» |

The last two are this session's; the rule is that a redesign keeps a negative control, so it is not
a relaxation. All four do.

### `[spec-gap]` — 6, and `[env]` — 1

`spec-gap` is not a defect class: all six (Dv285 286 290 296 297 300) are places where the SPEC was
silent and a ruling was needed, and every one of them was answered by an amendment or a team-lead
ruling within the day. `env` is Dv305 alone. Neither is routed.

---

## Deviations

**Dv325 — the contract's consumer table missed a seventh consumer, and grep could not have found
it.** Teaching `write_prereg_5c2.py` the name `amendment-3.19` moved the file's bytes, and
`results/prereg_5c2_run.json :: producer.sha256` pins exactly those bytes —
`test_the_record_carries_no_clock_and_names_its_producer` went red as a consequence of the fix
rather than of the amendment. The sealed record is NOT re-pinned (that is the producer's own
strongest refusal). The test recovers the sealed bytes from `git show 0e390ff:` — the commit that
landed the record and the producer together, and the producer's only commit until today — and
asserts both directions: the live file has moved, and the recovered file does not carry the
amendment's name. Same class as Dv281: a consumer table built by grep misses what grep cannot see.
[cause: contract-gap]

**Dv326 — the sitting's actual duration is not on disk, so the field is null.** The contract asks
for «operator time actual as relayed». Nothing was relayed and nothing in `docs/STATUS.md`,
`knowledge/daily_logs/2026-08-14.md` or `knowledge/hot.md` carries one; the only number anywhere is
STATUS's «СИДЕНИЕ (~45 мин)», written BEFORE the sitting as part of the plan and still standing in
the not-yet-updated «ТЫ ЗДЕСЬ» line. A plan is not a measurement, so
`sitting.operator_minutes` is `null` and `operator_minutes_note` says exactly this. Recording ~45
would have put this executor's invention in the record wearing the operator's name.
[cause: contract-gap]

**Dv327 — the `[model]` rule was routed to a home the contract did not offer.** The contract names
two candidates, «CLAUDE.md vs the prereg producer's docstring», and both were declined: CLAUDE.md is
capped at 200 lines and the boot census reads **13.4K against a 9.0K target**, so a rule that binds
only when a registration or a pack is written would be paid for in every session that writes
neither; a producer docstring reaches whoever opens that one file, and the next cycle's registration
is a new file. `.claude/rules/registrations-and-draws.md` is path-scoped — 0 tokens at startup,
loaded exactly when one of those producers is touched — and CLAUDE.md itself prescribes that
mechanism. Stated rather than done quietly, because choosing outside the offered set is the team
lead's to overrule. [cause: contract-gap]

**Dv328 — the retro's requested range is wider than the tag convention.** Dv249–Dv324 is 76
numbers; 45 carry `[cause:]` tags and all 45 are Dv280–Dv324. The convention began at 5c2-prep-c3a,
which its own report calls «the first contract on the audit template» — `docs/reports/5c2-prep-b.md`,
`-c1` and `-c2` contain zero `[cause:` strings. Reported as coverage instead of as a tally over a
range that does not exist, and the 31 earlier numbers are NOT counted as untagged findings — they
are deviations recorded before there was a tag to carry. [cause: process]

**Dv329 — wiring the witness created a hazard the ruling's wording could not name.** «Invoke the
witness from BOTH arms» describes a call site; it does not say what a call site does to an
exception already in flight. `finalise` runs inside `main`'s `except BaseException` and the original
exception is re-raised AFTER it, so a `SystemExit` from the witness — the way
`witness_phase_ledger` reports every one of its refusals, including the idempotent one — would have
replaced the reason the run died and skipped the re-raise entirely. Caught in design and closed by
`witness_the_phase` never raising; the failure is planted as a test with the phase ledger absent
altogether, asserting the operator still sees the handshake's refusal. [cause: contract-gap]

## Verify gate

```
$ make check
2332 passed, 2 skipped in 64.40s

$ ruff format --check .
272 files already formatted

$ python3 scripts/check-wikilinks.py
check-wikilinks: OK, none broken

$ git status --short          # after the report commit: clean
```

`make check` was green after `e8205b6`, `4e839b9` and `1fc50b8` — the three commits that touch code
— and the two step-0 commits are docs-only and red by design, which the contract states.

Session commits: `2bfd172` · `c7d1d57` · `e8205b6` · `4e839b9` · `1fc50b8` · `162ba0c` · this
report. The ADR is [[5c2-closed-the-sitting-and-the-shelf-life-redesign]].

## Process signals

* The contract's own consumer table was one row short, and the missing row was a HASH of the file
  the table told me to edit (Dv325). A table of consumers found by grep cannot see a consumer that
  is a digest — the same finding as Dv281, now twice.
* Asking «what would this assertion have to say to still be true» produced four different answers in
  four subsystems, and none of them was «delete it». That is worth a name, and it now has one.
* The `[cause:]` convention is 45 deviations old and already pays: the retro's tally was derivable
  by script and agreed with the team lead's independently-kept one to the number.
* Three of eight `[tooling]` deviations are shell procedure with no commit behind them. The
  instruments that audit this repo are less versioned than the repo.
* Two of this session's five deviations are the contract asking for something that does not exist
  (a relayed duration, a tag range) — cheap to answer honestly, expensive to answer plausibly.

# PROMPT-5c2-prep-a — the law can grow again, the phase cap moves 25 → 30, the phase ledger is repaired

**Contract:** `docs/SPEC.md` amendment **3.18 (3)** and this file. Read 3.18 only —
not the whole spec, and not 3.17 (its clauses are quoted below where they bind).
This file is the whole brief. **$0 session:** no pods, no endpoints, no OpenRouter,
no paid call of any kind. All artifacts in English. Team-lead files
(`docs/STATUS.md`, `docs/SPEC.md`, `docs/PRODUCT.md`, `docs/PROMPT-*.md`) are
read-and-commit, **never edit** — phase-end facts go to the daily log or
`implementation-notes.md`.

**Context in four lines:** the sku programme closed 2026-08-12 — B′ measured, two
bars PASS and one FAIL, the instrument closed by measurement. At the 5c2 briefing
(2026-08-13) the operator ruled three things, and the team lead wrote them into
`docs/SPEC.md` as **amendment 3.18**, which is already in your working tree,
unstaged. That amendment is the reason this contract exists: **it reddens three
tests as it stands**, and greening them is deliverable 1.

## Step 0 — the tail, and the one path that must NOT be committed alone

`git status --short` should show exactly: `docs/SPEC.md`, `docs/STATUS.md`,
`knowledge/daily_logs/2026-08-12.md`, `knowledge/hot.md`, `knowledge/index.md`
(modified) and `docs/PROMPT-5c2-prep-a.md` (this file, untracked).

Stage **by path** (never `git add -A` — the trap has fired with every queued
prompt since `docs/PROMPT-4.5g4.md`), two commits:

1. `docs: 5c2 opened — STATUS pointer of 12.08, PROMPT-5c2-prep-a` —
   `docs/STATUS.md` and `docs/PROMPT-5c2-prep-a.md`.
2. `docs(vault): the 12.08 tail` — the three `knowledge/` paths.

**`docs/SPEC.md` is NOT in either commit.** It carries amendment 3.18, whose text
moves the file's hash, and three tests pin that hash; committing it on its own
puts a red commit in the history. It rides with deliverable 1, in the same commit
as the code that greens it. Your own session output (hot.md refresh, today's daily
log, `/save` checkpoints) is pre-authorised into its own commit at session end —
do not stop for it. STOP only for a path none of these lists explains.

## Deliverable 1 — a law that can grow without breaking a sealed pin

**The failure, stated so you can reproduce it before you fix it:**
`results/sku_pilot_prereg_v4.json` and `results/sku_pilot_prereg_b2.json` both pin
`docs/SPEC.md` in `pinned_inputs` — not a quotation, the **whole file** with the
marked ratification blocks stripped off by `write_sku_prereg.registered_law()`.
Amendment 3.18 is new text, so the stripped hash moved and these fail:

```
tests/test_sku_prereg.py::test_every_pinned_input_still_hashes_to_what_it_says
tests/test_sku_prereg.py::test_the_record_rebuilds_identically_apart_from_its_timestamp
tests/test_sku_prereg_b2.py::test_the_shipped_registration_is_the_one_this_script_writes
```

Re-pinning the records is **forbidden** — they are the pilot's witness and
`tests/test_sku_prereg.py` says so in the comment above its `blocks` list. The
legal move is the one the file already uses for 3.17 (7)–(14): the new text wears
its own markers and the strip takes it off.

The team lead has already wrapped both additions in `docs/SPEC.md`:
`<!-- amendment-index begin … end -->` (the repaired amendment index near the top —
the heading's `rev. 3.14` is deliberately NOT corrected, because the pins hash that
line) and `<!-- amendment-3.18 begin … end -->` (the amendment itself).

What you build:

- `scripts/write_sku_prereg.py`: `RATIFICATION_NAME` learns the new family. One
  expression, one implementation — `write_sku_prereg_b2.py` and both test modules
  call `v4.registered_law`, so this is the single point of change:
  `r"^<!-- (sku-b-ratification(?:-\d+)?|amendment-(?:index|3\.\d+)) begin"`.
  Update the docstring beside it: what the family is FOR, and that a block whose
  name the expression does not know reddens the pin instead of passing quietly.
- `tests/test_sku_prereg.py`: extend the literal `blocks` enumeration — the names
  arrive in **document order**, so `amendment-index` is first and `amendment-3.18`
  last. Keep the enumeration's whole point: an amendment cannot arrive unnoticed.
  Mind the `for name in blocks[1:]` loop below it — its comment explains that the
  FIRST name is skipped because it is a prefix of the later ones, and that reason
  now belongs to `sku-b-ratification`, not to whatever sorts first.
- The negative control the fix is worth having: in `tmp_path`, a COPY of the spec
  with one line added OUTSIDE any marked block must fail to re-derive both pins.
  Never write to `docs/SPEC.md` from a test.

**The gate, and the team lead has already run it — reproduce it, do not trust it:**
with the extended expression, both sealed pins re-derive exactly and the live file
differs from both. `registered_law(SPEC)` re-derives v4's pin; `registered_law(SPEC,
keep=write_sku_prereg_b2.KEEP_BLOCKS)` re-derives B′'s. Both directions, per the
existing test's own rule: a live hash equal to the pin would mean the amendment
never landed.

**One commit:** `docs/SPEC.md` + the two code/test files together. `make check`
green ON that commit, not only in the working tree (Dv240: a test that reads a
released artifact lives in the commit that releases it).

## Deliverable 2 — the phase cap moves 25 → 30, in every home it has

SPEC 3.18 (3). The cap has **three** homes and a fourth thing that must not move:

- `scripts/runpod_guard.py :: PHASE_CAP_USD = 25.00` → `30.00`. This constant is
  what the guard ENFORCES (`read_ledger` returns the file untouched when it
  exists, so the file's field is documentation).
- `results/spend_phase4.json :: phase4_cap_usd: 25.0` → `30.0`. Documentation that
  contradicts the enforced constant is a lie waiting to be quoted.
- `tests/test_runpod_guard.py`: three literals — lines 26, 112 and 186 as the file
  stands, including `assert written["phase4_cap_usd"] == guard.PHASE_CAP_USD ==
  25.00`. Move them WITH the constant; a fixture pinned to the old cap is a test
  that passes for the wrong reason.
- **NOT moved:** `runpod_balance_at_phase4_start` (35.0), `anchored_at`, and every
  entry already in `sessions`. An anchor rewritten silently restarts the counter —
  the footgun the ledger's own note names. The refusal on a balance ABOVE the
  anchor stays exactly as it is: a top-up remains an operator decision, and no
  money was added here.

Quote the authority in the commit message: SPEC 3.18 (3), operator ruling
2026-08-13. One commit, `make check` green on it.

## Deliverable 3 — the phase ledger tells the truth again, and cannot drift silently

`results/spend_phase4.json` has not been appended since `2026-08-11T18:16:30Z`
(`sku-b-run`). Three paid sessions ran after it and live only in their own step
ledgers. The phase counter has been arithmetic-from-the-anchor ever since — right,
but unwitnessed by the file the guard reads.

- Write `scripts/repair_phase4_ledger.py`. It appends the three missing entries in
  time order, and every number in them is **read from the step ledger**, never
  typed: `results/spend_sku_b_v3.json`, `results/spend_sku_b_v4.json`,
  `results/spend_skub2.json` (each carries `runs[-1].balance` and its `at`).
  `spent_usd` = anchor − balance, in the guard's own shape and rounding;
  `remaining_usd` against **25.0**, the cap in force when that money was spent —
  each note says so and names its source file. A repaired history that quietly
  re-scores itself under today's cap is a rewritten history.
- Refuse rather than guess: if an appended entry's timestamp is not strictly after
  the last existing one, or a step ledger is missing, or an entry with that
  timestamp is already there, the script exits non-zero and writes nothing.
  Idempotent by construction — run it twice, get one set of entries.
- The permanent guard, because this is what actually went wrong: a test asserting
  that **every** `results/spend_*.json` step ledger with a paid run has a
  corresponding entry in `results/spend_phase4.json` (matched on the balance
  reading), so a paid session cannot leave the phase ledger silent again. If a
  historical ledger legitimately has no phase entry, name it in a literal
  exclusion list with the reason — a list that must be looked at, not a loosened
  match.
- Then ONE live, read-only run of the guard to write today's reading with its own
  hand: `python3.11 scripts/runpod_guard.py --note "5c2-prep-a: cap 25 → 30 per
  SPEC 3.18 (3); phase ledger repaired"`. It creates nothing — bare `runpodctl`
  reads only — and its printed table is the evidence the report carries. Expect
  the balance to sit BELOW `11.3347` by roughly the volume drip (~$0.012/h since
  2026-08-12T16:45Z on `qw4nwleanc`): report the number it actually prints, and if
  the guard REFUSES, stop and report — do not touch the anchor.

Two commits at most: the script + its tests, then the repaired ledger with the
guard's own entry.

## Verify gate — evidence, not assertions

1. `make check` — green after **every** commit, and the checkout table is run per
   commit as usual (mind Dv193: in a worktree `data/` is a symlink and
   `test_collect_5c1.py::test_the_guard_reads_the_pinned_paths_off_the_pin_file`
   is red on every tree including the control-parent; read the table only with the
   control beside it).
2. Paste the actual output of the pin re-derivation for BOTH records — the two
   booleans and the live-vs-pin comparison — not a sentence saying they pass.
3. Paste the guard's printed table (anchor, balance, delta, spent, remaining).
4. `git log --oneline` for the session, and `git status --short` clean at the end
   except your pre-authorised vault tail.

## Do NOT

- Do NOT edit `docs/SPEC.md`, `docs/STATUS.md`, `docs/PRODUCT.md` or
  `docs/PROMPT-*.md`. They are team-lead files (SPEC amendment 3.18 landed there
  by the team lead's hand). Commit them, never rewrite them.
- Do NOT re-pin `results/sku_pilot_prereg_v4.json` or
  `results/sku_pilot_prereg_b2.json`, and do not touch any sealed artifact of the
  sku programme (`results/sku_bar_verdicts*.json`, `results/sku_b_pair_verdicts*`,
  `results/sku_b_positions*`). If a pin will not re-derive, that is a finding for
  the report — never a number to update.
- Do NOT spend anything: no `pod create`, no `serverless`, no template, no
  OpenRouter call. The only RunPod contact allowed is the guard's read-only calls.
- Do NOT regenerate `results/spend_phase4.json` or edit its anchor and existing
  entries.
- Do NOT widen scope into the loop core, the census or the pre-registration —
  those are prep-b and prep-c, deliberately separate contracts.

## Report

`docs/reports/5c2-prep-a.md`, and keep `implementation-notes.md` current with a
**Deviations** section: every departure from this contract logged there and cited
in the report — silence is not compliance. Open the report with three plain
sentences before any table: what is now true that was not true this morning.

**Read-back before you start:** name the three gates of this contract in one line
each, and say which single commit carries `docs/SPEC.md`.

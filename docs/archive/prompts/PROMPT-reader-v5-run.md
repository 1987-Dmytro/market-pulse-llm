# PROMPT — reader-v5-run: one pod, both legs, and the stop-rule that ends the line

**One paid rung on a rented pod. Cap $0.45 all-in against the cycle-2 line ($19.15
remaining), enforced by `runpod_guard --step reader-v5 --step-cap 0.45`. ONE attempt: a
kill, a STOP, or a completed run with a failed bar closes the question. And the
registration's PROGRAMME STOP-RULE binds the whole line: if the run completes and bars
1 and 4 are not BOTH taken, prompt-engineering closes and the next step is an
architecture sitting — never a v6 of the same kind.**

**Instrument:** prompt v5 (`reader_thread_gm4_v5`, `c529d279…`), parser v5 behaviour,
gold r2 — all as registered in `results/prereg_reader_probe_v5.json` (`48b6cbde…`
before step 0's prose fix). Bars 1–4 object-equal to v4's; leg B mechanical m1–m4;
ceiling **4000** (operator ratified 17.08); echo duty over `per_comment ∪ noise`
(operator ratified 17.08). **The registration FREEZES the moment the pod exists.**

**Baseline:** `make check` 2 777 / 2 skipped (team lead's own run, 17.08).

## Step 0 — tail, and one prose fix INSIDE the unfrozen registration

1. Tail by live `git status`, by path (vault files; team-lead files verbatim if dirty).
2. **Fix the stale wording in the v5 registration's non-gating prose:**
   `bars.5_time_and_cost.reported_not_gating.finish_reason` still says «the 2 000-token
   ceiling» — v4's sentence inside a 4 000-ceiling instrument. Fix it in
   `scripts/write_reader_prereg_v5.py`, rebuild byte-identically, re-run
   `tests/test_reader_prereg_v5.py` (a pinned literal that reddens updates loudly),
   commit registration + producer + tests together. This is legal ONLY while no pod
   exists — after freeze the record may not move; that is why it is step 0.

## D1 ($0) — the pack, at its registered path

`PYTHONPATH=src python3.11 scripts/read_threads_reader_v5.py --pack
results/reader_v5_pack.json` — the path is load-bearing (Dv468: `--gate` reads the
pack for per-unit payable counts; a missing pack is a named refusal). 26 units — leg A
23 threads + leg B 3 chunks of `@klopotenkofood:6040` (16/16/11) — every rendering sha
verified against the record on the Mac BEFORE anything is billed, ceiling 4000 carried
in `serving.output_tokens` (a pack without it is refused by the runner).

## D2 — the run

Order inside the session, and the reason is the mission: **leg A first, leg B after.**
Leg A is the semantic answer three contracts have paid for; leg B is mechanics. If the
full-pass gate tightens mid-run, what survives a kill must be leg A.

1. **Anchor:** `python3.11 scripts/runpod_guard.py --step reader-v5 --step-cap 0.45` —
   fresh anchor, never regenerated. Three cloud listings BEFORE create (volume as
   positive control).
2. **Re-stage the volume:** `src/` HAS moved since v4's `aa0ca18` — stage the checkout
   at this contract's HEAD. Staging is proven by the pod-side handshake (narrowed task
   shas + `prompts.py` module sha + all 26 per-request shas), never by the staging
   command's exit code. `git status --short` on the pod checkout stays empty; the v5
   runner is scp'd to `/workspace/`, never into the checkout (v4's Dv452 stands).
3. **Create:** RTX 4090, EU-RO-1 SECURE. Read `runpodctl gpu list` TODAY before
   create; `costPerHr` from the create response is the meter of record and re-prices
   every registered figure ($0.74/h is a worked example — Dv448 law). Record
   `card_registered` vs card. Hard backstop `--terminate-after` 90 min.
4. **Watch with gates APPENDED** (the `gates` list; nothing overwritten): scp the
   partial results file inside the poll loop BEFORE every gate (a KILL read off a
   stale copy kills a healthy run); detached launch per the fixed runbook pattern
   (`nohup … </dev/null >log 2>&1 &`, liveness by `pgrep -af`, never by the launch's
   exit). The affordability deadline binds before the twelve-minute ceiling on this
   registration (Dv462) — at $0.74/h the first reply must land by ~675 s of
   create-elapsed; re-derive at the real price and paste the gate outputs verbatim.
5. **Generation:** the runner answers all 26 units in order, transport stop at the
   first balanced object, persisted bytes = the balanced prefix (a never-balancing
   reply persisted WHOLE and flagged), per-unit seconds / `finish_reason` / usage /
   `cut_chars` flushed as each lands. Full-pass gate re-checked after every unit,
   both projection legs, pessimistic binds, verdict re-derived from seconds.
6. **Delete, never stop.** Three listings after, read against the three from before,
   volume as the positive control. Guard read → expect a LOWER BOUND; close only when
   the walk answers (never over an unanswered walk); otherwise closing is the named
   debt with the command written down.

## D3 — scoring and the verdict record

`PYTHONPATH=src python3.11 scripts/score_reader_v5.py` on the Mac, from persisted rows
only: bars 1–4 over LEG A (collapsed as the bar, uncollapsed beside), m1–m4 over leg B,
bar 5 against the step ledger (three states). Beside the bars: the three-state echo
census per thread (what happened to `@matusi_ukr:22242` and `@VARUS_channel:10366` by
name), refusal census by shape vs v4's paired columns, repairs fired (expect 0),
`finish_reason` per unit at the 4 000 ceiling, tokens per answered row, and the stop's
telemetry — how many replies the criterion actually shortened ON THE POD and the
seconds it saved (the one thing prep could not measure). Bar-4 arithmetic named in the
report: which of the 7 non-agreed gold rows moved (needs ≥5).

## Verify (paste outputs, `python3.11` throughout)

```
make check                                        # green before and after, counts
runpodctl pod list -a                             # [] after deletion (plus the other two listings)
python3.11 scripts/runpod_guard.py --step reader-v5 --step-cap 0.45
shasum -a 256 results/prereg_reader_probe_v5.json # the frozen bytes the pod read under
<verdict record printed by its scorer: bars, m-bars, censuses, stop telemetry>
```

## Report

`docs/reports/reader-v5-run.md`, path-only in chat. Deviations from **Dv469** with
`[cause:]` tags; five-line Process signals. Read back first, one line each: the
one-attempt clause AND the programme stop-rule's consequence; the leg order and why;
what freezes when the pod exists; the affordability deadline at the real price; the
recovery clause below.

## Recovery clause (a caught fault must not strand the attempt)

The partial results file is scp'd continuously, so a pod that dies mid-run leaves its
answered units on the Mac. Within the SAME cap and the SAME frozen registration, a
replacement pod may be created to answer ONLY the units with no persisted reply —
answered units are NEVER re-asked (one attempt means one answer per unit). If the cap
cannot buy the remainder, STOP and report: that is the gate speaking, not a failure of
the contract.

## DO NOT

- No serverless anything. One pod at a time; delete, never stop.
- No cap raise, no anchor regeneration, no second pass at an answered unit, no edit to
  ANY frozen file once the pod exists (the registration included — step 0's fix is the
  last legal change).
- Leg B rows never reach a leg-A bar, a production aggregate, or a window price.
- Team-lead files: commit verbatim, never edit. Never `git add -A`.
- Numbers in the report point at artifact paths; prose never carries a figure the
  artifact does not.

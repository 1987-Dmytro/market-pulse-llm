# PROMPT — pass1-window: pass 1 over the WHOLE window-1 reader population on prompt v2 (D0 $0 → D1 paid, cap $1.50 → D2 $0)

**Fresh executor session. Authority:** the operator's rulings of 2026-08-21 in the
team-lead session, registered in `docs/STATUS.md` («Открытые решения», п. 1 (а)–(д)):
(а) `pass1_comment_gm4_v2` is the BASE prompt of pass 1 from now on; (б) the next
step is the end-to-end window run — pass 1 over every payable comment of window-1,
then pass 2 (signal assembly) against `docs/REFERENCE-signals-w1.md`; (д) two
contracts, one paid run each — THIS one is pass 1 only, cap **$1.50**;
`pass2-signals` is the next contract and is priced there from THIS run's census.
Read: this file → `docs/PROMPT-pass1-fewshot-r2.md` (the kill-clock this contract
inherits rung by rung) → `docs/reports/pass1-fewshot-r2.md` §D1 (the environment
readings: ssh ≤ 50 s · load 142.7 s · v2 2.726 s/call) → `results/prereg_pass1_fewshot_r2.json`
(the record whose `instruments` this one copies). Deviations from **Dv623**, enum v2;
five-line Process signals; team-lead files verbatim; never `git add -A`.

## What this run IS, and what it is not (state your assumptions against it)

- It is a PRODUCTION pass, not an evaluation: 1 032 payable comments of 129 threads
  (`gate_census_w1_reader.population()`, cell `narrow|varto_off|plus_spam+scam` — the
  count is re-derived by calling it, never typed), each rendered under v2 EXACTLY as
  the dev leg rendered it: `build_pass1_fewshot_packs.py::rendered_item` with five
  neighbours from `::neighbours` (labels MINUS the query's own thread — a comment is
  never shown its own label or its thread's) and the topic/entity block from
  `::context()` (= `build_pass1_sft.py::verdicts()` / `::envelope()`, the bought v5b /
  v4 / topup verdicts — NO reading is re-purchased). Import these functions; do not
  copy them.
- Its out-file is the INPUT of pass 2. The bar is therefore transport and
  completeness, pre-registered: **answered 1 032 / 1 032 · every row's
  `rendering_sha256` equals its pack item's · parse refusals ≤ 10 (1 %)**. Refusals
  are counted by cause, never dropped (the empty-class trap).
- **The fourteen gold rows and the 64 probe-b units are INSIDE this population and
  are answered like any other comment.** Their agreement with the gold is a
  REPORT-ONLY census row with the multiplicity named in the record («the fourth look
  at the fourteen: base, arm A, [v2 never shot], now v2 inside a production pass —
  a reading, never a bar»). It cannot be promoted to «v2 takes 12/14» by anyone,
  and the record says so in `return_to_the_operator`.
- By-product worth having, report-only: agreement on the **650 labelled rows**, and
  separately on the **450 labelled rows NOT in dev-200** — a larger reading of v2 than
  the dev gate's, on rows no prompt was ever tuned against. Both against the labels
  `results/labels_pass1_r1.jsonl` + `_r2.jsonl`, scored through `scorer.reader_comment_agreement`
  exactly as `gate_pass1_fewshot.py::leg_table` does — import it or call the same function.
- **What prices pass 2 (the census pass 2 needs):** per thread — payable comments,
  rows pass 1 labelled `категория_личное` / `молочный_бренд` / `сеть_ритейлер`
  (the pass-2 filter), their total characters, and the thread's entity block size.
  Pass 2 is ONE call per thread over those rows; its registration reads this table.

## Money — the H6 block (re-derive ALL of it as your step-1 refusal gate)

- **Generation:** 1 032 calls × **3.4075 s/call** = **3 516.54 s**. The rate is r2's
  MEASURED v2 figure 2.726 s/call × 1.25 — a named margin for the window's larger
  entity blocks, not the ×1.5 bound r2 charged (Process signal 5 of r2). Name the
  sample beside the number: «2.726 s/call over 200 dev rows, pod `8tpx8lf05n6skc`».
- **Seconds:** ssh 500 + stage/launch 150 + load 450 + generation 3 516.54 + overhead
  1 300 = **5 916.54 s = 1.6435 h → worst $1.3148 at $0.80/h** ($0.8710 at $0.53/h).
  Overhead 1 300 covers: copy-back of ≤ 1 032 rows on every poll, the completeness
  gate on the Mac, delete + listing. Nothing counted twice — ssh and staging have
  their own lines, as in r2.
- **Cap $1.50** (step cap = contract cap; no r1 pods to add). **Cumulative hard stop
  6 500 s = $1.4444 < $1.50**; session ceiling 1.50/0.80 = 1.875 h = 6 750 s ≥ hard stop.
- **Recovery reachability, asserted in the record:** one dead pod at rung 2 (500 s =
  $0.1111) + the full worst case = 6 416.54 ≤ 6 500 ✓ and $1.4259 ≤ $1.50 ✓; the
  widest dead pod that still fits is 583.46 s > 500 ✓. `re_creations_allowed: 1`;
  a SECOND dead pod = STOP, the session closes, the question returns to the operator.
- Card: RTX 4090 in EU-RO-1 (the volume `qw4nwleanc` pins the DC); price ceiling
  $0.80/h (rung 1). `BACKSTOP_TOLERANCE_SECONDS = 60.0` read FROM the record.

## The kill-clock — r2's rungs, inherited by NAME (the gate reads every number from the record)

1 price ≤ $0.80/h + `--terminate-after` = create + hard stop (+ tolerance) · 2 ssh
dead-man ≤ 500 s of create-elapsed · 3 launch → first reply ≤ 450 s of `launched_at`
(the POD writes the stamp; `--watch` copies it back; never typed) + create-anchored
backstop 1 100 s · 4 projection on EVERY poll against the hard stop and the cap, the
measured rate replacing the bound as rows land · 5 **liveness: 600 s since the last
new row → KILL** · 6 cumulative hard stop, platform-held · 7 the completeness bar on
the Mac after scp. Every rung has a producer, a fake-transport test in BOTH
directions, and is driven at $0 before the first `pod create`. Dv612/613/614/615/620
of r2 are the classes to test for explicitly: no typed stamps, no copied thresholds
without an H6 row, clock-bounded polls, `--price` runs the recovery check, one leg.

## D0 — at $0, before any pod (commits BEFORE the first `pod create`, checked by acceptance against the create stamp)

- `scripts/build_pass1_window_pack.py` → `results/pass1_window_pack.json`: ONE leg
  `v2`, 1 032 items in the population's own thread-grouped order, each with its five
  neighbours and the thread's context; records which ids are gold-14 / probe-64 /
  labelled-650 / dev-200 (so D2's census rows are derived, not grepped later); the
  contamination block becomes a **self-exclusion** block (0 items shown a neighbour
  from their own thread); length check against the 12 000-char ceiling (name the
  widest request; a request over the ceiling is a STOP at build time, not on the pod).
- `scripts/write_pass1_window_prereg.py` → `results/prereg_pass1_window.json`:
  `instruments` COPIED from r2's record with every pin resolved against the live file
  (the r2 producer's refusal), `kill_clock` by name, `money` with the H6 rows above,
  `bars` = the completeness bar, `population` = the pack's sha + counts,
  `return_to_the_operator` with the multiplicity sentence about the fourteen,
  `what_this_run_is_not` (not an evaluation; nothing here is a bar on v2's quality).
- `scripts/gate_pass1_window.py` — a sibling of `gate_pass1_fewshot.py` (import what
  is shared, say what you copied and why); `scripts/runbook_pass1_window.md` —
  r2's corrected runbook with ONE leg and no dev gate; the pod runner is
  `scripts/pass1_fewshot_pod_runner.py` with `--only v2` on a one-leg pack — if it
  cannot run a one-leg pack unchanged, that is a finding, named before any change.
- Guard step **`pass1-window`**, anchor at session start, `--step-cap 1.50`. Run
  record `results/pass1_window_run.json`; out-file as the pack names it.
- **ADR `v2-is-the-base-and-pass-2-is-not-a-one-shot-reader`** in
  `knowledge/decisions/` + INDEX line, quoting the operator's rulings (а)–(д) from
  `docs/STATUS.md` verbatim, including the reading of the 17.08 stop-rule: a per-thread
  assembly call over ALREADY-ATTRIBUTED comments is not the one-shot reader the
  stop-rule closed — it does no per-comment attribution and answers no question
  from the raw thread. The record binds the team lead too.
- `make check` green; `make preflight ARGS='gate_pass1_window.py prereg_pass1_window.json'`
  pasted; **the five-lens review before the create** (rung logic · arithmetic · what
  must not move · do the tests fail when the logic breaks · clause-by-clause
  compliance), each finding attacked by a skeptic, survivors fixed with a mutation
  watched to go red — r2's Dv613 class is the reason this is a step, not an option.
- Commits: pack builder + pack · producer + record + gate + tests (one commit, Dv609's
  reasoning) · runbook · ADR · guard anchor · vault tail — ALL before the first
  `pod create`.

## D1 — the paid run (one pod, one leg, never left unpolled)

Runbook order as r2's: `--price` (rung 1, records the pod either way) → clock-bounded
ssh poll (rung 2) → stage, `launched_at` written by the pod in the launch command →
`--watch` entered at once and never left (rungs 3/4/5/6 on every poll, rows copied
back each poll) → scp of out-file + `launched_at` + pod log, sha256 on the pod
(`LC_ALL=C sha256sum`) and on the Mac, four for four → `runpodctl pod delete` →
listing `pod list -a` / `serverless list` / `network-volume list` with the volume as
positive control → rung 7 on the Mac. Per-row evidence persists as r2's did: the
request as rendered (sha), the raw reply, `elapsed_since_start`, `boot_seconds`.
Recovery: one re-creation after a PROVEN deletion, within the same cap; the Mac's
copies of a dead pod's run directory are cleared first (Dv621).

## D2 — the census, $0 (`results/pass1_window_census.json` + the report)

1. The completeness bar: answered / refused by cause / sha mismatches → GO or RED.
2. Label distribution over the 1 032 (and per thread); the pass-2 filter table per
   thread (rows labelled категория_личное / молочный_бренд / сеть_ритейлер, their
   characters, the entity block size) with totals — this prices `pass2-signals`.
3. Report-only readings, each captioned «not a bar»: agreement on the 650 labelled
   rows; on the 450 not in dev-200; the dev-200 rows themselves (should reproduce
   r2's 136/200 · 38/49 up to decoding noise — state the difference, do not explain
   it away); the fourteen, with the multiplicity sentence.
4. Measured spans: ssh, load, s/call, per-poll copy-back — beside what was charged.
Report `docs/reports/pass1-window.md`, path-only in chat; Deviations from Dv623 on
enum v2; Process signals five lines; STEP SUM line from the guard.

## Read back FIRST, one line each

the population and who derives it · the five neighbours and what they exclude ·
the completeness bar (three numbers) · why the fourteen are a census row and never
a bar · the worst case, the cap, the hard stop, the recovery arithmetic · the
liveness rung · which record blocks are COPIED from r2 and which are new.

## DO NOT

No change to prompt v2, the neighbour rule, the labels, the gold, the sealed r1/r2
records or any pinned file; no second leg (no base run — the base was measured in
r2); no dev gate; no re-purchase of reader context; no generation before H6 and the
commits; never leave `--watch`; never two billing endpoints CONCURRENTLY (one
re-creation after a proven deletion is allowed); no third pod; team-lead files
verbatim (docs/STATUS.md, docs/SPEC.md, docs/PROMPT-*.md) — commit them, never edit.

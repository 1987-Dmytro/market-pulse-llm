# PROMPT — reader-v3-run: the paid re-read of the 23 threads, bars against gold r2

**One paid rung. Cap $0.35 all-in against the cycle-2 line ($19.98 remaining), enforced by
`runpod_guard --step reader-v3 --step-cap 0.35`. ONE attempt: a STOP from the go/no-go
closes the question — no retry, no cap raise mid-session.**

**The law of this run is `results/prereg_reader_probe_v3.json` — FROZEN.** You may not
edit the registration, the v3 prompt, or the parser after the endpoint exists
(`frozen_when_the_endpoint_exists`). The team lead's ruling on Dv426 stands: repair 3
stays NARROW as registered. Autonomy: full on mechanics, zero on anything the
registration states.

**Baseline:** `make check` 2 623 / 2 skipped at `4bc128b` (or current HEAD) + tail.

## Step 0 — tail

`knowledge/**` by live `git status`, one commit by path. Anything outside → STOP.

## The run, in probe-b's proven order (its report §4.1 is the runbook)

1. **Step anchor before anything billable:** `runpod_guard --step reader-v3 --step-cap
   0.35` — the new anchor records `anchored_at` (Dv419 machinery). Both step-ledger
   spellings are one file since Dv392 — confirm with `ls results/spend_reader*`.
2. **Stage the volume:** read `runpodctl gpu list` TODAY for the cheapest staging class
   (RTX 2000 Ada was $0.240/h with stock on 15.08 — read, don't assume); pod with
   `--terminate-after`; `repo/` moves by **fetch + hard reset to this contract's HEAD**,
   never `rm -rf` (the 467 MB adapter lives inside `repo/` and stays). The volume's own
   venv must render ALL THREE reader texts + the parse module byte-identical to this Mac
   — paste the shas. Delete the staging pod the moment it answers; prove by listing.
3. **Serve:** template + endpoint, `ADA_24` requested, workersMax 1, idle 60 s,
   execution 900 s (the API stores ms — `serving.execution_policy` is the one conversion
   point), flash-boot, volume `qw4nwleanc`. **Read `gpuIds` back from the create call —
   it is free** — and record the card. Never two billable endpoints concurrently — the
   goal is one meter running, not a naming rule.
4. **Handshake:** per-task sha map must carry v3 (Dv428's `handshake` check), commit =
   this contract's HEAD, `serving_config: READER`, base-no-adapter, batch 1.
5. **Warm-up = probe-b's same three threads** (pairing) → **go/no-go by the
   registration's arithmetic**: remainder + measured setup, pessimistic binds, the cap
   absorbs 1.165× against probe-b — a warm-up slower than that is the STOP working.
   Honor a STOP: delete, prove, close the step, report. The question closes.
6. **GO → read all 23.** Persist PER ROW, as the run happens: the rendered request and
   its per-thread sha (the registration pins them), the RAW reply byte-exact, the parse
   outcome with its `repairs: [...]` or refusal reason, billed seconds, `finish_reason`.
   A row that exists only in aggregate cannot be shown to the operator afterwards — the
   sitting rule.
7. **Delete endpoint + template; prove by the three listings** (positive control: the
   volume must appear). Recovery clause: after a PROVEN deletion, re-creating the
   template+endpoint within the same cap is authorized if a mid-session fix needs it.
8. **Close the step:** `runpod_guard --step reader-v3 --step-cap 0.35 --close` once the
   walk answers — settled figure, decomposition by kind, volume on its own line. If the
   walk still says «no rows», report the deletion-time reading as a LOWER BOUND and
   leave closing as a named debt for tomorrow's first guard run — never close over an
   unanswered walk (the guard refuses anyway).

## Scoring

Your run driver reproduces `write_reader_prereg_v3.bar_three_over_answers` for bar 3 —
same fields (`threads_registered`, `threads_with_a_verdict`, `threads_refused`,
`signals`, `reachable`, `passed`) — bars 1/2/4 against **gold r2**
(`results/reader_gold_w1_r2.json`), bar 5 against the step ledger. The verdict record
carries: bars as-run, the refusal census BY SHAPE (which of probe-b's six shapes
returned, which are new), the repair census (which repairs fired, how often), per-thread
`finish_reason` and a tokens-per-`per_comment`-row reading (Dv433's unlock — the window
decision needs it). Paired columns beside probe-b's numbers where the row exists in
both: parsed count, per-comment agreement, flagships, entities.

**The scorer module `scorer.py` stays untouched (Dv431)** — four sealed records pin it.

## Verify (paste outputs)

```
make check                          # green before and after; count stated
runpodctl serverless list && runpodctl pod list -a     # [] and [] after deletion
python3 scripts/runpod_guard.py --step reader-v3 --step-cap 0.35   # closed or lower-bound stated
<verdict record printed by its own reader: bars, refusal census, repair census, pairing table>
```

## Report

`docs/reports/reader-v3-run.md`, path-only in chat. Deviations from **Dv435** with
`[cause:]` tags; five-line Process signals. Read back first, one line each: the runbook
order; the 1.165× floor and what binds; bar 3's fields; what is persisted per row.

## DO NOT

- No edits to the registration, prompt v3, parser, gold r2, census cells — frozen law.
- No changes to `scorer.py`, POSITIONS/caption paths, r1, classification gate.
- Team-lead files: commit, never edit. Never `git add -A`.
- No cap raise, no second attempt after a STOP, no anchor regeneration.
- Injected labels: under the reader cell all 23 are production-reachable (Dv427) — but
  probe rows still never enter production aggregates or window prices.

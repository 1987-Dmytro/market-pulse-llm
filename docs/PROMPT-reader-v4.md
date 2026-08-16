# PROMPT — reader-v4: the registration re-cut, and the re-read on a POD with the boot in plain sight

**One paid rung on a rented pod. Cap $0.35 all-in against the cycle-2 line ($19.57
remaining), enforced by `runpod_guard --step reader-v4 --step-cap 0.35`. ONE attempt; a
kill or a STOP closes the question. No serverless anything — the operator's ruling after
v3's boot ate the cap: on a pod the boot is WATCHED and killable.**

**Instrument unchanged and untouchable:** prompt v3 (`22533644…`), parser v3, gold r2.
`results/prereg_reader_probe_v3.json` stays frozen as the record of the spent attempt.
This contract writes `results/prereg_reader_probe_v4.json` — same instrument shas, same
population, three registered differences (below) — and freezes it before the pod.

**Baseline:** `make check` 2 645 / 2 skipped at current HEAD + tail.

## Step 0 — tail and the v3 step debt

1. Tail by live `git status`, by path (vault commit; team-lead files verbatim if dirty).
2. **Close the `reader-v3` step:** the walk has posted (serverless 1 211 005 ms /
   $0.3718 on `77o1ing6cy0972`, pods $0.02) — `runpod_guard --step reader-v3
   --step-cap 0.35 --close --note "…"` now settles it with the decomposition. Its
   breach stands recorded; closing is bookkeeping, not amnesty (the guard knows).

## D1 ($0) — the v4 registration, three differences, everything else copied

`results/prereg_reader_probe_v4.json` via the v3 producer extended. Copied unchanged:
instrument shas (all three prompts + parser), population digest `ccef35fa4b9c771f…` and
its 23 threads, bars 1/2/4 thresholds, the per-thread request shas, one-attempt clause,
`frozen_when_the_pod_exists` (the pod is the resource now). The three differences:

1. **Bar 3 back over FIVE threads** — `["N2","N3","N4","N5","N6"]` — with v2's
   `excluded_with_cause` for N1 RESTORED verbatim (the reference's own S list reads S1
   in N1's thread; a bar that fails the reader for agreeing with the reference measures
   nothing). Dv440 closed. The `bar_three_over_answers` predicate and its fields stay.
2. **The vocabulary collapse is the BAR, symmetric** (team-lead adjudication under
   sitting ruling 4: the two words are ONE class): wherever bars 1/4 compare
   `subject_type`, «категория» ≡ «категория_личное» on BOTH sides — gold cell and
   reader answer alike. Gold r2 stays the gold; the prompt is not touched. The
   registration states the equivalence as a scoring rule with a test that drives it in
   both directions. Dv441 closed.
3. **Pod money arithmetic with a pre-registered kill rule.** The meter is the pod's own
   per-second price read from its create response. Registered gates:
   - staging: $0 expected — the volume is already at the right commit; verify shas,
     re-stage only if moved;
   - **boot kill rule: if the FIRST parsed-or-refused reply has not landed within
     12 minutes of the generation process starting, KILL the pod → STOP.** Ceiling of a
     killed boot ≈ $0.12 at $0.59/h — priced in the registration from the card's real
     rate;
   - full-pass projection: boot ≤ 720 s + reading ≈ 730 s (probe-b's 727.664 s worker
     for these 23) + margin → the go/no-go inequality solved for SECONDS, both numbers
     published (v3's Dv437 lesson: publish the pair the verdict re-derives from);
   - hard backstop: `--terminate-after` at create, 90 min.

## D2 ($0) — the pod transport

The generation runs ON the pod; parsing and scoring run on this Mac. Shape:
- ship the 23 rendered requests as a pack, each verified against the registration's
  per-thread sha BEFORE anything is sent; the on-pod runner loads the model ONCE
  (READER config: base, no adapter, batch 1, `enable_thinking=false`,
  `add_special_tokens=False` — the standing laws) and answers them in order, writing
  raw replies + per-reply worker seconds + `finish_reason`/usage to a results file as
  each lands;
- tail the load log LIVE (`python3 -u`) — the kill rule needs a clock you can see;
- bring the raw replies back byte-exact; parse with v3's `parse_reply` and score with
  `scripts/score_reader_v3.py` ON THE MAC, against the v4 registration (point the
  scorer at v4's bars; `scorer.py` stays untouched — Dv431 stands);
- persist per row exactly what the v3 contract listed: rendered request + sha, raw
  reply, parse outcome with `repairs`/refusal reason, seconds, `finish_reason` — to
  `results/reader_v4_w1.jsonl`, flushed as each reply lands (scp the partial file on a
  kill: a killed run must still show what it read).

Pod: **4090 (`ADA_24`-class) in EU-RO-1** (the volume pins the datacenter) — read
`runpodctl gpu list` TODAY for price and stock before create; record the card and
$/s in the run record; `pod list -a` before and after; **delete, never stop** — a
stopped pod still bills its disk. The three listings before anything is created and
after everything is deleted, volume as positive control.

## The run

Anchor first (`--step reader-v4 --step-cap 0.35`), then create, then watch: boot →
first reply inside 12 min or kill → all 23 → scp → delete → prove by listings → close
the step when the walk answers (or report the deletion reading as a LOWER BOUND and
leave closing as the named debt — never close over an unanswered walk). GO/STOP and
kill events are read from the registration's own numbers, pasted verbatim.

## Scoring and the verdict record

Bars 1/2/4 via probe-b's scoring functions under the v4 rules (collapse symmetric);
bar 3 via `bar_three_over_answers` over the five registered threads (the six-thread
reading reported BESIDE it for continuity with v3's registration, labelled); bar 5
against the step ledger. Also: refusal census by shape vs probe-b's, repair census,
per-thread `finish_reason`, tokens-per-`per_comment`-row (Dv433's window reading), and
the paired columns vs probe-b wherever the row exists in both.

## Verify (paste outputs)

```
make check                                   # green before and after, counts stated
runpodctl pod list -a                        # [] after deletion
python3 scripts/runpod_guard.py --step reader-v4 --step-cap 0.35   # closed or lower bound
<v4 registration digest + byte-identical rebuild>
<verdict record printed by its reader: bars, censuses, pairing table>
```

## Report

`docs/reports/reader-v4.md`, path-only in chat. Deviations from **Dv446** with
`[cause:]` tags; five-line Process signals. Read back first, one line each: the three
registered differences; the kill rule's clock and ceiling; what is persisted per row;
the deletion proof shape.

## DO NOT

- No serverless endpoint or template. One pod at a time; delete, never stop.
- No edits to prompt v3 / parser / gold r2 / v3 registration / `scorer.py` / shipped
  census files. The v4 registration freezes when the pod exists.
- No cap raise, no second attempt after a kill or STOP, no anchor regeneration.
- Team-lead files: commit verbatim, never edit. Never `git add -A`.
- Probe rows never enter production aggregates or window prices.

---
type: decision
date: 2026-08-20
status: accepted
tags: [decision, phase6, pass1, lora, sitting, gate, honesty-frame, money]
---

# The LoRA registration answered RED at 9 of 14 — line B is CLOSED and the question goes to sitting C

**The registration, the outcome, and what ships.** `results/prereg_lora_b.json` was committed before
`pod create` and the git clock proves it. The gate it registered —
`max(gold14(arm A), gold14(arm B)) ≥ 12 of 14` on the sealed gold r2, ONE attempt, tie ships arm B —
was applied by `scripts/score_lora_b.py` and came out **RED at 9 of 14**. The pre-registered
consequence fires without a re-decision: **line B is closed, nothing ships, and the question returns
to the sitting as option C, a different base.** A red bar is an ANSWER.

## What was registered

The sitting of 2026-08-18 chose line B and the sitting of 2026-08-19 sized it
([[sitting-b-line-b-and-the-team-lead-labels]]). Arm A is r1's 500 labelled units; arm B is r1 + r2's
650, so arm A's rows are a SUBSET of arm B's and the one variable is the r2 top-up. Both arms weighted
by `w_c = N/(5·n_c)` capped at 8.0. Supervision is `subject_type` alone — the team lead labelled one
field and training the other two as `null` would have put the bar out of reach at 11 of 14 before the
pod existed. Cap $6.00, base 9/14 sealed in probe-b's record and never re-run.

## What was measured

One paid session, pod `0cnth2accoyj0n`, RTX A6000 at **$0.53/h** in EU-RO-1, 13:21:44Z → 17:38:23Z:
**15 399 s, $2.3271 of the $6.00 cap** by the guard's pessimistic arm.

| | base (sealed) | arm A |
|---|---|---|
| gold-14 agreed | 9 | **9** |
| rows turned | — | none |
| rows lost | — | none |
| census-50 `None` | 25 | **9** |
| census-50 `не_наш_рынок` | 8 | **23** |

**Arm B was never trained.** Not for money — rung 5's guard reading was $2.1938 against a $2.50
milestone and passed — but for time: arm B needed 6 668 s at its own measured rate and the platform
backstop left 4 787 s, and with `save_every` 100 against arms of 62 and ~79 steps a backstop firing
mid-arm loses the arm whole. Rung 5 passed, rung 7 refused, the stricter binds.

## The finding the count hides

The identical 9 is not «the adapter did nothing». Arm A answered **two of the five misses
differently** from the base — 21601 and 48283 moved off `null` onto `сеть_ритейлер` and
`не_наш_рынок`, both still wrong — and on the 50 neighbour rows the profile moved hard: `None` fell
25 → 9 while `не_наш_рынок` rose 8 → 23.

**The fine-tune learned the training set's prior, not the discrimination.** 340 of arm B's 650 rows
are `не_наш_рынок` (52%), the class-weighted sampler was registered precisely to counter that, and it
did not hold. Training loss fell from 0.689 at step 5 to 0.0095 at step 60 on a head-only target of
one or two tokens — which is what memorising a label distribution looks like, not what learning a
decision looks like. 64 of 64 replies parsed; not one refusal, so nothing here is a transport loss.

This is what sitting C needs on the table: the failure was not «not enough data» and not «the format
collapsed». It is that supervising `subject_type` alone, on a set this skewed, teaches the marginal.

## What this record does NOT claim

- **Arm B is unmeasured.** The multiplicity the sitting accepted was two shots at one bar; one was
  taken. A single arm at 9 of 14 says nothing about whether 650 rows would have said 12.
- **The registered arithmetic drifted, in the cheap direction.** Arm A ran **62** optimizer steps
  where `ceil(500/16) × 2 = 64` was registered: with micro 2 the last two chunks of each epoch never
  complete an accumulation group. Measured **68.44 s/step** against a registered 61.047, and
  **33.19 GB** peak against the 35.13 GB measured on 45h2. Named, not fixed.

## The gap this session found, and it is the executor's

Rungs 4 and 8 — the s/step watchdog and the projection gate — **never fired**, because no `--train`
reading was taken while the meter ran. Arm A finished at 14:38:23Z and was found at 17:20Z:
**9 720 s of idle billing, $1.43 of the $2.33 spent.** The same arithmetic applied afterwards to the
recovered loss log says GO at every log line, so the rungs would not have caught it either:

> **there is no rung for «the arm finished and nobody noticed».** Every kill rule in this
> registration watches training that is too slow. None watches a pod that is not training at all.

And it was not free. Without those 9 720 s, arm B needed 6 668 s against 15 104 s of remaining
window — it would have fit with 8 436 s to spare. **The idle time is what turned a two-arm attempt
into a one-arm attempt**, halving the multiplicity the sitting had accepted and leaving the r2 top-up
unmeasured. [[long-run-watch-the-process]] · [[remote-job-outlives-its-watcher]]

The next contract of this shape needs an idle rung: a GPU-utilisation or process-liveness check
whose deadline runs from the last log line rather than from create.

## What ships

**Nothing.** Line B is closed. The adapter, its per-file hashes, the per-row replies and the loss log
are committed as evidence of the attempt, not as a deliverable. The ablation table above is what
sitting C is briefed with.

**The scorer runs after the LAST append to the run record, or its pin is of a state nobody can check
out** — the committed verdict pinned `3d0277c7…` while every copy of `results/lora_b_run.json` hashes
`aa20e10b…`, because the `train-a-retrospective` entry landed at 17:40:15Z after the scorer had
already read the file (Dv579, re-run in the addendum). [[provenance-cannot-name-itself]]

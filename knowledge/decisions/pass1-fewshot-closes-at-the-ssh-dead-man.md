---
type: decision
date: 2026-08-20
status: accepted
tags: [decision, phase6, pass1, prompt, gate, money, environment]
---

# pass1-fewshot: D0 is committed and green, and the paid session closed at rung 2 with the attempt intact

**The registration, the outcome, and what ships.** `results/prereg_pass1_fewshot.json` was committed
before `pod create` and the git clock proves it. The paid session it registered never generated a
token: **two RTX 4090s in EU-RO-1 at the registered `costPerHr` 0.74, both KILLed on rung 2 — the
180 s ssh dead-man — and the recovery clause's ONE re-creation is used.** Nothing ships, nothing is
measured, and **the ONE attempt is NOT spent**, which the registration's `attempt` clause states as
the outcome of exactly this state: a session that closes before any gold row is answered returns to
the operator. The question about the v2 prompt is still open, on purpose.

## What was registered, and it is all on disk

- **`results/pass1_holdout_100.json`** — 100 of the 650 labels, seed 20260820, **EVALUATION ONLY**,
  and `scripts/build_pass1_sft.py` now refuses to build a dataset carrying one of them. The
  exemption is line B's two SEALED arms, keyed on the shas `results/pass1_sft.json` pins rather than
  on their names. Registered BEFORE anyone trains again, which was the point of doing it first.
- **`pass1_comment_gm4_v2`** — v1's bytes plus one codebook clause («`subject_type` is what the
  comment is ABOUT, never what it mentions») and the examples slot. A strict prefix extension;
  **v1's own sha `5a4a3cb6…` did not move**, which is what keeps probe-b's evidence and the paired
  dev legs comparable.
- **`results/pass1_dev_pack.json`** — 200 labelled rows, each rendered TWICE as two legs: `base`
  under v1 with no examples, `v2` under v2 with five labelled neighbours. Same rows, same context,
  one difference.
- **`results/pass1_probe_b_pack_v2.json`** — probe-b's 64 units, identity and ORDER unchanged, under
  v2. The sealed pack is read and never touched.
- **`scripts/gate_pass1_fewshot.py`** — eight rungs, every threshold read out of the registration,
  and **rung 5 is a blocking loop the executor does not leave**: it copies the out-files and the pod
  log back and KILLs when no new answered row and no new log line have appeared for 600 s, measured
  from the LAST EVENT. That rung exists because lora-b billed 9 720 idle seconds under a
  registration whose every rung read a training log ([[no-rung-watches-an-idle-pod]]).
- **`scripts/score_pass1_fewshot.py`** — D2's verdict, which calls rung 7's own `dev_gate` and
  probe-b's own `bar_p1` rather than restating either.

## One example per class, and why it is the design

Nearest-k over the 650 labels is **52 % `не_наш_рынок`** — the exact marginal the adapter of line B
learned instead of the decision ([[lora-b-red-and-line-b-closes]],
[[an-identical-count-is-not-an-identical-model]]). A neighbour block drawn that way would teach the
same prior with none of the training. So the block is **one labelled comment per reading**, the four
subject types and the null, each the nearest by Jaccard over character 3-grams from a pool that
excludes the query's own thread. Balance is by construction and the record measures it: 200 of each
reading across the dev leg, 64 across the shot.

## What was measured, and it is about the environment

| | pod | created → deleted | billed | rung 2 reading |
|---|---|---|---|---|
| 1 | `7spsy61lpjumrz` | 20:56:55Z → 21:02:36Z | 341.0 s · $0.0701 | KILL at 262.5 s — **on my own instrument** |
| 2 | `juupgp6y77jvuz` | 21:03:41Z → 21:07:33Z | 232.0 s · $0.0477 | KILL at 231.9 s — **on the pod** |

**Pod 1's KILL was caused by the poller, and it stands anyway.** The loop grepped `"host"`, a key
`runpodctl ssh info` never emits — it answers `{"error": "pod not ready"}` and then an object
carrying `"ip"` and `"port"` — so it spun blind for 240 s, and the `--gate0` after it asserted the
endpoint had not answered. It had. A gate records the reading it is GIVEN, and a deadline that
cannot be demonstrated has not been passed; re-running a gate with a different flag after seeing its
verdict is the one thing this architecture exists to prevent. Deleted, proven by three listings with
the volume as the positive control.

**Pod 2's KILL is the finding.** Polled on `"port"` with the loop bounded at 170 s — inside the
rung — `runpodctl ssh info` still answered `pod not ready` at **231.9 s** of create-elapsed against
a registered **180 s**. probe-b passed the same rung on the same card in the same datacenter on
2026-08-18. So **180 s is a reading of that night and not a property of the stack**, exactly as the
boot on this stack has never been a constant (146.8 / 192.1 / 237.2 / 267 / 293 / 353 s).

## The consequences, and they bind

1. **The attempt is NOT spent.** No gold row and no dev row was answered. `docs/PROMPT-pass1-fewshot.md`
   D1 is unexecuted and D0 is committed and green.
2. **The recovery clause is USED.** `results/prereg_pass1_fewshot.json` allows ONE re-creation and
   it was made, after its arithmetic was computed and pasted ($0.0701 reading + $1.0949 worst case
   = $1.1650 ≤ $1.50; 5 667.6 s ≤ 6 300 s). **A third pod under this registration is not allowed.**
3. **Rung 2 needs the operator's word.** Either wait for the datacenter — lora-b's own precedent,
   where the operator ruled «ждать» and the window opened in about an hour — or re-register the
   dead-man from tonight's two readings. Re-registering is a NEW registration, not an edit: this one
   is committed, and its cumulative hard stop and its single recovery do not reset.
4. **A ruling that moves ONLY rung 2 ships the rung that fires next.** Rung 3's 450 s is derived in
   H6 from `max(measured boots) × 1.2748` — boots, the model-load window — and both `--boot` and the
   watch's own arming measure CREATE-elapsed, which also carries the ssh wait, the staging and the
   launch. probe-b bounds the gap: 657 s billed − 237.155 s boot − 330.3 s of generation = **89.5 s**
   of everything else, so its first reply landed near **326.7 s** with 123.3 s to spare. Tonight the
   ssh publish alone was unfinished at 231.9 s, and 231.9 + 89.5 + 237.2 = **558.6 s** against a
   450 s ceiling — killed by the loop, with no human in the path. The re-registration needs rung 3
   anchored on the LAUNCH, or a ceiling derived from create-to-first-reply, of which this stack has
   exactly one measurement.
5. **$0.1178 of the $1.50 cap is spent** on the clock's arithmetic (573.0 s × $0.74/h), against a
   guard balance delta of $0.0906 that is still settling. Cycle 2: **$5.8992 of $20.00, remaining
   $14.1008**.
6. **`scripts/score_pass1_fewshot.py` is not pinned** in the registration's `instruments` — lora-b's
   Dv584 class one contract later, except that this time the judge exists and is committed. It is a
   missing pin, and pins are not added to a committed registration.

## What this cost and what it bought

It cost $0.1178 and one recovery, and both were spent on the ssh dead-man rather than on the
question. It bought a D0 that is committed, green and adversarially reviewed before the money —
**twelve of the eighteen Deviations were found and CLOSED at $0**, among them a holdout allocation
that would have dropped the `молочный_бренд` class entirely and a liveness fingerprint that would
have kept a dead pod alive behind a flapping scp — plus one environment reading the next
registration needs and two findings (consequences 4 and 6) it must absorb.

The report is `docs/reports/pass1-fewshot.md`; the gate record is
`results/pass1_fewshot_run.json`, append-only, seven gates over two pods.

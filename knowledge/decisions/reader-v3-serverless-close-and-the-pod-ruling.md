---
type: decision
date: 2026-08-16
status: accepted
tags: [decision, phase6, comment-signals, reader, cost, runpod, serverless]
---

# reader-v3 closed at $0.3936 with nothing read, and the operator rules the reader onto a pod

**The attempt was spent on a boot.** `reader-v3-run` staged the instrument, opened a serverless
endpoint and never got an answer out of it. The step's ledger is the authority for every figure
below — `results/spend_reader_v3.json`, closing entry of `2026-08-16T17:08:16+00:00`, written by
`scripts/runpod_guard.py --step reader-v3 --step-cap 0.35 --close` in `bf2502f`:

```
settled_usd        0.393577          against a $0.35 cap
balance_delta_usd  0.413022
billing_since_usd  0.403299
  pods             0.021812          the staging pod and the zsh $SSHOPT loop
  network-volume    0.009722          always on, beside the run and inside no step
  serverless       0.371765          endpoint 77o1ing6cy0972, 1 211 005 ms, answered nothing
```

**What that buys, as a fact:** a cold start on this stack can cost more than the whole probe.
`1 211 005 ms` of billed worker time produced zero replies; the endpoint reported
`running: 1 · completed: 0 · retried: 0` for at least twenty minutes while the `info` job — which
IS the weight load — was never answered. Not one of the 23 registered threads was read, so every
bar of `results/prereg_reader_probe_v3.json` is **UNSCORED**, which is a different sentence from
«failed» and the report says so.

## The defect the money exposed: a gate downstream of the spend

v3's registration had exactly one go/no-go and it sat **after** a warm-up thread. A boot that never
reaches the warm-up never reaches the gate, so the run had no branch that could stop it — the
inequality was correct and unreachable. That is the whole finding, and it is a fact about where a
gate sits rather than about serverless. See `[[a_gate_downstream_of_the_spend]]`.

Closing is bookkeeping, not amnesty: the guard **refused first** (`REFUSED: reader-v3's $0.35 cap
is reached ($0.3936 spent)`, exit 1) and appended the settled entry underneath the refusal, so the
breach and the settlement are both in the file.

## The ruling — the operator, 2026-08-16, after reader-v3-run

**No serverless for the reader. One rented pod, with the boot in plain sight and a kill rule that
is code.** Three clauses, each answering a leg of the failure:

1. **The meter is a stopwatch from `pod create`.** A pod bills for every second it exists —
   provisioning, booting, generating, idle — so the cap is stated in SECONDS and every deadline is
   read against seconds since the create response. `pod stop` does not stop the bill; the run
   deletes and never stops.
2. **The boot is watched and killable.** The generation process is tailed live and unbuffered, and
   the deadline is `min(720 s, usable − elapsed − reading projection)`. Both numbers are printed
   when the deadline is set, because a deadline nobody can see pass is a deadline discovered
   afterwards, in a bill.
3. **The kill rule is a command, not an eyeball.** `--gate` returns `3 = WAIT`, `2 = KILL/STOP`,
   `0 = GO`, and the watch loop is a shell loop around it.

## What it was worth, measured the next evening

`reader-v4` ran the SAME instrument on the SAME 23 threads under the ruling, and its own ledger
settles at **$0.236118** of step resources (pods only; serverless `$0.0000`) for **23 of 23 threads
read**, boot **175.1 s**, pod alive 1 143 s. Same cap, same population, same prompt:

| step | settled (own resources) | threads read | bars scored |
|---|---:|---:|---|
| reader-v3 | $0.393577 — over the $0.35 cap | 0 of 23 | none, all UNSCORED |
| reader-v4 | $0.236118 — inside the cap | 23 of 23 | all five |

**The measurement the programme needed cost less than the boot that produced nothing.**

## Status of v3

`results/prereg_reader_probe_v3.json` stays **FROZEN and is not withdrawn**: it is the record of the
attempt that was spent, and the step ledger closed against it. v4 supersedes it as a registration
and names it in `supersedes`; the v3 prompt text, the v3 parser and gold r2 are exactly what v4
measured, which is what makes the two comparable at all.

Related: [[reader-sitting-16-08]] (ruling 2 registered the instrument this attempt was spent on),
[[reader-v4-closed-and-sitting-17-08]] (what the pod then measured), [[5b-parity-abort-and-pod-runtime]]
and [[srv2-program-close]] (the earlier serverless-versus-pod readings this ruling lands on top of).

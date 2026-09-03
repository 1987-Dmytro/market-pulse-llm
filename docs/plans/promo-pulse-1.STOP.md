# STOP — promo-pulse-1, 2026-09-03 (the eighth). The pod was bought twice and killed twice by MY OWN dead-man, which is set below the span it measures.

**Stop-point, and it is on §8's list: A RUNG FIRED** — the ssh dead-man, on both pods — and behind it
a design fork the plan does not settle: *which record's transport gate governs this step*. The
ruling's sequence was followed to the letter and stopped where the gate stopped it. **Nothing was
generated. No token was bought. Neither leg was staged.** Every listing after every delete is `[]`.

## What happened, in order

| | pod | create → delete | billed | rung 1 | outcome |
|---|---|---|---|---|---|
| segment 1 | `ocnsveqetsve8w` | 16:36:40Z → 16:40:15Z | 215 s · **$0.044194** | GO ($0.74 = registered) | no ssh port by 180 s |
| segment 2 | `gxuil044h61fkx` | 16:40:34Z → 16:44:15Z | 221 s · **$0.045428** | GO ($0.74 = registered) | no ssh port by 180 s, second machine |

`results/promo_dev_loop_run.json` — **$0.089622 of the $2.50 cap, $2.410378 left**, each segment
priced at its OWN `usd_per_hour × its own seconds` and never at a balance delta. Both pods reported
`"status": "RUNNING"` while `runpodctl ssh info` still answered `{"error": "pod not ready"}`.

**The ruling's create line is VINDICATED and is not the problem.** `--image
runpod/pytorch:1.0.2-cu1281-torch280-ubuntu2404`, `--data-center-ids EU-RO-1 --cloud-type SECURE
--ssh`, disk 30 — parsed, and both pods rented at the registered **$0.74/h** on the registered card.
The third correction was needed for a second reason the ruling did not have: `runpodctl pod create
--help` says `--terminate-after` is a **datetime** (`2026-04-15T00:00:00Z`), so the old `90m` was not
a smaller number — it was not a value of that flag at all. Derived from the cap it read
`2026-09-03T19:59:22Z` and `2026-09-03T20:03:16Z`, and the platform took it.

## The defect, from the records and not from the failure

* **What I registered:** `results/prereg_promo_dev_loop.json :: gates.ssh_deadman_seconds` = **180.0**,
  read out of `results/prereg_reader_probe_v5b.json` — a **PROBE**'s record.
* **What the production sibling registers for the same rung, the same image, the same card, the same
  datacenter:** `results/prereg_pass2_signals_r2.json :: kill_clock[rung 2].deadline_seconds` =
  **500.0**, and its own `rule` field carries the measurements: *«six readings run 14.5 → 262.5 and
  two pods of 2026-08-20 were still unreachable past 230 s»*.

**My gate is below the observed maximum of the very span it gates.** A healthy pod that publishes its
port at 262.5 s — a reading that is on record — is killed by it every single time. My two pods died
at 180 s and 184 s, inside the band where that evidence says no verdict is available yet, so I cannot
report that they were dead: I can only report that I stopped measuring before a measurement existed.
A gate that returns KILL before its measurement can be taken is not a gate, and its second firing is
not a second data point — it is the same instrument giving the same answer.

**The second recreate the runbook allows is deliberately UNUSED.** `gates.max_recreates` is 2 and I spent one. That clause was written for machine luck; two firings of an instrument set below its own span are not two data points, so the remaining recreate would have bought a third identical KILL for ≈$0.045 and ended the session with the same finding and less money. Refusing a purchase whose outcome the records already predict is cheaper than proving it a third time.

**Root cause, one sentence:** rung 0's overhead was borrowed from the sibling that SETTLED
(`results/pass2_signals_r2_run.json`) and the transport gate was borrowed from the probe — two
records for two halves of one transport model, and only the cheap half was checked against reality.

## The fix, priced at $0 — but it is a REGISTERED number, so it is yours

Take the dead-man from the same record the overhead comes from: **500 s**. Then a dead segment costs
500 + `delete_margin_seconds` 60 = 560 s = **$0.1151** at $0.74/h, two of them $0.2302, and the dear
corner $1.3193 + two dead segments = **$1.5495 — still inside $2.50** with the $0.30 holdout untouched.
`gates.terminate_after_minutes: 90` in the same record is voided by ruling (d) and should carry the
derived seconds instead; it printed beside every rung-1 GO above as a field that no longer describes
the pod that existed.

**I did not move it myself.** It lives in a pre-registration that was committed before the money and
whose own clause reads «no cap raise, never, mid-run»; a threshold not in the plan is a scope change.
Attempt 2 needs a NEW pre-registration file, not an edited one — a record cannot be rewritten after
its money has started ([[preregistration_is_a_file_not_a_constant]]).

## Two money questions for the ruling

1. **The step ledger has no anchor and I did not create one.** `runpod_guard.py --step promo-dev-loop`
   anchors at the balance NOW; anchoring after $0.0896 was spent would baseline the step above its own
   spend. Does attempt 2's registration open the step's ledger carrying $0.089622 as its opening
   balance, or is this attempt closed against the cycle alone?
2. **The lag is visible in the readings.** The guard's balance delta moved $3.5506 → **$3.6322**
   (+$0.0816) while its billing walk still reads $3.5409 — the 30–40 min PROCESS names. The pod-priced
   $0.089622 above is the quotable number; the two will not agree until the walk lands.

`make check` green at the bundle HEAD `5d0386b` before the create: **4 313 passed, 2 skipped, exit 0**.

**STOP — /goal clear**

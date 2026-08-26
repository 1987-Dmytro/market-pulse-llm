---
type: decision
date: 2026-08-26
status: proposed
tags: [decision, phase6, lora, training, rate, money, pod, kill, projection]
---

# The line trains at 89.961 s/step — and the gate that would have hidden it

`lora-c-run r3` executed on 2026-08-26 under ruling (т), cap $7.00 all-in. One pod,
**1 152 s = $0.4448**, KILLed by the projection rung after the smoke. This record is the English
long form; `docs/reports/lora-c-run-r3.md` is the report and carries every number, 73 of 73
re-derived by a checker the suite drives.

## The reading

**`provenance.json::run.seconds_per_step` = 89.961 s/step at `max_seq_len` 3 072, on an A100 PCIe.**
The first measurement of this line's training rate that has ever existed. The whole loop's wall
(539.8 s) over its six optimizer steps, at the registered `micro_batch_size: 2` and `grad_accum: 8`,
both of which came back unmoved.

It is not warm-up. The decomposition was registered BEFORE the smoke landed, and it says so: the
step-6 loss line covers one step and still divides by `log_every`, so multiplying it back gives that
step's own wall — **87.207 s**. Amortised start-up is **16.6 s of 539.8**, 3.1%.

| prior | s/step | taken at | this line is |
|---|---:|---|---:|
| registered by lora-b | 61.047 | ≤1 222 tokens, A6000 | **1.47×** |
| measured on lora-b arm A | 68.442 | ≤1 222 tokens, A6000 | **1.31×** |
| **measured here** | **89.961** | 1 445–2 975 tokens, A100 PCIe | — |

Amendment 3.26 (3) retired the tokens-per-character ratio model for CEILINGS. This retires it for
RATES: a projection from lora-b's readings would have been 31–47% under.

## Why the KILL, and why no charge explains it away

At 89.961 s/step the registered plan projects **21 284.8 s** against an 18 000 s stop and
**$8.1271** against a $7.00 cap. Solved backwards, the cap afforded 68.05 s/step and the stop 67.15;
the measurement is 1.32× and 1.34× those. Every corner of the two rates nobody had measured is still
over — even 6.14 s/call with the ten pass-2 threads read at $0 comes to **$7.33**. The KILL is the
rate.

## The finding underneath it

**`gate_lora_b.measured_step` would have said GO.** It takes `max(mean, last)` of the loss lines'
`seconds_per_step`, and each of those divides by `log_every` regardless of how many steps its window
held. On this session's own log it returns **53.690** against a loop that ran at **89.961** — a
40.3% understatement that lands under the 68.05 the cap afforded. The projection would have passed,
both arms would have trained into the platform's terminate flag, and the session would have spent
$6.95 for no adapter, no eval and no bar — and the frozen registration's one attempt with it.

Both halves of that defect were already in this repo's Deviation ledger — **Dv813** (the gate waits
for six loss lines and `log_every: 5` writes two) and **Dv814** (the last line is not a rate) — named
by the vramprobe report on 2026-08-25 and never fixed. They were fixed here because the r3 gate was
written by reading the trainer's own arithmetic rather than trusting the sibling
([[projected_rate_versus_measured_rate]], [[a_flag_that_asserts_turns_a_poll_into_a_verdict]]).

## What else the $0.4448 bought

**48 GB is closed by measurement.** Peak allocation was **49.54 GiB** and `nvidia-smi` read 57 297
MiB in use at 100% and 304.72 W. A 48 GB card has less total memory than this run allocates at its
peak, so all three cheap alternatives in the migration's stock table are refuted — the STATUS
blocker «48 GB на 3 072 не мерил никто» has an answer.

**A model load is not a constant: 40.22 s · 138.49 s · 13 s** — same weights, same volume, same
shipped loader, and the last two inside ONE pod. The cold read is 10.7× the warm one
([[a_rate_is_a_property_of_the_pod]]).

**Rung 2 came within 152 s of KILLing a healthy run.** A training stage prints nothing until step
`log_every`, so at 89.9 s/step the smoke was silent for 448 s against a 600 s deadline while the GPU
sat at 100%. The registered liveness signals — a log line, a byte-growth poll — do not cover that
window. The rung was not bent; the remedy belongs to the next contract
([[no_rung_watches_an_idle_pod]]).

## What is NOT spent

The frozen `results/prereg_lora_c.json` is unmoved and its **ONE attempt is UNSPENT**: rung 8 spends
it at the first reply an ADAPTER leg generates against E, and no arm was trained. The base columns
are r2's and were not re-bought. Six optimizer steps were bought, all of them the smoke's.

## The three prices, for the operator

| | seconds | usd |
|---|---:|---:|
| the plan as written | 21 284.8 | **8.2183** |
| **arm A alone** — 62 steps, one eval leg, one pass-2 leg | 10 447.4 | **4.0339** |
| both arms at ONE epoch (72 steps) — `epochs: 2` is frozen law | 14 807.6 | **5.7174** |

Cheaper hardware is not on the menu: 48 GB is closed by this session's own peak, and the $1.19
community row for this card is a different cloud type from the SECURE datacenter the volume lives
in. Raising the cap, halving the scope, or changing frozen law are three different decisions and all
three are the operator's.

Related: [[lora-c-the-volume-moves-to-ca-mtl-3]] · [[lora-c-the-card-cannot-train-at-3072]]

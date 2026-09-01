# `lora-c-run r3` — KILL at the projection rung: this line trains at 89.961 s/step

The session bought the one number it existed to buy and the number refused the plan.
**`provenance.json::run.seconds_per_step` = 89.961 s/step at `max_seq_len` 3 072 on an A100 PCIe** —
the first measurement of this line's training rate that has ever existed. Against it the registered
plan projects **21 284.8 s** on an 18 000 s hard stop and **$8.1271** on a $7.00 cap, so the
projection rung KILLed after the smoke, as it was registered to.

**$0.4448 of $7.00. Six gates, five GO and a KILL. The frozen registration's ONE attempt is
UNSPENT** — rung 8 spends it at the first reply an ADAPTER leg generates against eval set E, and no
arm was trained.

The finding underneath the KILL is bigger than the KILL. **The shipped gate this session inherited
would have said GO.** `gate_lora_b.measured_step`, on this session's own two loss lines, returns
**53.690** where the loop ran at **89.961** — and 53.690 sits under the 68.05 s/step the cap could
afford. The session would have trained both arms into the platform's terminate flag and produced no
adapter, no eval and no bar, for $6.95. The rung that caught it was written at $0 four hours before
the create, on nothing but a reading of the trainer's own arithmetic.

## The commits

| commit | what |
|---|---|
| `502f8bd` | the team lead's contract and STATUS, verbatim |
| `76eef15` | the team lead's migrate-r2 vault tail |
| `1fa4df1` | step 0.5 — the last `[-1]` over a `results/` ledger, and the close debt's home |
| `aa567b9` | the sidecar money record, the gate, and the four defects it exists for |
| `bca998b` | the runbook, the stock reading, the smoke's decomposition |
| `dabba2b` | the 15-thread charge is a BOUND, and the $0 reading says 10 |
| `d89ab8b` | the paid session's artifacts |
| this one | the report, its checker and the ADR |

---

## 1. The gates, each on a reading

Meter starts at `pod create` **2026-08-26T08:39:50Z** and stops at `pod delete` **08:59:02Z**.

| rung | what | reading | bound | verdict |
|---|---|---|---|---|
| 0 | price and card | `costPerHr` **1.39**, `A100 PCIe` | ≤$1.50/h, card `A100 PCIe`, price in a registered column | **GO** |
| 6 | the platform backstop | given `13:39:49Z`, computed `13:39:50Z` | 18 000 s, overshoot ≤60 s | **GO** |
| 1 | the ssh dead-man | **24.3 s** | 500 s | **GO** |
| — | the load proof, on BLOBS | **138.491 s**, 12 blobs, **0 grew**, **17.046** GiB of 79.25 on the card | 600 s, and no blob grows | **GO** |
| 4 | the smoke | **89.961 s/step**, `micro_batch` 2 → 2 | ≤181.5 s/step, instrument unmoved | **GO** |
| 5 | the projection | **21 284.8 s · $8.1271** | 18 000 s · $7.00 | **KILL** |
| 7 | never two billing resources | 1 pod, opened and closed | 1 | **GO** |
| 3 | the realised rate of an eval leg | never fired — no eval leg was bought | $7.00 | — |

Rung 2's silence clock is what every stage is graded on, and §5 records how close it came to
KILLing a healthy run.

---

## 2. The reading this session existed to buy

**89.961 s/step**, `results/lora_c_run_r3_smoke_provenance.json::run.seconds_per_step` — the whole
loop's wall (539.8 s) over its six optimizer steps, at `micro_batch_size` 2 and `grad_accum` 8, both
of which came back exactly as `config/qlora.yaml` registers them.

**It is not a warm-up artefact, and that was checkable because the decomposition was registered
before the smoke landed.** `log_every: 5` and `--max-steps 6` write two loss lines, and the second
one's window holds exactly ONE step while still dividing by `log_every` (Dv814). Multiplying it back
recovers that step's own wall:

| | seconds | what it is |
|---|---:|---|
| the loss line at step 5 | 89.938 | the first five steps' wall ÷ 5 — a real rate, and it carries the start-up |
| the loss line at step 6, as logged | 17.441 | ONE step's wall ÷ `log_every` — **not a rate** |
| the same line × `log_every` | **87.207** | that single step's own wall |
| the loop, `run.seconds` | 539.8 | |
| amortised start-up, `539.8 − 6 × 87.207` | **16.6** | 3.1% of the loop |

So the steady state is ~87 s/step and the graded 89.961 is 3.2% above it. Over arm A's 62 steps the
start-up would amortise ten times thinner; it does not move the answer.

**Against the two readings this repo owned before today:**

| prior | seconds/step | measured at | this line is |
|---|---:|---|---:|
| registered by lora-b | 61.047 | ≤1 222 tokens, A6000 | **1.47×** |
| measured on lora-b arm A | 68.442 | ≤1 222 tokens, A6000 | **1.31×** |
| **this line, measured** | **89.961** | 1 445–2 975 tokens, A100 PCIe | — |

Amendment 3.26 (3) retired the tokens-per-character ratio model for CEILINGS after it under-predicted
the widest row by 228 tokens. This is the reading that retires it for RATES: the contract forbade
projecting this line's s/step from lora-b's, and the two numbers a projection would have used are
31% and 47% under the truth.

---

## 3. What the KILL means, solved backwards

The projection rung fires on the guard's reading plus the remainder at measured rates. At the moment
it fired, 1 109.2 s were billed and $0.3371 was on the meter.

| | seconds | usd | over the cap | over the stop |
|---|---:|---:|---|---|
| charged 9.20 s/call · the registered 15-thread bound | 21 284.8 | 8.2183 | **yes** | **yes** |
| charged 9.20 · the **10** threads measured at $0 | 20 314.8 | 7.8438 | **yes** | **yes** |
| the old 6.14 s/call · 15 threads | 19 950.6 | 7.7032 | **yes** | **yes** |
| 6.14 · 10 — the most favourable corner both unmeasured inputs allow | 18 980.6 | 7.3286 | **yes** | **yes** |

**No corner fits.** The KILL is the RATE, not the conservatism of the charge — which is what the
break-even table registered before the create exists to establish. Solved the other way:

- the **cap** could afford **68.05 s/step**; measured is **1.32×** that;
- the **hard stop** could afford **67.15 s/step**; measured is **1.34×** that.

The 15-thread bound was the input that made the plan knife-edge, and it is not the input that
decided it: at 10 threads the break-even rises to 68.89 s/step and 89.961 still refuses.

**What would have fitted $7.00, each of them a separate operator decision and none of them this
session's to take:**

| | seconds | usd |
|---|---:|---:|
| the plan as written needs a cap of about | 21 284.8 | **8.2183** |
| **arm A alone** — 62 steps, one eval leg, one pass-2 leg | 10 447.4 | **4.0339** |
| both arms at ONE epoch (72 steps) — `epochs: 2` is frozen law | 14 807.6 | **5.7174** |

---

## 4. Money, by the pod's clock

| | |
|---|---|
| pod `otq63mmt7s2uf1`, A100 PCIe, CA-MTL-3 | 1 152.0 s × $1.39/h = **$0.4448** |
| cap | $7.00 all-in — **$6.5552 left**, 6.4% used |
| the pod against its hard stop | 1 152 s of 18 000 = **6.4%** |
| guard, balance delta, before the create | $10.0265 of $20.00 |
| guard, balance delta, at the close (08:59Z) | **$10.4726 of $20.00** |
| guard, balance delta, in the ledger row (09:14:45Z) | **$10.4921 of $20.00**, $9.5079 left |
| guard, the WALK — `billing_since_usd`, in the same row | **$10.026469**, of which `pods` **$7.2339** |

**Three readings of one step, and they disagree on purpose.** The contract asks for each to be named,
and naming them is the point:

| reading | for this step | what it prices |
|---|---:|---|
| the pod's own clock | **$0.4448** | 1 152.0 s × $1.39/h — the leg, and the only one that does |
| the balance delta at the close | **$0.4461** | 0.29% over the clock — the ACCOUNT, at a moment |
| the balance delta 15 minutes later | **$0.4656** | the same account, still growing at the two volumes' rate |
| the **walk**, `billing_since_usd` | **$0.0000** | `pods` reads $7.2339 before AND after — the pod is not in it yet |

The walk's silence is the registered behaviour and not a defect: Dv504/658/678 put the billing walk
**30–40 minutes** behind, and this pod died 15 minutes before the reading. Its total moved
$10.0070 → $10.0265 across the whole session, and every cent of that is `network-volume`
($2.4014 → $2.4208) — the two volumes' rent, which runs whether or not a pod exists. **A balance
delta prices the account and never the leg** ([[a_balance_delta_is_not_a_per_leg_cost]],
[[a_step_meter_on_a_balance_delta_never_stops]]): $0.4461 and $0.4656 are the same step read fifteen
minutes apart, and the difference is rent.

**This step has no separate step ledger and did not need one.** `runpod_guard.py --step` anchors a
sub-cap in its own file; this session's cap is enforced by the projection rung, and the close is
logged as a stamped row in `results/spend_cycle2.json` (`2026-08-26T09:14:45+00:00`) like every other
session's. The row carries BOTH readings — `balance_delta_usd` **$10.4921** and `billing_since_usd`
**$10.026469** — so the walk is a file and not a sentence, and the checker selects the row by its
stamp rather than by its position ([[select_one_row_refuse_ambiguity]]).

The 0.29% agreement is worth recording beside that debt for a second reason: the guard's 7% band
grades a $0.44 step comfortably, and the two records that cannot close under it lag by an ABSOLUTE
~3 cents on steps of $0.76 and $0.075 ([[a_relative_band_cannot_grade_a_cheap_step]]).

**Beside the step, not inside it: the two volumes.** 100 GB each at ~$0.07/GB/month is
**~$0.4667/day** for the pair, about **20.4 days** of what cycle 2 has left. `mp-lora-c` now also
holds this session's `/workspace/r3` — the smoke's 6-step adapter (489 868 882 bytes), its loss log
and its provenance.

---

## 5. What the free readings said that the plan could not have known

**48 GB is CLOSED, and it cost $0.44 to close.** The smoke's peak allocation was **49.54 GiB**, and
`nvidia-smi` read **57 297 MiB in use at 100% utilisation and 304.72 W** while it ran. A 48 GB card
has less total memory than this run allocates at its peak, so all three cheap alternatives in the
migration's stock table — every one of them 48 GB — are refuted by measurement rather than by
argument. `docs/STATUS.md`'s blocker «48 GB на 3 072 не мерил никто» has an answer.

**A model load is not a constant.** Three readings of the same weights off the same volume through
the same shipped loader:

| seconds | when | why they differ |
|---:|---|---|
| 40.22 | migrate r2, 2026-08-26 | the volume had just been written — page cache warm |
| **138.49** | this pod, first load | cold: nothing of 62.58 GB was in any cache |
| **13** | this pod, the smoke's own load, minutes later | the same 62.58 GB, now cached — the loader's own truncated seconds |

A **10.7×** spread inside ONE pod. The registered fixed part charged 60 s for one load and the full plan
needs nine of them; the cold/warm split is what makes that not matter, and it was not derived
([[a_rate_is_a_property_of_the_pod]]).

**Rung 2 came within 152 s of KILLing a healthy run, by construction.** A training stage prints
nothing until step `log_every`, so at 89.9 s/step the smoke was silent for **448 s** between the
setup line and the step-5 line, against a 600 s deadline. Nothing grew: no out-file, no adapter, no
byte. The signal that WAS available — `nvidia-smi` reading 100% and 304 W, and the process's own
state — is not one this registration lists. The rung did not fire and it was never bent; the remedy
belongs to the next contract ([[no_rung_watches_an_idle_pod]]).

**The gate this session inherited would have said GO.** `gate_lora_b.measured_step` takes
`max(mean, last)` of the loss lines' `seconds_per_step`, and on this session's real log that is
`max((89.938 + 17.441)/2, 17.441)` = **53.690**. Carried into the projection:

| | seconds | usd | verdict |
|---|---:|---:|---|
| the sibling's number, 53.690 s/step | 16 061.7 | 6.1104 | **GO** |
| the loop's own number, 89.961 s/step | 21 284.8 | 8.1271 | **KILL** |

A 40.3% understatement, landing on the wrong side of both bounds. The session would have trained
into the platform's terminate flag at 18 000 s and delivered nothing, for $6.95 — and the frozen
registration's one attempt would have gone with it.

**Ten threads, not fifteen.** Rebuilt from base v3's own out-file at $0 before the create, the
pass-2 pack held **10 of 16 reference threads and 43 rows**; r2's v2 leg held 11. Registered as a
report-only expectation beside the charged bound, and it did not change the verdict.

---

## 6. What is NOT spent, and what is on the volume

| | |
|---|---|
| the frozen registration `results/prereg_lora_c.json` | `4d5a8f1d34765b4a…`, asserted at every gate, **unmoved** |
| its ONE attempt (rung 8) | **UNSPENT** — no adapter leg generated a reply against E |
| optimizer steps bought | **6**, all of them the smoke's |
| adapters trained | **0** for either arm; the smoke's 6-step adapter is not one |
| eval calls, scored replies, bars | **0 · 0 · 0** |
| the base columns | r2's, re-read only; **not re-bought** |
| `mp-srv2` | listed before and after, never mounted, never written |
| `make fmt` | not run; both drifted files still pinned |

---

## 7. The numeric audit

| claim | reading |
|---|---|
| pods alive at any moment | **1** |
| gates appended to `results/lora_c_run_r3.json` | **6** — open · gate0 · load-proof · smoke · projection-smoke · close-pod |
| pulled files hashing identically on pod and Mac | **4 of 4** |
| blobs on the volume · blobs that grew across the load | **12 · 0** |
| whole-cache `du -sb` movement across the load | **0 bytes** — the migration's 40-byte bookkeeping had already been written |
| suite, baseline | **3 905 passed / 2 skipped**, `make check-stamped` «reading HOLDS» at `9fd506e` |
| suite, before the create | **3 997 passed / 2 skipped**, «reading HOLDS» at **`dabba2b`** — 3 905 + 92, the count PREDICTED before the reading |
| suite, closing | **NOT TAKEN — the one row on this page no reading backs.** `make check-stamped` was started three times and stopped three times, each time because the tree moved under it, and it refuses by design while the closing session's own files sit in the tree — so it can only be taken AFTER the commit that lands them. Prediction, stated before the reading and **UNCONFIRMED**: 3 999 passed / 2 skipped — 3 997 at `dabba2b` plus the 2 tests added since. `CLOSING_COUNT` / `CLOSING_SKIPPED` / `CLOSING_SHA` are placeholders and stay placeholders until a reading fills them; a prediction is not a verdict ([[gate_verdicts_need_an_artifact]]). **One commit follows that reading** and changes only this row and its checker row: a verify gate measured before the commits that follow it has not measured them, and saying so is cheaper than pretending otherwise ([[the_gates_evidence_outlived_its_artifact]]) |

| file | sha256 (first 16) |
|---|---|
| `results/prereg_lora_c_run_r3.json` | `8da50633d312bcf8` |
| `results/lora_c_run_r3_stock.json` | `37c838273374bfc0` |
| `results/lora_c_run_r3.json` | `7c944527e37ff01e` |
| `results/lora_c_run_r3_load_proof.json` | `1d83811ef43e8473` |
| `results/lora_c_run_r3_smoke_provenance.json` | `84bcd07fa8a89f8a` |
| `results/lora_c_run_r3_smoke_loss.jsonl` | `9529347afdf61ef8` |
| `results/lora_c_run_r3_artifacts/smoke.log` | `9af4d71a4fd6a156` |
| `scripts/gate_lora_c_run_r3.py` | `94b2189cead433ff` |
| `scripts/load_proof_r3_pod_runner.py` | `a5503d322cbdec53` |
| `tests/test_lora_c_run_r3.py` | `f34b7bf7f89f81be` |

---

## Deviations — from Dv837, enum v2

| Dv | cause | what |
|---|---|---|
| **837** | verify-gap | **the shipped smoke gate waits for six loss lines and `log_every: 5` writes two.** `gate_lora_c.smoke_gate` compares `len(seen)` to the registered step count, so a surviving smoke WAITs for ever; r2 never met it because its `--oom` flag short-circuited the count. Registered as Dv813 by the vramprobe report and never fixed. Fixed here, in r3's own gate, and driven both ways at $0 |
| **838** | verify-gap | **and it would have graded the wrong number.** `gate_lora_b.measured_step` reads the loss lines, whose `seconds_per_step` divides by `log_every` regardless of the window — on this session's own log it returns **53.690** against a loop that ran at **89.961**. That is under the 68.05 s/step the cap affords, so the projection would have said GO and the session would have burned $6.95 into the terminate flag with nothing to show. Registered as Dv814 and, like 813, never fixed. The remedy is `provenance.json::run.seconds_per_step` and the decomposition beside it |
| **839** | contract-gap | **«rung 5» names two different rungs.** D1's table makes rung 5 the projection; D2.3 says «load through the shipped loader → rung 5 (blob invariant)», which is the MIGRATION's numbering. Registered by NAME here (`the_load_proof`) so one integer does not carry two thresholds |
| **840** | verify-gap | **rung 2 has no liveness signal for a training stage's first window.** The registered signals are a log line or a byte-growth poll, and a training stage produces neither until step `log_every` — 448 s of silence here against a 600 s deadline, on a run reading 100% GPU and 304 W. The rung did not fire and was not bent; the next contract needs the GPU or process reading registered as a signal |
| **841** | contract-gap | **the fixed part charges ONE load at 60 s and the plan needs nine.** Every stage — smoke, two arms, two pass-1 evals, two pass-2 legs, the census — loads the model. The cold/warm split (138.49 s then 13 s) makes the omission harmless in the end, but it was an omission and not a derivation |
| **842** | tooling | **a model load is not a constant: 40.22 / 138.49 / 13 s**, same weights, same volume, same loader, and the last two inside one pod. Any plan that charges a load charges a distribution |
| **843** | tooling | **`nohup … &` over ssh does not release the channel.** The local ssh was killed at 120 s; the remote training survived, as `nohup` and the redirect promise, but the launch command must not be treated as a fast one. Confirmed by PID before anything was concluded from the silence |

`[cause: contract-gap 2 · verify-gap 3 · tooling 2]` — **seven rows**.

---

## What the operator is being asked

**Nothing is asked about the bars: no bar was scoreable and the attempt is intact.** What is asked
is the price of the same plan now that its one unknown is measured.

1. **The plan as written needs about $8.25 all-in on this card** ($8.2183 projected at charged
   rates). That is a cap, and a cap is the operator's word before an endpoint exists.
2. **Arm A alone fits the current $7.00 with room** — $4.0339 — and answers the ablation's first
   half. It leaves arm B, and with it every real `молочный_бренд` positive this line has, unmeasured.
3. **Both arms at one epoch fit** — $5.7174 — but `epochs: 2` is frozen law in `config/qlora.yaml`
   and changing it makes the arms a different instrument from the one the registration prices.

Cheaper hardware is not on the menu: 48 GB is closed by this session's own 49.54 GiB peak, and the
$1.19 community row for this card is a different cloud type from the SECURE datacenter the volume
lives in.

---

## Process signals

**A gate written at $0 four hours before the create is what stood between this session and a silent
$6.95.** The defect was not exotic: the trainer divides a window's wall by `log_every` whether or not
the window held `log_every` steps, and it is written down twice in this repo's own Deviation ledger.
Reading the producer beat trusting the sibling.

**Registering the decomposition BEFORE the smoke landed is what made the KILL readable.** «The rate
is inflated by start-up» is a plausible sentence in either direction; 16.6 s of 539.8 is not.
Derived after the verdict it would have been post-hoc.

**Every corner of the unknowns was priced before the create, and that is why the KILL took one
reading rather than an argument.** The break-even table said 62.15 s/step at the charge and 68.89 at
the $0 thread reading. 89.961 clears both, so nothing had to be re-litigated on a meter.

**The cheapest reading of the session was the most decisive.** `nvidia-smi` during the smoke closed
a registered blocker — 48 GB — that two paid sessions had left open, and it cost nothing beyond
looking.

**A KILL is compliance, and it should read like one.** $0.4448 spent, one attempt intact, one
measurement bought that no amount of $0 work could have produced, and a plan that now has a price.

# lora-b-run — D3a tightened the run at $0, and rung 1 stopped it before any endpoint

**Status: the ONE attempt is NOT spent. $0.0000 of the $6.00 cap. No pod was created — the
platform refused the create for the registered card, and the refusal is quoted below.**

D3a is executed and committed. D3 stopped at its first rung: the card every measured constant in
`results/prereg_lora_b.json` was measured on is out of stock in the one datacenter the network
volume pins, and the only 48 GB-class cards obtainable there price above the kill-clock's ceiling.
D4 has no reading to grade and does not run.

| step | outcome | commit |
|---|---|---|
| D3a — five tightenings, $0, before any pod | done | `39f5e32` |
| D4's scorer, built before the money | done | `5bd2fc9` |
| money anchor, before the pod exists | done | `03c486d` `26fc9a2` |
| D3 — the ONE paid session | **STOP at rung 1, no endpoint** | — |
| D4 — the verdict | not reached: no reading exists | — |

`make check` after every commit: ruff clean, **3 169 passed / 2 skipped** (3 118 / 2 before D3a).

---

## 1. D3a — the mask boundary, and the +1 that closes the straddle

`learn_chars` now runs one character past the `subject_type` value, through the separator that
closes it.

**The mechanism, and where the brief's prose is one character off its own number.** The brief says
the boundary should reach "THROUGH the closing quote of the `subject_type` value (+1 char), so a
value-final token merged with `"` can no longer straddle out of supervision". The boundary already
reached through the closing quote: `target_for` built the head as `json.dumps({msg_id,
subject_type})[:-1]`, which strips only the object's closing brace. A token merging the value's last
character with the quote (`к"`) ENDS exactly on the old boundary and was already supervised.

What actually straddled is the merge on the other side: `",`. `train_qlora.encode_pass1` masks on
token **END** offsets — `labels = [token if end <= learn else -100 …]` — so a token spanning the
closing quote and the comma ends at `learn + 1`, is masked, and takes the quote (and on a wider
merge the value's own tail) out of the loss. On the one field the gate scores. The brief's **number
is right and its sentence is one character off**; the tightening is implemented as +1, which is what
closes the real straddle.

**Asserted in both directions.** Old and new datasets, row by row:

```
arm a: 500 rows · row order preserved True
  keys that moved: {'learn_chars': 500}
  learn_chars deltas: {1: 500}
arm b: 650 rows · row order preserved True
  keys that moved: {'learn_chars': 650}
  learn_chars deltas: {1: 650}

BOTH DIRECTIONS: learn_chars +1 on every row, and nothing else moved.
```

Targets and prompts are byte-identical, so token counts, distributions, steps, the length bound and
all fourteen pre-existing H6 rows could not move — and did not.

**The guard was TIGHTENED, not relaxed.** `load_sft` demanded only that the supervised head END at
the label, which every boundary at or before the label satisfies. It now demands the head end at
`label + separator`, so the boundary this run REPLACED is a refusal:
`test_load_sft_refuses_the_boundary_this_run_replaced`. Without that, a regenerated dataset could
ship the old boundary and nothing in the suite would say which of the two was trained
([[a-moved-constant-fails-green]]).

**The straddle test flipped meaning rather than being made green.** The same `MergingTokenizer`, the
same row, two boundaries — the assertion is the difference between them:

```python
kept = supervised_text(MergingTokenizer(merge_at), row)          # this run's boundary
assert kept.endswith('"сеть_ритейлер",')

eroded = supervised_text(MergingTokenizer(merge_at), {**row, "learn_chars": merge_at})
assert eroded.endswith("сеть_ритейлер")                          # the boundary it replaced
assert not eroded.endswith('сеть_ритейлер"')                     # the quote is gone from the loss
```

The rule still errs toward supervising LESS: a merge that starts ON the separator still reaches past
the boundary and is dropped — it just can no longer take the value with it.

## 2. The clock is cumulative, and the flag that enforces it is said twice

Rung 7: **5.5 h ≈ $4.40 across ALL pods of the attempt**, and it sits under the $6.00 cap it
defends — the reader-topup lesson, that a hard stop above its own cap defends nothing. Each pod's
`--terminate-after` is that pod's own create plus the stop LESS what every closed pod already
billed.

The failure this is written against is not arithmetic, it is enforcement: **rung 7 is held by a
platform flag `gate_lora_b.py` cannot read back**. Computing the right stamp after the pod exists and
never comparing it to the one the platform got is a guard built and then bypassed. So `--open` takes
the stamp actually handed to `pod create` as a **required argument** and refuses a window longer than
the cumulative stop allows ([[the-guard-you-built-and-then-bypassed]]). Rounding the window down is
always accepted; only overshoot is bounded, at 60 s of clock slop.

`test_a_second_pods_backstop_is_the_hard_stop_LESS_what_the_first_one_billed` states it as a sum:

```python
assert 3600 + window.total_seconds() == stop     # two windows can never exceed the stop
```

and `test_a_backstop_longer_than_the_cumulative_stop_allows_is_REFUSED` gives a second pod a fresh
5.5 h window and gets a refusal.

## 3. The projection gate — two deviations from the contract's letter, both load-bearing

The contract's letter: `elapsed + steps_remaining × measured + (arm B's fitted 5 005.9 s if not yet
trained) + eval 660.7 s` against `$6.00 at the live price`. Registered here with two tightenings,
both strictly safer and both **necessary for the rung to do the job the contract gives it**:

1. **arm B's leg is priced at the rate the pod is actually running** — the larger of the fitted
   5 005.9 s and 82 steps × the measured s/step. A run at 100 s/step would otherwise under-project
   arm B by 40%.
2. **the projection is measured against the cumulative hard stop as well as the cap.** A projection
   above the stop projects a run the platform backstop cuts mid-arm — and there is no mid-arm
   checkpoint (`save_every` 100 against arms of 64 and 82 steps), so that cut loses the arm whole.
3. the registered 0.5 h of overhead is charged in the projection as well as in the worst case.

The record publishes the arithmetic that justifies them, at a step of arm A:

| s/step | reading | projected | verdict |
|---|---|---|---|
| 61.047 (measured) | this run's own registration | 3.2843 h · **$2.6275** | GO |
| 121.0 | **by the contract's letter** — fitted arm B, no overhead, cap only | 3.85 h | **GO** |
| 121.0 | with both tightenings | 5.7157 h · $4.5726 | **KILL** |

121 s/step never trips the 122 s watchdog. It is exactly the compliant-slow path the brief names,
and by the letter alone it clears the projection gate too. The measured row landing on **$2.6275** —
the registration's own `worst_case_usd`, to four decimals — is the cross-check that the gate's
arithmetic and the registration's are one arithmetic.

Expect rung 8 to fire before rung 4 in steady state: the projection KILLs around ~116 s/step and the
watchdog sits at 122. That is the design, not a defect.

## 4. The re-creation budget check, and three honest worst cases

| case | seconds | at $0.80/h |
|---|---|---|
| no incident | 11 823.6 | **$2.6275** |
| sanctioned re-creation (boot + A + B wasted + boot + B + eval) | 15 479.5 | **$3.4399** |
| the same, with the registered 0.5 h overhead | 17 279.5 | **$3.8399** |
| cumulative hard stop | 19 800 | **$4.40** |
| cap | — | $6.00 |

The brief's own enumeration for the re-creation carries no overhead while the no-incident case does,
so the comparable figure is published beside it rather than left as an apples-to-oranges $3.44. The
producer **refuses to build** if the stop stops sitting under the cap, if the sanctioned re-creation
with its overhead stops fitting inside the stop, or if the stop rises above the 7.5 h session
ceiling — three inequalities that two clauses could otherwise contradict each other on.

Rung 9 itself prices the ONE allowed re-creation at MEASURED rates before it exists, and refuses on
either bound. `test_the_recreation_prices_the_remaining_at_the_MEASURED_rate` shows the case a
per-pod budget cannot see: at 110 s/step a full restart is inside the cap on its own and over the
cumulative stop once an hour has been billed — **refused by the clock, not by the dollars**.

## 5. The format smoke, and when the attempt is SPENT

`results/lora_b_smoke_pack.json` — ONE training request, `@VARUS_channel:10349#20651`, built by the
same function that rendered the dataset row so the smoke checks the format the arm was trained on
and not a second spelling of it. Its `instruments` and `serving` blocks are READ out of probe-b's
own eval pack, so the smoke and the eval are one transport.

It is a transport-format check and **not a bar peek**, and that claim is asserted twice — by the
producer that builds the pack and by the gate that reads it:

```
eval pack items 64 · gold 14
arm A ∩ eval pack: []   arm B ∩ eval pack: []   arm A ∩ gold: []
```

Head-only supervision can in principle un-teach the four-key shape; this rung makes that a cheap
KILL instead of an invisible zero at the bar. Each arm smokes into its OWN out-file — never an arm's
eval file, because the shipped runner's resume skips every unit already answered (Dv560).

**The attempt is SPENT at the first GOLD-row reply generated** — not at `pod create`, not at a
training loss, and not at the smoke. That sentence is now in the record's `attempt` field, and it is
what makes today's outcome reportable as "not spent".

The whole rung was driven end to end at $0: the pack, through the real `pass1_pod_runner` on a fake
client, into `gate_lora_b --smoke`, which returns GO — and KILL on an unbalanced reply, a
short object, a wrong `msg_id` echo and a request sha that is not the pack's.

## 6. The enumerated prereg diff, asserted in both directions

```
=== BYTE-IDENTICAL, both directions (the brief's own list) ===
  IDENTICAL  bars                              1813 bytes  sha d09a218755fcfe8c…
  IDENTICAL  population.gold                    867 bytes  sha 7ea44e314234b403…
  IDENTICAL  instruments.prompt_sha256           92 bytes  sha 3b090ba62887bdf7…
  IDENTICAL  money.cap_usd_all_in                 3 bytes  sha 8ab31b5afaea5611…
  IDENTICAL  return_to_sitting                  326 bytes  sha 60bb9cabbebc78ae…

=== kill_clock: rungs GAINED only ===
  the contract's 6 rungs byte-identical; 10 now, gained [7, 8, 9, 10] (all tagged added=D3a)

=== every other moved key, enumerated ===
  MOVED arms.a.dataset.sha256          MOVED arms.b.dataset.sha256
  MOVED attempt                        MOVED frozen_when_the_pod_exists
  MOVED h6.rows                        MOVED instruments.sft_record.sha256
  ADDED instruments.smoke_pack         MOVED instruments.trainer.sha256
  ADDED money.arithmetic.cumulative    MOVED producer.borrowed…/pass1_sft.json
  MOVED producer.sha256                ADDED tightened_at_d3a
  ADDED training.supervision.boundary_char
  MOVED training.supervision.learn_chars

=== list gains, and the unmoved neighbours ===
  frozen_when_the_pod_exists 9 -> 10  gained ['results/lora_b_smoke_pack.json']
  h6.rows 14 -> 17  gained [cumulative_hard_stop_hours, cumulative_hard_stop_usd,
                            recreation_worst_case_usd]; every old row byte-identical;
                    mismatches none
  money.arithmetic 14 keys unmoved, gained ['cumulative']
  IDENTICAL: reachability · population · ablation · authority · contract · phase ·
             dropped_for_length · both sampler_weights
```

The tripwire held: `reachability` and every pre-existing H6 row are byte-identical, which is what
says the boundary moved and the arithmetic did not.

## 7. D4's scorer, built before the money rather than after it

The registration names `scripts/score_pass1_probe.py through score_lora_b's file swap` as the judge
of the bar, and **that file did not exist** — a registered bar with no producer
([[a-registered-bar-may-have-no-producer]]). It is $0, so it is built now and driven on fabricated
arms rather than first exercised on evidence that cost a session.

Nothing about the bar is new: `bar_p1` is called once per arm with lora-b's own registration, and
`read_pass1_probe.ingest` parses each arm's replies with its EVIDENCE constant swapped for the arm's.
This file's own are the arm rule — `max(gold14(A), gold14(B)) ≥ 12`, one attempt, tie ships arm B,
every clause read out of the record — and the ablation, PAIRED per row against the base's sealed
verdict, refused if that file is not the one the registration pinned.

Two refusals carry the money:

* **an arm with no replies is `not_evaluated`, never 0 of 14.** A zero reads a year later as "the
  adapter answered and was wrong" when the truth is a milestone STOP or a smoke KILL.
* **the scorer reads `results/lora_b_run.json` and REFUSES to score while an arm whose format smoke
  went GO has no replies on this machine.** "NO READING — the attempt is NOT spent" must never
  become the report of a session that spent it ([[a-checker-whose-failure-is-silence]]). The
  runbook's scp, the on-pod file name in `arms.*.eval_command` and this module's paths are asserted
  as one chain in the suite, because two of the three are not code.

---

## 8. D3 — STOP at rung 1, and the evidence for it

`scripts/runbook_lora_b.md` §0 ran clean. Three listings as the before-state, with the volume as the
positive control that the listing works at all:

```
runpodctl pod list -a          → []
runpodctl serverless list      → []
runpodctl network-volume list  → [{"dataCenterId":"EU-RO-1","id":"qw4nwleanc","name":"mp-srv2","size":100}]
git status --porcelain         → (empty)
gate_lora_b.py --pre-create-check
  → no pod is open · 0 closed, 0 s = $0.0000 billed · the hard stop leaves 19800 s
    for the next pod's --terminate-after                                       exit=0
```

The money anchor was taken and committed **before** the create, as the git clock requires:

```
LORA-B SPENT      $0.0000 of $6.00  (anchor $19.08 from runpod_balance_at_lora-b_start)
CYCLE 2 SPENT     $3.4268 of $20.00        REMAINING  $16.5732
```

**The create was refused by the platform.** This is the evidence, not the listing:

```
runpodctl pod create --name mp-lora-b --gpu-id 'NVIDIA RTX A6000' --gpu-count 1 \
  --network-volume-id qw4nwleanc --data-center-ids EU-RO-1 --cloud-type SECURE \
  --image runpod/pytorch:1.0.2-cu1281-torch280-ubuntu2404 --container-disk-in-gb 30 \
  --ports '22/tcp' --ssh --terminate-after '2026-08-20T15:30:57Z'

{"error":"failed to create pod: graphql error: There are no longer any instances available
 with the requested specifications. Please refresh and try again.","code":"graphql_error"}

runpodctl pod list -a → []
```

A refused create bills nothing and creates nothing; both are shown rather than assumed. The
`--terminate-after` handed to it was `now + 19 800 − 600` s — the cumulative window rounded DOWN, so
it could not overshoot whatever the create took.

### What EU-RO-1 actually has

The network volume `qw4nwleanc` pins the datacenter — `money.meter.datacenter`: "EU-RO-1, pinned by
network volume qw4nwleanc — **the volume decides**". Without it the boot is a 59 GB weights download
this registration did not price.

Two readings, twenty minutes apart, because the board moves — the second is the later one:

| card | memory | secure $/h | EU-RO-1 stock | reading |
|---|---|---|---|---|
| **RTX A6000** | 48 GB | **0.53** | **none** | the registration's own card — unobtainable |
| A40 | 48 GB | 0.44 | not in this DC | — |
| L40S | 48 GB | 0.99 | not in this DC | and above the ceiling anyway |
| **A100 80GB PCIe** | 80 GB | **1.39** | Low → **none** | **> $0.80/h → rung 1 STOP**, and it left the board while this was being written |
| RTX PRO 6000 Blackwell | 96 GB | 1.89 / 2.09 | Low | the ONLY obtainable card in this DC that can hold the run |
| MI300X | 192 GB | 2.39 | Low | AMD — NF4 through bitsandbytes is a different stack, unmeasured here |
| RTX PRO 4500 | 32 GB | 0.72 | High | under the ceiling, **too small: measured peak 35.13 GB** |
| RTX 4090 | 24 GB | 0.74 | Low | not A6000-class |

Rung 1 reads: *"live A6000-class price > $0.80/h at create → STOP, no endpoint."* In the one
datacenter this attempt can use, 48 GB-class silicon trades at $1.39/h. The rung is satisfied and
its verdict is STOP.

**The memory floor this run needs is measured, and it excludes every card under 48 GB.**
`results/train/45h2-arm-b/provenance.json` records `gpu_gb_peak` **35.13 GB** for the same base at
the same `max_seq_len` on a 49 140 MiB A6000. So the obtainable set in EU-RO-1 is not "cards under
$0.80/h" — it is "cards of 48 GB or more", and every one of those is above the ceiling.

Thirty-six readings of the stock over twenty minutes, every one `none`, before the create was
attempted and after. The A6000 does exist in **EU-SE-1** at Low stock — a different datacenter, with
no volume and no warm `/workspace/hf`.

### Why the available card was not substituted

`RTX PRO 4500` is under the price ceiling and in High stock, and it is **not what this registration
measured**:

* **61.047 s/step** is the A6000's, at seq 1408 / micro 2 × accum 8. Every downstream number rests
  on it: the watchdog is `2 × measured`, the projection gate prices the remaining steps and arm B's
  whole leg at it, and `worst_case_usd = $2.6275` is 146 steps of it. On another card the s/step is
  unmeasured, so **rung 4 and rung 8 lose their anchor** and the run would proceed with two kill
  rules whose thresholds mean nothing ([[the-smokes-rate-carries-the-smokes-transport]]).
* **32 GB is MEASURED to be too small, not argued to be.** `results/train/45h2-arm-b/provenance.json`
  is this exact stack — `google/gemma-4-31b-it` @ `842da379…`, NF4 double-quant, `max_seq_len` 1408,
  micro 2 × accum 8 — on an `NVIDIA RTX A6000` of 49 140 MiB, and its `gpu_gb_peak` is **35.13 GB**.
  That is over the RTX PRO 4500's 32 GB and over every 24 GB card in the datacenter. The same record
  reports **62.582 s/step**, which is where the registered 61.047 comes from, so the two facts are
  one measurement. `config/qlora.yaml` is frozen law and `max_seq_len` may not be lowered to
  compensate; and the trainer's own OOM handler halves `micro_batch` and doubles `grad_accum`, which
  holds the effective batch but changes the step time — so even a SURVIVED OOM invalidates the
  s/step the whole projection rests on ([[benchmark-the-accelerator]]).
* **an OOM would cost the arm whole.** `save_every` is 100 against arms of 64 and 82 steps, so
  `step % save_every` never fires and the only adapter written is the one after the loop. The
  recovery clause allows exactly one re-creation.

Substituting the card is therefore not a smaller version of this run; it is a different, unregistered
one. It is the operator's ruling to make **before** an endpoint exists, not the executor's after.

### The state this leaves

* **The ONE attempt is NOT spent.** No gold row was answered. No eval output was seen. Nothing was
  trained. `$0.0000` of the `$6.00` cap; cycle 2 stands at `$3.4268 of $20.00`.
* **Everything the paid session consumes is committed and green**: both datasets at the tightened
  boundary, the registration with rungs 7–10, the smoke pack, the runbook, `gate_lora_b.py`,
  `score_lora_b.py`, and the anchor.
* Both arms were assembled at $0 through the trainer's own `--build-only` on the exact commands the
  pod would run: 500 and 650 rows, the new `boundary_char` in the provenance, `train_sha256`
  `66b9dca9…` and `7b9aa9bd…`.
* The staging bundle is built and the five staged files exist, so a create that succeeds later goes
  straight to §2 of the runbook.

### The ruling this needs

The operator's answer of 2026-08-20 is **wait for the A6000**: the registration then executes exactly
as written, at $0 while waiting, and the attempt stays unspent if the card does not return today. A
free stock watch is running against EU-RO-1.

If it does not return, the choice is a ruling and not an executor's call:

| option | price | what it costs the registration |
|---|---|---|
| **wait** (chosen) | $0 | nothing — the run is the registered run |
| A100 80GB, $1.39/h | needs the ceiling raised BEFORE any endpoint | faster card, so possibly cheaper in absolute dollars, but `s/step` is unmeasured — rungs 4 and 8 need re-registering first. **And it went out of stock in EU-RO-1 while this was written** |
| RTX PRO 4500 32 GB, $0.72/h | inside the cap | **excluded by measurement** — this stack peaked at 35.13 GB on the A6000 |
| RTX PRO 6000 96 GB, $1.89–2.09/h | needs the ceiling raised BEFORE any endpoint | the only card obtainable in EU-RO-1 that can hold the run at all; s/step unmeasured |
| return to the sitting | $0 | line B stays open and unmeasured |

---

## Process — five lines

1. **contract-gap** — the registration pinned a datacenter through its volume and a card class
   through its constants, and pre-registered a rung for the card's PRICE. It did not pre-register
   what to do when that card is not *obtainable* there at all. The rung still answers — the
   obtainable 48 GB silicon is above the ceiling — but by arithmetic rather than by design.
   [[a-registered-bar-may-have-no-producer]]
2. **verify-gap** — the brief's own mechanism for the mask boundary was one character off its own
   number: it named the merge that was already supervised, not the one that straddled. Reading the
   producer instead of the prose is what found it, and the number it asked for was right.
   [[trace-the-producer-not-the-result]]
3. **verify-gap** — `load_sft` accepted every boundary at or before the label, so moving the
   boundary would have gone green in both positions. A guard that cannot see the move it is guarding
   is not a guard. [[a-moved-constant-fails-green]]
4. **contract-gap** — the projection gate as the brief writes it does not close the compliant-slow
   path the brief says it exists for: at 121 s/step the letter says GO. Two strictly-safer additions
   close it, and they are registered with the arithmetic that makes them necessary rather than
   applied quietly. [[an-absolute-bar-needs-a-reachability-state]]
5. **process** — rung 7 is enforced by a platform flag no local instrument can read back, and the
   first draft recomputed the correct stamp after the pod existed without ever comparing it. Making
   the caller SAY the value is what turned a recomputation into a check.
   [[the-guard-you-built-and-then-bypassed]]

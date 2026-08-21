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
   two spans this stack has MEASURED already exceed the ceiling by themselves — ssh 231.9 + boot
   237.155 = **469.1 s** against 450, before a byte is staged — killed by the loop, with no human in
   the path. *(Corrected at acceptance: the first version added probe-b's 89.5 s on top and read
   558.6 s, double-counting the ssh wait that 89.5 already contains.)* The re-registration needs rung 3
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

---

## r2 — the re-registration, 2026-08-21 (D0′ committed before any pod)

The operator's ruling of 21.08: **re-register; the STEP's budget stays $1.50 all-in.** r1's two pods
already bought $0.117783 of it, so r2's cap is **$1.38** and the step sum is $1.497783.
`results/prereg_pass1_fewshot_r2.json` is the new law, `docs/PROMPT-pass1-fewshot-r2.md` the
contract, `docs/reports/pass1-fewshot-r2.md` the report. **r1 is sealed and never re-opened** — the
file on disk is still byte for byte `c7cbfd1`, and a test asserts it against the commit.

**What moved, and only this.** The question, the bars, the packs, the prompt, the holdout, the dev
gate, the attempt and its multiplicity are COPIED out of r1's committed record, so «byte-identical»
is true by construction; every pin inside them is re-checked against the live file it names and a
divergence stops the producer. Two declared exceptions: `instruments.gate.sha256` (the one
instrument r2 amends, so r1's pin is «moved since» and is not re-pinned) and the new
`instruments.scorer_pass1_fewshot`, which is consequence 6 above, closed.

1. **Rung 2 — 500 s of create-elapsed, and it is a SPREAD.** probe-b saw ssh at 14.5 s on this card
   in this datacenter on 18.08; both pods of 20.08 were still `pod not ready` at 262.5 s and 231.9 s,
   and both are LOWER bounds because ssh was never observed up. The two readings are taken out of
   r1's own gate record, never typed. **500 and not 600** because the recovery clause must stay
   REACHABLE: at 600 the worst case itself grows to 5 576.552 s, so one dead pod plus it is
   6 176.552 s — past the 6 100 s hard stop. The dollars would still fit; the seconds do not, and the
   platform holds seconds. That counterfactual is a registered H6 row, not a sentence.
2. **Rung 3 — the ceiling did not move, its ANCHOR did.** 450 s is now measured from `launched_at`,
   a stamp the POD writes into its run directory in the same command that execs the runner and
   `--watch` copies back; the gate writes it into the pod's entry once and never moves it forward. A
   create-anchored **backstop of 1 100 s** (ssh 500 + stage/launch 150 + load 450) sits beside it and
   is what bounds a late stamp. Consequence 4 above, closed. A run record without the anchor cannot
   report GO on this rung.
3. **The money is re-derived, not re-quoted.** 5 476.552 s = 1.5213 h → worst $1.2170 at the $0.80/h
   ceiling; hard stop 6 100 s = $1.3556 < $1.38; overhead 1 300 s because ssh and staging now have
   their own lines, and H6 checks that the 650 s those lines add covers the 500 s the overhead lost.

**Four defects were found by an adversarial review BEFORE the first `pod create`**, and two of them
would have deleted a healthy pod with the attempt unspent:

- **rung 4 was still charging r1's repealed 1 800 s overhead.** `projection_gate` had been copied
  whole from r1, and `projection()` adds that number on every poll of the watch — against a hard stop
  r2 had also lowered from 6 300 to 6 100. On the recovery path the shot's FIRST poll projects
  6 476.6 s / 6 100 and kills. A block copied for its algorithm carried two numbers the amendment
  repealed [[the-old-record-with-one-field-replaced]].
- **the first reply was still being typed on r1's create-anchored recipe.** `create + boot_seconds`
  subtracts the ssh wait and the staging twice under a launch anchor, so a 460 s load reads as 415 s
  and rung 3 reports GO on the condition it was re-anchored to catch — Dv605 with the sign flipped.
  `--boot` takes no stamp now; it reads `elapsed_since_start` off the out-file
  [[a-flag-that-asserts-turns-a-poll-into-a-verdict]].
- **the ssh poll was bounded by an iteration count annotated as seconds.** r1's own record prices a
  turn at 6.65 s — 34 turns took 226 s of wall clock — so 95 turns is ~631 s, past the rung and past
  the 623.448 s at which the ONE re-creation stops fitting. Bounded by the clock now.
- **`--price` did not run the recovery clause** the runbook and the record both said it ran.

Each fix carries a mutation that was watched to go red. `make check` **3 265 / 2** (3 239/2 at step
0). The guard is anchored at `$16.4358` on `2026-08-21T11:36:55Z`, step spend `$0.0000 of $1.38`.

### r2's outcome — the dev gate is RED at +7 of +10, and the attempt is still intact

One RTX 4090 in EU-RO-1, **1 359.0 s = $0.27935** of the $1.38 cap, six gates over one pod, deletion
proven by three listings with the volume as the positive control. **Every rung passed except the one
that measures the question.** `our_v2 − our_base = +7` against the registered `+10`; the second
inequality passed by a mile (`+49` against `−5`); the base answered 31 of the 49 «our» rows, under
the 39 above which the delta would have been unreachable — so this is a **RED and not a STOP**, a
reading of the prompt rather than of the bar. **No gold row was answered. The ONE attempt is NOT
spent** and `results/pass1_probe_b_pack_v2.json` is unanswered.

**The finding, and it is not «v2 is worse».** v2 lifts overall agreement 87 → 136 of 200, and buys
almost all of it on `не_наш_рынок` (12 → 46, net +34). The 49 «our» rows move 31 → 38 — **13 fixed
and 7 broken**, so the codebook clause is *not monotone on the class it targets*. Three readings say
what actually happened:

- **the base's error was silence.** 13 of the 14 «our» rows v2 gained were rows the base answered
  `None`. The line was registered against «the base classifies by the mention»; on this dev set the
  base mostly did not classify at all.
- **v2's remaining error on «our» rows runs the OPPOSITE way from the clause.** Five of the seven
  losses are `категория_личное` answered `не_наш_рынок` — told that a retailer named inside a
  personal habit is a category comment, the model pushed the comment out of the market instead.
- **the mention-vs-about class is the one cell v2 did NOT move.** Over the same 200 rows the base
  confused `не_наш_рынок → категория` on 22 rows and v2 on **24** — two MORE — while v2 removed 36 of
  the base's 48 `не_наш_рынок → None` silences and cut the off-diagonal 113 → 64. The clause bought
  answers, not this discrimination.

So the clause is a real and cheap gain on the MARKET boundary and is not, by itself, an answer to
the mention-vs-about confusion. That is what goes to the operator with the table.

**Three environment readings the next registration should price from.** ssh was up **by 50 s** of
create-elapsed — an UPPER bound on a 5 s poll, where 20.08's two are lower bounds, so the publish
landed in (45, 50]. It sits inside the spread rung 2 was registered as (14.5 s … > 262.5 s), and the
500 s ceiling was never approached. The model load was **142.709 s**, a new floor for this stack
(the old range was 146.8 … 353). And **v2's prefill costs +18.9 %, not the +50 %** the bound charged:
2.293 s/call base against 2.726 s/call v2, where the registration charged 5.162 and 7.743. The whole
generation took 1 147 s of a budget that priced 3 076.552.

**Rung 3's new anchor earned itself on the pod.** The v2 leg's first row reads
`elapsed_since_start 2.72` with `boot_seconds 0.009` — the shipped `run()` is called once per leg and
re-zeros its own monotonic clock. A minimum across both legs would have recorded 2.72 s against a
450 s ceiling and reported GO on any load whatever; the gate read the base leg's **145.6 s**. That
defect was found by reading the transport before the create, not after it
[[two-instruments-two-inputs]].

**Money.** Step sum r1 `$0.117783` + r2 `$0.27935` = **$0.397133** of the `$1.50` the ruling left the
step; r2's cap was $1.38 and $1.10065 of it is unspent, and its recovery clause was never used — one
pod, one create. The guard's balance delta reads `$0.2637`, which carries $0.0097 of volume drip from
before the pod existed. Cycle 2: **$6.3377 of $20.00, remaining $13.6623**.

Report `docs/reports/pass1-fewshot-r2.md`; gate record `results/pass1_fewshot_r2_run.json`; verdict
`results/pass1_fewshot_verdict.json`. **Nothing was found on the pod that was not found before it.**

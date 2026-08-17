# reader-v5-run — one pod, both legs, and the stop-rule that ends the line

**Contract:** `docs/PROMPT-reader-v5-run.md` · **baseline claimed:** `make check` 2 777 / 2 skipped
(the team lead's own run, 17.08) · **baseline measured here: 9 failed / 2 768 passed** — see §1.2.

*This section is written BEFORE the pod exists and committed before `pod create`. If the session
dies with a pod open, the read-backs and step 0's evidence are already on disk.*

---

## 0. Read back, one line each

**The one-attempt clause, and what the programme stop-rule does with it.** A kill, a STOP, or a
completed run with a failed bar closes the question — there is no second pass at this registration;
and if the run COMPLETES with bars 1 and 4 not BOTH taken, the prompt-engineering line CLOSES and
the next step is an architecture sitting, never a v6 of the same kind. The rule is pre-registered
inside `results/prereg_reader_probe_v5.json` so it binds the reading of this run's own numbers
instead of being decided after them.

**The leg order and why.** Leg A's 23 whole threads first, complete, then leg B's 3 chunks. Leg A is
the semantic answer three contracts have paid for and leg B is mechanics: a stop inside leg B leaves
leg A complete and its four bars scored, a stop inside leg A leaves leg B unbought and scores
nothing. The pack is built in that order and read back off the built file as
`AAAAAAAAAAAAAAAAAAAAAAABBB`.

**What freezes when the pod exists.** The registration itself, gold r2, the reader cell census, v4's
registration, the `reader_thread_gm4_v5` text, `prompts.py`, `reader_v5.py`, `scorer.py` and
`probe_b_population.py`'s enumeration. Step 0's prose fix is the LAST legal change to any of them,
which is why it is step 0.

**The affordability deadline.** `usable_seconds − reading projection` = 2 129.189 − 1 454.0 =
**675.2 s of create-elapsed** at the registered worked example of $0.74/h, against the twelve-minute
ceiling's 720 s — so affordability binds first, always, on this registration
(`pre_generation_budget_seconds` is −44.785 and that negative sign IS the statement). Re-derived at
the price actually charged in §3.

**The recovery clause.** The partial jsonl is copied back continuously, so a pod that dies mid-run
leaves its answered units on the Mac. Inside the same cap and the same frozen registration a
replacement pod may answer ONLY the units with no persisted reply; answered units are never
re-asked. If the cap cannot buy the remainder — STOP, and that is the gate speaking.

---

## 1. Step 0 — the tail, a baseline that was not green, and one key of prose

### 1.1 The tail, by live `git status` and by path

```
 M docs/STATUS.md
 M knowledge/daily_logs/2026-08-17.md
 M knowledge/hot.md
 M knowledge/index.md
?? docs/PROMPT-reader-v5-run.md
```

- `b9eeeca` — `knowledge/**`, three files, staged by path (the `/save` checkpoint of 14:41).
- `9b32475` — `docs/STATUS.md` and `docs/PROMPT-reader-v5-run.md`, **verbatim**, in their own
  commit. Both are the team lead's; read and committed, never edited.

Never `git add -A`. The untracked prompt was read before staging.

### 1.2 The baseline was not green, and the cause was mine — **Dv469**

`make check` at the tail commit: **9 failed, 2 768 passed, 2 skipped in 373.53s**. Every failure in
`tests/test_volume_calc_5c1.py`, every one off one cause:

```
E           SystemExit: knowledge/hot.md: '~$0.24/day' is not in the file
FAILED tests/test_volume_calc_5c1.py::test_every_input_names_an_artifact_that_exists
... 9 of them
```

`scripts/volume_calc_5c1.py` reads two literals out of `knowledge/hot.md` with `quoted(HOT, …)` —
`~$0.24/day` and `80 GB is about what the` — as PRICED INPUTS, the guard that makes «every input
names its source artifact, no hand-typed numbers» true rather than aspirational. The `/save`
curation of 17.08 shrank hot.md's curated block 44 049 → 24 136 B and took both literals with it,
**together with the footgun note that named them**. The team lead's 2 777 was measured before that
curation, so the contract's baseline outran the tree.

**[cause: a curated vault file is a load-bearing input to a script, and the note saying so was
inside the block being curated.]** `b47e138` restores both literals verbatim under a Footguns
heading of their own; `tests/test_volume_calc_5c1.py` 10 passed.

### 1.3 The one prose fix inside the still-unfrozen registration

`bars.5_time_and_cost.reported_not_gating.finish_reason` was inherited from v4's frozen record word
for word and said «whether the longer v3 output hit the **2 000-token** ceiling» — v4's sentence
inside a 4 000-ceiling instrument. Fixed in the producer, at the `OUTPUT_CEILING` constant rather
than as a typed number.

**Red before green, in that order.** The producer edited alone:

```
$ PYTHONPATH=src python3.11 -m pytest tests/test_reader_prereg_v5.py -q
>       assert out.read_bytes() == RECORD_PATH.read_bytes()
E       assert b'{\n  "attem...ve"\n  }\n}\n' == b'{\n  "attem...ve"\n  }\n}\n'
E         At index 6180 diff: b'u' != b't'
FAILED tests/test_reader_prereg_v5.py::test_the_committed_registration_is_what_the_producer_writes_today
1 failed, 24 passed in 43.89s
```

Then the record REBUILT (never hand-edited) and re-run: **26 passed**. The whole diff of the record
is two lines — the prose key, and the producer's own self-pin:

```
-        "finish_reason": "per thread, … the longer v3 output hit the 2 000-token ceiling. …"
+        "finish_reason": "per unit, … v5's longer output hit the 4000-token ceiling …"
-    "sha256": "67de11f5c990b6ed76f93ac92474e3fa7705d85cec485433ecad152674367ad9"
+    "sha256": "97b3edbe38e0f16f77fc8a74cfe26fad23007cc99d4cd8c9f6583b6fe958e314"
```

`48b6cbde119ec3b1…` → **`8294673c89d4d904…`**. The record's two other mentions of 2 000 are correct
and stay: one is the counterfactual that makes bar m2 unreachable, the other is v4's own history.
The new guard is over the WHOLE record rather than that one key, because the defect was
inheritance — no prose may call 2 000 THE ceiling, and both legitimate mentions are asserted still
present. Negative control: the pre-fix record trips both halves.

Commit `66dc418` carries registration + producer + test together.

### 1.4 The recovery clause had no mechanism — **Dv470**

The contract's own recovery clause allows a replacement pod «to answer ONLY the units with no
persisted reply — answered units are NEVER re-asked». Nothing implemented it: `run()` iterated the
whole pack and opened `--out` in append mode, so a pod created after a mid-run death would have
re-asked all 26 from the top and written a SECOND reply for every unit that already had one. That is
worse than a wasted re-ask — the Mac's projection counts ROWS, so the duplicates would have loosened
the cap gate on a live pod.

**[cause: a clause headed «a caught fault must not strand the attempt» that cannot be executed.]**
`already_answered()` reads the ids the out-file carries and the loop skips them; `index` stays the
position in the PACK; a file carrying a foreign id is REFUSED before the model loads; a file that is
already complete returns without paying for a 59 GB boot. The pack stays whole (26 units, no
registered sha moves) and nothing frozen is touched — the registration pins neither runner.

Three new tests, all three FAIL against the previous runner (`git stash` the runner, run them:
3 failed / 30 deselected) and pass against this one. `4cf51c6`.

---

## 2. D1 — the pack, at its registered path

```
$ PYTHONPATH=src python3.11 scripts/read_threads_reader_v5.py --pack results/reader_v5_pack.json
pack results/reader_v5_pack.json · 26 units, every sha matches the record
  leg A 23 threads · leg B 3 chunks
  task reader_thread_gm4_v5 · parser be5a81641afc2aa5… · ceiling 4000 output tokens
```

Read back off the built FILE, not off the builder:

```
units: 26
first: @VARUS_channel:10348 | last: @klopotenkofood:6040#3of3
legs in order: AAAAAAAAAAAAAAAAAAAAAAABBB
leg B ids: ['@klopotenkofood:6040#1of3', '#2of3', '#3of3']
payable A: 134 | payable B: 43
ceiling: 4000 | tasks pinned: [reader_thread_gm4, _v2, _v3, _v5]
16a24d0cd436af0b2a871cc1cac89c0db6fe01e00bf35b237ad81fc3cdf7aee1  results/reader_v5_pack.json
8294673c89d4d9048204d212a8e8800390c37c630199fd2eecfcc19e6081c198  results/prereg_reader_probe_v5.json
```

Every one of the 26 renderings was hashed here, on the Mac, against the sha the registration pinned
for it — before anything billable exists. The pod holds them to the same 26 shas again before the
model is loaded.

Anchor, before the pod (`9d2398f` carries the pack, the step ledger and the cycle-2 session line):

```
$ python3.11 scripts/runpod_guard.py --step reader-v5 --step-cap 0.45 --note "reader-v5 anchor, before the pod"
CYCLE 2 SPENT     $0.8728 of $20.00
REMAINING         $19.1272
READER-V5 SPENT      $0.0000 of $0.45  (anchor $21.64 from runpod_balance_at_reader-v5_start)
anchored spend_reader_v5.json for reader-v5 — commit it and never regenerate it
```

### 2.1 The gate was solved backwards before create, and it has a knife-edge at unit 2

$0, and it is the number that decides whether this attempt survives its second reply. `projection()`
takes `of = len(pack["items"]) = 26`, so at `read = k` the binding factor is
`max((26 − k)/k, (177 − p)/p)` where `p` is the payable comments read so far. Leg B's 43 payable
comments are in that denominator and were not in v4's.

| after | unit | payable | binding leg | factor | mean s/unit that still fits (elapsed 400 s) |
|---|---|---|---|---|---|
| 1 | `@VARUS_channel:10348` | 7 | `by_unit` | 25.00 | **69.2** |
| 2 | `@VARUS_channel:10360` | 2 (9 read) | `by_payable_comment` | 18.67 | **46.3** |
| 3 | `@VARUS_channel:10366` | 12 (21 read) | `by_unit` | 7.67 | 73.5 |

The crossover is `p = 177/25 = 7.08`, so the first unit clears by_unit by 0.08 of a comment and the
SECOND unit is the knife-edge: a 2-comment thread read early makes the payable leg extrapolate the
remaining 168 comments off 9, and the gate has to be cleared on a mean of two threads.

What the evidence says the mean will be: v4 measured **36.621 s** and **38.975 s** on exactly these
two threads under v3 (`results/reader_v4_w1.jsonl`), a mean of 37.798 s; at the registration's own
output growth of 1.127 that is **42.60 s** against **46.3 s** allowed at 400 s of create-elapsed —
about 9% of margin. The margin is a function of elapsed at the second reply: 47.7 s allowed at 350 s,
46.3 at 400, 45.0 at 450, 43.6 at 500. **Every 100 s of pre-generation and boot costs 2.7 s of the
allowed mean**, which is why staging is timed and not improvised.

Simulated over all 26 units with `driver.projection` itself: at 44.5 s/thread and 107 s/chunk from a
305 s start the run completes GO with 480 s of headroom and the tightest margin anywhere is
**1.98 s/unit, at unit 2**; at leg A's own registered PROJECTION rate of 49.3 s/thread it STOPs at
unit 2. The projection is a pessimistic ceiling and the gate compares MEASURED seconds, so those are
not the same claim — but the distance between them is the whole risk of this run, and it is named
here rather than discovered in a log.

Nothing was done about it. The gate is the registered law (`go_no_go.gates.3_the_full_pass`,
word for word since probe-a), the registration froze at step 0, and re-ordering leg A to put
high-comment threads first would be loosening a cap guard by arrangement. **Dv471** records the
finding, not a change.

---

## 3. D2 — the run: the pod never became reachable, and the boot gate killed it

**Outcome in one line. The pod was created, billed for 727.9 seconds, and never answered `ssh info`
once. No unit was asked, no reply landed, no bar is scored. The boot gate returned KILL on its own
arithmetic at 721.5 s of create-elapsed and the pod was deleted 6 seconds later.**

### 3.1 The transport, written down (the thing v4's report did not carry)

Prepared at $0 BEFORE create, because every minute composing a command on a live pod is billed
(Dv442 is the precedent). None of it ran — the pod was never reachable — and it is recorded here so
the next attempt inherits it instead of rediscovering it.

There is **no git remote** in this repository (`git remote -v` is empty), so staging is a bundle, as
every runbook here does it. `git bundle create /tmp/market-pulse-v5.bundle HEAD` → **8.3 MB** at
`0ec2da6`. The clone goes to a **new** directory: `rm -rf repo` would destroy the gitignored 467 MB
adapter that lives inside `/workspace/repo` (probe-a's report, line 285).

```bash
scp <OPTS> -P <PORT> /tmp/market-pulse-v5.bundle results/reader_v5_pack.json \
    scripts/reader_v5_pod_runner.py scripts/reader_v4_pod_runner.py root@<HOST>:/workspace/
# on the pod
cd /workspace && rm -rf repo-v5 && git clone -q market-pulse-v5.bundle repo-v5
cd repo-v5 && git rev-parse HEAD && git status --short     # == the Mac's HEAD, empty
# detached launch, Dv454's form
ssh <OPTS> -p <PORT> root@<HOST> \
  'cd /workspace && HF_HOME=/workspace/hf nohup /workspace/venv/bin/python -u \
     /workspace/reader_v5_pod_runner.py --pack /workspace/reader_v5_pack.json \
     --out /workspace/reader_v5_pod.jsonl --repo /workspace/repo-v5 \
     </dev/null >/workspace/reader_v5_pod.log 2>&1 & echo launched $!'
ssh <OPTS> -p <PORT> root@<HOST> 'pgrep -af reader_v5_pod_runner.py'
```

**`reader_v4_pod_runner.py` ships too** — the v5 runner imports `check_instrument` from it, and the
copy sitting on the volume from v4's run is the pre-Dv457 one. **`--repo` must be passed
explicitly**: its argparse default is `/workspace/repo`, which is the `aa0ca18` checkout, and a
launch that took the default would have hashed the OLD `prompts.py` and refused with «the parser and
the renderer have parted» — the right refusal for the wrong reason, on a live pod.

### 3.2 The timeline, off the run record and the wall clock

Card: **RTX 4090, RO, `costPerHr` 0.74** — exactly the registered worked example, so
`priced_at_or_under_the_example: true` and no deadline is re-priced. `--terminate-after`
2026-08-17T14:48:12Z (create + 90 min).

| create-elapsed | wall | what | spent at $0.74/h |
|---|---|---|---|
| 0 s | 13:18:13Z | `pod create` — `ivw5z93im4hfnz`, RTX 4090, RO, `costPerHr` 0.74 | $0.0000 |
| 4.7 s | 13:18:17Z | `--open`: gate `open` **WAIT**, 670.5 s left, deadline 675.2 s | $0.0010 |
| 10.6 s | 13:18:23Z | `runpodctl ssh info` → `{"error": "pod not ready", "status": "RUNNING"}` | $0.0022 |
| 163 s · 171 s | | still `pod not ready`; `pod list -a` shows it RUNNING with `costPerHr` 0.74 | $0.0352 |
| 346.6 s | 13:23:59Z | gate `boot_kill` **WAIT**, 328.6 s left | $0.0713 |
| 337 s · 452 s · 559 s | | still `pod not ready` | |
| 559.3 s | 13:27:32Z | gate `boot_kill` **WAIT**, 115.8 s left — a 175 s model load no longer fits | $0.1150 |
| 718 s | | still `pod not ready`, twelfth minute | |
| **721.5 s** | 13:30:14Z | gate `boot_kill` **KILL**, `seconds_left −46.3` | **$0.1483** |
| 726 s | 13:30:19Z | `pod delete` → `{"deleted": true}` | |
| 727.9 s | 13:30:21Z | meter stops | **$0.1496 at the meter** |

**Four gate snapshots, all four in `results/reader_v5_run.json`, none overwritten** — the one lesson
v4's record left behind, and this is the run that needed it: three WAITs and the KILL are the whole
story of this attempt, and v4's scalar would have kept only the last.

```
open       2026-08-17T13:18:17+00:00 elapsed   4.7 left  670.5 -> WAIT
boot_kill  2026-08-17T13:23:59+00:00 elapsed 346.6 left  328.6 -> WAIT
boot_kill  2026-08-17T13:27:32+00:00 elapsed 559.3 left  115.8 -> WAIT
boot_kill  2026-08-17T13:30:14+00:00 elapsed 721.5 left  -46.3 -> KILL
```

The KILL is the gate's own verdict in the artefact, not a sentence in this report: `seconds_left`
= `usable_seconds − elapsed − reading_projection` = 2 129.2 − 721.5 − 1 454.0 = **−46.3**, and
`which_binds` says «affordability — the generation has not started, so the contract's twelve minutes
has no place on this axis yet». The registration predicted exactly that, in `pre_generation_budget_seconds`
= −44.785: on this run affordability binds from the first second and the twelve-minute ceiling never
gets to be the binding number. It never was.

### 3.3 What failed, said plainly

`ssh info` answered `pod not ready` on **every one of ~150 polls over 12 minutes** (six waiting
loops at a 3–4 s cadence, plus two single reads), while
`pod list -a` reported the pod `RUNNING` with its price from t≈10 s. reader-v4, same card, same
datacentre, same image, same volume, had ssh up at **17 s**. Nothing on this side ran: no scp, no
clone, no handshake, no model load. This is a provisioning failure at RunPod, in EU-RO-1 SECURE with
`stockStatus: Medium` read on the day, and there is nothing in the artefacts that can say more —
the pod was deleted, so no post-mortem is possible and none is claimed.

**[cause: the pod was billed as RUNNING while its ssh endpoint never came up; the boot deadline is
measured from `pod create` and does not care why.]** **Dv472.**

### 3.4 Delete, never stop — and the three listings

```
$ runpodctl pod delete ivw5z93im4hfnz
{"deleted": true, "id": "ivw5z93im4hfnz"}
```

Before (13:18:02Z) and after (13:30:24Z), read against each other:

| listing | before | after |
|---|---|---|
| `runpodctl pod list -a` | `[]` | `[]` |
| `runpodctl serverless list` | `[]` | `[]` |
| `runpodctl network-volume list` | `qw4nwleanc` `mp-srv2` EU-RO-1 100 GB | **identical** |

The volume is the positive control: three `[]`s would prove the command runs, not that the pod is
gone. Nothing else was created — no serverless, no template, no second pod.

### 3.5 The recovery clause was evaluated, and it refuses — with the arithmetic

Zero units were answered, so the «remainder» the clause speaks of is all 26. Its own test is whether
the cap can buy them:

```
guard balance delta (lower bound): spent $0.1406 -> $0.3094 left -> 1505.2 s -> usable 1445.2 s
                                   vs reading projection 1454.0 s  => DOES NOT FIT (short by  8.8 s)
pod meter, 727.9 s x $0.74/h:      spent $0.1496 -> $0.3004 left -> 1461.4 s -> usable 1401.4 s
                                   vs reading projection 1454.0 s  => DOES NOT FIT (short by 52.6 s)
```

Both readings fail, and both fail **before a single second of provisioning, staging or boot** — the
comparison is against the reading alone. On the loosest reading the shortfall is 8.8 s; on the meter,
which is the meter of record, it is 52.6 s. A replacement pod is therefore not authorised by the
clause it would have to be authorised by. **STOP, and that is the gate speaking, not a failure of
the contract** — the clause's own words.

---

## 4. D3 — there is nothing to score, and the scorers say so

Both instruments were driven anyway, because «no rows» is a statement an artefact should make:

```
$ PYTHONPATH=src python3.11 scripts/read_threads_reader_v5.py --ingest
results/reader_v5_pod.jsonl: the pod has written nothing yet

$ PYTHONPATH=src python3.11 scripts/score_reader_v5.py
results/reader_v5_w1.jsonl: no evidence — there is nothing to score
```

**Every bar is UNSCORED**, and that is the registered state rather than a failure: «every bar's state
is UNSCORED unless every registered thread was read». Nothing about the instrument was measured —
not prompt v5, not the transport stop, not the echo census, not the chunk merge, not the raised
ceiling. The $0 evidence from `reader-v5-prep` is untouched and still the only evidence there is.

| | |
|---|---|
| bars 1–4 (leg A) | **UNSCORED** — 0 of 23 threads read |
| leg B m1–m4 | **UNSCORED** — 0 of 3 chunks read |
| bar 5 time and cost | **OPEN** — $0.1406 lower bound of a $0.45 cap, not settled |
| completeness census | no rows |
| stop telemetry | no rows — the one thing prep could not measure is still unmeasured |
| bar 4's «which of the 7 moved» | unanswerable; the 7 are `21601`, `580124`, `580129`, `47899`, `47902`, `48283`, `578951`, and 5 of them had to move |

### 4.1 Bar 5 and the named debt

```
$ python3.11 scripts/runpod_guard.py --step reader-v5 --step-cap 0.45 --close --note "reader-v5 settled"
REFUSED: the billing walk over reader-v5's window answered «no billing rows yet», so there is no
settled figure to close on.
READER-V5 SPENT      $0.1406 of $0.45  (anchor $21.64 from runpod_balance_at_reader-v5_start)
  balance delta   $0.1406
  billing since   UNAVAILABLE (no billing rows yet) — the delta stands alone as a LOWER BOUND
```

**The step is NOT closed.** $0.1406 is a balance delta and a LOWER BOUND; the pod's own meter reads
727.9 s × $0.74/h = **$0.1496**, and the walk posts hours late. The debt and its command:

```
python3.11 scripts/runpod_guard.py --step reader-v5 --step-cap 0.45 --close --note "reader-v5 settled"
```

Cycle 2 after this attempt: **$1.0133 of $20.00 spent, $18.9867 free.**

### 4.2 What this does and does not close

- **The one-attempt clause fires.** «A kill … closes the question.» This registration's attempt is
  spent and there is no second pass at it. What follows is a new registration after a sitting.
- **The programme stop-rule does NOT fire.** Its condition is «**If this run COMPLETES** and bars 1
  and 4 are not BOTH taken». This run did not complete and no bar was scored, so it says nothing
  about whether the prompt-engineering line closes. That question is exactly as open as it was
  before the pod existed — and the operator's ruling of 17.08 stays armed for the run that does
  complete.
- **The instrument is untouched and paid for.** Prompt v5, the transport stop, the echo census, the
  merge, the scorer and the registration are all in the tree at $0 and none of them was exercised on
  a GPU. A new registration would re-register the same instrument, not rebuild it.

---

## 5. Deviations

| # | what | cause |
|---|---|---|
| **Dv469** | The baseline was 9 failed / 2 768 passed, not 2 777 / 2 skipped — `tests/test_volume_calc_5c1.py`, all nine off `knowledge/hot.md: '~$0.24/day' is not in the file` | *a curated vault file is a load-bearing input to a script, and the note saying so was inside the block being curated* |
| **Dv470** | The contract's recovery clause had no mechanism; the runner would have re-asked all 26 and appended duplicate rows the projection counts | *a clause headed «a caught fault must not strand the attempt» that cannot be executed* |
| **Dv471** | The full-pass gate has a knife-edge at unit 2 — 9% of margin, recorded and not changed | *leg B's 43 payable comments joined the projection's second denominator, and unit 2 has 2 payable comments* |
| **Dv472** | The pod was billed as RUNNING for 727.9 s and never answered `ssh info`; the run ended at the boot gate with zero rows | *the boot deadline is measured from `pod create` and does not care why the endpoint is absent* |
| **Dv473** | `raw_rows` would have raised on a torn last line of a file copied back mid-write, on the kill-rule path | *the partial jsonl is scp'd while the pod appends to it, so its final line can be half written* |
| **Dv474** | Verifying Dv469's fix by RUNNING `scripts/volume_calc_5c1.py` rewrote its shipped record and erased the operator's executed decision; restored from HEAD | *the producer was used as the check, and this producer's `main()` writes* |

**Dv474 in full, because it is the ugliest one here.** The check that «the literal is back» was
`PYTHONPATH=src python3.11 scripts/volume_calc_5c1.py` — and that script's `main()` WRITES
`results/volume_calc_5c1.json`. It moved `generated_at` from `2026-08-07T10:37:14+00:00` to today,
which widened the balance walk's window and let a top-up into it, and — far worse — it re-derived
`decision` from the script's default and **deleted the `executed` block**: the operator's ruling of
2026-08-07, the deleted CA-MTL-3 volume's id, size and datacentre, the whole record of a decision
this session had no part in. 8 insertions, 29 deletions.

It was caught by the after-run `make check` (`1 failed, 2781 passed`, the failure being
`test_the_idle_rate_is_reported_as_a_bound_not_as_an_estimate` asserting
`-11.1423 > 0.24`) and reverted with `git checkout --`; `tests/test_volume_calc_5c1.py` 10 passed
after. The read-only check that answers the same question without writing anything is
`calc.quoted(calc.HOT, "~$0.24/day", 0.24)` or `calc.inputs()`.

---

## 6. Verify

```
$ make check                    # before the pod, at 4cf51c6 (+ the untracked pack and ledger)
2781 passed, 2 skipped in 370.00s (0:06:10)
$ make check                    # after the pod — Dv474, one red, and it is the revert that fixes it
1 failed, 2781 passed, 2 skipped in 374.58s (0:06:14)
$ git checkout -- results/volume_calc_5c1.json && make check   # after the revert
2782 passed, 2 skipped
$ ruff check . && ruff format --check .
All checks passed! · 332 files already formatted

$ runpodctl pod list -a         # after deletion
[]
$ runpodctl serverless list
[]
$ runpodctl network-volume list
[{"dataCenterId": "EU-RO-1", "id": "qw4nwleanc", "name": "mp-srv2", "size": 100}]

$ python3.11 scripts/runpod_guard.py --step reader-v5 --step-cap 0.45
CYCLE 2 SPENT     $1.0133 of $20.00
REMAINING         $18.9867
READER-V5 SPENT      $0.1406 of $0.45  (anchor $21.64 from runpod_balance_at_reader-v5_start)
  billing since   UNAVAILABLE (no billing rows yet) — the delta stands alone as a LOWER BOUND

$ shasum -a 256 results/prereg_reader_probe_v5.json
8294673c89d4d9048204d212a8e8800390c37c630199fd2eecfcc19e6081c198
$ shasum -a 256 results/reader_v5_pack.json
16a24d0cd436af0b2a871cc1cac89c0db6fe01e00bf35b237ad81fc3cdf7aee1
```

The verdict record the scorer would have printed does not exist, and its absence is the refusal
quoted in §4. `results/reader_v5_run.json` is the artefact this attempt produced.

**«No edit to ANY frozen file once the pod exists», proved rather than asserted.** The pod lived
from 13:18:13Z to 13:30:19Z, which is **15:18:13–15:30:19 CEST**, and every commit in this
repository is stamped in CEST. The last commit touching anything on
`frozen_when_the_pod_exists` is `66dc418` at **15:05:41**, twelve and a half minutes before create;
the last commit of any kind before create is `0ec2da6` at **15:17:38**, thirty-five seconds before
it; the next commit of any kind is `e23c851` at **15:42:45**, twelve minutes after the deletion.

```
$ git log -1 --format='%h %cI' -- results/prereg_reader_probe_v5.json
66dc418 2026-08-17T15:05:41+02:00
$ git log -1 --format='%h %cI' -- src/market_pulse/prompts.py
9fe6dd4 2026-08-17T12:48:23+02:00
$ git log -1 --format='%h %cI' -- src/market_pulse/reader_v5.py
647b47f 2026-08-17T13:56:52+02:00
$ git log -1 --format='%h %cI' -- src/market_pulse/scorer.py
aa78c14 2026-08-15T19:45:03+02:00
$ git log -1 --format='%h %cI' -- results/reader_gold_w1_r2.json
3131bc0 2026-08-16T14:55:56+02:00
$ git log -1 --format='%h %cI' -- results/gate_census_w1_reader.json
9f0338d 2026-08-16T15:03:00+02:00
$ git log -1 --format='%h %cI' -- results/prereg_reader_probe_v4.json
f1bb539 2026-08-16T19:54:35+02:00
```

Nothing else was written while the pod existed either: the only file this session touched between
those two stamps is `results/reader_v5_run.json`, which the gate appends to and which is not frozen.

---

## 7. Process signals

1. **The gate's own KILL is in the record, and the append rule is why the record is readable at
   all.** Four snapshots — WAIT at 4.7 s, WAIT at 346.6 s, WAIT at 559.3 s, KILL at 721.5 s — are
   the whole attempt. v4 wrote these as a scalar and this run would have kept only the KILL, which
   is the one snapshot that says least: it is the three WAITs that show a deadline being watched
   go past rather than discovered in a bill.
2. **A boot deadline priced against a projection kills on provisioning, not on the model.** Nothing
   this run measured was about the reader. `pre_generation_budget_seconds` was already **−44.785**
   in the registration, which says in advance that this run had no slack before generation at all —
   and 12 minutes of an unreachable endpoint is a state neither the ceiling nor the model has an
   opinion about. A future registration that wants to survive a slow provision has to buy the
   headroom explicitly, not hope for it.
3. **The most valuable thing found in this contract cost $0 and was found by solving the gate
   backwards.** Dv471 — a 9% margin at unit 2, and where it comes from — was found by running
   `driver.projection()` over the built pack before create. It never got to matter, and on the next
   attempt it is the first number to look at: the pack's second unit has 2 payable comments and
   leg B's 43 are in the denominator.
4. **Two of the six deviations are things the contract asked for and did not have.** The recovery
   clause had no mechanism (Dv470) and the kill-rule path could raise on a torn line (Dv473). Both
   were written at $0 before create and neither ran. That is the correct order anyway: the
   alternative was writing them under a live meter with one attempt left.
5. **The baseline is a measurement, not a quotation (Dv469), and the fix for it did more damage
   than the defect (Dv474).** The contract's «2 777 / 2 skipped» was true when the team lead ran it
   and false in the tree it was handed to, because a curated vault file is a priced INPUT to a
   script and yesterday's `/save` reflowed it — the footgun note that named both literals having
   been deleted along with them. Then RUNNING that script to check the fix rewrote its shipped
   record and erased an operator ruling from 2026-08-07 that nothing in this contract touches. A
   producer is not a verifier; the suite caught it, which is the only reason this paragraph is
   about a revert instead of about a silent loss.

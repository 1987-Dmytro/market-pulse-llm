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

Anchor, before the pod (`74e2027` carries the pack, the step ledger and the cycle-2 session line):

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

## 3. D2 — the run

*(written as it happens)*

---

## 4. D3 — scoring and the verdict record

*(written after the pod is deleted)*

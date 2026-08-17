# pass1-probe — the instrument was built, the pod was bought, and the attempt died in my own code

**The measurement was NOT made.** Everything up to the model being loaded worked: the pack rebuilt
byte for byte, gate 0 went GO in 23.4 s, the handshake matched all four registered shas, and 64 of
64 requests rendered to the shas the registration pinned. Then `local_llm.ReaderClient.__init__`
probed the chat template through the runner's swapped `render`, that render assumed every call was a
pass-1 item, and the process raised `KeyError: 'topic'` — after the weights were in memory and
before a single reply. The pre-registered boot-kill deadline fired, the pod was deleted at **427.0
billed seconds = $0.087772 of a $0.20 cap**, and no bar is scored.

A second segment was priced against the registered arithmetic and REFUSED before it could be
created: its affordability deadline would be **76.2 s of create-elapsed** against a minimum boot
this stack has ever measured of **192.1 s**. The attempt closes. The finding is a defect in this
contract's own transport, not a finding about pass 1 — and pass 1 is exactly as unmeasured tonight
as it was this afternoon.

**And there is a second finding underneath it that changes what a next attempt should ask for.** The
registered boot ceiling was about to fire anyway: with the `KeyError` fixed, the first reply would
have landed **0.6–26.6 s** inside a 392 s deadline, because the load took **267–293 s** where the
registration charged v5b's **192.1 s**. The money was never the binding constraint — the $0.20 cap
still leaves 203 s of spare at tonight's boot. `BOOT_KILL_S = 300` is what bound, and it is the
constant a next registration has to move. Worked in D2 below.

---

## Read back first

- **What P1 gates:** ≥12 of the 14 gold rows of bar 4 agreed on their own `scored_fields`, through
  `scorer.reader_comment_agreement` — the reader's comparison, called and not restated. Nothing
  else gates.
- **What the census does not:** the 50 neighbour rows buy the per-thread `subject_type`
  distribution, the refusal shapes, the seconds and tokens per call and the window re-price. Not one
  of those numbers may move P1, and the registration says so in the bar's own `rule` field.
- **The return-to-sitting clause:** a failed bar goes BACK to the sitting — options B (labelled
  data + LoRA) and C (a different base). There is no pass1-v2 prompt without a sitting ruling, and
  the clause is inside the frozen record so it cannot be re-decided once a number exists.
- **Where the entity context comes from:** already-bought verdicts. Six of the seven gold threads
  from `results/reader_v5b_w1.jsonl`; **`@VARUS_channel:10613` from `results/reader_v4_w1.jsonl`**,
  because v5b refused it `malformed JSON` and v4 parsed it with a ten-entity block. Source and sha
  are recorded per thread. No reading was re-purchased.
- **The no-gold-in-prompt rule:** the prompt states rules and never a row. No gold `msg_id`, no gold
  thread key, no gold `subject_id`, and no 24-character run of any gold comment's text appears in
  it — driven from the gold file, not from a hand list.
- **When the registration freezes:** at the FIRST `pod create` of the attempt —
  **2026-08-17T18:41:24Z**. `dd1a1c1` carries the record and is timestamped 18:41:02Z, 22 s earlier.

---

## 0 — the tail

By live `git status`, by path, team-lead files in their own commit.

```
 M docs/STATUS.md                     -> 8460ae4  (team-lead, committed verbatim, never edited)
?? docs/PROMPT-pass1-probe.md         -> 8460ae4
 M knowledge/daily_logs/2026-08-17.md -> c25073e
 M knowledge/hot.md                   -> c25073e
 M knowledge/index.md                 -> c25073e
```

---

## 0.5 — the debts

### (1) `reader-v5b` is CLOSED at $0.312592, and ONLY bar 5 moved

The walk had answered «no billing rows yet» at 17:23Z and the guard refused, correctly. It was
re-checked read-only, pod-scoped, at 18:37Z and had posted **in full**:

```
$ runpodctl billing pods --pod-id r7702vbsrxhz0j --bucket-size hour --start-time 2026-08-17T16:00:00+00:00
[{"amount": 0.312591977417469, "diskSpaceBilledGb": 150,
  "gpuId": "NVIDIA GeForce RTX 4090", "time": "2026-08-17 16:00:00", "timeBilledMs": 1513961}]
```

**1 513 961 ms against the run record's 1 514.0 billed seconds** — the whole pod, 39 ms apart. That
is the discriminator the earlier refusal needed and did not have: not «are there rows» but «do the
rows cover the seconds the record says were billed». A partial walk would have frozen a low figure
into a record that is never re-derived, and at 17:23Z the same walk offered $0.0917 — 29% of the
truth.

```
$ python3.11 scripts/runpod_guard.py --step reader-v5b --step-cap 0.50 --close --note "reader-v5b settled"
CLOSED spend_reader_v5b.json at $0.3126 — entry APPENDED
READER-V5B CLOSED     $0.3126 of $0.50  (settled at 2026-08-17T18:38:37+00:00, window from 2026-08-17T16:21:29+00:00)
  pods            $0.3126
  network-volume  $0.0097   <- always on, beside the run and never inside it
  serverless      $0.0000
```

Settled **$0.312592**, pods only. The meter said $0.311211; the settlement is $0.001381 higher and
that is the billing's own rounding of the same 1 514 s, not a second reading of the run.

Re-scored, and the claim «only bar 5 moved» is a diff and not a sentence:

```
$ PYTHONPATH=src python3.11 scripts/score_reader_v5b.py
  bar 5_time_and_cost            CLOSED — passed True
TOP-LEVEL KEYS THAT MOVED: ['5_time_and_cost']
bars that moved: []
```

Every field that changed is inside `5_time_and_cost`: `state` OPEN → CLOSED, `passed` null → true,
`settled_usd` null → 0.312592, `lower_bound_usd` 0.0 → null, `sessions` 1 → 2, plus the ledger's own
sha. `bars` is byte-identical — bar 1 is still 2 of 5 and bar 4 is still 0.4286.
Verdict `8c975558b8da31cf…` → `d39cd2332a043a9b…`.

**Four bars of five now pass on paper and the two that matter still fail.** The stop-rule is
untouched by this close.

### (2) The ADR is written and it binds the team lead

`knowledge/decisions/reader-programme-closed-and-the-architecture-sitting-17-08.md` (`7ddbc5d`),
INDEX row appended. Its numbers are read out of `results/reader_v5b_verdict.json`, never out of
memory, and the row-by-row half is new: against v4's own fourteen, **exactly ONE gold row moved from
disagreement to agreement on attribution alone** (48283), 580124 lost its `stance` disagreement and
kept its `subject_type` one, three rows arrived out of ABSENCE through the echo duty and only one of
them agreed, and four went from scored to ABSENT when `@VARUS_channel:10613` was refused — two of
those four having AGREED under v4. None of that is the reader learning to attribute.

The withdrawn-order episode is recorded with its dates (ruled 17.08 in the contract, priced at $0 at
17:49 CEST, withdrawn 18:11, pack rebuilt 18:12, step anchored 18:21 — every one before the first
`pod create`) and with the measurement that confirmed the forecast (unit 17 read in 103.8 s against
105.3 s predicted).

The clause the contract asked for is in the record in as many words: **no new one-shot reader
registration may be written** — not under a new letter, not with a new prompt, not at a smaller cap.

### (3) The 22-ledger batch — 0 closed, 22 NAMED, and the reason is a code fact

**The batch as the contract describes it cannot be executed, and that is a property of
`scripts/runpod_guard.py`, not of the ledgers.** The contract says «a walk that answers «no rows» for
an old window closes at its recorded reading». `closing_record()` has no such path: `how != "read"`
returns `None`, and the caller turns `None` into a refusal. So the clause is unimplementable in
*both* branches — no rows refuses, and rows settle on everything-since.

That second half is the dangerous one and it is measured, not argued. `runpodctl billing` accepts
`--end-time` and `--bucket-size`; **the guard passes neither**, so `--close --since <old window>`
settles a step on every dollar billed from that window to *now*:

| ledger | window start (its own first session) | its recorded reading | what `--close --since` would settle it at | bounded walk (`--end-time`, which the guard never passes) |
|---|---|---|---|---|
| `45h2` | 2026-08-04T12:32:37Z | $8.8287 | **$22.988080** | $8.217558 |
| `5b` | 2026-08-06T12:16:12Z | $1.7069 | **$14.593890** | $1.484759 |
| `5c1_vis` | 2026-08-09T10:41:31Z | $0.4484 | **$10.609551** | $0.875542 |
| `srv2b` | 2026-08-08T17:35:05Z | $0.9999 | **$13.056833** | $0.939957 |
| `srv2c` | 2026-08-08T19:37:18Z | $0.1006 | **$12.066294** | $0.077418 |
| `srv2d` | 2026-08-08T21:00:57Z | $1.2332 | **$11.933193** | $1.163192 |
| `probe_a` | 2026-08-15T18:39:15Z | $0.0750 | **$1.246811** | $0.000000 |

Seven ledgers, $86.49 of «settled» figures against ~$13.4 actually recorded — on an account that has
spent ~$34 in its entire life. `srv2d` alone would be over-settled **10.26×**. The bounded column is
the control: with an end bound the walk agrees with each ledger's own reading to within 6–7%, which
says the ledgers are right and the missing bound is the whole defect.

The other fifteen split by cause:

- **Ten carry no RunPod anchor at all** — `3b`, `45d`, `45e`, `45g`, `45g2`–`45g6`, `5c1_captions`.
  These are OpenRouter-only steps that never ran a pod. The guard refuses them by name and the
  refusal returns BEFORE the write, so nothing is polluted — verified on `3b` against a hash of all
  29 ledgers:

```
$ python3.11 scripts/runpod_guard.py --step 3b --step-cap 1.00 --close --note "3b batch close attempt"
REFUSED: 3b has no anchor on disk — a step that never ran cannot be closed.        (exit 1)
$ find results -name 'spend_*.json' | sort | xargs shasum -a 256 | diff ledgers.before -
NONE — no ledger byte moved
```

- **Five carry an anchor and no window** — `5c2run`, `sku_b`, `sku_b_v3`, `sku_b_v4`, `skub2`. No
  `anchored_at` and no session, so `--close` without `--since` refuses and `--close --since <from the
  report>` lands in the over-settlement above. Verified on `srv2c`, same hash control:

```
$ python3.11 scripts/runpod_guard.py --step srv2c --step-cap 0.75 --close --note "srv2c batch close attempt"
REFUSED: spend_srv2c.json carries no `anchored_at` and no --since was given, so the closing
walk has no window to ask for.                                                     (exit 1)
NONE — no ledger byte moved by either probe
```

**Not one `--close` was run against the twelve anchored ledgers.** Writing is the irreversible
direction and the guard's own docstring names it: «Refusing to close is recoverable; a wrong
settlement is the one outcome that is not.» The batch is therefore reported as timeboxed and
skipped, with every one of the 22 named above and the debt handed forward with a shape: **teach the
guard an `--until` and re-run this table**, which is a money-path change with tests and belongs in
its own contract, not smuggled into this one.

---

## D1 — the pass-1 instrument, at $0

### The prompt carries the reader's law by REFERENCE

`pass1_comment_gm4_v1`, 2 521 characters, sha `5a4a3cb6ce4db89a…`. Its attribution paragraph is
`prompts.READER_ATTRIBUTION_LAW_V5` — **the same bytes the reader was asked with**, not a re-wording
of them. That matters for what the probe can conclude: if the same law in a shorter task reads
better, the finding is about the TASK SHAPE and not about a prompt someone re-tuned.

Making that possible meant cutting `READER_ATTRIBUTION_V5` in two, because its first sentence names
`"signals"` and `"per_comment"` and pass 1 has neither list. The cut had to move no byte of the v5
text, and the proof is the frozen record's own pin:

```
v5 prompt sha, live:                       c529d279321269e1…
results/prereg_reader_probe_v5b.json pins: c529d279321269e1…   MATCH
```

Everything else is short: the entity block is context and not a menu, the four ratified readings,
`stance` from the sentiment domain, `subject_id` off the comment or the block, and the msg_id echoed
back. One JSON object, nothing else.

**Contamination gate, with its positive control** (`tests/test_pass1_prompt.py`, the v5-prep fixture
over 5 corpus directories + gold r1/r2 + the reference):

```
$ python3.11 -m pytest -q tests/test_pass1_prompt.py
15 passed
```

- `test_the_corpus_matcher_finds_a_phrase_that_IS_in_the_store` — the negative control: a sentence
  taken out of the evidence store is FOUND by both comparisons (raw and normalised). Without it,
  «not found» could be the matcher.
- `test_no_example_in_the_pass1_prompt_occurs_anywhere_in_the_corpus` — every «…» quotation of ≥3
  words, driven from the TEXT and not from a hand list. Three examples, all of them the ones
  `tests/test_reader_prompt_v5.py` already proves synthetic.
- `test_the_prompt_names_no_gold_msg_id_no_gold_thread_and_no_gold_answer` — 14 ids, 7 thread keys,
  6 `subject_id` values and every 24-character window of all 14 gold comment texts. The populations
  are asserted non-empty first, so the loops cannot pass over nothing.

### The four readings, and why four is measured rather than chosen

The contract fixes the parser's domain at four `subject_type` readings where the reader parser has
five. The risk is that a reply spelling the fifth word is refused and costs a row. It is measured,
not guessed: over **v5b's 195 `per_comment` rows the word «категория» does not appear once**, while
v4's v3-text run spelled it on 3 of its 26 non-null rows. The v5 text stopped offering it and the
run proved the offer is what produced it.

### The MOVED manoeuvre, a second time

Registering the text inside `prompts.py` moves the module, and **four committed records pin its old
bytes**: the v5 and v5b registrations and both packs. They are not re-pinned — they froze when their
pods existed. `tests/test_prompts.py` gains a second sealing moment, `SEALED_AT_PASS1 = e657056`
(the tree reader-v5b's pod read 26 units under), with its own witness map: `pass1_comment_gm4_v1` for
`prompts.py` and `with_the_moved_module_put_back` for the v5b producer, each asserted ABSENT from
that commit's blob and PRESENT on disk.

One consequence was not free. `scripts/write_reader_prereg_v5b.py` refuses to build unless v5's
record rebuilds byte for byte, and it stopped rebuilding — in exactly two cells, both the module's
sha:

```
.instruments.parser.sha256                      rebuilt b59ad621… | frozen be5a8164…
.producer.borrowed.src/market_pulse/prompts.py  rebuilt b59ad621… | frozen be5a8164…
```

The guard now restores **those two enumerated paths and nothing else**, only when the rebuilt value
is today's live module sha, and refuses with the old message on any third difference. Narrowing a
money-path guard is only safe if what it stops seeing is named, so `the_readers_law_is_unmoved()`
compares the four reader texts against the frozen record's own `prompt_sha256` map and the four
domain tuples against literals — turning «prompts.py's bytes» into «the reader's law inside
prompts.py», which is what the guard was reaching for. Both halves are DRIVEN on hand-made pairs:
one differing only in the two allowed cells must come back equal, one that also moves the v5 text's
sha must not.

### The registration and the pack

`results/prereg_pass1_probe.json` `76bbf5612032faf7…` · `results/pass1_probe_pack.json`
`cefaf8122bce385b…`, both re-derived byte for byte by their producer and committed at `aa4c45d` /
`a45b46f` / `dd1a1c1`, all before the first pod.

**Population, enumerated and never chosen — 64 units:**

| thread | payable | gold | census | entity block |
|---|---|---|---|---|
| `@VARUS_channel:10348` | 7 | 1 | 6 | v5b, 2 entities |
| `@VARUS_channel:10613` | 10 | 4 | 6 | **v4, 10 entities** |
| `@mandziak:3676` | 9 | 2 | 7 | v5b, 2 |
| `@mandziak:3703` | 9 | 2 | 7 | v5b, **0 — legitimately empty** |
| `@matusi_ukr:22242` | 12 | 1 | 11 | v5b, 5 |
| `@matusi_ukr:22272` | 15 | 2 | 13 | v5b, 2 |
| `@matusi_ukr:22303` | 2 | 2 | 0 | v5b, 5 |
| **total** | **64** | **14** | **50** | |

Both halves are recomputed in the test from their own sources — the gold as a set of (thread, id)
pairs out of gold r2, the census as a set difference over `probe_b_population.population()` — and
both directions are asserted: nothing gold leaked into the census, nothing payable was left out.

**Bar P1 with its loss budget stated in advance.** ≥12 of 14 tolerates exactly **two** losses, and a
disagreement, a refusal and an ABSENT row each cost the same one row. Registered with the number
beside it, because v5b's bar 4 lost four rows to a single refused thread and the report had to name
that denominator afterwards. The registration also names the thread that carries the most gold rows:
`@VARUS_channel:10613` with **4** — **one refused thread there exceeds the whole budget on its own.**

**The projection has two readings and the pessimistic one gates.** A least-squares line over v5b's
26 calls gives `seconds ≈ 1.062 + 0.052599 × completion_tokens`, which at ~35.6 tokens predicts
**2.93 s** a call — but the line was fitted between 96 and 2 056 tokens, so using it would
extrapolate below its own range. What is registered instead is **v5b's own cheapest call**:
`@mandziak:3701`, 96 completion tokens, 2 659 prompt tokens, **6.402 s**. It is heavier than any
pass-1 request on both axes, on the same card, the same transport and the same serving config — so
it is a bound with no forecast in it.

**The gate solved backwards over the built pack, published before create** (Dv471's method):

```
cap $0.20 buys 973.0 s · usable 913.0 s · 64 units at the registered bound of 6.402 s
reading projection 409.7 s · boot 192.1 s · budget 203.2 s · affordability 503.2 s
unit 1 @VARUS_channel:10348#20594 · 6.402 s vs a zero-boot ceiling of 14.3 s -> clears True
full pass: first STOP after None unit(s) · tightest margin 4.94 s/unit at unit 1
```

No STOP at any of the 64 units and no knife-edge to report. The corner with no provisioning forecast
in it — `usable ÷ units` = 14.26 s — clears at 2.2×. And there is structurally no second leg to
find: every pass-1 unit carries exactly one payable comment, so the gate's by-payable leg and its
by-unit leg are the same number. v5b's knife lived in the gap between them; this pack has no gap.

---

## D2 — the run

Anchor `results/spend_pass1_probe.json` at $21.1257116004, `2026-08-17T18:39:40Z`, cap $0.20,
committed in `bc4c829` **before** anything was created. Three listings immediately before create:
`pod list -a` `[]`, `serverless list` `[]`, `network-volume list` `qw4nwleanc` `mp-srv2` EU-RO-1
100 GB — the volume is the positive control that the listing works at all. `--pre-create-check` →
`may_create: true`, segment 0 of 3.

| create-elapsed | wall | what |
|---|---|---|
| 0 s | 18:41:24Z | `pod create` — `rx89zok35e5ca6`, RTX 4090, RO, `costPerHr` **0.74**, exactly the registered worked example, so no deadline is re-priced |
| 5.6 s | 18:41:30Z | `--open`: segment 1 recorded, gate `open` **WAIT**, 174.4 s left on gate 0 |
| 12–18 s | | `runpodctl ssh info` → `{"error": "pod not ready", "status": "RUNNING"}` ×6 |
| ~18 s | 18:41:42Z | **the endpoint answered** — `213.173.99.35:12533` |
| 23.4 s | 18:41:47Z | gate `gate0` **GO**, 156.6 s unused, recreates left 2 |
| 43 s | 18:42:07Z | scp: the 8.62 MB bundle at `dd1a1c1`, the pack, and all three runners |
| 81 s | 18:42:45Z | `git clone` → `repo-pass1`; `HEAD = dd1a1c1fc34f64e6…` = the Mac's HEAD; `git status --short` empty; `/workspace/hf` 59 G |
| 92 s | 18:42:56Z | detached launch, `--repo /workspace/repo-pass1` passed explicitly |
| 92.3 s | | `instrument OK · parser a4a5a5d08546f53a…` · **64 requests match the registration's per-item shas** · `ceiling 256 output tokens · stop at the brace` |
| ~385 s | 18:47:49Z | the watcher's `kill -0 156` returns DEAD with **0 rows on disk** |
| 392 s | | the registered **boot-kill deadline** (generation start + 300 s) passes with no reply |
| 427 s | 18:48:31Z | `pod delete` → `{"deleted": true}`; `pod list -a` `[]` |

**Gate 0 worked twice running.** 23.4 s against a 180 s dead-man, on the second pod since the rule
was bought. The transport difference reader-v5b paid for is now measured on two independent creates.

**And then the run died in my own code.** Transcribed from `/workspace/pass1.log` while the pod was
still alive — **that file died with the pod and is not recoverable.** The contract's own «partial scp
before every gate» would have brought it back and this run never made one, so the traceback below is
the only surviving copy and it is a session read rather than an artifact:

```
File "/workspace/repo-pass1/src/market_pulse/local_llm.py", line 580, in __init__
    self._assert_template_emits_bos()
File "/workspace/repo-pass1/src/market_pulse/local_llm.py", line 589, in _assert_template_emits_bos
    if not self.render(prompts.READER_TASK_V2, probe).startswith(bos):
File "/workspace/reader_v5_pod_runner.py", line 149, in render
    [{"role": "user", "content": render(prompts, item, task)}],
File "/workspace/pass1_pod_runner.py", line 43, in render
    item["topic"],
KeyError: 'topic'
```

`ReaderClient.__init__` will not build a client until it has proved the chat template still emits
`<bos>`, and it proves it by rendering a READER-shaped probe with `READER_TASK_V2` through
`self.render`. `self.render` is the runner's — which this contract had SWAPPED for pass 1's. The
swap assumed every call it would ever see was a pass-1 item.

**Why the stub-driven test could not see it.** `tests/test_pass1_transport.py` drives
`podrunner.main` end to end with a fake client, and the fake client is passed as `loader=`, which
replaces `load_reader` — the function whose last line constructs the `ReaderClient` whose
constructor makes the call. **A stub that replaces the class also replaces its constructor's
guard.** Nine tests passed over a code path that could not reach the defect.

### The number the sitting needs: the boot ceiling was 0.6–26.6 s away from killing this run anyway

The `KeyError` is a one-line fix and it hides a second, bigger finding. **The registered boot-kill
deadline was about to fire regardless.**

| | |
|---|---|
| generation started | 18:42:56Z = **92 s** of create-elapsed |
| boot ceiling | 92 + `BOOT_KILL_S` 300 = **392 s** = 18:47:56Z |
| affordability deadline | 913.0 − 409.7 = **503.3 s** = 18:49:47Z |
| the gate takes `min()` | so **392 s binds**, and it is the boot ceiling, not the money |
| the crash | between the watcher's ALIVE at 18:47:23 and its DEAD at 18:47:49 — **[359, 385] s** |
| so the load took | **[267, 293] s**, against the 192.1 s the registration charged |

With `render` correct, the first reply lands one call after the model is ready: **[361.9, 387.9] s**
at the fitted 2.93 s, **[365.4, 391.4] s** at the registered bound of 6.402 s. Against a 392 s
ceiling that is a margin of **4.1–30.1 s** on the fit and **0.6–26.6 s** on the bound. The run would
have squeaked through the boot gate and then held the full pass comfortably (after unit 1 at ~385 s,
the projection is 574 s at the fit and 788 s at the bound, both inside 913 s).

**So the weakest number in the registration is `BOOT_KILL_S = 300`, and it was set from v5b's
192.1 s boot on the same card and the same volume.** Tonight the same load took 267–293 s — a 1.4×–
1.5× spread on a number the record treated as a constant. That is the ceiling a next attempt has to
move, and the cap is not the problem: at a 300 s boot charge the registered bound needs 709.7 s of
the 913.0 s the $0.20 cap already buys, leaving 203.3 s spare.

The only witness to the crash moment is the watcher's ALIVE/DEAD pair, so the ranges above are
bounds and not readings. Precision this report cannot have is not spent here.

### The second segment was priced and REFUSED

```
segment 1 billed        427.0 s = $0.087772
cap left                $0.112228 = 546.0 s
usable for segment 2    486.0 s  (one more delete margin)
registered projection   409.7 s  -> affordability deadline  76.2 s of create-elapsed
the FITTED projection   187.8 s  -> affordability deadline 298.2 s of create-elapsed
boot measured v5b       192.1 s (cold, same card, same volume)
boot measured segment 1 [267, 293] s (launch 18:42:56Z -> crash inside the watcher's
                        ALIVE 18:47:23 / DEAD 18:47:49 pair; the pod is gone, so this is a bound)
```

Under the registered bound a first reply would have to land at 76.2 s of create-elapsed, and no boot
this stack has ever measured is under 192.1 s. Under the optimistic fit the deadline is 298.2 s against
segment 1's own boot of 267–293 s — between 5 s and 31 s of margin, before staging, on a pod whose
page cache would be cold again. **The attempt closes on its own arithmetic, and it closes under both readings.** No cap
raise was considered; the registration's one-attempt clause and the contract's DO NOT both say the
sitting owns the next move.

---

## D3 — scoring

**Nothing to score.** `results/pass1_probe_rows.jsonl` does not exist, because
`results/pass1_probe_pod.jsonl` was never written to. `scripts/score_pass1_probe.py` is built,
committed and DRIVEN on hand-made evidence (`tests/test_score_pass1_probe.py`, 9 tests) so that the
instrument is ready and its own behaviour is known:

- bar P1 calls `scorer.reader_comment_agreement` and `score_reader_probe_b.collapse` — the reader's
  own comparison and the reader's own collapse, imported and never restated;
- the bar is a COUNT and the boundary is driven from both sides: 0 and 2 losses pass, 3 fails;
- an ABSENT row costs the same one row as a disagreement and is counted apart, with the narrower
  rate over the rows the model answered published beside the registered one;
- no evidence at all is **fourteen absent rows**, not a rate over nothing;
- and one measured finding worth carrying: **the vocabulary collapse is a NO-OP for this
  instrument.** Bar 4 needed it because the v3 text offered both spellings; pass 1's text offers only
  the four and its parser refuses the fifth, so no answer it can produce is on either side of the
  map. The same rows score 14 of 14 with the collapse and 14 of 14 without it. That is a property of
  bar P1 the next sitting should not have to rediscover.

---

## Money

| | |
|---|---|
| `pass1-probe` step | **$0.087772** of $0.20 — one segment, 427.0 s, deleted |
| billing walk | `[]` at 18:58Z — has not posted; the step is **NOT closed** and carries a named debt |
| `reader-v5b` step | CLOSED at **$0.312592** of $0.50 this session |
| cycle 2 | $1.3840 of $20.00 · remaining **$18.6160** (the pass-1 pod is not in the walk yet) |

The step close for `pass1-probe` is this report's named debt, exactly as v5b's was:
`python3.11 scripts/runpod_guard.py --step pass1-probe --step-cap 0.20 --close --note "pass1-probe
settled"`, once the pod-scoped walk reaches ~427 000 ms. Do not run it on a partial walk — the
closing path settles on the WALK alone, with no pessimistic maximum against the balance delta, and a
partial walk freezes a low figure into a record that is never re-derived.

---

## Verify

```
$ make check                                    # at aa4c45d, D1 built, before any pod
2859 passed, 2 skipped in 455.73s (0:07:35)
$ make check                                    # at 31ac998, scorer + transport tests
2877 passed, 2 skipped in 482.76s (0:08:02)
$ make check                                    # at 90f1cc6, after the fix
2879 passed, 2 skipped in 461.60s (0:07:41)
$ python3.11 -m ruff format --check .
345 files already formatted
$ runpodctl pod list -a          # after the delete
[]
$ runpodctl serverless list
[]
$ runpodctl network-volume list  # the positive control: the listing works at all
[{"dataCenterId": "EU-RO-1", "id": "qw4nwleanc", "name": "mp-srv2", "size": 100}]
$ python3.11 scripts/runpod_guard.py --step pass1-probe --step-cap 0.20
PASS1-PROBE SPENT      $0.0000 of $0.20  (anchor $21.13 from runpod_balance_at_pass1-probe_start)
  balance delta   $0.0000
  billing since   UNAVAILABLE (no billing rows yet) — the delta stands alone as a LOWER BOUND
$ shasum -a 256 results/prereg_pass1_probe.json results/pass1_probe_pack.json \
      results/pass1_probe_run.json results/reader_v5b_verdict.json
76bbf5612032faf7a39e9188c5f0659a7b6a38fb275a159893472cc9afae1b91  results/prereg_pass1_probe.json
cefaf8122bce385bda1bdc55de4b857fa3d92da978f8ac8ce18e4769f40c7842  results/pass1_probe_pack.json
e5206f5a8a14017d064fb032bc95dee676e49ed1e8ecaa044181f54fcca48c26  results/pass1_probe_run.json
d39cd2332a043a9b20899cd77cd4645aeb2d85bc4ab121995a5d4254122a1740  results/reader_v5b_verdict.json
$ PYTHONPATH=src python3.11 scripts/read_pass1_probe.py --pack
{"pack": "results/pass1_probe_pack.json", "units": 64, "gold": 14, "census": 50,
 "rebuilds_byte_for_byte": true}
$ PYTHONPATH=src python3.11 scripts/write_pass1_prereg.py
wrote results/prereg_pass1_probe.json  sha256 76bbf5612032faf7…
wrote results/pass1_probe_pack.json  sha256 cefaf8122bce385b…
  cap $0.20 buys 973.0 s · usable 913.0 s · 64 units at 6.402 s
  reading projection 409.7 s · boot 192.1 s · budget 203.2 s · affordability 503.2 s
  unit 1 @VARUS_channel:10348#20594 · 6.402 s vs a zero-boot ceiling of 14.3 s -> clears True
  full pass: first STOP after None unit(s) · tightest margin 4.94 s/unit at unit 1
  population: 14 gold + 50 census = 64 units over 7 threads
$ python3.11 -m pytest -q tests/test_pass1_prompt.py tests/test_pass1_prereg.py \
      tests/test_pass1_transport.py tests/test_score_pass1_probe.py
48 passed
```

The contamination gate's own three tests and their positive control are in that 48; the gate is
reproduced in D1 above with the sentence each one proves.

---

## Deviations from Dv482

| # | what | cause |
|---|---|---|
| **Dv483** | **The 22-ledger batch closed ZERO ledgers.** The contract's «a walk that answers «no rows» closes at its recorded reading» has no implementation — `closing_record()` returns `None` on anything but `"read"` and the caller refuses. And the guard passes neither `--end-time` nor `--bucket-size` to `runpodctl billing`, so `--close --since <old window>` settles a step on everything billed since: measured at 2.6×–156× over seven ledgers, $86.49 against ~$13.4 recorded, `srv2d` alone 10.26×. All 22 named by cause, none written to, both refusal classes proved with a 29-file hash control. | `[cause: a-brief-can-outrun-the-document]` |
| **Dv484** | **The attempt was spent by a defect in this contract's own runner.** `local_llm.ReaderClient.__init__` renders a READER probe through `self.render` before it will build a client; the swapped render assumed a pass-1 item and raised `KeyError: 'topic'` after the weights were loaded. 427.0 billed seconds, $0.087772, zero replies. Fixed red-first — the new test reproduces that exact `KeyError` — and a second test asserts `local_llm`'s probe literal is still the one it guards against. | `[cause: a-guard-wired-only-when-it-can-fire]` |
| **Dv485** | **The stub that proved the transport also hid the defect.** `podrunner.main` was driven end to end with a fake client passed as `loader=`, which replaces `load_reader` — the function whose last line constructs the client whose CONSTRUCTOR makes the failing call. Nine green tests over a path that could not reach it. The new test drives the swapped `render` directly with the shipped probe instead of through the client. | `[cause: the-vendors-own-worker-is-the-control]` |
| **Dv486** | **The registration crashed the transport before the pod, twice, on SHAPE.** `read_threads_reader_v5b` reads `go_no_go.gates.0_transport_ssh_deadman.max_recreates` and `money.arithmetic.boot_kill_seconds` off the registration; my first record carried `go_no_go` as prose and named the boot rule `boot_kill_rule`. The first was caught by `--pre-create-check` at $0 and the record was regenerated before create. **The second was not** — `--deadlines` raised `KeyError: 'boot_deadline_rule'` with the pod running, and the deadline had to be computed by hand from the registered numbers. A frozen record cannot be repaired, so the gate this contract most needed at that moment was the one it could not execute. | `[cause: a-registered-bar-may-have-no-producer]` |
| **Dv487** | **`producer.sha256` pinned a file that was not committed when the pod was created, so the registration's own re-derivation test was RED at the commit the pod cloned.** At `dd1a1c1` (18:41:02Z) the producer on disk hashes `16dee2f4…`, which is what the record pins; `git show dd1a1c1:scripts/write_pass1_prereg.py` hashes `8aab2a94…`. A checkout of that commit therefore cannot rebuild the record it carries, and `test_the_committed_registration_and_pack_are_what_the_producer_writes_today` would fail on it — the pod cloned that tree 81 s later. `registration()`'s `git ls-files` / `git diff HEAD` guard covers the record and not the files it PINS. The bytes are unchanged and committed at `90f1cc6`, so it is recoverable; the check that would have caught it is running each commit's own suite. | `[cause: a-commit-must-run-its-own-suite]` |
| **Dv488** | **A partial billing walk is a third state and the guard cannot see it.** At 17:23Z the v5b walk answered «no billing rows yet» and refused; by 18:37Z it had posted 1 513 961 ms of 1 514.0 s. In between it offered $0.0917 — 29% of the truth — and `closing_record` would have settled on it, because the closing path takes the WALK alone with no pessimistic maximum against the balance delta. The discriminator used here was `--pod-id … --bucket-size hour` against the run record's own billed seconds. | `[cause: a-settlement-is-a-reading-too]` |
| **Dv489** | **Adding one prompt to `prompts.py` broke a frozen record's re-derivation, and the repair had to be narrowed rather than removed.** Two byte ranges of the v5 record moved, both the module's sha; the v5b producer's object-equality guard now restores exactly those two enumerated paths, only when the value is today's live sha, and refuses on any third difference. What the narrowing stops seeing is named and closed: the four reader texts and the four domain tuples are compared directly, so «prompts.py's bytes» became «the reader's law inside prompts.py». Both halves driven on hand-made pairs. | `[cause: a-hash-is-not-the-claim-it-carries]` |

---

## Process signals

1. **The gate that mattered most was the one the record could not run.** Two registration-shape
   crashes; the cheap one fired before the pod and cost $0, the expensive one fired with the meter
   running and forced hand arithmetic. A registration is an INPUT to shipped code — the next one
   should be driven through every transport command it will ever see, at $0, before it is committed.
2. **A stub can be green over a path it cannot reach.** The fake client replaced the constructor
   whose self-check killed the run. Where a shipped class is replaced wholesale, at least one test
   must drive the real code path the replacement short-circuits.
3. **Solving the gate backwards is still the cheapest thing in this repo.** The 64-unit table, the
   zero-boot corner and the two-reading projection all cost $0 and all held — the run died 300 s
   before any of them could bind, and the segment-2 refusal was arithmetic nobody had to argue.
4. **Measure a walk's COMPLETENESS, not its emptiness.** «No rows yet» and «29% of the rows» look
   identical to a caller that only asks whether the list is empty, and one of them settles a record
   forever.
5. **$0.088 bought two real facts.** Gate 0 has now gone GO twice on two independent creates, at
   23.4 s and 24 s against a 180 s dead-man — the transport reader-v5b paid to fix is fixed. And the
   boot on this stack is not 192.1 s but 192–293 s across two runs, which is the constant the next
   registration has to charge from. Everything else this contract bought, it bought at $0.

---

## What is NOT decided

Pass 1 is unmeasured. Bar P1 has no number, the census has no rows, and the window re-price has no
input. The instrument, the registration, the pack, the transport and the scorer are all built,
committed, green and — as of `90f1cc6` — free of the defect that ate the attempt. **Whether a second
attempt is authorised is the sitting's call, not this contract's**, and the registration's own
one-attempt clause plus the contract's DO NOT both point the same way.

If it is authorised, the number to move is **not the cap**. At tonight's measured boot the registered
bound needs 709.7 s of the 913.0 s the $0.20 cap already buys, with 203.3 s spare — the money was
never the binding constraint. What bound was **`BOOT_KILL_S = 300`**, charged from v5b's 192.1 s
while the same load on the same card and the same volume took 267–293 s tonight, and it would have
fired 0.6–26.6 s after a corrected first reply. A next registration should charge boot from BOTH
measurements rather than the lower one, and set the ceiling above the higher: ~300 s charged, ~420 s
ruled. That is a one-constant change to a record, and it is the difference between an attempt that
measures pass 1 and an attempt that measures provisioning variance.

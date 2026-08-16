# reader-v3-run — the instrument was staged, the boot never answered, and the cap was gone

**Contract:** `docs/PROMPT-reader-v3-run.md` · **law:** `results/prereg_reader_probe_v3.json` (FROZEN)
· **baseline:** `make check` 2 623 passed / 2 skipped at `4bc128b` · **HEAD at the start:** `4bc128b`
· **HEAD the volume served:** `aa0ca18`.

**Outcome in one line.** Step 0, the driver, the scorer and their 21 tests landed at $0 before any
endpoint existed; the volume moved `f0fd745 → aa0ca18` by fetch and hard reset and rendered all
**three** reader texts and the parser module byte-identical to this Mac; the endpoint came up with
`gpuIds: ADA_24` read back for free — and then the **`info` job was never answered**. Twenty minutes
of a worker RunPod reported as `running` with `completed: 0`, and the step's balance delta went
$0.0000 → **$0.3918 against a $0.35 cap**. The endpoint and template were deleted, the deletion is
proven by the same three listings taken before anything was created, and **not one thread was read**.
Every bar is UNSCORED. The contract's one attempt is spent, and what it bought is a measurement:
**a cold start on this stack can cost more than the whole probe.**

The two findings this contract really yields were bought at **$0**, before the money moved, and they
survive the run failing — §5 and §6. Both are defects in the frozen registration, both are things the
next registration has to decide before anyone pays again.

---

## 0. Step 0 — the tail, two commits by path

`git status` before anything: three vault files, `docs/STATUS.md` modified, and this contract
untracked.

The contract says «`knowledge/**` by live `git status`, one commit by path. Anything outside → STOP».
Two files are outside, and neither is the executor's: `docs/STATUS.md`'s diff is the team lead's own
record of the `reader-v3-prep` acceptance, and `docs/PROMPT-reader-v3-run.md` is this contract. Both
take the house manoeuvre probe-b §0.1 and `fabd2f3` already fixed — committed verbatim, staged by
path, never `git add -A`, never edited. Dv436.

→ `0c97b3e` (the vault) · `8598948` (the two team-lead files).

---

## 1. D1 ($0) — the run driver, and the gate's real threshold

`53fc13b` · `scripts/read_threads_reader_v3.py`, `tests/test_read_threads_reader_v3.py`.

probe-b's arithmetic is unchanged and the pieces that **cannot** differ are imported from that
driver rather than retyped — `threads_of` (the population digest and the per-request sha),
`handshake` (Dv428's two comparisons in their two messages), `expected_worker`, `job_item`,
`key_of`. What is new is what the registration made new: the task, the ledger, the evidence file,
and the card the projection is compared against.

### 1.1 Dv437 — the stop threshold is 69.592 billed seconds, not 1.165×

The registration publishes `max_slowdown_vs_probe_b: 1.165` and the contract asks the report to read
back «the 1.165× floor and what binds». Read back, and it is **not** what the gate stops on.

1.165× bounds the **whole pass**: 847.8 seconds the cap buys after setup ÷ probe-b's 727.664. The
go/no-go stops on the **warm-up**, whose own seconds are inside the total and from which the unread
remainder is projected. With 3 warm-up threads / 11 payable against 20 threads / 123 payable unread,
the per-payable projection binds at **11.1818×**, and the inequality

    setup + billed × rate × (1 + 11.1818) ≤ cap

solves to **billed ≤ 69.592 s** — which against probe-b's own 62.276 s for exactly this draw is
**1.117×**, not 1.165×. A gate checked against the published number would have opened a run about
$0.02 over the cap.

Both numbers are in the run record's `stop_threshold` block with the reading that separates them,
and the test drives both sides one thousandth of a second apart: at 23.197 s a thread the warm-up
bills 69.591 and the total is $0.349995 — GO; at 23.198 it bills 69.594, $0.350006 — STOP.

**And the published dollars cannot tell those two apart.** Both print `projected_total_usd: 0.35`,
because $0.3500064 rounds to four decimals exactly like $0.3499948. The record therefore names the
pair a reader checks the verdict against — `warm_up.billed_seconds` against
`stop_threshold.warm_up_billed_seconds_that_still_fit` — and the test asserts the rounded dollars
are equal on both sides so nobody re-derives the verdict from them
([[a_record_must_re_derive_from_what_it_publishes]]). `[cause: registration-arithmetic]`

### 1.2 Dv438 — which reading of «billed» is taken is recorded, not assumed

`EndpointClient.timing()` starts its wall clock at the first request of the **process**, and in this
driver that is `info()`. Run against a cold endpoint, the boot lands inside `wall_seconds` — a
~180 s reading on a gate whose threshold is 69.592 s, i.e. a STOP that is an artefact of where a
process began. probe-b never saw it because its `--handshake` and `--warm-up` were separate
invocations with a warm worker between them.

The pessimistic maximum is **kept** — it is probe-b's rule and the pairing rests on it — and all
three legs plus the gap are persisted (`live_worker_seconds`, `live_wall_seconds`,
`persisted_worker_seconds`, `wall_ahead_of_the_jobs_by`), with a loud stderr line when wall runs
more than 30 s ahead of the jobs' own seconds. The test drives a 180 s bonus and asserts the STOP is
attributable in the artefact instead of arriving unexplained. `[cause: instrument-change]`

### 1.3 What is persisted per row

The contract's step 6, read back: **the rendered request itself** and its per-thread sha (the
registration pins the sha; only the text lets a reader see what the model was shown when a verdict is
argued about later), the reply byte-exact, the parse outcome with its `repairs: [...]` or the
refusal's reason string, `finish_reason`, `usage`, and both seconds readings — written to
`results/reader_v3_w1.jsonl` and flushed **as each reply lands**, never at the end.

---

## 2. D2 ($0) — the scorer

`1846e5a` · `scripts/score_reader_v3.py`, `tests/test_reader_v3_verdict.py`.

Bars 1, 2 and 4 go through **probe-b's own scoring functions** against gold r2, so the paired
columns are one arithmetic on both sides rather than two readings of one word. Bar 3 **calls**
`write_reader_prereg_v3.bar_three_over_answers`: the registration says the run's scorer «reproduces
this predicate and may not invent a second reading of it», and the strongest available form of that
is to use the producer. Bar 5 reads the step ledger in all three of its states.

Bar 3's fields, read back as the contract asks: `threads_registered`, `threads_with_a_verdict`,
`threads_refused`, `signals`, `reachable`, `passed` — and the scorer refuses to emit a result missing
any of them, naming the producer in the message.

The refusal census derives **both** probe-b baselines rather than transcribing a table: the causes
its run recorded (five over ten refusals) and the causes its same 23 replies produce under **today's**
parser (four — the registration's own 19-of-23 measurement, recomputed). probe-b's report says «six
shapes» in prose and the registration names a seventh reply; a hand-copied table would have been
wrong about which shapes are new.

Everything in this file and its 11 tests runs at $0 over an evidence file the test writes, so nothing
here reads the run's artefacts and nothing here was red in the commits that precede them.

---

## 3. The paid pass, in the runbook's order

### 3.1 What was created, and when

The three listings were taken **before** anything existed — `serverless list` `[]`, `pod list -a`
`[]`, `network-volume list` `[ qw4nwleanc · mp-srv2 · 100 GB · EU-RO-1 ]`. Without that «before»,
step 7 is a hope rather than a proof.

| time (UTC) | step | balance | delta |
|---|---|---|---|
| 15:16:06 | `runpod_guard --step reader-v3 --step-cap 0.35` — anchor written | $22.4805947722 | — |
| 15:20:40 | staging pod `xv61n7icutxcsl`, **RTX 2000 Ada $0.240/h**, EU-RO-1, `--terminate-after 17:25Z` | | |
| 15:27:33 | pod deleted, `pod list -a` `[]`, guard session logged | $22.4805947722 | **$0.0000** |
| after 15:27:33 | template `faby45gvzx` (READER, no adapter variable) | | |
| after 15:27:33 | endpoint `77o1ing6cy0972` — `gpuIds: ADA_24`, workersMax 1, idle 60 s, `executionTimeoutMs: 900000`, FLASHBOOT, volume `qw4nwleanc` | | |
| ~15:29 → ~15:47 | `--handshake`: the `info` job outstanding, never answered | | |
| before 15:49:41 | endpoint + template deleted; the three listings re-read | | |
| 15:49:41 | guard — **REFUSED**, exit 1 | $22.0888293554 | **$0.3918** |
| 15:52:33 | guard — the same reading to ten decimals, and see §4 for why that is not a stop | $22.0888293554 | $0.3917654168 |
| 16:09:47 | guard — the volume's rent posts and the delta climbs again | — | $0.4033 |

`runpodctl gpu list` was read **today** rather than assumed: RTX 2000 Ada at **$0.240/h**, EU-RO-1,
stock Low — still the cheapest class with stock, and still the one probe-b staged on. `ls
results/spend_reader*` returns exactly one file (Dv392, still fixed).

### 3.2 The staging succeeded, and it is durable

`repo/` moved **`f0fd745` → `aa0ca18` by fetch + hard reset**, never `rm -rf`: the gitignored 467 MB
adapter lives inside `repo/` and is still there at **489 840 816 bytes**, byte-identical to what
probe-b left. The checkout is clean.

Then the strongest check available before an endpoint exists, over **all three** registered texts and
the parser module, rendered by the volume's **own** venv:

```
reader_thread_gm4        b272115637f784ad63c6fb2483e0b0ac3d6381901a096dc1cb5406b81a46c8cd
reader_thread_gm4_v2     9d281bc80f18c91b6b0c32cbcdb37540504be887887d0dd1f1ab1c25841250c5
reader_thread_gm4_v3     22533644cf35420eb18599c7329f80ea5ffa877b7aec8cb9eca292b80998803f
prompts.py (the parser)  dfa7a79f39ed7d6248951f77b89af11b68f086ee376da7fc4a6341d1267d2ee4
```

All four equal this Mac's and all four equal the registration's `prompt_sha256` map and
`parser.sha256`. `start.sh` on the volume already hashed to the checkout's
`scripts/start_5b_worker.sh` (`5b3bcbb2f59372f4`) and was re-copied anyway.

**The volume is staged at this contract's HEAD and stays that way.** Whatever the next contract is,
it does not have to buy this rung again.

### 3.3 `gpuIds` was read back before the first job, and it is free

```
"gpuIds": "ADA_24", "workersMax": 1, "idleTimeout": 60,
"executionTimeoutMs": 900000, "flashBootType": "FLASHBOOT", "networkVolumeId": "qw4nwleanc"
```

The class requested is the class recorded. `executionTimeoutMs: 900000` is the one seconds→
milliseconds conversion point and it converted correctly.

### 3.4 The handshake that never came back — Dv439

`op: info` is not a cheap call on this worker: `Worker` loads lazily at the **first** job, so `info`
is the 31 B NF4 load off the network volume. probe-b's boot to first answer was **2 min 59 s** on a
warm flash-boot cache; probe-a's was **6 min 13 s** cold.

This one was outstanding for **at least twenty minutes** and answered nothing. Two health readings,
about eleven minutes apart, both identical:

```
jobs:    {"completed": 0, "failed": 0, "inProgress": 0, "inQueue": 1, "retried": 0}
workers: {"idle": 0, "initializing": 0, "ready": 0, "running": 1, "throttled": 0, "unhealthy": 0}
```

The guard read $0.3062 of $0.35 with nothing bought, then $0.3918 — over the cap — and refused:

```
REFUSED: reader-v3's $0.35 cap is reached ($0.3918 spent).
         Stop and report — an overrun aborts, it does not raise the cap.
```

**The endpoint and template were deleted the moment the reading was over the cap.** The recovery
clause of step 7 authorises re-creating them «within the same cap»; there is no cap left, and «no cap
raise mid-session» is the contract's own word. The question closes here.

`[cause: cold-start]` — and §7 says why that tag is provisional.

### 3.5 Deleted, and proven

```
$ runpodctl serverless delete 77o1ing6cy0972 → {"deleted": true}
$ runpodctl template   delete faby45gvzx     → {"deleted": true}
$ runpodctl serverless list                  → []
$ runpodctl pod list -a                      → []
$ runpodctl network-volume list              → [ qw4nwleanc · mp-srv2 · 100 GB · EU-RO-1 ]
```

The same three listings were taken **before** anything was created and read the same, the volume
included as the positive control. That is what makes this a deletion proof.

---

## 4. The money, and what cannot yet be said about it

**$0.3918 at the deletion, and it is a LOWER BOUND that is still climbing.** Four readings of the
same step, in the order they were taken:

| reading (UTC) | balance | delta | what it is |
|---|---|---|---|
| 15:27:33 | $22.4805947722 | **$0.0000** | after seven minutes of staging pod — RunPod had posted nothing |
| 15:49:41 | $22.0888293554 | **$0.3918** | minutes after the deletion; **the figure this report quotes** |
| 15:52:33 | $22.0888293554 | $0.3918 | unchanged to ten decimals |
| 16:09:47 | — | **$0.4033** | and moving again |

The two identical readings three minutes apart do **not** mean the meter stopped, and an earlier
draft of this section said they did. They mean the volume's rent posts in coarse chunks: over the
same span the cycle-2 walk's `network-volume` line went $0.0194 → $0.0292, which is $0.0098 of the
$0.0115 the delta gained. **This is Dv412 exactly** — a step meter built on a balance delta measures
the ACCOUNT and never stops ([[a_step_meter_on_a_balance_delta_never_stops]]). The reading taken
closest to the deletion is the one that means anything about the step, and it is the one quoted
everywhere in this report.

**And it cannot be decomposed by subtraction, so this report does not try.** At 15:27:33Z the delta
was exactly $0.0000 while the staging pod had already run seven minutes. The $0.3918 that appeared
later is a settlement event, not a meter anyone watched accumulate
([[a_balance_delta_is_not_a_per_leg_cost]]).

What the billing walk says over the step's window, now:

```
$ runpodctl billing pods           --start-time 2026-08-16T15:16:00Z → []
$ runpodctl billing serverless     --start-time 2026-08-16T15:16:00Z → []
$ runpodctl billing network-volume --start-time 2026-08-16T15:16:00Z → []
```

Nothing has posted. Since the **cycle-2** anchor at 12:14:48Z the only rows are the volume's —
`network-volume` $0.0194 at 15:52 and $0.0292 by 16:09 — and pods and serverless are empty there too.
**Not one second of the staging pod or of the endpoint has been billed into a row yet.**

So, per the contract's own clause: **the deletion-time reading is reported as a LOWER BOUND and
closing the step is a named debt** for tomorrow's first guard run. The guard refuses to close and the
refusal is the evidence:

```
REFUSED: the billing walk over reader-v3's window answered «no billing rows yet»,
         so there is no settled figure to close on.
```

The one thing that can be bounded: the always-on volume rents at the measured ≈$0.0092/h, so over the
33.5 minutes from the anchor to the deletion-time reading its share inside $0.3918 is **at most
≈$0.005**. Taking it out does not bring the step under $0.35.

`results/spend_reader_v3.json` carries the anchor and **one** session entry — the staging note,
written at 15:27:33Z when the delta still read $0.0000. It carries no closing entry and no
deletion-time figure, because `main()` returns on its refusals before the `--note` block runs. That
is the guard behaving correctly and it was **not** worked around by hand: the deletion-time reading
lives in this report, where a number that no walk has settled belongs.

**Cycle 2 read $0.4209 of $20.00 at 15:49:41Z and $0.4325 at 16:09:47Z — $19.5675 remaining on the
later reading. Phase 4 stays CLOSED at $32.4708 of $33.00.** Cycle-2 figures carry their reading time
for the same reason the step's do.

### 4.1 The number this run really bought

The registration's `setup_usd` is **$0.0900**, derived from probe-b's settled step minus its own
reading. This session spent **≈$0.39 before a single thread was read**. That is a 4.3× miss on the
one constant every projection in the reader programme rests on, and it is the most consequential
thing this contract measured.

A $0.35 cap cannot cover a boot of this length. Whether the answer is a larger cap, a pre-warmed
endpoint, a boot proven on a cheap pod before the serverless meter opens (`scripts/runbook_srv2b.md`
§C.3 already does exactly that for config A), or a different card — that is an operator decision and
this report does not take it.

---

## 5. Finding 1 — bar 3's population grew from five threads to six, and nobody said so

Measured at $0, in `tests/test_reader_v3_verdict.py`, and it is a defect in the frozen registration.

`prereg_reader_probe_v2.json` registers bar 3 over **`["N2","N3","N4","N5","N6"]`** and carries an
`excluded_with_cause` block for N1:

> carried unchanged from v1: the reference's own S list reads a signal inside this thread (S1, msg
> 21420) … A bar that failed the reader for agreeing with the reference would measure nothing.

`prereg_reader_probe_v3.json` registers it over **`["N1","N2","N3","N4","N5","N6"]`**. The producer
`write_reader_prereg_v3.bars()` takes `[one["id"] for one in gold["noise_threads"]]` — every noise id
in the gold — and **the exclusion did not come with it**. `docs/reports/reader-v3-prep.md` never
mentions the widening; `tests/test_reader_prereg_v3.py` asserts `scored_over == every noise id`, so
the widening is now law and under test while the reason it was once narrower is nowhere.

**The consequence is not cosmetic: a reader that agrees with the reference now FAILS bar 3.** S1 is a
signal the reference itself reads in `@VARUS_channel:10529`, which is N1's thread.

Scored **as registered**, over six. The bar recomputed over v2's five is reported beside it, and the
test plants one signal in N1 to show the two disagreeing on the same evidence — the registered bar
fails with `signals: 1`, the beside-bar passes with `signals: 0`. Dv440, `[cause: registration-defect]`

It also means the paired column against probe-b compares **two different bars**, and the verdict
record says so in the field rather than in a footnote.

---

## 6. Finding 2 — gold r2 is the bar, and the vocabulary now points the other way

Also measured at $0, also a property of the frozen registration.

Ruling 4 adjudicated «категория» and «категория_личное» as **one class**. r2 applies that by
re-labelling twelve gold cells from the first word to the second, and the registration makes r2 the
bar so that «the collapsed reading is the BAR rather than a number reported beside it».

But **the v3 prompt still offers both words.** `prompts.READER_SUBJECT_TYPES` is
`(молочный_бренд, сеть_ритейлер, категория, категория_личное, не_наш_рынок)` and none of the six
`_swap` calls that make v3 touches it. So a reader that answers the reference's «категория» on one of
the eight per-comment cells r2 moved is scored **wrong** by the very bar built to adjudicate the two
as one class — the opposite direction from probe-b, where the reader said «категория_личное» and the
gold said «категория».

probe-b's evidence says this is not hypothetical: `results/reader_probe_b_refusals.json` records msg
21599 as gold «категория» against a reader «категория_личное», and collapsing the two moved bar 4
from 0.357 to 0.429.

Scored **as registered** — r2, no collapse in the gating number. The collapsed reading is reported
beside bars 1 and 4, applied to gold and to the answers alike, and the test proves the direction: a
reader answering «категория» on the eight moved cells scores 6 of 14 as registered and 14 of 14
collapsed. Dv441, `[cause: registration-defect]`

---

## 7. The bars

**Every one is UNSCORED, and none of them failed.** Zero threads were read; there is no evidence file
and no run record. The scorer's own refusal is the artefact that says so:

```
$ PYTHONPATH=src python3 scripts/score_reader_v3.py
results/reader_v3_w1.jsonl: no evidence — there is nothing to score
```

| bar | threshold | result |
|---|---|---|
| 1 flagships | 5 of 5 cases | **UNSCORED** — no thread read |
| 2 entity cases | 4 of 4 cases | **UNSCORED** — no thread read |
| 3 noise | 0 signals over the threads with a verdict | **UNSCORED** — and see §5 |
| 4 per-comment | rate ≥ 0.80 against gold r2 | **UNSCORED** — and see §6 |
| 5 time and cost | ≤ $0.35 all-in | **BREACHED** — $0.3918 lower bound, unsettled |

The non-gating readings the contract asked for — the refusal census by shape, the repair census,
`finish_reason` per thread and the tokens-per-`per_comment`-row measurement Dv433 needs for the
window — are all implemented, all tested, and all **unmeasured**. The 129-thread window's output
ceiling stays an open risk with no reading against it.

---

## 8. Deviations

| id | what | cause |
|---|---|---|
| **Dv436** | Step 0's tail carried two files outside `knowledge/**`. Both are the team lead's — the STATUS edit recording the `reader-v3-prep` acceptance, and this contract itself. Committed verbatim by path in their own commit, never edited; probe-b §0.1 and `fabd2f3` are the precedent. The STOP clause is about executor work in progress. | `[cause: team-lead-files]` |
| **Dv437** | The registration's `max_slowdown_vs_probe_b: 1.165` is a whole-pass bound; the gate stops at **69.592 billed seconds / 1.117×**. Published in the run record with both numbers and driven from both sides by a test. | `[cause: registration-arithmetic]` |
| **Dv438** | `wall_seconds` starts at the process's first request, so a cold endpoint puts its boot inside the gate's window. Reading kept pessimistic, all three legs recorded, loud line on a gap over 30 s. | `[cause: instrument-change]` |
| **Dv439** | `scripts/preflight_serving_guards.py` asserted `len(set(rendered)) == 2` over `sorted(prompts.READER)` — so it **FAILED** the moment v3 was registered, refusing a paid run because the family it guards had grown. Dv428's shape, one script over. Now against `len(prompts.READER)`; negative control checked both ways at the console. 63 PASS / 0 FAIL, exit 0. → `cca0534` | `[cause: instrument-change]` |
| **Dv440** | Bar 3's registered population widened 5 → 6 between v2 and v3 and v2's stated exclusion of N1 was dropped silently. §5. | `[cause: registration-defect]` |
| **Dv441** | Gold r2 is the bar while the prompt still offers both vocabulary words, so the collapse now points the other way. §6. | `[cause: registration-defect]` |
| **Dv442** | zsh does not word-split an unquoted `$SSHOPT`, so the first staging `ssh` loop failed on option parsing for five minutes while the pod billed — a footgun `scripts/runbook_4b.md` §90 already names, in a shell that was not the one it was written for. ≈$0.02 of the cap. Options written out literally afterwards. | `[cause: harness]` |
| **Dv443** | **The cap was consumed before a single thread.** ≥20 minutes of a worker RunPod reported `running` with `completed: 0` and `retried: 0`. §3.4. | `[cause: cold-start]` |
| **Dv444** | The step cannot be CLOSED: the billing walk has posted nothing, and the guard refuses to settle on it. The deletion-time reading stands as a LOWER BOUND and closing is a named debt for the next guard run. | `[cause: billing-latency]` |
| **Dv445** | `tests/test_repair_phase4_ledger.py`'s silence check demanded every paid step run's balance appear in `results/spend_phase4.json`. Phase 4 is CLOSED and the guard writes a step's session into `results/spend_cycle2.json`, so **this contract's first `--note` reddened a suite that had been green for a week** — the run was witnessed exactly as it should be, by the other ledger. Both live ledgers are read now, the excuse table is untouched, and the check still names a run witnessed by neither. §8.1. → `6fde752` | `[cause: line-took-over]` |

### 8.1 Dv445, and the control that came with it

The invariant was never «the phase ledger hears about it» — it is «the ledger the guard reads before
a start hears about it», and since amendment 3.23 (1) there are two of those. The old check was a
true statement about a world in which Phase 4 was the only place a paid session could land, and it
stopped being true the moment the line took over ([[the_control_whose_premise_stopped_being_true]],
[[a_green_suite_can_have_a_shelf_life]] — the operator's first tick reddens it).

A guard extended to a second source without a control over that source is a guard tested on the half
it already had, so there are **two** negative controls now, one per ledger. The old one drops skub2's
entry from the phase ledger. The new one empties the line's sessions and requires every step that ran
after the close to be named — proven at the console rather than asserted:

```
with the real line ledger : []
with it emptied           : [('results/spend_reader_v3.json', '2026-08-16T15:27:33+00:00', 22.4805947722)]
```

And the green path now asserts its own premise — Phase 4 carries a closing entry and the line's
sessions are non-empty — so an empty cycle-2 ledger cannot make the union silently equal the older
half while the test goes on passing.

**Dv443's tag is provisional, and one free reading decides it.** When
`runpodctl billing serverless --start-time 2026-08-16T15:16:00Z` posts a `timeBilledMs` for
`77o1ing6cy0972`, it discriminates between two different findings:

* **≈1 100 s billed** → a worker that really was loading the whole time. The cause is the cold start
  and the answer is about the cap, the card, or pre-warming.
* **≪1 100 s billed** → the worker was not executing for most of that window, and what was seen is
  the srv-2b delivery shape (`inQueue` with a worker assigned, no execution) that `MIN_RUNPOD_SDK`
  exists to prevent — a different finding and a different next contract.

The evidence available now leans to the first: `workers.running: 1` says RunPod believed the job was
executing, which is **not** srv-2b's shape (there, workers sat available and idle), and
`jobs.retried: 0` says nothing was re-dispatched. That is evidence, not a conclusion. The reading is
free and it is the debt above.

---

## 9. Process signals

1. **A projection published as a ratio is not the ratio the gate uses.** 1.165× and 1.117× are both
   true sentences about the same registration and only one of them stops a run. Solving the gate's
   own inequality backwards, for the seconds instead of the dollars, is what made the difference
   visible — and cost nothing.
2. **A rounded field cannot carry a boundary.** $0.3499948 and $0.3500064 both print as `0.3500`.
   Where a verdict turns on an inequality, the record has to publish the pair the inequality is over.
3. **A guard written for a family of two refuses when the family becomes three.** Twice now
   (Dv428, Dv439), in two different files, both times toward *refusing* — which is the safe
   direction and also the one that costs a paid session five minutes of confusion at the worst
   moment.
4. **The rung that produces nothing is inside the cap, and it can be the whole cap.**
   [[the_setup_is_inside_the_cap]] said to divide the cap by the measured rate before opening a gated
   run. It was divided — and the setup constant that went into the division was measured on a boot
   four times faster than the one that turned up.
5. **The findings that survived are the ones bought before the money.** Both §5 and §6 are readings
   of the frozen registration, made by tests at $0. The paid rung produced no reading at all, and
   the contract is not empty because of what preceded it.

---

## 10. What this leaves the operator

**The instrument is built, staged and frozen; the measurement is not made.**

* `results/prereg_reader_probe_v3.json` is untouched. The driver, the scorer and 21 tests are
  committed and green. The volume is staged at `aa0ca18` and renders all three reader texts and the
  parser byte-identically — **the next attempt does not pay for staging again.**
* **The one attempt is spent and no bar was scored.** Under the contract's own rule that closes the
  question; re-opening it is an operator decision, not this session's.
* **Two defects in the frozen registration are measured and reported** (§5, §6). Neither can be
  fixed by the run contract — a registration a run may amend is a registration the run wrote — and
  both change what the next one should register: whether bar 3 is over five threads or six, and
  whether the vocabulary collapse belongs in the gold, in the prompt's subject list, or in the
  scorer.
* **`setup_usd: 0.0900` is wrong by 4.3× on today's evidence.** Any future reader cap has to be set
  against a boot that can cost $0.39, or against a runbook that proves the boot on a $0.24/h pod
  before the serverless meter opens.
* **One debt, and it is free to pay:** the first guard run of the next session settles
  `reader-v3` and, with it, decides Dv443's cause.

---

## Verify

```
$ make check                            # baseline, at 4bc128b
2623 passed, 2 skipped in 190.81s

$ make check                            # after D1, D2 and the preflight fix, at cca0534
2644 passed, 2 skipped in 249.19s

$ make check                            # RED after the first --note, and Dv445 is why
2 failed, 2642 passed, 2 skipped
FAILED tests/test_repair_phase4_ledger.py::test_no_paid_step_ledger_is_silent_in_the_phase_ledger
FAILED tests/test_repair_phase4_ledger.py::test_the_silence_check_fires_when_a_phase_entry_goes_missing

$ make check                            # after the witness fix, at 6fde752
2645 passed, 2 skipped in 252.74s
$ ruff format --check . && ruff check .
316 files already formatted
All checks passed!

$ HF_HUB_OFFLINE=1 PYTHONPATH=src python3 scripts/preflight_serving_guards.py
63 PASS · 0 FAIL · exit 0

$ PYTHONPATH=src python3 scripts/probe_b_population.py
probe-b population: 23 threads · 134 payable comments · 4 injected
  digest ccef35fa4b9c771f…

$ runpodctl serverless list && runpodctl pod list -a && runpodctl network-volume list
[]
[]
[ qw4nwleanc · mp-srv2 · 100 GB · EU-RO-1 ]      # the positive control

$ python3 scripts/runpod_guard.py --step reader-v3 --step-cap 0.35 ; echo $?   # 15:49:41Z
PHASE 4 CLOSED    $32.4708 of $33.00
CYCLE 2 SPENT     $0.4209 of $20.00
REMAINING         $19.5791
READER-V3 SPENT      $0.3918 of $0.35  (anchor $22.48 from runpod_balance_at_reader-v3_start)
  balance delta   $0.3918
  billing since   UNAVAILABLE (no billing rows yet) — the delta stands alone as a LOWER BOUND
REFUSED: reader-v3's $0.35 cap is reached ($0.3918 spent). Stop and report — an overrun aborts,
         it does not raise the cap.
1

$ python3 scripts/runpod_guard.py --step reader-v3 --step-cap 0.35                # 16:09:47Z
CYCLE 2 SPENT     $0.4325 of $20.00
REMAINING         $19.5675
READER-V3 SPENT      $0.4033 of $0.35   # Dv412: the delta measures the ACCOUNT and never stops
  billing since   $0.0292 (read)        # cycle-2 window; network-volume only, pods and serverless $0

$ python3 scripts/runpod_guard.py --step reader-v3 --step-cap 0.35 --close --note "…" ; echo $?
REFUSED: the billing walk over reader-v3's window answered «no billing rows yet», so there is no
         settled figure to close on.
1

$ ls results/spend_reader*
results/spend_reader_v3.json            # Dv392: one step, one ledger

$ PYTHONPATH=src python3 scripts/score_reader_v3.py
results/reader_v3_w1.jsonl: no evidence — there is nothing to score
```

**The per-commit rule, stated rather than listed:** the verifier ran on the tree of every commit that
moves code or a test. `0c97b3e` and `8598948` move only vault and team-lead documentation and nothing
in `tests/` opens `knowledge/` or `docs/reports`.

**Two commits are RED on their own trees and are named rather than rewritten.** Checked out one by
one in a throwaway worktree rather than reasoned about:

```
aa0ca18  ->  11 passed          # the anchor alone; no gpu_sessions entry to witness yet
ae58b25  ->  2 failed, 9 passed # the first --note lands, and Dv445 fires
1b7b0bc  ->  2 failed, 9 passed # this report's first version, on the same tree
6fde752  ->  12 passed          # the witness fix, and the second negative control
```

The honest history is a red commit and its repair. The two new test files are
independent of each other — neither imports the other's subject — so each of `53fc13b` and `1846e5a`
is green on its own tree.

**Commits:** `0c97b3e` · `8598948` · `53fc13b` · `1846e5a` · `cca0534` · `aa0ca18` · `ae58b25` ·
`1b7b0bc` (this report's first version) · `6fde752`, plus this report's own amendment.

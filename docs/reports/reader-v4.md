# reader-v4 — 23 threads read on a pod for $0.2446, and the reader fails two of five bars

**The measurement is made.** Everything three contracts have been trying to buy is on disk: the v3
instrument read all 23 threads of the registered population, one pass, inside the cap, and the bars
were computed against gold r2 under the two scoring differences the team lead ruled. Two of the five
bars FAIL. That is the answer, and by the registration's one-attempt clause it closes the question:
what follows is a new registration after a sitting, never a second pass at this one.

```
1_flagships              FAIL   2 of 5 cases   (uncollapsed 1 of 5)
2_entity_cases           PASS   4 of 4 cases
3_noise                  PASS   0 signals over five answered threads
4_per_comment_agreement  FAIL   0.500          (uncollapsed 0.357; the bar is 0.80)
5_time_and_cost          OPEN   $0.2446 lower bound of $0.35 — the walk has not posted
```

Verdict record `results/reader_v4_verdict.json` (`7f5c96c8352ad052…`), evidence
`results/reader_v4_w1.jsonl` (`bd696f803b6c4ecb…`), the pod's own raw file
`results/reader_v4_pod.jsonl` (`6f59a32be5c13c4f…`) and its live log `results/reader_v4_pod.log`.

## 0. Read back, one line each

**The three registered differences.** (1) Bar 3 is over v2's five noise threads `N2–N6` with v2's own
`excluded_with_cause` for N1, read out of the frozen v2 record and checked against a literal in the
producer; (2) the vocabulary collapse is the BAR and it is symmetric — «категория» ≡
«категория_личное» on the gold cell and on the reader's answer alike, wherever bars 1 and 4 compare
`subject_type`; (3) the money is a pod's — one machine billed for every second it exists, with a
kill rule on the boot.

**The kill rule's clock and its ceiling.** The clock is seconds since the `pod create` response,
because that is when the meter started; the ceiling is the contract's twelve minutes from the
generation process starting, and the affordability deadline (usable seconds minus the reading
projection) is measured from create — the two are put on the create-elapsed axis before they are
compared and the tighter binds.

**What is persisted per row.** The rendered request and its sha256, the raw reply byte for byte, the
parse outcome with `repairs` or the refusal's reason, the seconds, `finish_reason` and the token
usage — flushed one line at a time on the pod as each reply lands, and again on the Mac when the
replies are parsed.

**The deletion proof's shape.** Three listings after the delete — `pod list -a`, `serverless list`,
`network-volume list` — read against the same three taken before anything was created, with the
volume appearing in both as the positive control that the command discriminates at all.

## 1. Step 0 — the tail and the v3 debt

The live `git status` carried three vault files and two the executor may not edit. Committed in two
commits by path, never `git add -A`:

- `4621df4` — `knowledge/**`: the `/save` checkpoint's daily-log section, `hot.md`'s curated block
  and the regenerated index.
- `64bc710` — `docs/STATUS.md` and `docs/PROMPT-reader-v4.md`, **verbatim**. Both are the team
  lead's. **Dv446.**

**The v3 step is CLOSED at $0.3936**, `bf2502f`. The walk had posted, so the debt the previous
report named is paid off with a number instead of a bound:

```
$ python3 scripts/runpod_guard.py --step reader-v3 --step-cap 0.35 --close --note "…"
REFUSED: reader-v3's $0.35 cap is reached ($0.3936 spent). Stop and report — an overrun aborts, it does not raise the cap.
CLOSED spend_reader_v3.json at $0.3936 — entry APPENDED
READER-V3 CLOSED     $0.3936 of $0.35  (settled at 2026-08-16T17:08:16+00:00, window from 2026-08-16T15:16:06+00:00)
  pods            $0.0218
  network-volume  $0.0097   <- always on, beside the run and never inside it
  serverless      $0.3718
```

Exit 1, and both halves of that output matter: the close appends the settled figure and the refusal
above it records the breach. serverless $0.371765 is the 1 211 005 ms boot on `77o1ing6cy0972` that
answered nothing; pods $0.021812 is the staging pod and the zsh `$SSHOPT` loop. Closing is
bookkeeping, not amnesty, and the guard says so on its own.

### 1.1 That close reddened a week-green suite, and the guard was right — Dv447

`tests/test_repair_phase4_ledger.py` went red naming the file, the timestamp and the balance:
`('results/spend_reader_v3.json', '2026-08-16T17:08:16+00:00', 22.0675725277)`. Two things lined up.
`--close` skips the `--note` branch that writes the live ledger, **and** a step over its cap returns
before that branch is reached at all — so a fresh balance reading existed in one file and
`results/spend_cycle2.json`, the file the guard reads before every start, had never heard it.

Fixed in `ae7be77`: the witness is written **beside the closing entry**, not after the refusal, so a
cap breach cannot take it with it. `line_reading()` is now the one shape both the `--note` path and
a close write — the check that reads them matches on `balance`, and two spellings would be two
shapes in one file. The new test drives a close whose settled figure BREACHES its cap (exit 1, line
written anyway); it is red without the fix with `IndexError: list index out of range`, and its
negative control is `--close` with no step, where the line closes itself and a second entry would
double-count. `results/spend_cycle2.json` also carries the line's own later reading of the same
money, taken by the guard at 17:42:26Z — the balance had not moved, so the exact-balance match
closes with no excuse needed.

## 2. D1 — the registration, and one number the contract could not have known

`results/prereg_reader_probe_v4.json` — `8a26784c85deb806…`, frozen in `12c3707` and amended once in
`f1bb539`, **both before the pod existed**. `scripts/write_reader_prereg_v4.py` rebuilds it
byte-identically; `tests/test_reader_prereg_v4.py` holds all eleven of its claims.

The whole `instruments` block is **object-equal to v3's** — not re-derived. A re-derived prompt sha
would agree today and be free to disagree the day `prompts.py` moves; equality with the frozen block
is the strongest available form of «the instrument does not move».

**The contract's worked example is priced at $0.59/h and the card is not that price — Dv448.**
`runpodctl gpu list`, read on the day, EU-RO-1 SECURE:

| card | $/h | EU-RO-1 stock |
|---|---:|---|
| **NVIDIA GeForce RTX 4090** | **0.74** | Low |
| NVIDIA RTX PRO 4500 Blackwell | 0.72 | High |
| NVIDIA RTX PRO 4000 Blackwell | 0.57 | Medium |
| NVIDIA L4 | 0.49 | Low |

So every figure is recomputed from $0.74/h and the contract's «≈$0.12 for a killed boot» becomes
**$0.148**. The cap buys **1 702.7 s**, of which **1 642.7 s** are usable once 60 s are held back for
the deletion itself — a pod killed at exactly the second the cap buys has already spent the cap.

The registration publishes the arithmetic as a TABLE rather than a forecast, because three boots are
on record for this stack and they disagree by 6.7× (probe-a 373 s, probe-b 179 s, reader-v3 >1 200 s):

| boot | seconds left for reading | slowdown vs probe-b that fits | all-in at probe-b's rate |
|---:|---:|---:|---:|
| 180 s | 1 267.7 | 1.742× | $0.2267 |
| 300 s | 1 147.7 | 1.577× | $0.2513 |
| 480 s | 967.7 | 1.330× | $0.2883 |
| 600 s | 847.7 | 1.165× | $0.3130 |
| 720 s | 727.7 | 1.000× | $0.3377 |

The reading projection is probe-b's **worker** leg (727.664 s) and not its wall leg (802.103 s): wall
carries a serverless queue and an HTTP round trip a pod's contiguous generation loop does not have,
and taking the larger figure would be a unit error rather than pessimism.

### 2.1 The projection had one leg and should have had two — Dv449

v4's first draft of gate 3 projected the unread remainder one way, unread threads ÷ read threads.
v3's registration had registered two — «the pessimistic of the per-thread and per-payable-comment
projections» — and that is part of what «everything else copied» was meant to preserve. A single leg
is looser in the one direction a cap guard may not be loose in, and this population's threads carry
between 1 and 15 payable comments against a prompt that asks for an output row per comment.

Restored in `f1bb539`, **before the pod existed**, so it is a correction of my own omission and not a
fourth difference. The driver's own check refused the run while the file differed from HEAD, which is
the guard doing its job:

```
results/prereg_reader_probe_v4.json differs from HEAD. The committed registration is the one this
run is read against — and it is FROZEN: restore the file, do not commit the change.
```

## 3. D2 — the transport

Two new files, `ac6bfee`. **`scripts/read_threads_reader_v4.py`** is the Mac half — the pack, the two
clocks, the gates, the ingest; **`scripts/reader_v4_pod_runner.py`** is the only thing that runs on
the pod, and it neither parses nor scores.

What crosses is a **pack**: the 23 thread items with the registered sha of each rendered request. The
pod renders each one **itself** through `prompts.reader_messages_gm4` and refuses unless the sha
matches — one check that covers both a comment edited in the store and a volume a session behind.
The same check runs first on the Mac, where it costs $0. Both refusals — the three-prompt handshake
and the per-request sha — run **before the model is loaded**, and their tests assert `loaded == []`
with the passing premise asserted beside them.

Two smaller decisions, both about keeping a proof intact:

- the runner is scp'd to `/workspace/`, **never** into `/workspace/repo/scripts/`, so the checkout's
  `git status --short` stays empty and remains the staging proof. **Dv452.**
- the pack **copies** the registration's dicts instead of aliasing them. A pack that shares the
  record's objects can be edited into agreeing with it, and the pod's whole handshake is that the
  two can differ. (Found by a test that poisoned the module-level record through the pack.)

**`--gate` reads the Mac's copy of a file the pod writes — Dv453.** «No reply has landed» is a
statement about a FILE. The runbook puts the scp inside the poll loop, before every gate, and the
boot-kill block carries `read_from` with the copy's path and the moment it was fetched, so a stale
reading is visible in the artefact rather than arriving as an unexplained KILL.

The kill rule is **code, not eyeballing**: `--gate` returns **3 = WAIT**, **2 = KILL/STOP**,
**0 = GO**, and the watch loop is a command.

## 4. The run

`scripts/runbook_reader_v4.md` is the order that was followed. Anchor `05df60d` at
**$22.0675725277, 2026-08-16T17:49:04Z** — written before the pod existed and never regenerated.
Before-state: `pods []`, `serverless []`, volume `qw4nwleanc` in EU-RO-1.

| create-elapsed | UTC | what | spent |
|---:|---|---|---:|
| 0 s | 18:00:12 | `pod create` — `p7kyjc5ak4pq1n`, RTX 4090, RO, **`costPerHr` 0.74** as registered | $0.0000 |
| 17 s | 18:00:29 | ssh up; pack + runner scp'd | $0.0035 |
| 31 s | 18:00:43 | volume checkout verified: `aa0ca18`, `git status --short` empty, `/workspace/hf` present, `NVIDIA GeForce RTX 4090, 24564 MiB` | $0.0064 |
| **39 s** | 18:00:51 | generation launched — **inside the 195.0 s pre-generation budget**, so the twelve minutes binds at create-elapsed **759.0 s** | $0.0080 |
| 39 s | 18:00:51 | instrument OK · parser `dfa7a79f39ed7d62…` · 23 requests match their shas | |
| 214 s | 18:03:46 | **READY** — boot **175.1 s** | $0.0440 |
| **268 s** | 18:04:40 | first reply, **36.621 s**, threshold **62.496 s** → **GO** | $0.0550 |
| 787 s | 18:13:19 | re-gate at 12 threads: 45.444 s/thread, projected 1 286.7 s, still GO | $0.1617 |
| 1 083 s | 18:19:15 | **DONE · 23 replies** | |
| **1 143 s** | 18:19:15 | `pod delete` — `"deleted": true` | **$0.2350 at the meter** |

The go/no-go, verbatim from `results/reader_v4_run.json`, at the first reply:

```json
{"threads_read": 1, "threads_unread": 22,
 "payable_comments_read": 7, "payable_comments_unread": 127,
 "elapsed_since_create_seconds": 267.8, "measured_seconds_per_thread": 36.621,
 "projections": {"by_thread": {"factor": 22.0, "seconds": 805.7},
                 "by_payable_comment": {"factor": 18.1429, "seconds": 664.4},
                 "binding": {"factor": 22.0, "seconds": 805.7, "which": "by_thread"}},
 "slowdown_vs_probe_b": 1.158, "usable_seconds": 1642.7,
 "projected_total_seconds": 1073.4, "headroom_seconds": 569.3,
 "seconds_per_thread_that_still_fits": 62.496, "verdict": "GO"}
```

Both legs computed, the pessimistic one binding, and the verdict re-derives from the pair of seconds
and never from the dollars.

### 4.1 The deletion, proven

```
$ runpodctl pod delete p7kyjc5ak4pq1n     →  { "deleted": true, "id": "p7kyjc5ak4pq1n" }
$ runpodctl pod list -a                   →  []
$ runpodctl serverless list               →  []            (none was ever created)
$ runpodctl network-volume list           →  [ { "dataCenterId": "EU-RO-1", "id": "qw4nwleanc",
                                                 "name": "mp-srv2", "size": 100 } ]
```

The third listing is the positive control: three `[]` would prove the command runs, not that the pod
is gone.

### 4.2 The money, and the one thing that is not settled — Dv455

```
$ python3 scripts/runpod_guard.py --step reader-v4 --step-cap 0.35
READER-V4 SPENT      $0.2446 of $0.35  (anchor $22.07 from runpod_balance_at_reader-v4_start)
  balance delta   $0.2446
  billing since   UNAVAILABLE (no billing rows yet) — the delta stands alone as a LOWER BOUND
CYCLE 2 SPENT     $0.6868 of $20.00
REMAINING         $19.3132
```

`--close` was attempted and **refused**, correctly:

```
REFUSED: the billing walk over reader-v4's window answered «no billing rows yet», so there is no
settled figure to close on.
```

So bar 5 is **OPEN** at a lower bound of **$0.2446** — which also carries the always-on volume, and
that belongs to no step. The meter's own arithmetic says the pod itself cost **1 143 s × $0.74/h =
$0.2350**. Closing is the named debt for the next guard run and a figure is never invented here.

## 5. The bars

### Bar 1 — flagships: 2 of 5, FAIL

| case | thread | signals found |
|---|---|---|
| F1 | `@VARUS_channel:10613` | F1a ✓, F1b ✗, F1c ✗ |
| F2 | `@matusi_ukr:22303` | F2a ✗ |
| F3 | `@mandziak:3676` | F3a ✗ — **the reply refused**, `two disagreeing objects: quote` |
| F4 | `@mandziak:3703` | F4a ✓ |
| F5 | `@matusi_ukr:22272` | F5a ✓ |

Scored **collapsed**, which is what carries it from 1 to 2: F4's «похвала» signal is answered with
the reference's word and the ruling makes that right. probe-b also reached 2 of 5.

### Bar 2 — entity cases: 4 of 4, PASS

E1 `не_наш_рынок` on Гармонія, E2 `молочный_бренд` on Селянське, E3 `сеть_ритейлер` on Varus, and E4
answered as the ABSENCE case it is — no entity names varto in either of its two threads. probe-b
reached 2 of 4, so this bar is a real gain and it is the one bar the collapse does not touch.

### Bar 3 — noise: 0 signals over five answered threads, PASS

All five of `N2–N6` returned a parsed verdict and none of them carried a signal. N1
(`@VARUS_channel:10529`) is excluded by v2's cause, restored — and, reported beside the bar, **its
reply refused** under v3 (`two disagreeing objects: name`), so v3's six-thread reading would have
been 0 signals over five answered threads and one refusal. On this evidence the two registrations
agree; they did not have to.

`@sashafitnesslife:3939` is N3 and carries **0 payable comments** — its zero is produced by the
gate's plus-spam silencer and not by the reader, exactly as v2 registered and as v4 carries forward.
So four of the five threads can move this bar.

### Bar 4 — per-comment agreement: 0.500, FAIL (the bar is 0.80)

14 gold rows: **7 agreed, 4 disagreed, 3 absent**.

| msg_id | what happened |
|---|---|
| 21601 | `subject_type` gold `категория` → reader `сеть_ритейлер` |
| 580124 | `subject_type` gold `молочный_бренд` → `сеть_ритейлер`; `stance` gold `negative` → none |
| 580129 | `subject_type` gold `категория` → `молочный_бренд` |
| 48283 | `subject_type` gold `категория` → none |
| 47899, 47902, 578951 | **absent** — the reader wrote no `per_comment` row for them at all |

Every gold value above is the **collapsed** one, so not one of these four is a vocabulary
disagreement: they are the reader reading a comment about a category as a comment about the chain.

The collapse is worth exactly the gap between the two columns: **0.357 uncollapsed → 0.500 as the
bar**. Ruling 4 is measured now, and it is not enough on its own.

### Bar 5 — see §4.2. OPEN, lower bound $0.2446 of $0.35.

## 6. What the instrument did, beside the bars

**19 of 23 replies parsed, against probe-b's 13.** And **zero container repairs fired** — every one of
the nine registered repair names shows 0. The registration forbids attributing a recovered reply to
the parser or to the prompt, and this report does not; what the census does establish, without an
ablation, is that **no recovered reply came through a repair**, because none ran. The other half of
A did fire: the refuse-on-conflict clause **removed two replies**, one of which probe-b had parsed
(`@VARUS_channel:10529`). A's net effect on the parse count here is 0 recovered and 2 refused.

| refusal shape | v4 | probe-b as run (v2) | probe-b's replies re-read under today's parser |
|---|---:|---:|---:|
| `two disagreeing objects: name` | 1 | — | 1 |
| `two disagreeing objects: quote` | 1 | — | — |
| `signals.aspect is not a string` | 1 | 1 | 1 |
| `missing field: evidence` | 1 | 2 | 2 |
| `missing field: entities` | — | 2 | — |
| `signals is not a list` | — | 4 | — |
| `noise is not a list` | — | 1 | — |

The three container shapes probe-b drowned in — `signals is not a list`, `noise is not a list`,
`missing field: entities` — are gone. `two disagreeing objects: quote` is new against both baselines.

**The output ceiling, Dv433's reading, bought.** `finish_reason: length` on **0 of 23**, same as
probe-b. Over the 19 parsed threads: 15 299 completion tokens, **93 `per_comment` rows returned
against 111 requested (0.838)**, so **164.51 tokens per returned row and 137.83 per requested row**.
Even under a prompt that asks for a row for EVERY comment, one row in six is missing — which is also
where three of bar 4's absences come from.

**The window re-price this unlocks.** The reader census cell's largest thread carries **125** payable
comments (`@matusi_ukr:22058`). At 137.83 tokens per requested row that is **~17 200 output tokens
for one thread**, against a registered ceiling of 2 000. Computed here, decided nowhere: no window
pass is opened by this contract, and the three threads above a hundred payable comments were already
named as a window risk.

**Seconds.** 907.6 s of generation over 23 threads = **39.461 s a thread**, against probe-b's
31.6376 s on the same card and the same threads: **1.247×**. v3's longer output is what that buys,
and the registration called the 727.664 s projection a floor for exactly this reason.

| thread | payable | probe-b s | v4 s | probe-b | v4 |
|---|---:|---:|---:|---|---|
| `@VARUS_channel:10348` | 7 | 30.8 | 36.6 | missing field: entities | parsed |
| `@VARUS_channel:10360` | 2 | 38.1 | 39.0 | missing field: entities | parsed |
| `@VARUS_channel:10366` | 12 | 22.9 | 52.3 | parsed | parsed |
| `@VARUS_channel:10451` | 4 | 19.0 | 33.6 | parsed | parsed |
| `@VARUS_channel:10465` | 5 | 29.1 | 38.7 | parsed | parsed |
| `@VARUS_channel:10471` | 5 | 41.6 | 48.8 | parsed | parsed |
| `@VARUS_channel:10529` | 2 | 29.1 | 29.5 | parsed | **two disagreeing objects: name** |
| `@VARUS_channel:10593` | 2 | 31.4 | 24.7 | missing field: evidence | parsed |
| `@VARUS_channel:10603` | 5 | 36.3 | 48.5 | parsed | parsed |
| `@VARUS_channel:10613` | 10 | 78.5 | 94.6 | parsed | parsed |
| `@mandziak:3676` | 9 | 41.2 | 55.2 | noise is not a list | **two disagreeing objects: quote** |
| `@mandziak:3684` | 12 | 27.9 | 43.9 | parsed | parsed |
| `@mandziak:3689` | 8 | 33.0 | 40.7 | signals.aspect is not a string | signals.aspect is not a string |
| `@mandziak:3701` | 3 | 9.1 | 16.4 | parsed | parsed |
| `@mandziak:3703` | 9 | 37.1 | 55.8 | parsed | parsed |
| `@matusi_ukr:22242` | 12 | 48.2 | 45.3 | parsed | parsed |
| `@matusi_ukr:22272` | 15 | 71.3 | 93.4 | parsed | parsed |
| `@matusi_ukr:22303` | 2 | 41.2 | 38.5 | parsed | parsed |
| `@retsepty:7312` | 3 | 11.1 | 11.0 | signals is not a list | parsed |
| `@retsepty:7325` | 2 | 10.0 | 9.8 | signals is not a list | parsed |
| `@retsepty:7327` | 1 | 7.9 | 7.6 | signals is not a list | parsed |
| `@sashafitnesslife:3939` | 0 | 6.7 | 6.3 | signals is not a list | parsed |
| `@tarilka_malyuka:715` | 4 | 26.3 | 37.4 | missing field: evidence | missing field: evidence |

**The paired columns, and which of them are the same measurement.** Bar 3 is the only bar paired
outright — v4 restores exactly the five threads probe-b was scored on. Bars 1 and 4 are paired only
on their COLLAPSED columns (probe-b 2 of 5 and 0.429; v4 2 of 5 and 0.500), and even then bar 4's two
sides rest on different golds, which is the whole reason the collapse is the bar. The seconds columns
are **not the same unit**: probe-b's are billed serverless worker seconds, v4's are a pod's
generation seconds around one `ReaderClient.read` call, and the pod's boot and idle are in neither —
bar 5 is where the money is.

## 7. Deviations

| id | what | cause |
|---|---|---|
| **Dv446** | Step 0's tail carried two files outside `knowledge/**` — `docs/STATUS.md` and this contract. Both are the team lead's; committed verbatim by path in their own commit, never edited. | `[cause: team-lead-files]` |
| **Dv447** | Closing the v3 step reddened a week-green `make check`: the guard's `--close` never witnessed the live line ledger, and a cap refusal returns before the `--note` branch. Fixed in the guard, beside the closing entry, with a test red without it. | `[cause: guard-gap]` |
| **Dv448** | The contract prices a killed boot at «≈$0.12 at $0.59/h». The 4090 in EU-RO-1 reads **$0.74/h** today, so every figure is recomputed and the killed boot is $0.148. | `[cause: read-the-price]` |
| **Dv449** | v4's first draft of gate 3 projected the remainder one way; v3 had registered the pessimistic max of two, and «everything else copied» covers it. Restored before the pod existed. | `[cause: my-omission]` |
| **Dv450** | `score_reader_v3.money()` gained `ledger_path`/`phase` parameters so bar 5 has ONE implementation across generations. Resolved at call time, not bound as a default — v3's own suite caught that in one run. The daily log's sha for that file is superseded. | `[cause: one-reading]` |
| **Dv451** | The contract says «score with `scripts/score_reader_v3.py` … pointed at v4's bars». Done by CALLING it from a new `scripts/score_reader_v4.py` rather than editing a shipped artefact; the report says so where a reader will look. | `[cause: reading-of-the-clause]` |
| **Dv452** | The on-pod runner was scp'd to `/workspace/`, not into `/workspace/repo/scripts/`, so the checkout stays clean and `git status --short` remains the staging proof. | `[cause: keep-the-proof]` |
| **Dv453** | `--gate` reads the Mac's copy of a file the pod writes. The runbook puts the scp inside the poll loop and the record carries `read_from` with the copy's age. | `[cause: two-machines]` |
| **Dv454** | The detached-launch ssh call timed out at 2 min although the runner had started: `nohup … &` still holds the ssh channel. Verified alive by `pgrep -af` on the pod; the boot was already running and nothing was lost. | `[cause: ssh-detach]` |
| **Dv455** | The step could not be CLOSED — the billing walk answers «no billing rows yet». $0.2446 stands as a LOWER BOUND and closing is a named debt. | `[cause: billing-lag]` |

## 8. Verify

```
$ make check
2685 passed, 2 skipped in 295.41s (0:04:55)          # baseline at 48a32d7 + tail: 2645 passed, 2 skipped

$ runpodctl pod list -a
[]

$ python3 scripts/runpod_guard.py --step reader-v4 --step-cap 0.35
READER-V4 SPENT      $0.2446 of $0.35  (anchor $22.07 from runpod_balance_at_reader-v4_start)
  balance delta   $0.2446
  billing since   UNAVAILABLE (no billing rows yet) — the delta stands alone as a LOWER BOUND

$ shasum -a 256 results/prereg_reader_probe_v4.json
8a26784c85deb8064747e78af2296121b6ebebc531bfc830bfdc52d2afe717e9

$ PYTHONPATH=src python3 scripts/write_reader_prereg_v4.py --out /tmp/again.json && cmp results/prereg_reader_probe_v4.json /tmp/again.json
byte-identical rebuild: OK

$ PYTHONPATH=src python3 scripts/score_reader_v4.py
wrote results/reader_v4_verdict.json  sha256 7f5c96c8352ad052…
  outcome GO · 23 of 23 threads read
  bar 1_flagships                SCORED — False (collapsed)
  bar 2_entity_cases             SCORED — True
  bar 3_noise                    SCORED — True
  bar 4_per_comment_agreement    SCORED — False (collapsed)
  bar 5_time_and_cost            OPEN — passed None
  replies: 19 parsed · 4 refused
  refusals by shape: {'missing field: evidence': 1, 'signals.aspect is not a string': 1,
                      'two disagreeing objects: name': 1, 'two disagreeing objects: quote': 1}
  repairs fired: {…all nine registered names: 0}
  finish_reason length: 0 · tokens per requested per_comment row: 137.83
```

The per-commit rule: `make check` was green at `48a32d7` (2 645 / 2 skipped) before the tail, red for
exactly the two commits between the v3 close and its repair — `bf2502f` (the close) and `05df60d`
(the anchor), both of which carry ledger data and no code — and green again from `ae7be77` onward.
That redness is Dv447 and it is named rather than rewritten: the ledger a guard refused to accept is
the honest history.

## 9. Process signals

1. **The gate that could fire was the whole difference.** v3 registered a go/no-go downstream of an
   unbounded boot and had no branch that could stop it; v4 put a clock on the resource that spends
   and every deadline was checked while the money ran. Same cap, same instrument, same population:
   $0.3918 for nothing, then $0.2446 for all 23 threads.
2. **Two of this contract's best moves were corrections found before the money.** The card is $0.74/h
   and not $0.59; the projection had one leg and needed two. Both were free to find and both would
   have been expensive to discover from a bill.
3. **The suite caught the guard, not the model.** Closing the v3 step reddened a check written weeks
   ago for exactly this silence, and it named the file, the timestamp and the balance. A guard that
   has never been seen to fire is a guard nobody has tested; this one fired on its author.
4. **The collapse was worth measuring and is not the answer.** Ruling 4 lifts bar 1 from 1 to 2 and
   bar 4 from 0.357 to 0.500. The four remaining bar-4 disagreements are not vocabulary at all —
   they are the reader calling a comment about a category a comment about the chain.
5. **The instrument's parse half was bought and never used.** Zero container repairs fired across 23
   replies; the refuse-on-conflict clause removed two. What recovered six replies against probe-b was
   not a repair, and the registration is right that no ablation was bought to say more than that.

## 10. What is open

- **Close the step** once the walk posts:
  `python3 scripts/runpod_guard.py --step reader-v4 --step-cap 0.35 --close --note "reader-v4 settled"`.
  Refusing over an unanswered walk is the correct behaviour and it did.
- **The bars failed and the attempt is spent.** By the registration's own clause the next move is a
  design sitting and a new registration — not another pass at this one. The evidence a sitting needs
  is on disk per row: the request, the raw reply, the parse outcome and the seconds.
- **The window is priced but not opened.** 137.83 tokens per requested `per_comment` row against a
  2 000-token ceiling and a largest thread of 125 payable comments is a decision for the operator,
  not a run.
